# EGFR 突變分析專案完整詳解

這個系統的目標是從 TCGA 資料庫下載肺腺癌 (LUAD) 的基因數據，並分析 EGFR 基因的致病突變與抗藥性突變是否同時存在 (Co-occurrence)。


## 1. 環境需求 (Requirements)

本專案需要 Python 3.x 環境，並安裝以下套件：
*   `pandas`: 數據處理
*   `requests`: 網路下載
*   `matplotlib`: 繪圖基礎
*   `seaborn`: 進階繪圖
*   `pyyaml`: 讀取設定檔

您可以透過以下指令一次安裝所有套件：

```bash
pip install -r requirements.txt
```

---

## 2. 程式碼運作詳解 (Code Explanation)

這份文件將逐一解釋每個程式檔案中的程式碼區塊在做什麼。

### 1. 設定檔 (config.yaml)
這是整個專案的控制中心。

#### [區塊 1: Project 設定]
```yaml
project:
  id: "TCGA-LUAD" ...
```
說明：設定我們要從 GDC 資料庫抓取哪個專案的資料 (肺腺癌 TCGA-LUAD)，以及要抓取的資料格式 (MAF)。

#### [區塊 2: Paths 路徑]
```yaml
paths:
  data_dir: "./data" ...
```
說明：定義檔案要存在哪裡。
- `raw_maf`: 下載下來的原始大檔名。
- `cleaned_csv`: 清洗後只剩 EGFR 的檔名。
- `output_dir`: 最終圖表輸出的資料夾。

#### [區塊 3: Analysis 分析參數]
```yaml
analysis:
  gene: "EGFR"
  mutations: ...
```
說明：定義我們要分析的基因 (EGFR) 以及哪些突變算「致病 (Sensitizing)」、哪些算「抗藥 (Resistance)」。

### 2. 下載腳本 (download_tcga_data.py)
負責從網路下載數據。

#### [區塊 1: 載入套件與設定]
```python
import requests ...
def load_config(): ...
```
說明：載入必要的工具包 (requests 用來上網抓資料)，並讀取 config.yaml 裡的設定。

#### [區塊 2: get_file_ids 函式]
```python
def get_file_ids(num_files=50):
    files_endpt = "https://api.gdc.cancer.gov/files"
    filters = { ... }
```
說明：這是「搜尋」功能的實作。
- 它會向 GDC API 發送請求。
- filters 設定了搜尋條件：要是 TCGA-LUAD 專案、要是 MAF 格式、要是 Open Access (公開) 的資料。
- 最後回傳找到的檔案 ID 列表。

#### [區塊 3: download_file 函式]
```python
def download_file(file_id, file_name):
    data_endpt = f"https://api.gdc.cancer.gov/data/{file_id}"
    with requests.get(...) as r: ...
```
說明：這是「下載」功能的實作。
- 根據檔案 ID 下載具體的檔案。
- 使用 stream=True 模式，這樣下載大檔案時才不會把記憶體撐爆。

#### [區塊 4: merge_mafs 函式]
```python
def merge_mafs(file_paths, output_path):
    dfs = []
    for p in file_paths:
        df = pd.read_csv(...)
    merged_df = pd.concat(...)
```
說明：這是「合併」功能的實作。
- 因為我們下載了 50 個病人的小檔案，這個函式把這 50 個表格「黏」在一起 (pd.concat)，變成一個大表格。

#### [區塊 5: Main 主程式]
```python
if __name__ == "__main__":
    if os.path.exists(final_path):
        print("檔案已存在...")
    else:
        files_info = get_file_ids(...)
        # ... 下載與合併 ...
```
說明：程式的進入點。
1. **檢查檔案**: 先檢查最終的 MAF 檔案是否已經存在。
2. **跳過**: 如果存在，直接跳過下載步驟，節省時間。
3. **執行下載**: 如果不存在，才執行搜尋、下載、解壓縮、合併與清理的完整流程。

### 3. 清洗腳本 (clean_data.py)
負責把雜訊濾掉，只留精華。

#### [區塊 1: classify_mutation 函式 (核心邏輯)]
```python
def classify_mutation(row):
    hgvsp = str(row['HGVSp_Short'])
    if 'L858R' in hgvsp: return "L858R"
    if 'T790M' in hgvsp: return "T790M"
    ...
```
說明：這是最重要的大腦。
- 它讀取每一行數據的「蛋白質變化 (HGVSp_Short)」欄位。
- 如果看到 "L858R"，就貼上 "L858R" 的標籤。
- 如果看到 "T790M"，就貼上 "T790M" 的標籤。
- 這是我們定義什麼是「致病」和「抗藥」的地方。

