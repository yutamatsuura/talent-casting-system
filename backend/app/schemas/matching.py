"""マッチングエンドポイント用Pydanticスキーマ（requirements.md準拠）"""
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from datetime import datetime


class MatchingFormData(BaseModel):
    """フォームデータスキーマ（フロントエンド → バックエンド）"""

    industry: str = Field(..., description="業種名")
    target_segments: str = Field(..., min_length=1, description="ターゲット層（単一選択）")
    purpose: str = Field(..., min_length=1, max_length=255, description="起用目的")
    budget: str = Field(..., description="予算区分")
    company_name: str = Field(..., min_length=1, max_length=255, description="企業名")
    email: str = Field(..., pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", description="メールアドレス")
    contact_name: str = Field(..., min_length=1, max_length=255, description="担当者名")
    phone: str = Field(..., min_length=1, max_length=50, description="電話番号")
    genre_preference: str = Field(..., min_length=1, max_length=50, description="ジャンル希望の有無")
    preferred_genres: Optional[List[str]] = Field(None, description="希望するジャンルリスト")
    session_id: Optional[str] = Field(None, max_length=100, description="セッションID")

    @field_validator("target_segments")
    @classmethod
    def validate_target_segments(cls, v: str) -> str:
        """ターゲット層バリデーション"""
        if not v or v.strip() == "":
            raise ValueError("ターゲット層を選択してください")

        # 許可されたターゲット層のリスト
        allowed_segments = [
            "男性12-19歳",
            "女性12-19歳",
            "男性20-34歳",
            "女性20-34歳",
            "男性35-49歳",
            "女性35-49歳",
            "男性50-69歳",
            "女性50-69歳",
        ]

        if v not in allowed_segments:
            raise ValueError(f"無効なターゲット層です: {v}")

        return v

    model_config = {
        "json_schema_extra": {
            "example": {
                "industry": "化粧品・ヘアケア・オーラルケア",
                "target_segments": "女性20-34歳",
                "purpose": "商品の認知度向上",
                "budget": "1,000万円～3,000万円未満",
                "company_name": "株式会社テストクライアント",
                "email": "test@talent-casting-dev.local",
            }
        }
    }


class TalentResult(BaseModel):
    """タレント結果スキーマ（バックエンド → フロントエンド）"""

    account_id: int = Field(..., description="アカウントID（新DB主キー）")
    name: str = Field(..., description="タレント名（name_full_for_matching）")
    kana: Optional[str] = Field(None, description="タレント名（カナ）")
    category: Optional[str] = Field(None, description="カテゴリ（act_genre）")
    matching_score: float = Field(..., ge=0.0, le=100.0, description="マッチングスコア（0-100）")
    ranking: int = Field(..., ge=1, le=30, description="ランキング（1-30）")
    base_power_score: Optional[float] = Field(None, description="基礎パワー得点")
    image_adjustment: Optional[float] = Field(None, description="業種イメージ加減点")
    is_recommended: bool = Field(False, description="おすすめタレントかどうか")
    is_currently_in_cm: bool = Field(False, description="現在CM出演中かどうか")

    model_config = {
        "json_schema_extra": {
            "example": {
                "account_id": 12345,
                "name": "サンプルタレント",
                "kana": "サンプルタレント",
                "category": "俳優",
                "matching_score": 98.5,
                "ranking": 1,
                "base_power_score": 85.3,
                "image_adjustment": 12.0,
                "is_recommended": True,
                "is_currently_in_cm": False,
            }
        }
    }


class MatchingResponse(BaseModel):
    """マッチング結果レスポンススキーマ"""

    success: bool = Field(True, description="処理成功フラグ")
    total_results: int = Field(..., ge=0, le=30, description="結果件数（最大30件）")
    results: List[TalentResult] = Field(..., max_length=30, description="タレント結果リスト")
    processing_time_ms: Optional[float] = Field(None, description="処理時間（ミリ秒）")
    timestamp: datetime = Field(default_factory=datetime.now, description="レスポンス生成時刻")
    session_id: Optional[str] = Field(None, description="セッションID")

    model_config = {
        "json_schema_extra": {
            "example": {
                "success": True,
                "total_results": 30,
                "results": [
                    {
                        "account_id": 12345,
                        "name": "サンプルタレント1",
                        "kana": "サンプルタレント1",
                        "category": "俳優",
                        "matching_score": 98.5,
                        "ranking": 1,
                        "base_power_score": 85.3,
                        "image_adjustment": 12.0,
                        "is_recommended": True,
                        "is_currently_in_cm": False,
                    }
                ],
                "processing_time_ms": 242.5,
                "timestamp": "2025-11-28T12:00:00",
            }
        }
    }


class MatchingErrorResponse(BaseModel):
    """マッチングエラーレスポンススキーマ"""

    success: bool = Field(False, description="処理失敗フラグ")
    error_code: str = Field(..., description="エラーコード")
    error_message: str = Field(..., description="エラーメッセージ")
    timestamp: datetime = Field(default_factory=datetime.now, description="エラー発生時刻")

    model_config = {
        "json_schema_extra": {
            "example": {
                "success": False,
                "error_code": "INVALID_BUDGET",
                "error_message": "指定された予算区分が存在しません",
                "timestamp": "2025-11-28T12:00:00",
            }
        }
    }
