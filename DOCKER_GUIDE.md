# EGFR 突變分析專案 - Docker 使用指南

本文件提供詳細的 Docker 使用說明和疑難排解步驟。

## 目錄
1. [前置檢查](#前置檢查)
2. [使用 Docker 執行](#使用-docker-執行)
3. [使用 Docker Compose 執行](#使用-docker-compose-執行)
4. [疑難排解](#疑難排解)

---

## 前置檢查

### 1. 確認 Docker 已安裝並運行

**Windows:**
```powershell
# 檢查 Docker 版本
docker --version

# 檢查 Docker 是否運行
docker ps
```

**Linux / macOS:**
```bash
# 檢查 Docker 版本
docker --version

# 檢查 Docker 服務狀態
sudo systemctl status docker  # Linux
docker ps  # macOS
```

如果看到錯誤訊息，請：
- **Windows**: 啟動 Docker Desktop
- **Linux**: `sudo systemctl start docker`
- **macOS**: 啟動 Docker Desktop

### 2. 確認 Docker Compose 已安裝

```bash
# 舊版本
docker-compose --version

# 新版本（Docker Compose V2）
docker compose version
```

---

## 使用 Docker 執行

### 步驟 1: 建立 Docker 映像

```bash
cd /path/to/project  # 切換到專案目錄
docker build -t egfr-analysis .
```

**預期輸出範例：**
```
[+] Building 45.2s (12/12) FINISHED
 => [1/7] FROM docker.io/library/python:3.9-slim
 => [2/7] WORKDIR /app
 ...
 => Successfully tagged egfr-analysis:latest
```

### 步驟 2: 建立目錄

```bash
# Windows PowerShell
New-Item -ItemType Directory -Force -Path data, results

# Linux / macOS / Git Bash
mkdir -p data results
```

### 步驟 3: 執行容器

**Windows PowerShell:**
```powershell
docker run --rm `
  -v ${PWD}/data:/app/data `
  -v ${PWD}/results:/app/results `
  egfr-analysis
```

**Linux / macOS / Git Bash:**
```bash
docker run --rm \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/results:/app/results \
  egfr-analysis
```

**Windows CMD:**
```cmd
docker run --rm -v %cd%/data:/app/data -v %cd%/results:/app/results egfr-analysis
```

---

## 使用 Docker Compose 執行

### 方法 A: 使用新版指令（推薦）

```bash
# 建立並執行
docker compose up

# 背景執行
docker compose up -d

# 查看日誌
docker compose logs -f

# 停止
docker compose down
```

### 方法 B: 使用舊版指令

```bash
# 建立並執行
docker-compose up

# 背景執行
docker-compose up -d

# 查看日誌
docker-compose logs -f

# 停止
docker-compose down
```

---

## 疑難排解

### 問題 1: Docker Desktop 未啟動

**錯誤訊息：**
```
error during connect: Get "http://.../pipe/dockerDesktopLinuxEngine/..."
```

**解決方法：**
1. 啟動 Docker Desktop 應用程式
2. 等待 Docker 完全啟動（圖示變綠）
3. 重新執行指令

### 問題 2: 專案名稱錯誤（中文目錄）

**錯誤訊息：**
```
project name must not be empty
```

**解決方法 A: 移動專案到英文路徑**
```bash
# 將專案移至英文路徑
move "E:\概論" "E:\egfr-analysis"
cd E:\egfr-analysis
```

**解決方法 B: 使用 docker run 而非 docker-compose**
直接使用方法 2 的 `docker run` 指令。

### 問題 3: 權限錯誤（Linux）

**錯誤訊息：**
```
Permission denied: '/app/data'
```

**解決方法：**
```bash
# 修改目錄權限
sudo chown -R $USER:$USER data results

# 或使用 sudo 執行
sudo docker-compose up
```

### 問題 4: 映像建立失敗

**錯誤訊息：**
```
failed to solve with frontend dockerfile.v0
```

**解決方法：**
```bash
# 清理 Docker 快取
docker system prune -a

# 重新建立（不使用快取）
docker build --no-cache -t egfr-analysis .

# 或使用 docker-compose
docker-compose build --no-cache
```

### 問題 5: 網路連線問題

**錯誤訊息：**
```
Could not connect to GDC API
```

**解決方法：**
1. 檢查網路連線
2. 如果在公司網路，可能需要設定 proxy：

```bash
# 設定 proxy（如果需要）
docker build --build-arg HTTP_PROXY=http://proxy.example.com:8080 \
             --build-arg HTTPS_PROXY=http://proxy.example.com:8080 \
             -t egfr-analysis .
```

### 問題 6: 磁碟空間不足

**錯誤訊息：**
```
no space left on device
```

**解決方法：**
```bash
# 清理未使用的映像和容器
docker system prune -a

# 查看磁碟使用情況
docker system df
```

### 問題 7: 容器無法存取本地檔案

**症狀：** 容器執行後，`data/` 或 `results/` 目錄是空的

**解決方法：**

**Windows - 確認 Docker Desktop 設定：**
1. 開啟 Docker Desktop
2. Settings → Resources → File Sharing
3. 確認專案所在磁碟機（如 E:\）已被加入共享清單
4. 重新啟動 Docker Desktop

**Linux - 使用絕對路徑：**
```bash
docker run --rm \
  -v /absolute/path/to/data:/app/data \
  -v /absolute/path/to/results:/app/results \
  egfr-analysis
```

---

## 驗證安裝

執行以下指令測試 Docker 是否正常運作：

```bash
# 測試 Docker
docker run hello-world

# 測試 Python 容器
docker run --rm python:3.9-slim python --version
```

如果以上指令都能正常執行，表示 Docker 環境正常。

---

## 進階技巧

### 只執行特定階段

```bash
# 只下載資料
docker run --rm -v $(pwd)/data:/app/data egfr-analysis python download_tcga_data.py

# 只清洗資料
docker run --rm -v $(pwd)/data:/app/data egfr-analysis python clean_data.py

# 只分析
docker run --rm -v $(pwd)/data:/app/data -v $(pwd)/results:/app/results egfr-analysis python analyze_cooccurrence.py
```

### 進入容器除錯

```bash
docker run -it --rm \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/results:/app/results \
  egfr-analysis /bin/bash
```

進入後可以：
```bash
# 查看檔案
ls -la data/
ls -la results/

# 手動執行腳本
python download_tcga_data.py

# 安裝額外工具
apt-get update && apt-get install -y vim
```

---

## 需要協助？

如果遇到其他問題，請：
1. 檢查 Docker Desktop 是否正常運行
2. 查看詳細錯誤訊息：`docker-compose logs`
3. 確認專案路徑不包含中文字元
4. 嘗試使用 `docker run` 而非 `docker-compose`
