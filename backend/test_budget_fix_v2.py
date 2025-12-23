#!/usr/bin/env python3
"""
予算フィルタリング修正版のテスト
1. 新垣結衣が正しく除外されるか確認
2. 適切な予算範囲のタレントが表示されるか確認
"""
import asyncio
import asyncpg
from app.core.config import settings

async def test_budget_logic():
    """修正後の予算フィルタリングロジックをテスト"""
    conn = await asyncpg.connect(settings.database_url)

    try:
        print("=" * 60)
        print("予算フィルタリング修正版テスト")
        print("=" * 60)

        # 1,000万円～3,000万円未満の検索をシミュレート
        budget_max = 29999999  # 3,000万円未満の上限（円単位）

        print(f"\nテスト条件:")
        print(f"  予算範囲: 1,000万円～3,000万円未満")
        print(f"  max_amount: {budget_max:,}円")
        print(f"  万円換算: {budget_max / 10000}万円")

        # 修正後のロジックでテスト
        test_query = """
        SELECT
            ma.name_full_for_matching,
            ma.account_id,
            mta.money_min_one_year,
            mta.money_max_one_year,
            CASE
                WHEN mta.money_min_one_year IS NOT NULL AND mta.money_max_one_year IS NOT NULL
                     AND mta.money_min_one_year <= $1 / 10000 THEN 'PASS (MIN<=budget)'
                WHEN mta.money_min_one_year IS NOT NULL AND mta.money_max_one_year IS NULL
                     AND mta.money_min_one_year <= $1 / 10000 THEN 'PASS (MIN<=budget, no MAX)'
                WHEN mta.money_min_one_year IS NULL AND mta.money_max_one_year IS NOT NULL
                     AND mta.money_max_one_year <= $1 / 10000 THEN 'PASS (no MIN, MAX<=budget)'
                ELSE 'FILTER OUT'
            END as filter_result
        FROM m_account ma
        LEFT JOIN m_talent_act mta ON ma.account_id = mta.account_id
        WHERE ma.del_flag = 0
          AND mta.account_id IS NOT NULL
          AND (ma.name_full_for_matching LIKE '%新垣%'
               OR ma.name_full_for_matching LIKE '%結衣%'
               OR ma.name_full_for_matching LIKE '%夏川%')
        ORDER BY mta.money_min_one_year DESC
        """

        print(f"\n検索対象タレント（新垣、夏川等）:")
        results = await conn.fetch(test_query, budget_max)

        for row in results:
            name = row['name_full_for_matching']
            min_val = row['money_min_one_year']
            max_val = row['money_max_one_year']
            result = row['filter_result']

            print(f"  - {name}")
            print(f"    MIN: {min_val}万円, MAX: {max_val}万円")
            print(f"    判定: {result}")

            if '新垣' in name:
                if result == 'FILTER OUT':
                    print("    ✅ 新垣結衣が正しく除外されました")
                else:
                    print("    ❌ 新垣結衣が除外されていません！")
            print()

        # 実際にフィルタを通過するタレントの数をチェック
        count_query = """
        SELECT COUNT(*) as total_count
        FROM m_account ma
        LEFT JOIN m_talent_act mta ON ma.account_id = mta.account_id
        WHERE ma.del_flag = 0
          AND mta.account_id IS NOT NULL
          AND (
            (mta.money_min_one_year IS NOT NULL AND mta.money_max_one_year IS NOT NULL
             AND mta.money_min_one_year <= $1 / 10000)
            OR
            (mta.money_min_one_year IS NOT NULL AND mta.money_max_one_year IS NULL
             AND mta.money_min_one_year <= $1 / 10000)
            OR
            (mta.money_min_one_year IS NULL AND mta.money_max_one_year IS NOT NULL
             AND mta.money_max_one_year <= $1 / 10000)
          )
        """

        count_result = await conn.fetchrow(count_query, budget_max)
        total_count = count_result['total_count']

        print(f"フィルタ通過タレント総数: {total_count}名")

        if total_count > 0:
            print("✅ 修正により適切な数のタレントが表示されるようになりました")
        else:
            print("❌ まだ全てのタレントが除外されています")

        # サンプルで通過するタレントを表示
        sample_query = """
        SELECT
            ma.name_full_for_matching,
            mta.money_min_one_year,
            mta.money_max_one_year
        FROM m_account ma
        LEFT JOIN m_talent_act mta ON ma.account_id = mta.account_id
        WHERE ma.del_flag = 0
          AND mta.account_id IS NOT NULL
          AND (
            (mta.money_min_one_year IS NOT NULL AND mta.money_max_one_year IS NOT NULL
             AND mta.money_min_one_year <= $1 / 10000)
            OR
            (mta.money_min_one_year IS NOT NULL AND mta.money_max_one_year IS NULL
             AND mta.money_min_one_year <= $1 / 10000)
            OR
            (mta.money_min_one_year IS NULL AND mta.money_max_one_year IS NOT NULL
             AND mta.money_max_one_year <= $1 / 10000)
          )
        ORDER BY mta.money_min_one_year
        LIMIT 10
        """

        print(f"\n通過するタレント（サンプル10件）:")
        sample_results = await conn.fetch(sample_query, budget_max)
        for row in sample_results:
            print(f"  - {row['name_full_for_matching']}: MIN={row['money_min_one_year']}万円, MAX={row['money_max_one_year']}万円")

    except Exception as e:
        print(f"エラー: {e}")
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(test_budget_logic())