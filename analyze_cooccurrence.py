import pandas as pd
import numpy as np
from collections import Counter
import yaml
import os

# --- Configuration ---
def load_config():
    with open("config.yaml", "r") as f:
        return yaml.safe_load(f)

config = load_config()
INPUT_FILE = config['paths']['cleaned_csv']
OUTPUT_DIR = config['paths']['output_dir']

def analyze_cooccurrence(df_clean):
    """
    Stage 3: 找出 L858R+T790M 等組合
    輸入：cleaned_csv (從 Stage 2)
    輸出：那些統計數字！
    """
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    print("Stage 3: Co-occurrence Analysis")
    print("=" * 50)
    
    # Step 1: 按病人分組，每個病人有哪些突變
    # 我們同時收集 HGVSp_Short (用於細節) 和 Mutation_Group (用於統計)
    patient_data = df_clean.groupby('Tumor_Sample_Barcode').agg({
        'HGVSp_Short': set,
        'Mutation_Group': set
    }).reset_index()
    
    total_patients = len(patient_data)
    
    print(f" 共有 {total_patients} 位病人的腫瘤樣本被檢測出帶有 EGFR 基因突變")
    
    # Step 2: 計算突變群組數量 (Mutation Group Counts)
    # 這樣才能跟 visualize_results.py 的圖表對上 (圖表是畫 Group)
    all_groups = []
    for groups in patient_data['Mutation_Group']:
        all_groups.extend(groups)
    
    group_counts = Counter(all_groups)
    print("\n 突變群組統計 (對應圖表):")
    for group, count in group_counts.most_common(10):
        percentage = (count / total_patients) * 100
        print(f"  {group:30s}: {count:3d} 例 ({percentage:5.1f}%)")
    
    # Step 3: 找 L858R + T790M 組合 核心！
    # 為了兼容性，我們同時檢查有 'p.' 和沒有 'p.' 的情況，或者直接檢查關鍵字
    l858r_t790m_cases = patient_data[
        patient_data['HGVSp_Short'].apply(
            lambda x: any('L858R' in m for m in x) and any('T790M' in m for m in x)
        )
    ]
    
    l858r_count = len(patient_data[patient_data['HGVSp_Short'].apply(lambda x: any('L858R' in m for m in x))])
    t790m_count = len(patient_data[patient_data['HGVSp_Short'].apply(lambda x: any('T790M' in m for m in x))])
    combo_count = len(l858r_t790m_cases)
    
    print(f"\n 關鍵組合統計:")
    print(f"  L858R:      {l858r_count:3d} 病例 ({l858r_count/total_patients*100:5.1f}%)")
    print(f"  T790M:       {t790m_count:3d} 病例 ({t790m_count/total_patients*100:5.1f}%)")
    print(f"  L858R+T790M: {combo_count:3d} 病例 ({combo_count/total_patients*100:5.1f}%) ")
    
    # Step 4: 保存結果
    results = {
        'total_patients': total_patients,
        'l858r_only': l858r_count - combo_count,
        't790m_only': t790m_count - combo_count,
        'l858r_t790m_combo': combo_count,
        'patient_ids_with_combo': l858r_t790m_cases['Tumor_Sample_Barcode'].tolist()
    }
    
    output_path = os.path.join(OUTPUT_DIR, 'cooccurrence_stats.csv')
    pd.DataFrame([results]).to_csv(output_path, index=False)
    print(f"\n結果已保存: {output_path}")
    
    # 為了兼容 visualize_results.py，我們也產生舊格式的 patient_analysis.csv
    # 重新建構舊格式的 status
    old_results = []
    for idx, row in patient_data.iterrows():
        muts = row['HGVSp_Short']
        pid = row['Tumor_Sample_Barcode']
        has_sens = any(m for m in muts if 'L858R' in m or 'Exon 19' in m or 'del' in str(m).lower()) # 簡化判斷
        has_res = any(m for m in muts if 'T790M' in m or 'C797S' in m)
        
        status = "Other"
        if has_sens and has_res:
            status = "Co-occurrence"
        elif has_sens:
            status = "Sensitizing Only"
        elif has_res:
            status = "Resistance Only"
            
        old_results.append({
            "Patient_ID": pid,
            "Mutations": ", ".join(muts),
            "Status": status
        })
    pd.DataFrame(old_results).to_csv(os.path.join(OUTPUT_DIR, "patient_analysis.csv"), index=False)
    
    return results

if __name__ == "__main__":
    print(f"Reading data from {INPUT_FILE}...")
    try:
        df_clean = pd.read_csv(INPUT_FILE)
        results = analyze_cooccurrence(df_clean)
    except FileNotFoundError:
        print(f"Error: File {INPUT_FILE} not found.")
