#!/usr/bin/env python3
"""
予算フィルタリング修正の検証スクリプト
新垣結衣が正しく除外されることを確認
"""
import os
import asyncio
import asyncpg
from dotenv import load_dotenv
from pathlib import Path

# 環境変数の読み込み
project_root = Path(__file__).parent.parent
env_file = project_root / '.env.local'
load_dotenv(env_file)

async def verify_budget_fix():
    """修正後の予算フィルタリングを検証"""
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ ERROR: DATABASE_URL not found")
        return

    conn = await asyncpg.connect(database_url)

    try:
        print("="*80)
        print("🔍 予算フィルタリング修正の検証")
        print("="*80)

        budget_max = 30000000  # 3,000万円

        # 修正後のロジックを再現
        query = """
        WITH step0_budget_filter AS (
            SELECT DISTINCT ma.account_id, ma.name_full_for_matching as name,
                   mta.money_min_one_year, mta.money_max_one_year,
                   mta.money_min_one_year * 10000 as min_in_yen,
                   mta.money_max_one_year * 10000 as max_in_yen
            FROM m_account ma
            LEFT JOIN m_talent_act mta ON ma.account_id = mta.account_id
            WHERE ma.del_flag = 0
              AND ma.account_id = 30  -- 新垣結衣
              AND mta.account_id IS NOT NULL
              AND (
                (mta.money_min_one_year IS NOT NULL AND mta.money_max_one_year IS NOT NULL
                 AND mta.money_min_one_year * 10000 <= $1)
                OR
                (mta.money_min_one_year IS NOT NULL AND mta.money_max_one_year IS NULL
                 AND mta.money_min_one_year * 10000 <= $1)
                OR
                (mta.money_min_one_year IS NULL AND mta.money_max_one_year IS NOT NULL
                 AND mta.money_max_one_year * 10000 <= $1)
              )
        )
        SELECT * FROM step0_budget_filter;
        """

        print("\n【修正後】予算フィルタリングテスト")
        print("-" * 80)
        print(f"ユーザー予算上限: {budget_max:,}円 (3,000万円)")
        print(f"新垣結衣 account_id: 30")
        print()

        result = await conn.fetch(query, budget_max)

        if result:
            print("❌ FAIL: 新垣結衣が含まれています（修正が適用されていない可能性）")
            for row in result:
                print(f"\n  タレント名: {row['name']}")
                print(f"  MIN（万円単位）: {row['money_min_one_year']:,}")
                print(f"  MAX（万円単位）: {row['money_max_one_year'] if row['money_max_one_year'] else 'NULL'}")
                print(f"  MIN（円単位）: {row['min_in_yen']:,}円" if row['min_in_yen'] else "  MIN（円単位）: NULL")
                print(f"  MAX（円単位）: {row['max_in_yen']:,}円" if row['max_in_yen'] else "  MAX（円単位）: NULL")
        else:
            print("✅ SUCCESS: 新垣結衣が正しく除外されました！")

        # 追加検証: 予算内のタレントが通過することを確認
        print("\n" + "="*80)
        print("【追加検証】予算内タレントが通過することを確認")
        print("="*80)

        query2 = """
        WITH step0_budget_filter AS (
            SELECT DISTINCT ma.account_id, ma.name_full_for_matching as name,
                   mta.money_min_one_year, mta.money_max_one_year,
                   mta.money_min_one_year * 10000 as min_in_yen
            FROM m_account ma
            LEFT JOIN m_talent_act mta ON ma.account_id = mta.account_id
            WHERE ma.del_flag = 0
              AND mta.account_id IS NOT NULL
              AND (
                (mta.money_min_one_year IS NOT NULL AND mta.money_max_one_year IS NOT NULL
                 AND mta.money_min_one_year * 10000 <= $1)
                OR
                (mta.money_min_one_year IS NOT NULL AND mta.money_max_one_year IS NULL
                 AND mta.money_min_one_year * 10000 <= $1)
                OR
                (mta.money_min_one_year IS NULL AND mta.money_max_one_year IS NOT NULL
                 AND mta.money_max_one_year * 10000 <= $1)
              )
            ORDER BY mta.money_min_one_year DESC
            LIMIT 5
        )
        SELECT * FROM step0_budget_filter;
        """

        result2 = await conn.fetch(query2, budget_max)

        if result2:
            print(f"\n予算内タレント（上位5名）:")
            print("-" * 80)
            for row in result2:
                min_man = f"{row['money_min_one_year']:,}万円" if row['money_min_one_year'] else "NULL"
                min_yen = f"{row['min_in_yen']:,}円" if row['min_in_yen'] else "NULL"
                print(f"  {row['name']:20s} | MIN: {min_man:15s} ({min_yen})")
        else:
            print("⚠️  予算内のタレントが見つかりません（これは問題です）")

        print("\n" + "="*80)
        print("✅ 検証完了")
        print("="*80)

    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(verify_budget_fix())