#### [區塊 2: process_maf 函式]
```python
def process_maf():
    df = pd.read_csv(...)
    egfr_df = df[df['Hugo_Symbol'] == 'EGFR'].copy()
    egfr_df['Mutation_Group'] = egfr_df.apply(classify_mutation, axis=1)
```
說明：
1. 讀取原始大檔。
2. `df['Hugo_Symbol'] == 'EGFR'`：這行指令把所有不是 EGFR 的基因都丟掉。
3. `.apply(classify_mutation)`：對篩選出來的每一行，執行上面的分類函式。
4. 最後存成 CSV。

### 4. 分析腳本 (analyze_cooccurrence.py)
負責統計分析。

#### [區塊 1: analyze_cooccurrence 函式]
```python
def analyze_cooccurrence(df_clean):
    # ...
    patient_mutations = df_clean.groupby('Tumor_Sample_Barcode')['HGVSp_Short'].apply(set).reset_index()
```
說明：
- `groupby`: 將數據按病人分組。
- `.apply(set)`: 收集每個病人的所有突變 (HGVSp_Short)，例如 `{p.L858R, p.T790M}`。

#### [區塊 2: 統計邏輯]
```python
# 計算單獨突變數量
mutation_counts = Counter(all_mutations)

# 找 L858R + T790M 組合
l858r_t790m_cases = patient_mutations[
    patient_mutations['HGVSp_Short'].apply(
        lambda x: any('L858R' in m for m in x) and any('T790M' in m for m in x)
    )
]
```
說明：
- 使用 `Counter` 計算所有突變的出現頻率。
- 使用 `lambda` 函數精確篩選同時帶有 **L858R** 和 **T790M** 的病人，這是驗證抗藥性機制的核心步驟。
- 程式會輸出詳細的統計數字 (包含百分比) 和 Emoji 標示的結果。

### 5. 視覺化腳本 (visualize_results.py)
負責畫圖。

#### [區塊 1: 繪圖設定]
```python
sns.set_theme(style="whitegrid")
```
說明：設定圖表的風格，讓背景有格線，比較好看。

#### [區塊 2: 繪製長條圖]
```python
sns.barplot(x=mutation_counts.index, y=mutation_counts.values, palette="viridis")
```
說明：
- 使用 Seaborn (sns) 畫長條圖。
- x 軸是突變類型，y 軸是數量。
- palette="viridis" 設定顏色主題。
- `plt.savefig(...)` 把畫好的圖存成圖片檔。

### 6. 總指揮腳本 (run_pipeline.py)
負責按順序執行所有步驟。

#### [區塊 1: run_step 函式]
```python
def run_step(script_name, description):
    subprocess.run([sys.executable, script_name], check=True)
```
說明：這是一個通用的函式，用來執行其他的 Python 腳本。它會呼叫系統指令來跑程式。

#### [區塊 2: main 函式]
```python
def main():
    run_step("download_tcga_data.py", "Data Acquisition")
    run_step("clean_data.py", "Data Cleaning")
    ...
```
說明：
- 依序呼叫 run_step。
- 確保先下載，再清洗，再分析，最後畫圖。順序不能錯。

---

## 3. 系統架構與流程 (Workflow)

整個流水線分為五個階段，由 `run_pipeline.py` 負責統一指揮：

### 第一階段：資料獲取 (Data Acquisition)
*   **執行腳本**: `download_tcga_data.py`
*   **動作**:
    1.  讀取 `config.yaml` 設定檔。
    2.  **檢查機制**: 程式會先檢查 `data/TCGA_LUAD_Somatic_Mutations_Raw.maf` 是否已存在。
        *   **若存在**: 直接跳過下載，節省時間。
        *   **若不存在**: 才會向 GDC API 發送請求，下載並合併 50 個病人的數據。
    3.  **自動清理**: 下載完成後會刪除暫存檔。
*   **產出檔案**: `data/TCGA_LUAD_Somatic_Mutations_Raw.maf`

### 第二階段：資料清洗 (Data Cleaning)
*   **執行腳本**: `clean_data.py`
*   **動作**:
    1.  讀取原始 MAF 檔。
    2.  **篩選**: 只保留 `Hugo_Symbol` 為 "EGFR" 的資料列。
    3.  **分類 (Feature Identification)**: 根據蛋白質變化 (HGVSp_Short) 欄位，將突變貼上標籤：
        *   **致病突變 (Sensitizing)**: 如 L858R, Exon 19 Del。
        *   **抗藥突變 (Resistance)**: 如 T790M, C797S。
        *   **其他**: 無法歸類的突變。
