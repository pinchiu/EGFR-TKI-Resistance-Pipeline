import pandas as pd
import re
import os
import yaml
from tqdm import tqdm

# --- Configuration ---
def load_config():
    with open("config.yaml", "r") as f:
        return yaml.safe_load(f)

config = load_config()
INPUT_FILE = config['paths']['raw_maf']
OUTPUT_FILE = config['paths']['cleaned_csv']

def classify_mutation(row):
    """
    Classify mutation type based on HGVSp_Short.
    """
    hgvsp = str(row['HGVSp_Short'])
    
    if pd.isna(hgvsp) or hgvsp == 'nan':
        return "Unknown"

    # 1. Sensitizing Mutations
    if 'L858R' in hgvsp:
        return "L858R"
    if re.search(r'(E746|L747|T751|A750|S752).*del', hgvsp): 
        return "Exon 19 Del"
    if 'G719' in hgvsp:
        return "G719X"
    if 'L861Q' in hgvsp:
        return "L861Q"
    if 'S768I' in hgvsp:
        return "S768I"

    # 2. Resistance Mutations
    if 'T790M' in hgvsp:
        return "T790M"
    if 'C797S' in hgvsp:
        return "C797S"
    
    # 3. Exon 20 Insertion
    # Includes 'ins' or 'dup' in the range of amino acids 763-775
    if ('ins' in hgvsp or 'dup' in hgvsp) and re.search(r'(76[3-9]|77[0-5])', hgvsp):
        return "Exon 20 Ins"

    # 4. Other EGFR Mutations
    return "Other EGFR Mutation"

def process_maf():
    print(f"開始讀取 {INPUT_FILE}...")
    
    use_cols = [
        'Hugo_Symbol',
        'HGVSp_Short',
        'Variant_Classification',
        'Tumor_Sample_Barcode',
        'Chromosome',
        'Start_Position'
    ]
    
    try:
        df = pd.read_csv(INPUT_FILE, sep='\t', comment='#', usecols=use_cols, low_memory=False)
    except FileNotFoundError:
        print(f"錯誤：找不到檔案 {INPUT_FILE}。")
        return

    print(f"原始數據包含 {len(df)} 個突變。")

    # Filter for EGFR
    egfr_df = df[df['Hugo_Symbol'] == 'EGFR'].copy()
    print(f"已過濾 EGFR 突變：{len(egfr_df)}")

    if len(egfr_df) == 0:
        print("警告：未發現 EGFR 數據。")
        return

    # Apply classification
    print("正在分類突變...")
    tqdm.pandas(desc="Classifying")
    egfr_df['Mutation_Group'] = egfr_df.progress_apply(classify_mutation, axis=1)

    # Save result
    egfr_df.to_csv(OUTPUT_FILE, index=False)
    print(f"處理完成。數據已儲存至：{OUTPUT_FILE}")
    print("-" * 30)
    print("初步統計：")
    print(egfr_df['Mutation_Group'].value_counts())

if __name__ == "__main__":
    process_maf()