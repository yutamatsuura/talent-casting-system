#!/usr/bin/env python3
"""
タレント予算データの単位確認
"""
import asyncio
import asyncpg

async def check_talent_money_data():
    """m_talent_actテーブルの予算データ確認"""
    print("=" * 80)
    print("🔍 タレント予算データ単位調査")
    print("=" * 80)

    try:
        conn = await asyncpg.connect(
            host='ep-sparkling-smoke-a183z7h8-pooler.ap-southeast-1.aws.neon.tech',
            user='neondb_owner',
            password='npg_5X1MlRZzVheF',
            database='neondb',
            ssl='require'
        )

        # タレントの予算データサンプル確認
        print("📊 m_talent_actテーブルの予算データサンプル:")
        money_query = """
        SELECT
            account_id,
            money_min_one_year,
            money_max_one_year
        FROM m_talent_act
        WHERE money_min_one_year IS NOT NULL
           OR money_max_one_year IS NOT NULL
        ORDER BY account_id
        LIMIT 10
        """
        money_rows = await conn.fetch(money_query)

        for row in money_rows:
            print(f"   account_id: {row['account_id']}, "
                  f"MIN: {row['money_min_one_year']}, "
                  f"MAX: {row['money_max_one_year']}")

        # 999万円以下のタレント数確認
        print(f"\n🧪 予算フィルタリングテスト:")

        # テスト1: 999（万円）以上のタレント数
        test1_query = """
        SELECT COUNT(*) as count
        FROM m_talent_act
        WHERE account_id IS NOT NULL
          AND (
            (money_min_one_year IS NOT NULL AND money_max_one_year IS NOT NULL
             AND 999 >= money_min_one_year)
            OR
            (money_min_one_year IS NOT NULL AND money_max_one_year IS NULL
             AND 999 >= money_min_one_year)
            OR
            (money_min_one_year IS NULL AND money_max_one_year IS NOT NULL
             AND 999 >= money_max_one_year)
          )
        """
        test1_result = await conn.fetchrow(test1_query)
        print(f"   999(万円)以上のタレント数: {test1_result['count']}")

        # テスト2: 9990000（円）以上のタレント数
        test2_query = """
        SELECT COUNT(*) as count
        FROM m_talent_act
        WHERE account_id IS NOT NULL
          AND (
            (money_min_one_year IS NOT NULL AND money_max_one_year IS NOT NULL
             AND 9990000 >= money_min_one_year)
            OR
            (money_min_one_year IS NOT NULL AND money_max_one_year IS NULL
             AND 9990000 >= money_min_one_year)
            OR
            (money_min_one_year IS NULL AND money_max_one_year IS NOT NULL
             AND 9990000 >= money_max_one_year)
          )
        """
        test2_result = await conn.fetchrow(test2_query)
        print(f"   9990000(円)以上のタレント数: {test2_result['count']}")

        # 予算データの統計確認
        stats_query = """
        SELECT
            MIN(money_min_one_year) as min_min,
            MAX(money_min_one_year) as max_min,
            AVG(money_min_one_year) as avg_min,
            MIN(money_max_one_year) as min_max,
            MAX(money_max_one_year) as max_max,
            AVG(money_max_one_year) as avg_max,
            COUNT(*) as total_with_data
        FROM m_talent_act
        WHERE money_min_one_year IS NOT NULL
           OR money_max_one_year IS NOT NULL
        """
        stats_result = await conn.fetchrow(stats_query)
        print(f"\n📈 予算データ統計:")
        print(f"   MIN値範囲: {stats_result['min_min']} ～ {stats_result['max_min']} (平均: {stats_result['avg_min']:.0f})")
        print(f"   MAX値範囲: {stats_result['min_max']} ～ {stats_result['max_max']} (平均: {stats_result['avg_max']:.0f})")
        print(f"   データ件数: {stats_result['total_with_data']}")

        await conn.close()

    except Exception as e:
        print(f"❌ エラー: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(check_talent_money_data())