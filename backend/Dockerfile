# タレントキャスティングシステム - Cloud Run用Dockerfile
# 簡略化版（権限問題回避）

FROM python:3.11-slim

# システム依存関係インストール
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# ワーキングディレクトリ設定
WORKDIR /app

# Python依存関係インストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコードをコピー
COPY . .

# Cloud Run環境変数
ENV PYTHONPATH=/app

# ポート公開（動的）
EXPOSE 8080

# 起動コマンド（Cloud Run PORT環境変数対応）
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080} --workers 1"]