#!/usr/bin/env python3
"""industry_imagesテーブルを正しい20業種に合わせて更新するスクリプト"""

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

# 業種-イメージ紐付けデータ（正しい20業種版 - 仮設定）
# ※クライアント確認中のため、業界常識に基づく論理的なマッピング
INDUSTRY_IMAGES_DATA = [
    # 1. 食品 → 清潔感がある、信頼できる
    {"industry_id": 1, "image_item_id": 2},
    {"industry_id": 1, "image_item_id": 4},

    # 2. 菓子・氷菓 → 可愛い、おもしろい
    {"industry_id": 2, "image_item_id": 5},
    {"industry_id": 2, "image_item_id": 1},

    # 3. 乳製品 → 清潔感がある、信頼できる
    {"industry_id": 3, "image_item_id": 2},
    {"industry_id": 3, "image_item_id": 4},

    # 4. 清涼飲料水 → 清潔感がある、おもしろい
    {"industry_id": 4, "image_item_id": 2},
    {"industry_id": 4, "image_item_id": 1},

    # 5. アルコール飲料 → カッコいい、大人っぽい
    {"industry_id": 5, "image_item_id": 6},
    {"industry_id": 5, "image_item_id": 7},

    # 6. フードサービス → おもしろい、信頼できる
    {"industry_id": 6, "image_item_id": 1},
    {"industry_id": 6, "image_item_id": 4},

    # 7. 医薬品・医療・健康食品 → 信頼できる、清潔感がある
    {"industry_id": 7, "image_item_id": 4},
    {"industry_id": 7, "image_item_id": 2},

    # 8. 化粧品・ヘアケア・オーラルケア → 清潔感がある、可愛い
    {"industry_id": 8, "image_item_id": 2},
    {"industry_id": 8, "image_item_id": 5},

    # 9. トイレタリー → 清潔感がある、信頼できる
    {"industry_id": 9, "image_item_id": 2},
    {"industry_id": 9, "image_item_id": 4},

    # 10. 自動車関連 → カッコいい、信頼できる
    {"industry_id": 10, "image_item_id": 6},
    {"industry_id": 10, "image_item_id": 4},

    # 11. 家電 → カッコいい、信頼できる
    {"industry_id": 11, "image_item_id": 6},
    {"industry_id": 11, "image_item_id": 4},

    # 12. 通信・IT → カッコいい、個性的
    {"industry_id": 12, "image_item_id": 6},
    {"industry_id": 12, "image_item_id": 3},

    # 13. ゲーム・エンターテイメント・アプリ → おもしろい、個性的
    {"industry_id": 13, "image_item_id": 1},
    {"industry_id": 13, "image_item_id": 3},

    # 14. 流通・通販 → 信頼できる、おもしろい
    {"industry_id": 14, "image_item_id": 4},
    {"industry_id": 14, "image_item_id": 1},

    # 15. ファッション → カッコいい、個性的
    {"industry_id": 15, "image_item_id": 6},
    {"industry_id": 15, "image_item_id": 3},

    # 16. 貴金属 → カッコいい、大人っぽい
    {"industry_id": 16, "image_item_id": 6},
    {"industry_id": 16, "image_item_id": 7},

    # 17. 金融・不動産 → 信頼できる、大人っぽい
    {"industry_id": 17, "image_item_id": 4},
    {"industry_id": 17, "image_item_id": 7},

    # 18. エネルギー・輸送・交通 → 信頼できる、カッコいい
    {"industry_id": 18, "image_item_id": 4},
    {"industry_id": 18, "image_item_id": 6},

    # 19. 教育・出版・公共団体 → 信頼できる、大人っぽい
    {"industry_id": 19, "image_item_id": 4},
    {"industry_id": 19, "image_item_id": 7},

    # 20. 観光 → おもしろい、可愛い
    {"industry_id": 20, "image_item_id": 1},
    {"industry_id": 20, "image_item_id": 5},
]

async def clear_industry_images():
    """industry_imagesテーブルのみクリア"""
    print("\n🧹 Clearing existing industry_images data...")

    async with await get_async_session() as session:
        await session.execute(delete(IndustryImage))
        await session.commit()
        print("✅ Industry_images data cleared")

async def seed_updated_industry_images():
    """更新されたindustry_imagesデータ投入"""
    print("\n📥 Seeding updated industry_images data...")

    async with await get_async_session() as session:
        for mapping_data in INDUSTRY_IMAGES_DATA:
            industry_image = IndustryImage(**mapping_data)
            session.add(industry_image)

        await session.commit()
        print(f"✅ Industry_images seeded: {len(INDUSTRY_IMAGES_DATA)} records")

        return len(INDUSTRY_IMAGES_DATA)

async def verify_seeding():
    """投入結果の検証"""
    print("\n🔍 Verifying seeded data...")

    async with await get_async_session() as session:
        result = await session.execute(select(IndustryImage))
        industry_images = result.scalars().all()

        print(f"📊 Total industry_images records: {len(industry_images)}")

        # 業種別の集計
        industry_counts = {}
        for industry_image in industry_images:
            industry_id = industry_image.industry_id
            industry_counts[industry_id] = industry_counts.get(industry_id, 0) + 1

        print("📊 Records per industry:")
        for industry_id, count in sorted(industry_counts.items()):
            print(f"   Industry {industry_id}: {count} image items")

        return len(industry_images)

async def main():
    """メイン処理"""
    print("=" * 60)
    print("🚀 Starting industry_images update for correct 20 industries...")
    print("=" * 60)
    print("注意: これは仮のマッピングです。クライアント確認後に変更される可能性があります")
    print("=" * 60)

    try:
        # industry_imagesテーブルクリア
        await clear_industry_images()

        # 更新されたindustry_imagesデータ投入
        seeded_count = await seed_updated_industry_images()

        # 投入結果検証
        total_count = await verify_seeding()

        print("\n" + "=" * 60)
        print("✅ Industry_images update completed successfully!")
        print("=" * 60)
        print(f"📊 Summary:")
        print(f"   - Seeded: {seeded_count} records (40件: 20業種×2イメージ)")
        print(f"   - Verified: {total_count} records")
        print(f"   - Status: ✅ STEP 2 matching ready (temporary mapping)")
        print("=" * 60)
        print("🔔 注意: マッピングはクライアント確認中のため、暫定版です")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ Error during update: {e}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    asyncio.run(main())