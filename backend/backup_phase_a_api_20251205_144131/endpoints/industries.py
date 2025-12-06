"""業種マスタAPIエンドポイント（STEP2業種イメージ査定用）"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.connection import get_db_session
from app.models import Industry, ImageItem, IndustryImage
from app.schemas.industries import IndustryListResponse, IndustryResponse, ImageItemResponse

router = APIRouter()


@router.get("/industries", summary="業種一覧取得")
async def get_industries():
    """
    業種一覧を取得するシンプルなエンドポイント
    """
    from app.db.connection import get_asyncpg_connection

    try:
        conn = await get_asyncpg_connection()
        try:
            # シンプルなクエリで業界一覧を取得
            rows = await conn.fetch("""
                SELECT industry_id, industry_name
                FROM industries
                ORDER BY industry_id
            """)

            industries = [
                {
                    "id": row["industry_id"],
                    "name": row["industry_name"],
                    "display_order": row["industry_id"]
                }
                for row in rows
            ]

            return {
                "total": len(industries),
                "industries": industries
            }
        finally:
            await conn.close()

    except Exception as e:
        print(f"❌ Database error in GET /api/industries: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail="業種一覧の取得に失敗しました。しばらく待ってから再試行してください。",
        )
