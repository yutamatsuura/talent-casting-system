"""データベース統計確認スクリプト
作成日: 2025-11-28
目的: 実データ件数の確認（4,819件の検証）
"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import select, func
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from app.models import (
    Talent,
    Industry,
    TargetSegment,
    ImageItem,
    TalentImage,
    TalentScore
)


async def check_database_stats():
    """データベース統計確認"""
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
    from urllib.parse import urlparse, urlunparse
    parsed = urlparse(database_url)
    clean_url = urlunparse((parsed.scheme, parsed.netloc, parsed.path, '', '', ''))

    print("=" * 80)
    print("📊 データベース統計情報")
    print("=" * 80)
    print(f"接続先: {clean_url[:60]}...\n")

    # SQLAlchemy Async Engine作成
    engine = create_async_engine(clean_url, echo=False)
    async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session_maker() as session:
        # Talents（タレント）
        stmt = select(func.count()).select_from(Talent)
        result = await session.execute(stmt)
        talent_count = result.scalar()
        print(f"✅ Talents（タレント）: {talent_count:,}件")

        # Industries（業種）
        stmt = select(func.count()).select_from(Industry)
        result = await session.execute(stmt)
        industry_count = result.scalar()
        print(f"✅ Industries（業種）: {industry_count:,}件")

        # TargetSegments（ターゲット層）
        stmt = select(func.count()).select_from(TargetSegment)
        result = await session.execute(stmt)
        target_segment_count = result.scalar()
        print(f"✅ Target Segments（ターゲット層）: {target_segment_count:,}件")

        # ImageItems（イメージ項目）
        stmt = select(func.count()).select_from(ImageItem)
        result = await session.execute(stmt)
        image_item_count = result.scalar()
        print(f"✅ Image Items（イメージ項目）: {image_item_count:,}件")

        # TalentImages（タレントイメージスコア）
        stmt = select(func.count()).select_from(TalentImage)
        result = await session.execute(stmt)
        talent_image_count = result.scalar()
        print(f"✅ Talent Images（タレントイメージスコア）: {talent_image_count:,}件")

        # TalentScores（タレントスコア: VR/TPR）
        stmt = select(func.count()).select_from(TalentScore)
        result = await session.execute(stmt)
        talent_score_count = result.scalar()
        print(f"✅ Talent Scores（VR/TPRスコア）: {talent_score_count:,}件")

        print("\n" + "=" * 80)
        print("📈 期待値との比較")
        print("=" * 80)

        # タレント件数の確認（期待: 4,819件）
        expected_talents = 4819
        if talent_count == expected_talents:
            print(f"✅ タレント件数: 期待通り ({talent_count:,}件 = {expected_talents:,}件)")
        else:
            print(f"⚠️  タレント件数: 差異あり ({talent_count:,}件 != {expected_talents:,}件)")

        # 業種件数の確認（期待: 20件）
        expected_industries = 20
        if industry_count == expected_industries:
            print(f"✅ 業種件数: 期待通り ({industry_count}件 = {expected_industries}件)")
        else:
            print(f"⚠️  業種件数: 差異あり ({industry_count}件 != {expected_industries}件)")

        # ターゲット層件数の確認（期待: 8件）
        expected_target_segments = 8
        if target_segment_count == expected_target_segments:
            print(f"✅ ターゲット層件数: 期待通り ({target_segment_count}件 = {expected_target_segments}件)")
        else:
            print(f"⚠️  ターゲット層件数: 差異あり ({target_segment_count}件 != {expected_target_segments}件)")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(check_database_stats())
