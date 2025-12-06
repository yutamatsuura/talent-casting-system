#!/usr/bin/env python3
"""予算区分マスタを正しい4区分に修正（クライアント正式仕様）"""

import asyncio
import sys
from pathlib import Path

# backend/appへのパスを追加
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import select, delete
from app.db.connection import init_db, get_session_maker
from app.models import BudgetRange

# グローバル変数でセッションメーカーを保持
AsyncSessionLocal = None

async def get_async_session():
    """非同期セッション取得"""
    global AsyncSessionLocal
    if AsyncSessionLocal is None:
        await init_db()
        AsyncSessionLocal = get_session_maker()
    return AsyncSessionLocal()

# 正しい予算区分データ（クライアント正式仕様）
CORRECT_BUDGET_RANGES_DATA = [
    {
        "id": 1,
        "name": "1,000万円未満",
        "min_amount": 0.00,
        "max_amount": 9999999.00,
        "display_order": 1
    },
    {
        "id": 2,
        "name": "1,000万円～3,000万円未満",
        "min_amount": 10000000.00,
        "max_amount": 29999999.00,
        "display_order": 2
    },
    {
        "id": 3,
        "name": "3,000万円～1億円未満",
        "min_amount": 30000000.00,
        "max_amount": 99999999.00,
        "display_order": 3
    },
    {
        "id": 4,
        "name": "1億円以上",
        "min_amount": 100000000.00,
        "max_amount": 999999999.00,
        "display_order": 4
    }
]

async def clear_budget_ranges():
    """既存の予算区分データをクリア"""
    print("\n🧹 Clearing existing budget_ranges data...")

    async with await get_async_session() as session:
        await session.execute(delete(BudgetRange))
        await session.commit()
        print("✅ Budget_ranges data cleared")

async def seed_correct_budget_ranges():
    """正しい予算区分データを投入"""
    print("\n📥 Seeding correct budget_ranges data (client specification)...")

    async with await get_async_session() as session:
        for budget_data in CORRECT_BUDGET_RANGES_DATA:
            budget_range = BudgetRange(**budget_data)
            session.add(budget_range)

        await session.commit()
        print(f"✅ Budget_ranges seeded: {len(CORRECT_BUDGET_RANGES_DATA)} records")

        return len(CORRECT_BUDGET_RANGES_DATA)

async def verify_seeding():
    """投入結果の検証"""
    print("\n🔍 Verifying correct budget_ranges data...")

    async with await get_async_session() as session:
        result = await session.execute(select(BudgetRange).order_by(BudgetRange.display_order))
        budget_ranges = result.scalars().all()

        print(f"📊 Total budget_ranges records: {len(budget_ranges)}")
        print("📊 Corrected budget ranges list:")
        for budget_range in budget_ranges:
            print(f"   {budget_range.id}: {budget_range.name}")
            print(f"       {budget_range.min_amount:,}円 ～ {budget_range.max_amount:,}円")

        return len(budget_ranges)

async def main():
    """メイン処理"""
    print("=" * 80)
    print("🚀 Correcting budget_ranges to client specification...")
    print("=" * 80)
    print("📋 Original issue: Incorrect 4 budget categories")
    print("🎯 Correct specification (client provided):")
    for budget_data in CORRECT_BUDGET_RANGES_DATA:
        print(f"   - {budget_data['name']}: {budget_data['min_amount']:,.0f}円～{budget_data['max_amount']:,.0f}円")
    print("=" * 80)

    try:
        # 既存の予算区分データクリア
        await clear_budget_ranges()

        # 正しい予算区分データ投入
        seeded_count = await seed_correct_budget_ranges()

        # 投入結果検証
        total_count = await verify_seeding()

        print("\n" + "=" * 80)
        print("✅ Budget_ranges correction completed successfully!")
        print("=" * 80)
        print(f"📊 Summary:")
        print(f"   - Seeded: {seeded_count} records")
        print(f"   - Verified: {total_count} records")
        print(f"   - Status: ✅ Client specification compliant")
        print("=" * 80)
        print("🔄 Next step: Update matching API to use correct budget filtering")
        print("=" * 80)

    except Exception as e:
        print(f"\n❌ Error during correction: {e}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    asyncio.run(main())