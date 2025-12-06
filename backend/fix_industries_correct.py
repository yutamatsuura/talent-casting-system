#!/usr/bin/env python3
"""業種マスタデータを正しい20業種に修正するスクリプト"""

import asyncio
import sys
from pathlib import Path

# backend/appへのパスを追加
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import select, delete
from app.db.connection import init_db, get_session_maker
from app.models import Industry

# グローバル変数でセッションメーカーを保持
AsyncSessionLocal = None

async def get_async_session():
    """非同期セッション取得"""
    global AsyncSessionLocal
    if AsyncSessionLocal is None:
        await init_db()
        AsyncSessionLocal = get_session_maker()
    return AsyncSessionLocal()

# 正しい20業種データ（ユーザー提供）
CORRECT_INDUSTRIES_DATA = [
    {"id": 1, "name": "食品", "display_order": 1},
    {"id": 2, "name": "菓子・氷菓", "display_order": 2},
    {"id": 3, "name": "乳製品", "display_order": 3},
    {"id": 4, "name": "清涼飲料水", "display_order": 4},
    {"id": 5, "name": "アルコール飲料", "display_order": 5},
    {"id": 6, "name": "フードサービス", "display_order": 6},
    {"id": 7, "name": "医薬品・医療・健康食品", "display_order": 7},
    {"id": 8, "name": "化粧品・ヘアケア・オーラルケア", "display_order": 8},
    {"id": 9, "name": "トイレタリー", "display_order": 9},
    {"id": 10, "name": "自動車関連", "display_order": 10},
    {"id": 11, "name": "家電", "display_order": 11},
    {"id": 12, "name": "通信・IT", "display_order": 12},
    {"id": 13, "name": "ゲーム・エンターテイメント・アプリ", "display_order": 13},
    {"id": 14, "name": "流通・通販", "display_order": 14},
    {"id": 15, "name": "ファッション", "display_order": 15},
    {"id": 16, "name": "貴金属", "display_order": 16},
    {"id": 17, "name": "金融・不動産", "display_order": 17},
    {"id": 18, "name": "エネルギー・輸送・交通", "display_order": 18},
    {"id": 19, "name": "教育・出版・公共団体", "display_order": 19},
    {"id": 20, "name": "観光", "display_order": 20},
]

async def clear_industries():
    """既存の業種データをクリア"""
    print("\n🧹 Clearing existing industries data...")

    async with await get_async_session() as session:
        await session.execute(delete(Industry))
        await session.commit()
        print("✅ Industries data cleared")

async def seed_correct_industries():
    """正しい業種データを投入"""
    print("\n📥 Seeding correct industries data...")

    async with await get_async_session() as session:
        for industry_data in CORRECT_INDUSTRIES_DATA:
            industry = Industry(**industry_data)
            session.add(industry)

        await session.commit()
        print(f"✅ Industries seeded: {len(CORRECT_INDUSTRIES_DATA)} records")

        return len(CORRECT_INDUSTRIES_DATA)

async def verify_seeding():
    """投入結果の検証"""
    print("\n🔍 Verifying seeded industries data...")

    async with await get_async_session() as session:
        result = await session.execute(select(Industry).order_by(Industry.id))
        industries = result.scalars().all()

        print(f"📊 Total industries records: {len(industries)}")
        print("📊 Updated industries list:")
        for industry in industries:
            print(f"   {industry.id}: {industry.name}")

        return len(industries)

async def main():
    """メイン処理"""
    print("=" * 60)
    print("🚀 Starting industries correction to proper 20 types...")
    print("=")
    print("正しい業種（ユーザー提供）:")
    for industry_data in CORRECT_INDUSTRIES_DATA:
        print(f"   {industry_data['id']}: {industry_data['name']}")
    print("=" * 60)

    try:
        # 既存の業種データクリア
        await clear_industries()

        # 正しい業種データ投入
        seeded_count = await seed_correct_industries()

        # 投入結果検証
        total_count = await verify_seeding()

        print("\n" + "=" * 60)
        print("✅ Industries correction completed successfully!")
        print("=" * 60)
        print(f"📊 Summary:")
        print(f"   - Seeded: {seeded_count} records")
        print(f"   - Verified: {total_count} records")
        print(f"   - Status: ✅ Correct 20 industries ready")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ Error during correction: {e}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    asyncio.run(main())