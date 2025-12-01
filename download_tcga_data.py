import requests
import json
import os
import gzip
import shutil
import yaml
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm 

# --- Configuration ---
def load_config():
    try:
        with open("config.yaml", "r") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        # Fallback config if file not found
        return {
            'project': {'id': 'TCGA-LUAD', 'data_format': 'MAF', 'workflow_type': 'Aliquot Ensemble Somatic Variant Merging and Masking'},
            'paths': {'data_dir': './data', 'raw_maf': 'tcga_luad_all_merged.maf'}
        }

config = load_config()
PROJECT_ID = config['project']['id']
DATA_FORMAT = config['project']['data_format']
WORKFLOW_TYPE = config['project']['workflow_type']
SAVE_DIR = config['paths']['data_dir']
FINAL_FILENAME = os.path.basename(config['paths']['raw_maf'])
MAX_WORKERS = 10 # 設定同時下載的線程數 (建議 5-20)

def get_file_ids(num_files=10000):
    """ Search for file IDs via GDC API """
    files_endpt = "https://api.gdc.cancer.gov/files"
    
    filters = {
        "op": "and",
        "content": [
            {"op": "=", "content": {"field": "cases.project.project_id", "value": PROJECT_ID}},
            {"op": "=", "content": {"field": "files.data_format", "value": DATA_FORMAT}},
            {"op": "=", "content": {"field": "analysis.workflow_type", "value": WORKFLOW_TYPE}},
            {"op": "=", "content": {"field": "access", "value": "open"}} 
        ]
    }

    params = {
        "filters": json.dumps(filters),
        "fields": "file_id,file_name,file_size",
        "format": "json",
        "size": str(num_files)
    }

    print(f"Searching for files in {PROJECT_ID}...")
    response = requests.get(files_endpt, params=params)
    data = response.json()
    
    if response.status_code == 200 and data['data']['hits']:
        hits = data['data']['hits']
        print(f"Found {len(hits)} files.")
        return hits
    return []

def download_file(file_info):
    """ Wrapper function for threading """
    file_id = file_info['file_id']
    file_name = file_info['file_name']
    
    data_endpt = f"https://api.gdc.cancer.gov/data/{file_id}"
    
    if not os.path.exists(SAVE_DIR):
        os.makedirs(SAVE_DIR, exist_ok=True)
        
    save_path = os.path.join(SAVE_DIR, file_name)
    
    # Skip if exists
    if os.path.exists(save_path):
        return save_path
    
    try:
        with requests.get(data_endpt, stream=True) as r:
            r.raise_for_status()
            with open(save_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192): 
                    f.write(chunk)
        return save_path
    except Exception:
        return None

def unzip_file(gz_path):
    """ Unzip .gz file """
    if not gz_path or not gz_path.endswith('.gz'):
        return gz_path
    unzipped_path = gz_path[:-3]
    if os.path.exists(unzipped_path):
        return unzipped_path
    try:
        with gzip.open(gz_path, 'rb') as f_in:
            with open(unzipped_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        return unzipped_path
    except Exception:
        return None

def merge_mafs(file_paths, output_path):
    print(f"Merging {len(file_paths)} MAF files...")
    dfs = []
    
    # 這裡也可以優化，但記憶體通常是瓶頸，所以維持循序讀取比較安全
    for p in tqdm(file_paths, desc="Reading CSVs"):
        if p and os.path.exists(p):
            try:
                # 只讀取重要欄位以節省記憶體
                use_cols = ['Hugo_Symbol', 'Variant_Classification', 'HGVSp_Short', 'Tumor_Sample_Barcode', 'Chromosome', 'Start_Position']
                df = pd.read_csv(p, sep='\t', comment='#', low_memory=False, usecols=lambda c: c in use_cols)
                dfs.append(df)
            except Exception:
                pass
    
    if dfs:
        merged_df = pd.concat(dfs, ignore_index=True)
        merged_df.to_csv(output_path, sep='\t', index=False)
        print(f"Done! Merged file: {output_path}")
        print(f"Total mutations: {len(merged_df)}")

if __name__ == "__main__":
    final_path = os.path.join(SAVE_DIR, FINAL_FILENAME)
    
    if os.path.exists(final_path):
        print(f"Target file {final_path} already exists.")
    else:
        # 1. Get List
        files_info = get_file_ids()
        
        maf_paths = []
        gz_paths = []

        # 2. Parallel Download (多執行緒下載)
        print(f"Starting parallel download with {MAX_WORKERS} workers...")
        
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            # Submit tasks
            future_to_file = {executor.submit(download_file, info): info for info in files_info}
            
            # Process results as they complete
            for future in tqdm(as_completed(future_to_file), total=len(files_info), desc="Downloading"):
                result_path = future.result()
                if result_path:
                    gz_paths.append(result_path)

        # 3. Parallel Unzip (多執行緒解壓縮)
        print("Starting parallel unzip...")
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            maf_paths = list(tqdm(executor.map(unzip_file, gz_paths), total=len(gz_paths), desc="Unzipping"))

        # Filter out None
        maf_paths = [p for p in maf_paths if p]

        # 4. Merge
        if maf_paths:
            merge_mafs(maf_paths, final_path)
            
            # Cleanup
            print("Cleaning up temporary files...")
            for p in maf_paths:
                if os.path.exists(p): os.remove(p)
                gz = p + ".gz"
                if os.path.exists(gz): os.remove(gz)