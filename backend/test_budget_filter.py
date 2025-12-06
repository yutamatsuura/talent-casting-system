"""予算フィルタリング修正の動作確認テストスクリプト"""
import asyncio
import sys
from pathlib import Path

# バックエンドモジュールへのパスを追加
sys.path.insert(0, str(Path(__file__).parent))

from app.db.connection import get_asyncpg_connection


async def test_budget_filter():
    """予算フィルタリングロジックのテスト"""
    conn = await get_asyncpg_connection()
    try:
        print("=" * 80)
        print("予算フィルタリング修正テスト")
        print("=" * 80)

        # テストケース1: 「1,000万円未満」選択時のシミュレーション
        print("\n[テストケース1] 「1,000万円未満」選択時")
        print("-" * 80)
        max_budget_1 = 1000.0
        query_1 = """
        SELECT
            ma.account_id,
            ma.name_full_for_matching,
            mta.money_max_one_year
        FROM m_account ma
        LEFT JOIN m_talent_act mta ON ma.account_id = mta.account_id
        WHERE (
            mta.money_max_one_year IS NULL
            OR ($1 = 'Infinity'::float8 OR mta.money_max_one_year <= $1)
        )
        ORDER BY mta.money_max_one_year NULLS LAST, ma.account_id
        LIMIT 10
        """
        rows_1 = await conn.fetch(query_1, max_budget_1)
        print(f"抽出件数: {len(rows_1)}件")
        print("\n上位10件のタレント:")
        for row in rows_1:
            budget_str = f"{row['money_max_one_year']:.1f}万円" if row['money_max_one_year'] else "NULL(要相談)"
            print(f"  - {row['name_full_for_matching']}: {budget_str}")

        # テストケース2: 「1,000万円〜3,000万円未満」選択時のシミュレーション
        print("\n[テストケース2] 「1,000万円〜3,000万円未満」選択時")
        print("-" * 80)
        max_budget_2 = 3000.0
        query_2 = """
        SELECT
            ma.account_id,
            ma.name_full_for_matching,
            mta.money_max_one_year,
            CASE
                WHEN mta.money_max_one_year IS NULL THEN 'NULL(要相談)'
                WHEN mta.money_max_one_year < 1000 THEN '1,000万円未満'
                WHEN mta.money_max_one_year >= 1000 AND mta.money_max_one_year < 3000 THEN '1,000〜3,000万円'
            END as budget_category
        FROM m_account ma
        LEFT JOIN m_talent_act mta ON ma.account_id = mta.account_id
        WHERE (
            mta.money_max_one_year IS NULL
            OR ($1 = 'Infinity'::float8 OR mta.money_max_one_year <= $1)
        )
        ORDER BY mta.money_max_one_year NULLS LAST, ma.account_id
        LIMIT 15
        """
        rows_2 = await conn.fetch(query_2, max_budget_2)
        print(f"抽出件数: {len(rows_2)}件")
        print("\n上位15件のタレント（予算区分別）:")

        # 予算区分ごとにカウント
        budget_categories = {}
        for row in rows_2:
            category = row['budget_category']
            if category not in budget_categories:
                budget_categories[category] = []
            budget_categories[category].append(row)

        for category, talents in budget_categories.items():
            print(f"\n  [{category}] {len(talents)}件")
            for talent in talents[:5]:  # 各カテゴリ最大5件表示
                budget_str = f"{talent['money_max_one_year']:.1f}万円" if talent['money_max_one_year'] else "NULL"
                print(f"    - {talent['name_full_for_matching']}: {budget_str}")

        # テストケース3: 「1億円以上」選択時のシミュレーション
        print("\n[テストケース3] 「1億円以上」選択時")
        print("-" * 80)
        max_budget_3 = float('inf')
        query_3 = """
        SELECT
            COUNT(*) as total_count,
            COUNT(mta.money_max_one_year) as with_budget_count,
            COUNT(*) - COUNT(mta.money_max_one_year) as null_count
        FROM m_account ma
        LEFT JOIN m_talent_act mta ON ma.account_id = mta.account_id
        WHERE (
            mta.money_max_one_year IS NULL
            OR ($1 = 'Infinity'::float8 OR mta.money_max_one_year <= $1)
        )
        """
        summary_3 = await conn.fetchrow(query_3, max_budget_3)
        print(f"総抽出件数: {summary_3['total_count']}件")
        print(f"  - 予算あり: {summary_3['with_budget_count']}件")
        print(f"  - NULL(要相談): {summary_3['null_count']}件")

        # 全体の統計情報
        print("\n[全体統計]")
        print("-" * 80)
        stats_query = """
        SELECT
            COUNT(DISTINCT ma.account_id) as total_talents,
            COUNT(DISTINCT CASE WHEN mta.money_max_one_year IS NOT NULL THEN ma.account_id END) as talents_with_budget,
            COUNT(DISTINCT CASE WHEN mta.money_max_one_year IS NULL THEN ma.account_id END) as talents_without_budget,
            MIN(mta.money_max_one_year) as min_budget,
            MAX(mta.money_max_one_year) as max_budget,
            AVG(mta.money_max_one_year) as avg_budget
        FROM m_account ma
        LEFT JOIN m_talent_act mta ON ma.account_id = mta.account_id
        """
        stats = await conn.fetchrow(stats_query)
        print(f"総タレント数: {stats['total_talents']}名")
        print(f"予算データあり: {stats['talents_with_budget']}名")
        print(f"予算データなし(NULL): {stats['talents_without_budget']}名")
        if stats['min_budget']:
            print(f"最低予算: {stats['min_budget']:.1f}万円")
            print(f"最高予算: {stats['max_budget']:.1f}万円")
            print(f"平均予算: {stats['avg_budget']:.1f}万円")

        print("\n" + "=" * 80)
        print("テスト完了!")
        print("=" * 80)

    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(test_budget_filter())