*   **產出檔案**: `EGFR_Mutations_Cleaned_Processed.csv`

### 第三階段：共現性分析 (Co-occurrence Analysis)
*   **執行腳本**: `analyze_cooccurrence.py`
*   **動作**:
    1.  讀取清洗後的 CSV 檔。
    2.  **精確統計**: 使用 `Counter` 計算各種突變的發生頻率與百分比。
    3.  **尋找抗藥機制**: 專門篩選同時帶有 **L858R** 和 **T790M** 的病人，這是臨床上驗證獲得性抗藥性的關鍵指標。
    4.  **輸出報表**: 產生包含詳細統計數字的 CSV 報表。
*   **產出檔案**: 
    *   `results/cooccurrence_stats.csv` (詳細統計)
    *   `results/patient_analysis.csv` (用於繪圖的格式)

### 第四階段：視覺化 (Visualization)
*   **執行腳本**: `visualize_results.py`
*   **動作**:
    1.  使用 `matplotlib` 和 `seaborn` 繪圖庫。
    2.  **長條圖 1**: 各種 EGFR 突變出現的頻率 (Mutation Frequency)。
    3.  **長條圖 2**: 病人分類統計 (Patient Status)，顯示有多少人同時帶有抗藥性。
*   **產出檔案**: 
    *   `results/mutation_frequency.png`
    *   `results/patient_status.png`

---

## 4. 生物特殊名詞 (Biological Terms)

在代碼中，我們使用了以下生物學和生物資訊學的專有名詞：

*   **EGFR (Epidermal Growth Factor Receptor)**: 表皮生長因子受體。這是我們主要分析的基因，其突變與肺腺癌的治療反應密切相關。
*   **LUAD (Lung Adenocarcinoma)**: 肺腺癌。我們從 TCGA 下載的數據項目代碼 (TCGA-LUAD)。
*   **TCGA (The Cancer Genome Atlas)**: 癌症基因圖譜計畫。我們數據的來源資料庫。
*   **GDC (Genomic Data Commons)**: 基因組數據共享平台。我們通過其 API 下載數據。
*   **MAF (Mutation Annotation Format)**: 突變註釋格式。這是一種標準的文字檔案格式，用於儲存基因突變資訊。
*   **Sensitizing Mutations (敏感性突變)**: 這些突變會讓腫瘤對 TKI (酪氨酸激酶抑制劑) 藥物敏感（有效）。
    *   **L858R**: 第 21 外顯子上的點突變。
    *   **Exon 19 Del**: 第 19 外顯子的缺失突變 (Deletion)。
    *   **G719X, L861Q, S768I**: 其他較少見的敏感性突變。
*   **Resistance Mutations (抗藥性突變)**: 這些突變會導致腫瘤對第一代或第二代 TKI 藥物產生抗藥性。
    *   **T790M**: 最常見的抗藥性突變，位於第 20 外顯子。
    *   **C797S**: 與第三代 TKI 藥物抗藥性相關的突變。
    *   **Exon 20 Ins**: 第 20 外顯子的插入突變 (Insertion)，通常對傳統 TKI 藥物具有抗性。
*   **HGVSp_Short**: 蛋白質層次的變異表示法 (例如 p.L858R)。
*   **Hugo_Symbol**: 基因的標準符號 (例如 EGFR)。

## 5. 如何執行

在終端機中執行以下指令即可跑完所有流程：

```bash
python run_pipeline.py
```

## 5. 檔案結構說明

*   **`config.yaml`**: **控制中心**。所有的設定都在這裡，例如檔案路徑、基因名稱、突變列表。如果你想改分析別的基因 (例如 KRAS)，只要改這裡就好。
*   **`requirements.txt`**: **安裝清單**。列出了執行此程式需要的 Python 套件 (如 pandas, requests)。
*   **`EGFR_Resistance_Mutations_Ground_Truth.csv`**: **標準答案**。我們預先定義好的抗藥性突變列表，作為參考基準。

## 6. 資料流向圖 (Data Flow)

1.  **雲端 (GDC API)**
    ⬇️ 下載
2.  **原始數據 (`.maf`)**
    ⬇️ 清洗 (`clean_data.py`)
3.  **乾淨數據 (`.csv`)**
    ⬇️ 分析 (`analyze_cooccurrence.py`)
4.  **統計結果 (`.csv`)**
    ⬇️ 繪圖 (`visualize_results.py`)
5.  **圖表 (`.png`)**
