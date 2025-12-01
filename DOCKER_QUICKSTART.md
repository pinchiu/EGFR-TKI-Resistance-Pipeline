# Docker 快速入門指南

這是最簡單的 Docker 執行步驟說明。

## 您將會得到什麼？
完成本指南後，您將會在電腦上自動完成：
1. 下載肺腺癌基因數據
2. 分析 EGFR 突變
3. 產生精美的統計圖表

---

## 前置準備

### 確認 Docker 已安裝

開啟 PowerShell 或終端機，執行：

```powershell
docker --version
```

如果看到版本號（例如 `Docker version 20.10.x`），表示已安裝。

如果沒有安裝，請到 https://www.docker.com/get-started 下載並安裝 Docker Desktop。

---

## 執行步驟

### 步驟 1: 下載專案 (Clone)

在新電腦的終端機執行：

```powershell
# 請將 URL 換成您的 GitHub 專案網址
git clone https://github.com/YOUR_USERNAME/egfr-analysis.git
cd egfr-analysis
```

### 步驟 2: 建立 Docker 映像

這個步驟會建立一個包含所有程式和依賴套件的 Docker 映像。

```powershell
docker build -t egfr-analysis .
```

**說明：**
- `docker build`: 建立映像的指令
- `-t egfr-analysis`: 為映像命名
- `.`: 使用當前目錄的 Dockerfile

**預期結果：**
- 會看到很多步驟在執行（Step 1/7, Step 2/7...）
- 包含安裝中文字型（Noto Sans CJK）以支援圖表中文顯示
- 最後顯示 `Successfully tagged egfr-analysis:latest`
- 大約需要 2-3 分鐘（首次建立）

### 步驟 3: 建立資料目錄

建立用來存放下載資料和分析結果的目錄。

```powershell
New-Item -ItemType Directory -Force -Path data, results
```

### 步驟 4: 執行分析

執行 Docker 容器來進行完整的 EGFR 突變分析。

```powershell
docker run --rm -v ${PWD}/data:/app/data -v ${PWD}/results:/app/results egfr-analysis
```

**說明：**
- `docker run`: 執行容器
- `--rm`: 執行完畢後自動刪除容器（但資料會保留）
- `-v ${PWD}/data:/app/data`: 將本地 `data/` 目錄掛載到容器內
- `-v ${PWD}/results:/app/results`: 將本地 `results/` 目錄掛載到容器內
- `egfr-analysis`: 使用我們剛才建立的映像

**預期結果：**
- 會看到分析流程的進度訊息
- 包含：資料下載 → 資料清洗 → 共現性分析 → 視覺化
- 最後顯示「流程執行成功完成」

### 步驟 5: 查看結果

分析完成後，檢查生成的檔案。

```powershell
# 查看 data 目錄
Get-ChildItem data

# 查看 results 目錄
Get-ChildItem results
```

**預期結果：**

**data/ 目錄應包含：**
- `TCGA_LUAD_Somatic_Mutations_Raw.maf` - 原始突變資料（約 22 MB）

**results/ 目錄應包含：**
- `cooccurrence_stats.csv` - 共現性統計資料
- `mutation_frequency.png` - 突變頻率圖表
- `patient_analysis.csv` - 病人分析資料
- `patient_status.png` - 病人狀態圖表

---

## 常見問題

### Q1: 如果看到 "Docker daemon is not running" 錯誤？

**解決方法：**
1. 開啟 Docker Desktop 應用程式
2. 等待 Docker 圖示變成綠色（表示已啟動）
3. 重新執行指令

### Q2: 如果想重新執行分析？

**解決方法：**
```powershell
# 刪除舊的資料
Remove-Item -Recurse -Force data, results

# 重新建立目錄
New-Item -ItemType Directory -Force -Path data, results

# 重新執行
docker run --rm -v ${PWD}/data:/app/data -v ${PWD}/results:/app/results egfr-analysis
```

### Q3: 如何在另一台電腦執行？

由於本專案已發布至 GitHub，在另一台電腦上執行非常簡單：

1.  **安裝 Docker Desktop**。
2.  **Git Clone** 下載專案。
3.  執行 `docker build` 和 `docker run`。

> **注意**：您 **不需要** 在新電腦上安裝 Python 或任何程式庫！Docker 會處理好所有環境。
