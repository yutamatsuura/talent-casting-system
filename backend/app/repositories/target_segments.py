"""ターゲット層マスタのリポジトリ層
作成日: 2025-11-28
目的: データベースからターゲット層データを取得する処理
"""
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import TargetSegment


class TargetSegmentRepository:
    """ターゲット層マスタのリポジトリ"""

    def __init__(self, session: AsyncSession) -> None:
        """リポジトリの初期化

        Args:
            session: 非同期SQLAlchemyセッション
        """
        self.session = session

    async def get_all(self) -> List[TargetSegment]:
        """全ターゲット層を取得（target_segment_id順）

        Returns:
            TargetSegmentモデルのリスト（target_segment_id昇順）
        """
        stmt = select(TargetSegment).order_by(TargetSegment.target_segment_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_id(self, target_segment_id: int) -> Optional[TargetSegment]:
        """IDでターゲット層を取得

        Args:
            target_segment_id: ターゲット層ID（9-16）

        Returns:
            TargetSegmentモデル（存在しない場合はNone）
        """
        stmt = select(TargetSegment).where(TargetSegment.target_segment_id == target_segment_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_code(self, code: str) -> Optional[TargetSegment]:
        """コードでターゲット層を取得

        Args:
            code: ターゲット層コード（例: M1, F2）

        Returns:
            TargetSegmentモデル（存在しない場合はNone）
        """
        stmt = select(TargetSegment).where(TargetSegment.code == code)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
