# タレントキャスティングシステム - バックエンドAPI

FastAPI + PostgreSQL(Neon) による5段階マッチングロジック実装

## 技術スタック

- **Python**: 3.13.5
- **FastAPI**: 0.115.6
- **Uvicorn**: 0.34.0 (ASGIサーバー)
- **asyncpg**: 0.30.0 (高速PostgreSQL接続)
- **SQLAlchemy**: 2.0.36 (ORM)
- **Pydantic**: 2.10.6 (データバリデーション)
- **PostgreSQL**: Neon Launch ($19/月)

## セットアップ

### 1. 仮想環境作成・有効化

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# または
venv\Scripts\activate  # Windows
```

### 2. 依存パッケージインストール

```bash
pip install -r requirements.txt
```

### 3. 環境変数設定

プロジェクトルートの `.env.local` ファイルが必要です。
必須項目: `DATABASE_URL`

### 4. サーバー起動

```bash
# 起動スクリプト使用
./start.sh

# または手動起動
uvicorn app.main:app --host 0.0.0.0 --port 8432 --reload
```

## エンドポイント

### ヘルスチェック

```bash
GET http://localhost:8432/api/health

# レスポンス例
{
  "status": "healthy",
  "timestamp": "2025-11-27T22:43:54.750594",
  "environment": "development",
  "database": "connected",
  "message": "Talent Casting System API is running"
}
```

### API ドキュメント

- **Swagger UI**: http://localhost:8432/api/docs
- **ReDoc**: http://localhost:8432/api/redoc
- **OpenAPI JSON**: http://localhost:8432/api/openapi.json

## ディレクトリ構造

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPIメインアプリケーション
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py              # 環境変数管理
│   ├── db/
│   │   ├── __init__.py
│   │   └── connection.py          # DB接続管理
│   ├── api/
│   │   ├── __init__.py
│   │   └── endpoints/
│   │       ├── __init__.py
│   │       └── health.py          # ヘルスチェック
│   ├── models/                    # SQLAlchemyモデル（今後実装）
│   └── schemas/                   # Pydanticスキーマ（今後実装）
├── requirements.txt               # 依存パッケージ
├── start.sh                       # 開発サーバー起動スクリプト
└── venv/                          # Python仮想環境
```

## 実装状況

### ✅ スライス1: 基盤インフラストラクチャ（完了: 2025-11-28）

- [x] FastAPI基本設定
- [x] CORS設定
- [x] データベース接続（asyncpg + SQLAlchemy 2.0）
- [x] 環境変数管理（Pydantic Settings）
- [x] ヘルスチェックエンドポイント

### 🚧 スライス2: マスターデータAPI（次のステップ）

- [ ] GET /api/industries（業種マスタ）
- [ ] GET /api/target-segments（ターゲット層マスタ）

### 🚧 スライス3: 5段階マッチングエンジン（予定）

- [ ] POST /api/matching

## 開発メモ

### データベース接続確認

```python
# app/db/connection.pyのcheck_db_connection()を使用
# SELECT 1クエリでシンプルな接続確認
```

### CORS設定

CLAUDE.md準拠により、CORS Originは環境変数 `CORS_ORIGIN` から読み込み（ハードコード禁止）

### ホットリロード

`--reload` オプション有効により、`app/` ディレクトリ内のファイル変更を自動検知して再起動

## トラブルシューティング

### Pydanticバージョンエラー

typing-extensionsのバージョン不整合が発生した場合:

```bash
pip install --upgrade typing-extensions pydantic pydantic-settings
```

### データベース接続エラー

1. `.env.local` ファイルの `DATABASE_URL` を確認
2. Neon PostgreSQLの接続文字列形式: `postgresql://user:password@host/database?sslmode=require`

## 参考

- 詳細仕様: `docs/requirements.md`
- 進捗管理: `docs/SCOPE_PROGRESS.md`
- プロジェクト設定: `CLAUDE.md`
