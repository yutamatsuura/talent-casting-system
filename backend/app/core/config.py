"""環境変数管理・設定ファイル（CLAUDE.md準拠）"""
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field, ConfigDict
import os


class Settings(BaseSettings):
    """アプリケーション設定クラス"""
    model_config = ConfigDict(
        env_file=os.path.join(os.path.dirname(__file__), "..", "..", "..", ".env.local"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"  # 未定義のフィールドを無視
    )

    # ===== 基本設定 =====
    node_env: str = Field(default="development", alias="NODE_ENV")

    # ===== ポート設定（CLAUDE.md準拠）=====
    api_port: int = Field(default=8432, alias="API_PORT")
    database_port: int = Field(default=5433, alias="DATABASE_PORT")

    # ===== URL設定（開発環境）=====
    frontend_url: str = Field(default="http://localhost:3248", alias="FRONTEND_URL")
    backend_url: str = Field(default="http://localhost:8432", alias="BACKEND_URL")

    # ===== CORS設定（重要！ハードコード禁止）=====
    cors_origin: str = Field(default="http://localhost:3248", alias="CORS_ORIGIN")

    # ===== データベース接続 =====
    database_url: str = Field(..., alias="DATABASE_URL")

    # ===== データベース最適化設定 (Phase A1最適化) =====
    db_pool_size: int = Field(default=5, alias="DB_POOL_SIZE")  # 10→5: 接続数半減
    db_max_overflow: int = Field(default=10, alias="DB_MAX_OVERFLOW")  # 20→10: オーバーフロー削減
    db_pool_timeout: int = Field(default=10, alias="DB_POOL_TIMEOUT")  # 30→10: タイムアウト短縮
    db_pool_recycle: int = Field(default=600, alias="DB_POOL_RECYCLE")  # 1800→600: 接続回転強化

    # ===== セキュリティ設定 =====
    rate_limit_per_second: int = Field(default=10, alias="RATE_LIMIT_PER_SECOND")


def get_settings() -> Settings:
    """設定インスタンスを取得（シングルトン）"""
    return Settings()


# グローバル設定インスタンス
settings = get_settings()
