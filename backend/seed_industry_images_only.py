#!/usr/bin/env python3
"""industry_imagesテーブルのみ投入スクリプト（既存データ保護版）"""

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

# 業種-イメージ紐付けデータ（STEP2業種イメージ査定用）
# seed_master_data.pyから抽出
INDUSTRY_IMAGES_DATA = [
    # 食品（id=1）→ 清潔感がある、信頼できる
    {"industry_id": 1, "image_item_id": 2},
    {"industry_id": 1, "image_item_id": 4},

    # 菓子・氷菓（id=2）→ 可愛い、おもしろい
    {"industry_id": 2, "image_item_id": 5},
    {"industry_id": 2, "image_item_id": 1},

    # 乳製品（id=3）→ 清潔感がある、信頼できる
    {"industry_id": 3, "image_item_id": 2},
    {"industry_id": 3, "image_item_id": 4},

    # 清涼飲料水（id=4）→ 清潔感がある、おもしろい
    {"industry_id": 4, "image_item_id": 2},
    {"industry_id": 4, "image_item_id": 1},

    # アルコール飲料（id=5）→ カッコいい、大人っぽい
    {"industry_id": 5, "image_item_id": 6},
    {"industry_id": 5, "image_item_id": 7},

    # フードサービス（id=6）→ おもしろい、信頼できる
    {"industry_id": 6, "image_item_id": 1},
    {"industry_id": 6, "image_item_id": 4},

    # 医薬品・医療・健康食品（id=7）→ 信頼できる、清潔感がある
    {"industry_id": 7, "image_item_id": 4},
    {"industry_id": 7, "image_item_id": 2},

    # 化粧品・ヘアケア・オーラルケア（id=8）→ 清潔感がある、可愛い
    {"industry_id": 8, "image_item_id": 2},
    {"industry_id": 8, "image_item_id": 5},

    # トイレタリー（id=9）→ 清潔感がある、信頼できる
    {"industry_id": 9, "image_item_id": 2},
    {"industry_id": 9, "image_item_id": 4},

    # 自動車関連（id=10）→ カッコいい、信頼できる
    {"industry_id": 10, "image_item_id": 6},
    {"industry_id": 10, "image_item_id": 4},

    # 家電（id=11）→ カッコいい、信頼できる
    {"industry_id": 11, "image_item_id": 6},
    {"industry_id": 11, "image_item_id": 4},

    # 通信・IT（id=12）→ カッコいい、個性的
    {"industry_id": 12, "image_item_id": 6},
    {"industry_id": 12, "image_item_id": 3},

    # ゲーム・エンターテイメント・アプリ（id=13）→ おもしろい、個性的
    {"industry_id": 13, "image_item_id": 1},
    {"industry_id": 13, "image_item_id": 3},

    # 流通・通販（id=14）→ 信頼できる、おもしろい
    {"industry_id": 14, "image_item_id": 4},
    {"industry_id": 14, "image_item_id": 1},

    # ファッション（id=15）→ カッコいい、個性的
    {"industry_id": 15, "image_item_id": 6},
    {"industry_id": 15, "image_item_id": 3},

    # 貴金属（id=16）→ カッコいい、大人っぽい
    {"industry_id": 16, "image_item_id": 6},
    {"industry_id": 16, "image_item_id": 7},

    # 金融・不動産（id=17）→ 信頼できる、大人っぽい
    {"industry_id": 17, "image_item_id": 4},
    {"industry_id": 17, "image_item_id": 7},

    # エネルギー・輸送・交通（id=18）→ 信頼できる、カッコいい
    {"industry_id": 18, "image_item_id": 4},
    {"industry_id": 18, "image_item_id": 6},

    # 教育・出版・公共団体（id=19）→ 信頼できる、大人っぽい
    {"industry_id": 19, "image_item_id": 4},
    {"industry_id": 19, "image_item_id": 7},

    # 観光（id=20）→ おもしろい、可愛い
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

async def seed_industry_images():
    """industry_imagesテーブルにデータ投入"""
    print("\n📥 Seeding industry_images data...")

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
    print("🚀 Starting industry_images seeding (existing data protection)...")
    print("=" * 60)

    try:
        # industry_imagesテーブルのみクリア
        await clear_industry_images()

        # industry_imagesデータ投入
        seeded_count = await seed_industry_images()

        # 投入結果検証
        total_count = await verify_seeding()

        print("\n" + "=" * 60)
        print("✅ Industry_images seeding completed successfully!")
        print("=" * 60)
        print(f"📊 Summary:")
        print(f"   - Seeded: {seeded_count} records")
        print(f"   - Verified: {total_count} records")
        print(f"   - Status: ✅ STEP 2 matching ready")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ Error during seeding: {e}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    asyncio.run(main())