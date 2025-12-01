# 使用官方 Python 3.9 slim 映像作為基礎
FROM python:3.9-slim

# 設定工作目錄
WORKDIR /app

# 設定環境變數
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

# 安裝系統依賴和中文字型
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    fonts-noto-cjk \
    fontconfig \
    && fc-cache -fv \
    && rm -rf /var/lib/apt/lists/*

# 複製 requirements.txt 並安裝 Python 依賴
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# 複製專案檔案到容器
COPY . .

# 建立必要的目錄
RUN mkdir -p data results

# 設定容器啟動時的預設命令
CMD ["python", "run_pipeline.py"]
