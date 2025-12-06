"""業種・イメージ項目スキーマ定義（バリデーション・シリアライゼーション）"""
from pydantic import BaseModel, Field
from typing import Optional


class ImageItemResponse(BaseModel):
    """イメージ項目レスポンススキーマ"""
    id: int = Field(..., description="イメージ項目ID")
    code: str = Field(..., description="イメージ項目コード（例: clean, cool）")
    name: str = Field(..., description="イメージ項目名（例: 清潔感がある、カッコいい）")
    description: Optional[str] = Field(None, description="イメージ項目説明")
    display_order: int = Field(default=0, description="表示順序")

    model_config = {
        "from_attributes": True  # Pydantic v2対応（旧orm_mode）
    }


class IndustryResponse(BaseModel):
    """業種レスポンススキーマ"""
    id: int = Field(..., description="業種ID")
    name: str = Field(..., description="業種名（例: 化粧品・ヘアケア・オーラルケア）")
    display_order: int = Field(default=0, description="表示順序")
    required_images: list[ImageItemResponse] = Field(
        default_factory=list,
        description="業種に求められるイメージ項目リスト（STEP2業種イメージ査定用）"
    )

    model_config = {
        "from_attributes": True
    }


class IndustryListResponse(BaseModel):
    """業種一覧レスポンススキーマ"""
    total: int = Field(..., description="総件数")
    industries: list[IndustryResponse] = Field(..., description="業種リスト")

    model_config = {
        "from_attributes": True
    }
