"""
タレント詳細情報関連のPydanticスキーマ定義

フロントエンドのTalentDetailInfo型に対応するスキーマ
"""

from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class CMHistoryDetail(BaseModel):
    """CM履歴詳細情報"""
    client_name: str = Field(..., description="クライアント名/スポンサー名")
    product_name: str = Field(default="", description="商品名/サービス名（空文字もあり）")
    use_period_start: str = Field(default="", description="使用開始日 (YYYY-MM-DD形式)")
    use_period_end: str = Field(default="", description="使用終了日 (YYYY-MM-DD形式)")
    agency_name: str = Field(default="", description="代理店名（稀少データ）")
    production_name: str = Field(default="", description="制作会社名（稀少データ）")
    director: str = Field(default="", description="監督名（稀少データ）")
    category: str = Field(default="その他", description="推定されたCMカテゴリ")
    note: str = Field(default="", description="備考・契約状況等")
    rival_category_type_cd1: Optional[int] = Field(None, description="競合カテゴリコード1")
    rival_category_type_cd2: Optional[int] = Field(None, description="競合カテゴリコード2")
    rival_category_type_cd3: Optional[int] = Field(None, description="競合カテゴリコード3")
    rival_category_type_cd4: Optional[int] = Field(None, description="競合カテゴリコード4")

    model_config = {
        "from_attributes": True
    }


class TalentDetailResponse(BaseModel):
    """タレント詳細情報レスポンス"""
    account_id: int = Field(..., description="タレントアカウントID")
    name: str = Field(..., description="タレント名")
    kana: Optional[str] = Field(None, description="ふりがな（姓 名の形式）")
    category: Optional[str] = Field(None, description="タレントカテゴリ（act_genre）")
    age: Optional[int] = Field(None, description="年齢（birthdayから計算）")
    company_name: Optional[str] = Field(None, description="所属事務所名")
    birthplace: Optional[str] = Field(None, description="出身地（都道府県名）")
    introduction: Optional[str] = Field(None, description="自己紹介文（現在未実装）")
    cm_history: List[CMHistoryDetail] = Field(default_factory=list, description="CM出演履歴一覧")
    base_power_score: Optional[float] = Field(None, description="基礎パワー得点（STEP1スコア）")
    image_adjustment: Optional[float] = Field(None, description="業種イメージ査定調整値（STEP2スコア）")
    image_url: Optional[str] = Field(None, description="タレント画像URL")

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "account_id": 1165,
                "name": "川口春奈",
                "kana": "カワグチ ハルナ",
                "category": "女優",
                "age": 29,
                "company_name": "研音",
                "birthplace": "長崎県",
                "introduction": None,
                "cm_history": [
                    {
                        "client_name": "アムタス",
                        "product_name": "めちゃコミック",
                        "use_period_start": "2020-12-25",
                        "use_period_end": "2025-12-24",
                        "agency_name": "ティー・ワイ・オー+ワンスカイ",
                        "production_name": "TYO MONSTER",
                        "director": "浜崎慎治",
                        "category": "エンターテイメント",
                        "note": "【2025/1 契約あり確認】"
                    }
                ],
                "base_power_score": 67.5,
                "image_adjustment": 8.2,
                "image_url": "/placeholder-user.jpg"
            }
        }
    }