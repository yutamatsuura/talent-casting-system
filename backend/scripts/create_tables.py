"""データベーステーブル作成スクリプト"""
import asyncio
import sys
from pathlib import Path

# backend/appへのパスを追加
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db.connection import init_db, get_engine
from app.models import Base
from app.core.config import settings


async def create_tables():
    """全テーブルを作成"""
    print("🔧 Creating database tables...")
    print(f"📍 Database: {settings.database_url[:50]}...")

    # エンジン初期化
    await init_db()
    engine = get_engine()

    async with engine.begin() as conn:
        # 全テーブル削除（開発環境のみ）
        if settings.node_env == "development":
            print("⚠️  Dropping existing tables (development mode)...")
            await conn.run_sync(Base.metadata.drop_all)

        # 全テーブル作成
        print("✨ Creating tables...")
        await conn.run_sync(Base.metadata.create_all)

    print("✅ Database tables created successfully!")
    print("\n📋 Created tables:")
    for table_name in Base.metadata.tables.keys():
        print(f"   - {table_name}")


if __name__ == "__main__":
    asyncio.run(create_tables())
