#!/usr/bin/env python3
"""
予算の単位を正確に確認（修正版）
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
            mta.money_max_one_year
        FROM m_account ma
        JOIN m_talent_act mta ON ma.account_id = mta.account_id
        WHERE ma.del_flag = 0
          AND mta.money_max_one_year IS NOT NULL
        ORDER BY mta.money_max_one_year DESC
        LIMIT 15
        """

        talents = await conn.fetch(talent_money_query)

        print("\n💰 タレント契約金額トップ15:")
        print("ID   | 名前           | 契約金額")
        print("-" * 45)

        for talent in talents:
            name = (talent['name_full_for_matching'] or 'Unknown')[:12].ljust(12)
            amount = talent['money_max_one_year'] or 0

            # 金額の解釈
            if amount == 15000:
                interpretation = "→ 1億5000万円？ or 1500万円？"
            elif amount == 30000:
                interpretation = "→ 3億円？ or 3000万円？"
            else:
                interpretation = ""

            print(f"{talent['account_id']:>4} | {name} | {amount:>10} {interpretation}")

        # 2. 予算区分の単位確認
        print("\n\n💳 予算区分マスタ:")
        budget_query = "SELECT range_name, max_amount FROM budget_ranges ORDER BY max_amount"
        budgets = await conn.fetch(budget_query)

        for budget in budgets:
            amount = budget['max_amount']
            if amount == 2999:
                interpretation = "→ 2999万円なら約3000万円"
            elif amount == 9999:
                interpretation = "→ 9999万円なら約1億円"
            else:
                interpretation = ""

            print(f"'{budget['range_name']}' → {amount} {interpretation}")

        # 3. 明石家さんまの具体例で検証
        print(f"\n\n🎯 明石家さんま(15000)の解釈検証:")

        sanma_query = """
        SELECT account_id, name_full_for_matching, money_max_one_year
        FROM m_account ma
        JOIN m_talent_act mta ON ma.account_id = mta.account_id
        WHERE ma.name_full_for_matching LIKE '%さんま%'
        """

        sanma_result = await conn.fetch(sanma_query)

        if sanma_result:
            for sanma in sanma_result:
                amount = sanma['money_max_one_year']
                print(f"  明石家さんま: {amount}")
                print(f"  もし単位が万円なら: {amount}万円")
                print(f"  もし1000万円単位なら: {amount/10}億円 = {amount*1000}万円")

        # 4. '1,000万円〜3,000万円未満'での実際のフィルタリング
        print(f"\n\n🔍 '1,000万円〜3,000万円未満'でのフィルタリングテスト:")
        print("予算上限設定値: 2999")

        filter_test_query = """
        SELECT
            COUNT(*) as total_count,
            COUNT(CASE WHEN mta.money_max_one_year IS NULL THEN 1 END) as null_count,
            COUNT(CASE WHEN mta.money_max_one_year <= 2999 THEN 1 END) as pass_count,
            COUNT(CASE WHEN mta.money_max_one_year > 2999 THEN 1 END) as reject_count,
            MIN(mta.money_max_one_year) as min_amount,
            MAX(mta.money_max_one_year) as max_amount
        FROM m_account ma
        LEFT JOIN m_talent_act mta ON ma.account_id = mta.account_id
        WHERE ma.del_flag = 0
        """

        filter_stats = await conn.fetchrow(filter_test_query)

        print(f"\n📊 フィルタリング統計:")
        print(f"   総タレント数: {filter_stats['total_count']}")
        print(f"   契約金額NULL: {filter_stats['null_count']}")
        print(f"   2999以下(PASS): {filter_stats['pass_count']}")
        print(f"   2999超過(REJECT): {filter_stats['reject_count']}")
        print(f"   最小金額: {filter_stats['min_amount']}")
        print(f"   最大金額: {filter_stats['max_amount']}")

        # 5. 2999以下のタレントサンプル
        print(f"\n\n✅ 2999以下で通過するタレントサンプル:")

        pass_sample_query = """
        SELECT ma.account_id, ma.name_full_for_matching, mta.money_max_one_year
        FROM m_account ma
        JOIN m_talent_act mta ON ma.account_id = mta.account_id
        WHERE ma.del_flag = 0
          AND mta.money_max_one_year <= 2999
        ORDER BY mta.money_max_one_year DESC
        LIMIT 10
        """

        pass_samples = await conn.fetch(pass_sample_query)

        for sample in pass_samples:
            name = (sample['name_full_for_matching'] or 'Unknown')[:15].ljust(15)
            amount = sample['money_max_one_year']
            print(f"   {sample['account_id']:>4} | {name} | {amount:>6}")

    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(verify_budget_units())