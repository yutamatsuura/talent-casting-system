#!/usr/bin/env python3
"""
新垣結衣の正しいaccount_idを検索
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

async def find_aragaki():
    """新垣結衣を検索"""
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ ERROR: DATABASE_URL not found")
        return

    conn = await asyncpg.connect(database_url)

    try:
        print("="*80)
        print("🔍 新垣結衣 検索")
        print("="*80)

        # 名前で検索
        query = """
        SELECT
            ma.account_id,
            ma.name_full_for_matching as talent_name,
            mta.money_min_one_year,
            mta.money_max_one_year
        FROM m_account ma
        LEFT JOIN m_talent_act mta ON ma.account_id = mta.account_id
        WHERE ma.name_full_for_matching LIKE '%新垣%'
           OR ma.name_full_for_matching LIKE '%ガッキー%'
           OR ma.name_full_for_matching LIKE '%aragaki%'
        ORDER BY ma.account_id;
        """

        results = await conn.fetch(query)

        if results:
            print(f"\n検索結果: {len(results)}件")
            print("-" * 80)
            for row in results:
                min_str = f"{row['money_min_one_year']:,}" if row['money_min_one_year'] else "NULL"
                max_str = f"{row['money_max_one_year']:,}" if row['money_max_one_year'] else "NULL"
                print(f"ID: {row['account_id']:6d} | 名前: {row['talent_name']:20s} | MIN: {min_str:15s} | MAX: {max_str:15s}")
        else:
            print("\n⚠️  新垣結衣が見つかりません")

        # 予算帯で検索（MIN/MAX が 4000-5000 の範囲）
        print("\n" + "="*80)
        print("🔍 予算帯 4,000-5,000 のタレント検索（単位問題の可能性）")
        print("="*80)

        query2 = """
        SELECT
            ma.account_id,
            ma.name_full_for_matching as talent_name,
            mta.money_min_one_year,
            mta.money_max_one_year
        FROM m_account ma
        LEFT JOIN m_talent_act mta ON ma.account_id = mta.account_id
        WHERE (mta.money_min_one_year BETWEEN 3000 AND 6000
               OR mta.money_max_one_year BETWEEN 3000 AND 6000)
        ORDER BY mta.money_max_one_year DESC
        LIMIT 10;
        """

        results2 = await conn.fetch(query2)

        if results2:
            print(f"\n検索結果: {len(results2)}件")
            print("-" * 80)
            for row in results2:
                min_str = f"{row['money_min_one_year']:,}" if row['money_min_one_year'] else "NULL"
                max_str = f"{row['money_max_one_year']:,}" if row['money_max_one_year'] else "NULL"
                print(f"ID: {row['account_id']:6d} | 名前: {row['talent_name']:20s} | MIN: {min_str:15s} | MAX: {max_str:15s}")

    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(find_aragaki())
