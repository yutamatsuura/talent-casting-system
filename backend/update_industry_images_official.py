#!/usr/bin/env python3
"""正式マッピング表に基づくindustry_images更新（1業種1イメージ）"""

import asyncio
import sys
from pathlib import Path

# backend/appへのパスを追加
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import select, delete
from app.db.connection import init_db, get_session_maker
from app.models import IndustryImage

# グローバル変数でセッションメーカーを保持
AsyncSessionLocal = None

async def get_async_session():
    """非同期セッション取得"""
    global AsyncSessionLocal
    if AsyncSessionLocal is None:
        await init_db()
        AsyncSessionLocal = get_session_maker()
    return AsyncSessionLocal()

# 正式マッピング表データ（クライアント提供・1業種1イメージ）
OFFICIAL_INDUSTRY_IMAGES_DATA = [
    # 1. 食品 → 個性的な（image_item_id=3）
    {"industry_id": 1, "image_item_id": 3},

    # 2. 菓子・氷菓 → おもしろい（image_item_id=1）
    {"industry_id": 2, "image_item_id": 1},

    # 3. 乳製品 → 清潔感がある（image_item_id=2）
    {"industry_id": 3, "image_item_id": 2},

    # 4. 清涼飲料水 → 清潔感がある（image_item_id=2）
    {"industry_id": 4, "image_item_id": 2},

    # 5. アルコール飲料 → 大人の魅力がある（image_item_id=7）※25歳以上フィルタ
    {"industry_id": 5, "image_item_id": 7},

    # 6. フードサービス → 信頼できる（image_item_id=4）
    {"industry_id": 6, "image_item_id": 4},

    # 7. 医薬品・医療・健康食品 → 信頼できる（image_item_id=4）
    {"industry_id": 7, "image_item_id": 4},

    # 8. 化粧品・ヘアケア・オーラルケア → 清潔感がある（image_item_id=2）
    {"industry_id": 8, "image_item_id": 2},

    # 9. トイレタリー → 清潔感がある（image_item_id=2）
    {"industry_id": 9, "image_item_id": 2},

    # 10. 自動車関連 → 信頼できる（image_item_id=4）
    {"industry_id": 10, "image_item_id": 4},

    # 11. 家電 → 信頼できる（image_item_id=4）
    {"industry_id": 11, "image_item_id": 4},

    # 12. 通信・IT → 信頼できる（image_item_id=4）※画像推定
    {"industry_id": 12, "image_item_id": 4},

    # 13. ゲーム・エンターテイメント・アプリ → おもしろい（image_item_id=1）
    {"industry_id": 13, "image_item_id": 1},

    # 14. 流通・通販 → 信頼できる（image_item_id=4）
    {"industry_id": 14, "image_item_id": 4},

    # 15. ファッション → 個性的な（image_item_id=3）
    {"industry_id": 15, "image_item_id": 3},

    # 16. 貴金属 → 大人の魅力がある（image_item_id=7）
    {"industry_id": 16, "image_item_id": 7},

    # 17. 金融・不動産 → 信頼できる（image_item_id=4）
    {"industry_id": 17, "image_item_id": 4},

    # 18. エネルギー・輸送・交通 → 信頼できる（image_item_id=4）
    {"industry_id": 18, "image_item_id": 4},

    # 19. 教育・出版・公共団体 → 信頼できる（image_item_id=4）
    {"industry_id": 19, "image_item_id": 4},

    # 20. 観光 → おもしろい（image_item_id=1）
    {"industry_id": 20, "image_item_id": 1},
]

async def clear_industry_images():
    """industry_imagesテーブルクリア"""
    print("\n🧹 Clearing existing industry_images data...")

    async with await get_async_session() as session:
        await session.execute(delete(IndustryImage))
        await session.commit()
        print("✅ Industry_images data cleared")

async def seed_official_industry_images():
    """正式マッピング表に基づくindustry_imagesデータ投入"""
    print("\n📥 Seeding official industry_images data (1 industry = 1 image)...")

    async with await get_async_session() as session:
        for mapping_data in OFFICIAL_INDUSTRY_IMAGES_DATA:
            industry_image = IndustryImage(**mapping_data)
            session.add(industry_image)

        await session.commit()
        print(f"✅ Official industry_images seeded: {len(OFFICIAL_INDUSTRY_IMAGES_DATA)} records")

        return len(OFFICIAL_INDUSTRY_IMAGES_DATA)

async def verify_seeding():
    """投入結果の検証"""
    print("\n🔍 Verifying official seeded data...")

    async with await get_async_session() as session:
        result = await session.execute(select(IndustryImage))
        industry_images = result.scalars().all()

        print(f"📊 Total industry_images records: {len(industry_images)}")

        # 業種別の集計
        industry_counts = {}
        for industry_image in industry_images:
            industry_id = industry_image.industry_id
            industry_counts[industry_id] = industry_counts.get(industry_id, 0) + 1

        print("📊 Records per industry (official mapping):")
        for industry_id, count in sorted(industry_counts.items()):
            print(f"   Industry {industry_id}: {count} image item(s)")

        # 重複チェック
        if max(industry_counts.values()) > 1:
            print("⚠️  WARNING: Multiple images found per industry!")
        else:
            print("✅ All industries have exactly 1 image (official specification)")

        return len(industry_images)

async def main():
    """メイン処理"""
    print("=" * 70)
    print("🚀 Updating industry_images to official mapping (1 industry = 1 image)...")
    print("=" * 70)
    print("📋 Official mapping source: Client-provided screenshot (2025-12-02)")
    print("🚨 Special note: Alcohol industry requires 25+ age filtering")
    print("=" * 70)

    try:
        # industry_imagesテーブルクリア
        await clear_industry_images()

        # 正式マッピングデータ投入
        seeded_count = await seed_official_industry_images()

        # 投入結果検証
        total_count = await verify_seeding()

        print("\n" + "=" * 70)
        print("✅ Official industry_images mapping completed successfully!")
        print("=" * 70)
        print(f"📊 Summary:")
        print(f"   - Seeded: {seeded_count} records (20 industries × 1 image each)")
        print(f"   - Verified: {total_count} records")
        print(f"   - Status: ✅ Official client specification compliant")
        print("=" * 70)
        print("🔔 Next step: Implement alcohol industry age filtering (25+ only)")
        print("=" * 70)

    except Exception as e:
        print(f"\n❌ Error during official mapping update: {e}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    asyncio.run(main())