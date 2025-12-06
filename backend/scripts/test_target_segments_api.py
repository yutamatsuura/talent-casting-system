"""ターゲット層API動作確認スクリプト
作成日: 2025-11-28
目的: GET /api/target-segments の動作確認
"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import select
from pathlib import Path

# モデルのインポート
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from app.models import TargetSegment


async def test_direct_db_access():
    """データベース直接アクセステスト"""
    # 環境変数から DATABASE_URL を取得
    env_path = Path(__file__).parent.parent.parent / ".env.local"
    database_url = None

    with open(env_path, "r") as f:
        for line in f:
            if line.startswith("DATABASE_URL="):
                database_url = line.strip().split("=", 1)[1]
                break

    if not database_url:
        raise ValueError("DATABASE_URL not found in .env.local")

    # PostgreSQL URLをasyncpg用に変換
    database_url = database_url.replace("postgresql://", "postgresql+asyncpg://")

    # sslmode等のパラメータを除去
    from urllib.parse import urlparse, urlunparse
    parsed = urlparse(database_url)
    # クエリパラメータを除去したURL
    clean_url = urlunparse((parsed.scheme, parsed.netloc, parsed.path, '', '', ''))

    print(f"📊 Connecting to database: {clean_url[:60]}...")

    # SQLAlchemy Async Engine作成
    engine = create_async_engine(clean_url, echo=False)
    async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session_maker() as session:
        # ターゲット層を全件取得
        stmt = select(TargetSegment).order_by(TargetSegment.display_order)
        result = await session.execute(stmt)
        target_segments = list(result.scalars().all())

        print(f"\n✅ Successfully fetched {len(target_segments)} target segments!\n")

        print(f"{'ID':<5} {'Code':<10} {'Name':<20} {'Gender':<10} {'Age Range':<15}")
        print("-" * 70)
        for ts in target_segments:
            print(f"{ts.id:<5} {ts.code:<10} {ts.name:<20} {ts.gender:<10} {ts.age_range:<15}")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(test_direct_db_access())
