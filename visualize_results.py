import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import yaml
import os

# --- Configuration ---
def load_config():
    with open("config.yaml", "r") as f:
        return yaml.safe_load(f)

config = load_config()
INPUT_FILE = config['paths']['cleaned_csv']
PATIENT_FILE = os.path.join(config['paths']['output_dir'], "patient_analysis.csv")
OUTPUT_DIR = config['paths']['output_dir']

def visualize_results():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        
    # Set style (no emojis, clean look)
    sns.set_theme(style="whitegrid")
    # 設定字型：優先使用 Noto Sans CJK JP (Docker default for CJK), 回退到 Microsoft JhengHei (Windows)
    plt.rcParams['font.sans-serif'] = ['Noto Sans CJK JP', 'Noto Sans CJK TC', 'Noto Sans CJK SC', 'Microsoft JhengHei', 'DejaVu Sans']
    plt.rcParams['axes.unicode_minus'] = False

    
    # 1. Mutation Frequency Bar Chart
    print("正在產生突變頻率圖表...")
    try:
        df = pd.read_csv(INPUT_FILE)
    except FileNotFoundError:
        print(f"錯誤：找不到檔案 {INPUT_FILE}。")
        return

    plt.figure(figsize=(12, 6))
    mutation_counts = df['Mutation_Group'].value_counts()
    sns.barplot(x=mutation_counts.index, y=mutation_counts.values, palette="viridis")
    plt.title("TCGA-LUAD 中的 EGFR 突變頻率")
    plt.xlabel("突變類型")
    plt.ylabel("數量")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "mutation_frequency.png"))
    plt.close()
    
    # 2. Co-occurrence Status Bar Chart
    print("正在產生共現狀態圖表...")
    try:
        patient_df = pd.read_csv(PATIENT_FILE)
    except FileNotFoundError:
        print(f"錯誤：找不到檔案 {PATIENT_FILE}。請先執行 analyze_cooccurrence.py。")
        return

    plt.figure(figsize=(8, 6))
    status_counts = patient_df['Status'].value_counts()
    sns.barplot(x=status_counts.index, y=status_counts.values, palette="magma")
    plt.title("病人突變狀態分佈")
    plt.xlabel("狀態")
    plt.ylabel("病人數量")
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "patient_status.png"))
    plt.close()

    print(f"視覺化完成。圖表已儲存至 {OUTPUT_DIR} 資料夾")

if __name__ == "__main__":
    visualize_results()
