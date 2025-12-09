#!/usr/bin/env python3
"""
予算の単位を正確に確認
"""
import asyncio
from app.db.connection import get_asyncpg_connection

async def verify_budget_units():
    print("🔍 予算単位の正確な確認")
    print("=" * 50)

    conn = await get_asyncpg_connection()
    try:
        # 1. 実際のタレント契約金額確認
        talent_money_query = """
        SELECT
            ma.account_id,
            ma.name_full_for_matching,
            mta.money_max_one_year,
            -- 1億5000万円なら150000が格納されているはず
            CASE
                WHEN mta.money_max_one_year >= 100000 THEN CONCAT(mta.money_max_one_year/10000, '億円')
                WHEN mta.money_max_one_year >= 10000 THEN CONCAT(mta.money_max_one_year/10000, '億円')
                ELSE CONCAT(mta.money_max_one_year, '万円')
            END as amount_display
        FROM m_account ma
        JOIN m_talent_act mta ON ma.account_id = mta.account_id
        WHERE ma.del_flag = 0
        ORDER BY mta.money_max_one_year DESC
        LIMIT 15
        """

        talents = await conn.fetch(talent_money_query)

        print("\n💰 タレント契約金額トップ15:")
        print("ID   | 名前           | 契約金額    | 表示")
        print("-" * 55)

        for talent in talents:
            name = (talent['name_full_for_matching'] or 'Unknown')[:12].ljust(12)
            amount = talent['money_max_one_year']
            display = talent['amount_display']
            print(f"{talent['account_id']:>4} | {name} | {amount:>10} | {display}")

        # 2. 予算区分の単位確認
        print("\n\n💳 予算区分マスタ:")
        budget_query = """
        SELECT range_name, max_amount,
               CASE
                   WHEN max_amount >= 10000 THEN CONCAT(max_amount/10000, '億円')
                   ELSE CONCAT(max_amount, '万円')
               END as budget_display
        FROM budget_ranges
        ORDER BY max_amount
        """

        budgets = await conn.fetch(budget_query)
        for budget in budgets:
            print(f"'{budget['range_name']}' → {budget['max_amount']} ({budget['budget_display']})")

        # 3. 実際のフィルタリング確認（1,000万円〜3,000万円未満 = 2999）
        print(f"\n\n🔍 '1,000万円〜3,000万円未満'での実際のフィルタリング:")
        print("予算上限: 2999")

        filter_test_query = """
        SELECT
            ma.account_id,
            ma.name_full_for_matching,
            mta.money_max_one_year,
            CASE
                WHEN mta.money_max_one_year IS NULL THEN 'PASS (NULL)'
                WHEN mta.money_max_one_year <= 2999 THEN 'PASS'
                ELSE 'REJECT'
            END as filter_result
        FROM m_account ma
        LEFT JOIN m_talent_act mta ON ma.account_id = mta.account_id
        WHERE ma.del_flag = 0
        ORDER BY mta.money_max_one_year DESC NULLS LAST
        LIMIT 20
        """

        filter_results = await conn.fetch(filter_test_query)

        print("\nID   | 名前           | 契約金額    | フィルタ結果")
        print("-" * 60)

        pass_count = 0
        reject_count = 0

        for result in filter_results:
            name = (result['name_full_for_matching'] or 'Unknown')[:12].ljust(12)
            amount = result['money_max_one_year'] or 'NULL'
            filter_result = result['filter_result']

            if filter_result == 'PASS' or filter_result == 'PASS (NULL)':
                pass_count += 1
            else:
                reject_count += 1

            print(f"{result['account_id']:>4} | {name} | {str(amount):>10} | {filter_result}")

        # 4. 総計確認
        print(f"\n📊 フィルタ結果サマリー（上位20名中）:")
        print(f"   PASS: {pass_count}名")
        print(f"   REJECT: {reject_count}名")

        # 5. 全体の統計
        stats_query = """
        SELECT
            COUNT(*) as total_talents,
            COUNT(CASE WHEN mta.money_max_one_year IS NULL THEN 1 END) as null_amount,
            COUNT(CASE WHEN mta.money_max_one_year <= 2999 THEN 1 END) as within_budget,
            COUNT(CASE WHEN mta.money_max_one_year > 2999 THEN 1 END) as over_budget
        FROM m_account ma
        LEFT JOIN m_talent_act mta ON ma.account_id = mta.account_id
        WHERE ma.del_flag = 0
        """

        stats = await conn.fetchrow(stats_query)

        print(f"\n📈 全体統計:")
        print(f"   総タレント数: {stats['total_talents']}")
        print(f"   契約金額NULL: {stats['null_amount']}")
        print(f"   2999以下: {stats['within_budget']}")
        print(f"   2999超過: {stats['over_budget']}")

    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(verify_budget_units())