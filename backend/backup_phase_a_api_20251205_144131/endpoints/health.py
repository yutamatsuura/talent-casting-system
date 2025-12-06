"""ヘルスチェックエンドポイント（システム状態・DB接続確認）"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime
from app.db.connection import check_db_connection
from app.core.config import settings

router = APIRouter()


class HealthResponse(BaseModel):
    """ヘルスチェックレスポンス"""
    status: str
    timestamp: str
    environment: str
    database: str
    message: str


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    GET /api/health

    システム状態とデータベース接続確認

    Returns:
        HealthResponse: システム状態情報
    """
    # データベース接続確認
    db_connected = await check_db_connection()

    if not db_connected:
        raise HTTPException(
            status_code=503,
            detail="Database connection failed"
        )

    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow().isoformat(),
        environment=settings.node_env,
        database="connected",
        message="Talent Casting System API is running"
    )
