"""FastAPI メインアプリケーション（CLAUDE.md準拠）"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.config import settings
from app.db.connection import init_db, close_db
from app.api.endpoints import health, target_segments, industries, matching, tracking, admin, recommended_talents, talents, admin_debug


@asynccontextmanager
async def lifespan(app: FastAPI):
    """アプリケーションライフサイクル管理"""
    # 起動時処理
    print("🚀 Starting Talent Casting System API...")
    await init_db()
    # 機密情報をマスキングして表示
    masked_url = settings.database_url
    if '@' in masked_url:
        # postgresql://user:password@host... → postgresql://***@host...
        parts = masked_url.split('@')
        if len(parts) >= 2:
            masked_url = f"{parts[0].split('://')[0]}://***@{parts[1]}"
    print(f"✅ Database initialized: {masked_url[:60]}...")
    print(f"✅ Environment: {settings.node_env}")
    print(f"✅ CORS Origin: {settings.cors_origin}")

    yield

    # 終了時処理
    print("🛑 Shutting down Talent Casting System API...")
    await close_db()
    print("✅ Database connections closed")


# FastAPI アプリケーション作成
app = FastAPI(
    title="Talent Casting System API",
    description="5段階マッチングロジックによるタレントキャスティング支援システム",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# CORS設定（本番運用診断対応: セキュリティ強化）
# 環境変数のみ使用、ハードコード禁止
cors_origins = []
if settings.cors_origin:
    cors_origins.append(settings.cors_origin)

# 開発環境のフロントエンドドメインを追加
development_origins = [
    "http://localhost:3248",  # 管理画面・診断システム
    "http://localhost:3247",  # ランディングページ
]
cors_origins.extend(development_origins)

# 本番フロントエンドドメインを追加
production_origins = [
    "https://talent-casting-diagnosis.vercel.app",
    "https://e-spirit.vercel.app"
]
cors_origins.extend(production_origins)
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],  # 管理画面のCRUD操作に必要
    allow_headers=[
        "Content-Type",
        "Authorization",
        "Accept",
        "X-Requested-With",
        "Origin",
        "Access-Control-Request-Method",
        "Access-Control-Request-Headers"
    ],  # Preflightヘッダーを追加
    expose_headers=["Content-Type"],  # レスポンスヘッダー制限
    max_age=3600,  # Preflight結果をキャッシュ（1時間）
)

# ルーター登録
app.include_router(health.router, prefix="/api", tags=["Health Check"])
app.include_router(target_segments.router, prefix="/api", tags=["Master Data"])
app.include_router(industries.router, prefix="/api", tags=["Master Data"])
app.include_router(matching.router, prefix="/api", tags=["Matching Engine"])
app.include_router(tracking.router, prefix="/api", tags=["Tracking"])
app.include_router(admin.router, prefix="/api", tags=["Admin Panel"])
app.include_router(recommended_talents.router, prefix="/api", tags=["Recommended Talents"])
app.include_router(talents.router, prefix="/api/talents", tags=["Talent Details"])
app.include_router(admin_debug.router, prefix="/api", tags=["Debug Export"])


@app.get("/")
async def root():
    """ルートエンドポイント"""
    return {
        "message": "Talent Casting System API",
        "version": "1.0.0",
        "docs": "/api/docs",
    }
