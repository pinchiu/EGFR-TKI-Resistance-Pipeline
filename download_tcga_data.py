import requests
import json
import os
import gzip
import shutil
import yaml
import pandas as pd

# --- Configuration ---
def load_config():
    with open("config.yaml", "r") as f:
        return yaml.safe_load(f)

config = load_config()
PROJECT_ID = config['project']['id']
DATA_FORMAT = config['project']['data_format']
WORKFLOW_TYPE = config['project']['workflow_type']
SAVE_DIR = config['paths']['data_dir']
FINAL_FILENAME = os.path.basename(config['paths']['raw_maf'])

def get_file_ids(num_files=50):
    """
    Search for file IDs via GDC API.
    """
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

    print(f"正在搜尋 {PROJECT_ID} 中的 {num_files} 個 {WORKFLOW_TYPE} 檔案...")
    response = requests.get(files_endpt, params=params)
    
    if response.status_code != 200:
        print("API 請求失敗")
        return []

    data = response.json()
    if data['data']['hits']:
        hits = data['data']['hits']
        print(f"找到 {len(hits)} 個檔案。")
        return hits
    else:
        print("未找到符合的檔案。")
        return []

def download_file(file_id, file_name):
    """
    Download file by ID.
    """
    data_endpt = f"https://api.gdc.cancer.gov/data/{file_id}"
    
    if not os.path.exists(SAVE_DIR):
        os.makedirs(SAVE_DIR)
        
    save_path = os.path.join(SAVE_DIR, file_name)
    
    if os.path.exists(save_path):
        print(f"檔案 {file_name} 已存在。跳過。")
        return save_path
    
    print(f"正在下載 {file_name}...")
    
    try:
        with requests.get(data_endpt, stream=True) as r:
            r.raise_for_status()
            with open(save_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192): 
                    f.write(chunk)
    except Exception as e:
        print(f"下載失敗 {file_name}: {e}")
        return None
                
    return save_path

def unzip_file(gz_path):
    """
    Unzip .gz file.
    """
    if not gz_path or not gz_path.endswith('.gz'):
        return gz_path
        
    unzipped_path = gz_path[:-3] # Remove .gz
    
    if os.path.exists(unzipped_path):
        return unzipped_path

    print(f"正在解壓縮：{os.path.basename(gz_path)} ...")
    
    try:
        with gzip.open(gz_path, 'rb') as f_in:
            with open(unzipped_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
    except Exception as e:
        print(f"解壓縮失敗 {gz_path}: {e}")
        return None
            
    return unzipped_path

def merge_mafs(file_paths, output_path):
    print(f"正在合併 {len(file_paths)} 個 MAF 檔案...")
    
    dfs = []
    for p in file_paths:
        if p and os.path.exists(p):
            try:
                # Read only necessary columns to save memory, or read all if needed
                # MAF files can be messy, use low_memory=False
                df = pd.read_csv(p, sep='\t', comment='#', low_memory=False)
                dfs.append(df)
            except Exception as e:
                print(f"讀取錯誤 {p}: {e}")
    
    if not dfs:
        print("沒有數據可合併。")
        return

    merged_df = pd.concat(dfs, ignore_index=True)
    merged_df.to_csv(output_path, sep='\t', index=False)
    print(f"已合併 MAF 儲存至 {output_path}")
    print(f"總突變數：{len(merged_df)}")

if __name__ == "__main__":
    final_path = os.path.join(SAVE_DIR, FINAL_FILENAME)
    
    # Check if final file already exists
    if os.path.exists(final_path):
        print(f"檔案 {final_path} 已存在。跳過下載步驟。")
    else:
        # 1. Get List of Files
        files_info = get_file_ids(num_files=50) # Try 50 files
        
        maf_files = []
        
        # 2. Download and Unzip Loop
        for info in files_info:
            gz_path = download_file(info['file_id'], info['file_name'])
            maf_path = unzip_file(gz_path)
            if maf_path:
                maf_files.append(maf_path)
                
        # 3. Merge
        if maf_files:
            merge_mafs(maf_files, final_path)
            
            # Cleanup individual files
            print("正在清理臨時檔案...")
            for p in maf_files:
                if os.path.exists(p):
                    os.remove(p)
                # Also try to remove the .gz version if it exists
                gz_p = p + ".gz"
                if os.path.exists(gz_p):
                    os.remove(gz_p)
                    
            print("完成！")
            print(f"合併後的 MAF 檔案位置：")
            print(os.path.abspath(final_path))