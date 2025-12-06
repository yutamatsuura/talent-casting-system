#!/bin/bash
# FastAPI開発サーバー起動スクリプト
# CLAUDE.md準拠: ポート8432、ホットリロード有効

cd "$(dirname "$0")"
source venv/bin/activate

echo "🚀 Starting FastAPI server on port 8432..."
uvicorn app.main:app --host 0.0.0.0 --port 8432 --reload --reload-dir app
