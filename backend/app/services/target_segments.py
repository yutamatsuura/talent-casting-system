"""ターゲット層マスタのサービス層
作成日: 2025-11-28
目的: ターゲット層データの取得ビジネスロジック
"""
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.target_segments import TargetSegmentRepository
from app.schemas.target_segments import TargetSegmentResponse, TargetSegmentsListResponse


class TargetSegmentService:
    """ターゲット層マスタのサービス"""

    def __init__(self, session: AsyncSession) -> None:
        """サービスの初期化

        Args:
            session: 非同期SQLAlchemyセッション
        """
        self.session = session
        self.repository = TargetSegmentRepository(session)

    async def get_all_target_segments(self) -> TargetSegmentsListResponse:
        """全ターゲット層を取得してレスポンス形式に変換

        Returns:
            TargetSegmentsListResponse（total + items）
        """
        # リポジトリから全データ取得
        target_segments = await self.repository.get_all()

        # Pydanticスキーマに変換
        items = [
            TargetSegmentResponse.model_validate(segment) for segment in target_segments
        ]

        # レスポンス形式で返却
        return TargetSegmentsListResponse(total=len(items), items=items)
