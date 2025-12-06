# タレントキャスティングシステム - Cloud Run用Dockerfile
# 最適化設定: マルチステージビルド + セキュリティ対応

# ===== ビルドステージ =====
FROM python:3.11-slim as builder

# セキュリティ: 非rootユーザー作成
RUN groupadd -r appuser && useradd -r -g appuser appuser

# システム依存関係インストール
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Python依存関係インストール
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ===== 本番ステージ =====
FROM python:3.11-slim

# セキュリティ: 非root実行
RUN groupadd -r appuser && useradd -r -g appuser appuser

# 最小限のシステム依存関係
RUN apt-get update && apt-get install -y \
    libpq5 \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Python環境をコピー
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# アプリケーションコード
WORKDIR /app
COPY . .

# 権限設定
RUN chown -R appuser:appuser /app
USER appuser

# ヘルスチェック
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8080/api/health')"

# Cloud Run環境変数
ENV PYTHONPATH=/app
ENV PORT=8080
ENV HOST=0.0.0.0

# ポート公開
EXPOSE 8080

# 起動コマンド（Cloud Run最適化）
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "1", "--loop", "uvloop"]