import subprocess
import sys
import time

def run_step(script_name, description):
    print(f"--- 步驟：{description} ({script_name}) ---")
    start_time = time.time()
    
    try:
        # Run the script using the current python interpreter
        result = subprocess.run([sys.executable, script_name], check=True)
        elapsed = time.time() - start_time
        print(f"步驟完成，耗時 {elapsed:.2f} 秒。\n")
    except subprocess.CalledProcessError as e:
        print(f"執行錯誤 {script_name}: {e}")
        sys.exit(1)

def main():
    print("開始執行 EGFR 突變分析流程...")
    print("=" * 50)
    
    # 1. Download
    run_step("download_tcga_data.py", "數據獲取")
    
    # 2. Clean
    run_step("clean_data.py", "數據清理")
    
    # 3. Analyze
    run_step("analyze_cooccurrence.py", "共現性分析")
    
    # 4. Visualize
    run_step("visualize_results.py", "視覺化")
    
    print("=" * 50)
    print("流程執行成功完成。")

if __name__ == "__main__":
    main()
