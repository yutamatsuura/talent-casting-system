"""ターゲット層マスタAPIエンドポイント
作成日: 2025-11-28
目的: GET /api/target-segments の実装
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.connection import get_db
from app.services.target_segments import TargetSegmentService
from app.schemas.target_segments import TargetSegmentsListResponse

router = APIRouter()


@router.get(
    "/target-segments",
    response_model=TargetSegmentsListResponse,
    summary="ターゲット層一覧取得",
    description="8ターゲット層（男性・女性 × 4年齢区分）の一覧を取得",
    status_code=status.HTTP_200_OK,
)
async def get_target_segments(
    db: AsyncSession = Depends(get_db),
) -> TargetSegmentsListResponse:
    """ターゲット層一覧取得API

    Args:
        db: データベースセッション（依存性注入）

    Returns:
        TargetSegmentsListResponse: ターゲット層一覧（total + items）

    Raises:
        HTTPException: データベースエラー時に500エラー
    """
    try:
        # サービス層を呼び出し
        service = TargetSegmentService(db)
        result = await service.get_all_target_segments()

        # 正常レスポンス
        return result

    except Exception as e:
        # エラーハンドリング
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch target segments: {str(e)}",
        ) from e
