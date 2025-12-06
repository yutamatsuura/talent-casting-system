"""ターゲット層マスタのPydanticスキーマ定義
作成日: 2025-11-28
目的: GET /api/target-segments のレスポンス型定義
"""
from pydantic import BaseModel, Field
from datetime import datetime


class TargetSegmentBase(BaseModel):
    """ターゲット層の基本スキーマ（新DB構造対応）"""

    segment_name: str = Field(..., description="ターゲット層名（例: 男性12-19歳）", max_length=50)
    gender: str = Field(None, description="性別（男性 or 女性）", max_length=10)
    age_min: int = Field(None, description="最小年齢", ge=0)
    age_max: int = Field(None, description="最大年齢", ge=0)


class TargetSegmentResponse(TargetSegmentBase):
    """ターゲット層のレスポンススキーマ（GET /api/target-segments）"""

    target_segment_id: int = Field(..., description="ターゲット層ID（9-16）", ge=1)
    created_at: datetime = Field(..., description="作成日時")
    updated_at: datetime = Field(..., description="更新日時")

    model_config = {
        "from_attributes": True  # SQLAlchemyモデルからの変換を許可
    }


class TargetSegmentsListResponse(BaseModel):
    """ターゲット層一覧のレスポンススキーマ"""

    total: int = Field(..., description="総件数", ge=0)
    items: list[TargetSegmentResponse] = Field(..., description="ターゲット層リスト")
