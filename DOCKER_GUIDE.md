# Docker 完整指南與疑難排解

本文件提供詳細的 Docker 使用說明，適用於進階使用者或遇到問題時參考。

---

## 目錄

1. [為什麼使用 Docker?](#為什麼使用-docker)
2. [詳細安裝步驟](#詳細安裝步驟)
3. [執行指令詳解](#執行指令詳解)
4. [疑難排解 (Troubleshooting)](#疑難排解-troubleshooting)
5. [進階技巧](#進階技巧)
6. [發布到 GitHub (GHCR)](#發布到-github-ghcr)

---

## 為什麼使用 Docker?

本專案使用 Docker 容器化技術，主要解決以下問題：
*   **環境一致性**：不管在 Windows, Mac 或 Linux，執行結果都一樣。
*   **簡化安裝**：不需要手動安裝 Python, pandas, matplotlib 等套件。
*   **隔離性**：不會影響您電腦上原本的 Python 環境。

---

## 詳細安裝步驟

### Windows
1. 下載 [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop/)。
2. 執行安裝程式，依指示完成安裝。
3. **重要**：安裝完成後，請重新啟動電腦。
4. 啟動 Docker Desktop，等待左下角圖示變綠。

### macOS
1. 下載 [Docker Desktop for Mac](https://www.docker.com/products/docker-desktop/) (注意選擇 Intel 或 Apple Silicon 版本)。
2. 拖曳到 Applications 資料夾。
3. 啟動 Docker，授權必要的權限。

### Linux (Ubuntu)
```bash
sudo apt-get update
sudo apt-get install docker.io
sudo usermod -aG docker $USER
# 重新登入以套用權限
```

---

## 執行指令詳解

### 1. 建立映像 (Build)

```bash
docker build -t egfr-analysis .
```
*   `-t`: Tag，給映像取名字。
*   `.`: Context，告訴 Docker 檔案在哪裡（這裡指當前目錄）。

### 2. 執行容器 (Run)

```bash
docker run --rm -v ${PWD}/data:/app/data -v ${PWD}/results:/app/results egfr-analysis
```
*   `--rm`: 容器停止後自動刪除，保持乾淨。
*   `-v`: Volume 掛載，格式為 `宿主機路徑:容器內路徑`。這讓容器可以看到您的檔案，並把結果存回您的電腦。

---

## 疑難排解 (Troubleshooting)

### 1. Docker daemon is not running
*   **症狀**：執行指令時出現 `error during connect: ...`
*   **原因**：Docker Desktop 沒開，或還沒啟動完成。
*   **解法**：開啟 Docker Desktop，等待燈號變綠。

### 2. 路徑問題 (Path not found)
*   **症狀**：`docker: Error response from daemon: ... includes invalid characters`
*   **原因**：Windows 路徑包含中文或特殊符號。
*   **解法**：
    *   使用 PowerShell 而不是 CMD。
    *   確保使用 `${PWD}` (PowerShell) 或 `%cd%` (CMD)。
    *   如果還是不行，試著把專案移到全英文路徑（如 `C:\Projects\egfr`）。

### 3. 權限錯誤 (Permission denied)
*   **症狀**：`EACCES: permission denied`
*   **原因**：Docker 沒有權限讀寫您的資料夾。
*   **解法**：
    *   Windows: 以「系統管理員身分」執行 PowerShell。
    *   Linux/Mac: 檢查資料夾權限 (`chmod 755`)。

### 4. 映像建立失敗 (Build failed)
*   **症狀**：在 `docker build` 過程中停住或報錯。
*   **原因**：網路問題導致無法下載套件。
*   **解法**：
    *   檢查網路連線。
    *   嘗試加入 `--no-cache` 重跑：`docker build --no-cache -t egfr-analysis .`

---

## 進階技巧

### 進入容器互動模式
如果您想進去容器裡面「逛逛」或手動執行 Python 指令：

```bash
docker run -it --rm -v ${PWD}/data:/app/data egfr-analysis /bin/bash
```
*   `-it`: Interactive TTY，讓您可以跟容器互動。
*   `/bin/bash`: 指定要執行的殼層 (Shell)。

進入後，您會看到 `#` 提示符號，可以輸入 `ls`, `python` 等指令。輸入 `exit` 離開。

---

## 發布到 GitHub (GHCR)

如果您想將這個 Docker 映像分享給其他人，或在其他電腦上直接下載使用（不用自己 build），可以將它發布到 **GitHub Container Registry (GHCR)**。

### 步驟 1: 準備 GitHub Token (PAT)

1.  登入 GitHub，前往 **Settings** > **Developer settings** > **Personal access tokens** > **Tokens (classic)**。
2.  點擊 **Generate new token (classic)**。
3.  勾選 `write:packages` 和 `delete:packages` 權限。
4.  複製生成的 Token（只會顯示一次！）。

### 步驟 2: 登入 GHCR

在終端機執行：
```bash
# 將 YOUR_TOKEN 換成剛才複製的 Token
# 將 YOUR_USERNAME 換成您的 GitHub 帳號
echo "YOUR_TOKEN" | docker login ghcr.io -u YOUR_USERNAME --password-stdin
```

### 步驟 3: 標記映像 (Tag)

將本地的 `egfr-analysis` 映像標記為 GitHub 的格式：

```bash
# 格式: docker tag <本地名稱> ghcr.io/<GitHub帳號>/<映像名稱>:latest
docker tag egfr-analysis ghcr.io/YOUR_USERNAME/egfr-analysis:latest
```

### 步驟 4: 推送映像 (Push)

```bash
docker push ghcr.io/YOUR_USERNAME/egfr-analysis:latest
```

### 步驟 5: 在其他電腦下載使用

一旦發布成功，其他電腦就不需要 `Dockerfile` 了，直接執行：

```bash
# 1. 下載映像
docker pull ghcr.io/YOUR_USERNAME/egfr-analysis:latest

# 2. 執行 (記得改映像名稱)
docker run --rm -v ${PWD}/data:/app/data -v ${PWD}/results:/app/results ghcr.io/YOUR_USERNAME/egfr-analysis:latest
```
