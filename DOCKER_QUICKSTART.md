# Docker 快速入門指南

這是最簡單的 Docker 執行步驟說明。

---

## 前置準備

### 確認 Docker 已安裝

開啟 PowerShell 或終端機，執行：

```powershell
docker --version
```

如果看到版本號（例如 `Docker version 28.5.1`），表示已安裝。

如果沒有安裝，請到 https://www.docker.com/get-started 下載並安裝 Docker Desktop。

---

## 執行步驟

### 步驟 1: 開啟終端機並切換到專案目錄

**Windows PowerShell:**
```powershell
cd E:\概論
```

**或使用英文路徑（如果您已移動專案）:**
```powershell
cd E:\egfr-analysis
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

**預期結果：**
- 會在專案目錄下建立 `data/` 和 `results/` 兩個資料夾

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

## 完整範例（複製貼上即可）

如果您想一次執行所有步驟，可以複製以下指令：

```powershell
# 切換到專案目錄
cd E:\概論

# 建立 Docker 映像
docker build -t egfr-analysis .

# 建立資料目錄
New-Item -ItemType Directory -Force -Path data, results

# 執行分析
docker run --rm -v ${PWD}/data:/app/data -v ${PWD}/results:/app/results egfr-analysis

# 查看結果
Get-ChildItem results
```

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

### Q3: 如果只想執行特定步驟？

**只下載資料：**
```powershell
docker run --rm -v ${PWD}/data:/app/data egfr-analysis python download_tcga_data.py
```

**只清洗資料：**
```powershell
docker run --rm -v ${PWD}/data:/app/data egfr-analysis python clean_data.py
```

**只分析：**
```powershell
docker run --rm -v ${PWD}/data:/app/data -v ${PWD}/results:/app/results egfr-analysis python analyze_cooccurrence.py
```

**只視覺化：**
```powershell
docker run --rm -v ${PWD}/data:/app/data -v ${PWD}/results:/app/results egfr-analysis python visualize_results.py
```

### Q4: 如何進入容器內部除錯？

**解決方法：**
```powershell
docker run -it --rm -v ${PWD}/data:/app/data -v ${PWD}/results:/app/results egfr-analysis /bin/bash
```

進入後可以手動執行指令：
```bash
ls -la data/
python download_tcga_data.py
python clean_data.py
exit  # 離開容器
```

---

## 清理 Docker 資源

如果想清理 Docker 映像和容器以釋放空間：

```powershell
# 刪除 egfr-analysis 映像
docker rmi egfr-analysis

# 清理所有未使用的映像和容器
docker system prune -a
```

---

## 需要更多協助？

- 詳細的疑難排解：請參考 [DOCKER_GUIDE.md](DOCKER_GUIDE.md)
- 完整的專案說明：請參考 [README.md](README.md)
