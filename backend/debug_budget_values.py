#!/usr/bin/env python3
"""
デバッグ: データベースの実際の予算値を調査
新垣結衣の予算データと他のタレントの予算データを確認
"""
import asyncio
import asyncpg
from app.core.config import settings

async def debug_budget_values():
    """データベースの実際の予算値を調査"""
    conn = await asyncpg.connect(settings.database_url)

    try:
        print("=" * 60)
        print("データベース予算値調査")
        print("=" * 60)

        # 新垣結衣の予算データを確認
        print("\n1. 新垣結衣の予算データ:")
        aragaki_query = """
        SELECT
            ma.name_full_for_matching,
            ma.account_id,
            mta.money_min_one_year,
            mta.money_max_one_year,
            mta.money_min_one_year * 10000 as min_converted,
            mta.money_max_one_year * 10000 as max_converted
        FROM m_account ma
        LEFT JOIN m_talent_act mta ON ma.account_id = mta.account_id
        WHERE ma.name_full_for_matching LIKE '%新垣%' OR ma.name_full_for_matching LIKE '%結衣%'
        ORDER BY ma.name_full_for_matching
        """

        aragaki_results = await conn.fetch(aragaki_query)
        for row in aragaki_results:
            print(f"  - {row['name_full_for_matching']}")
            print(f"    ID: {row['account_id']}")
            print(f"    money_min_one_year: {row['money_min_one_year']}")
            print(f"    money_max_one_year: {row['money_max_one_year']}")
            print(f"    min_converted (x10000): {row['min_converted']}")
            print(f"    max_converted (x10000): {row['max_converted']}")
            print()

        # 他のタレントの予算データをサンプル確認
        print("2. 他のタレントの予算データ (サンプル10件):")
        sample_query = """
        SELECT
            ma.name_full_for_matching,
            mta.money_min_one_year,
            mta.money_max_one_year
        FROM m_account ma
        LEFT JOIN m_talent_act mta ON ma.account_id = mta.account_id
        WHERE mta.money_min_one_year IS NOT NULL
        ORDER BY mta.money_min_one_year
        LIMIT 10
        """

        sample_results = await conn.fetch(sample_query)
        for row in sample_results:
            print(f"  - {row['name_full_for_matching']}: MIN={row['money_min_one_year']}, MAX={row['money_max_one_year']}")

        # 予算範囲の統計
        print("\n3. 予算範囲の統計:")
        stats_query = """
        SELECT
            MIN(money_min_one_year) as min_budget,
            MAX(money_min_one_year) as max_budget,
            AVG(money_min_one_year) as avg_budget,
            COUNT(*) as total_count
        FROM m_talent_act
        WHERE money_min_one_year IS NOT NULL
        """

        stats = await conn.fetchrow(stats_query)
        print(f"  最小予算: {stats['min_budget']}")
        print(f"  最大予算: {stats['max_budget']}")
        print(f"  平均予算: {stats['avg_budget']:.2f}")
        print(f"  総件数: {stats['total_count']}")

        # ユーザーが選択する予算範囲との比較
        print("\n4. 予算範囲との比較:")
        print("  ユーザー選択: '1,000万円～3,000万円未満'")
        print("  これは10,000,000円～29,999,999円")
        if aragaki_results and aragaki_results[0]['money_min_one_year']:
            min_val = aragaki_results[0]['money_min_one_year']
            print(f"  新垣結衣のmin予算: {min_val}")
            print(f"  これが万円単位なら: {min_val}万円 = {min_val * 10000}円")
            print(f"  これが円単位なら: {min_val}円")
            print(f"  1,000万円～3,000万円未満 (10,000,000円～29,999,999円) と比較:")
            print(f"    現在のロジック(x10000): {min_val * 10000} <= 10,000,000 = {min_val * 10000 <= 10000000}")
            print(f"    修正前のロジック(そのまま): {min_val} <= 10,000,000 = {min_val <= 10000000}")
        else:
            print(f"  新垣結衣のデータが見つかりません")

    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(debug_budget_values())