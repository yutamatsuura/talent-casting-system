"""管理機能用テーブル作成スクリプト"""
import asyncio
import sys
from pathlib import Path

# backend/appへのパスを追加
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db.connection import init_db, get_engine
from app.models import FormSubmission, ButtonClick
from app.core.config import settings


async def create_admin_tables():
    """管理機能用テーブルのみを作成"""
    print("🔧 Creating admin tracking tables...")
    print(f"📍 Database: {settings.database_url[:50]}...")

    # エンジン初期化
    await init_db()
    engine = get_engine()

    async with engine.begin() as conn:
        # FormSubmissionテーブル作成
        print("✨ Creating form_submissions table...")
        await conn.run_sync(FormSubmission.__table__.create, checkfirst=True)

        # ButtonClickテーブル作成
        print("✨ Creating button_clicks table...")
        await conn.run_sync(ButtonClick.__table__.create, checkfirst=True)

    print("✅ Admin tracking tables created successfully!")
    print("\n📋 Created tables:")
    print(f"   - {FormSubmission.__tablename__}")
    print(f"   - {ButtonClick.__tablename__}")


if __name__ == "__main__":
    asyncio.run(create_admin_tables())