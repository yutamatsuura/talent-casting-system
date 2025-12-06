#!/usr/bin/env python3
"""
m_talent_actテーブルのデータカバレッジ調査

調査項目:
1. m_accountとm_talent_actの結合状況
2. money_max_one_yearがNULLのタレント数
3. おすすめタレント（仁村紗和）の具体的なデータ状況
4. 予算フィルタで除外されるタレントの割合
"""

import asyncio
from app.db.connection import get_asyncpg_connection

async def investigate_talent_act_coverage():
    print("🔍 m_talent_actテーブルデータカバレッジ調査")
    print("=" * 60)

    conn = await get_asyncpg_connection()
    try:
        # 1. 基本統計情報
        print("\n1️⃣ 基本統計情報")

        # m_accountの総数
        total_accounts = await conn.fetchval("SELECT COUNT(*) FROM m_account WHERE del_flag = 0")
        print(f"有効なm_account総数: {total_accounts:,}")

        # m_talent_actの総数
        total_talent_acts = await conn.fetchval("SELECT COUNT(*) FROM m_talent_act")
        print(f"m_talent_act総数: {total_talent_acts:,}")

        # 結合可能なタレント数
        join_count = await conn.fetchval("""
            SELECT COUNT(*) FROM m_account ma
            INNER JOIN m_talent_act mta ON ma.account_id = mta.account_id
            WHERE ma.del_flag = 0
        """)
        print(f"m_talent_actと結合可能: {join_count:,}")

        # カバレッジ率
        coverage_rate = (join_count / total_accounts * 100) if total_accounts > 0 else 0
        print(f"カバレッジ率: {coverage_rate:.2f}%")

        print()

        # 2. money_max_one_year の状況
        print("2️⃣ money_max_one_year データ状況")

        # money_max_one_yearがNULLでないレコード数
        money_not_null = await conn.fetchval("""
            SELECT COUNT(*) FROM m_talent_act
            WHERE money_max_one_year IS NOT NULL
        """)
        print(f"money_max_one_year NOT NULL: {money_not_null:,}")

        # money_max_one_yearがNULLのレコード数
        money_null = await conn.fetchval("""
            SELECT COUNT(*) FROM m_talent_act
            WHERE money_max_one_year IS NULL
        """)
        print(f"money_max_one_year NULL: {money_null:,}")

        # NULLの割合
        null_rate = (money_null / total_talent_acts * 100) if total_talent_acts > 0 else 0
        print(f"NULLの割合: {null_rate:.2f}%")

        print()

        # 3. 仁村紗和の具体的なデータ状況
        print("3️⃣ 仁村紗和のデータ状況確認")

        # account_id = 123の詳細確認
        kimura_data = await conn.fetchrow("""
            SELECT
                ma.account_id,
                ma.name_full_for_matching,
                ma.del_flag,
                mta.account_id as talent_act_id,
                mta.money_max_one_year,
                mta.money_min_one_year
            FROM m_account ma
            LEFT JOIN m_talent_act mta ON ma.account_id = mta.account_id
            WHERE ma.account_id = 123
        """)

        if kimura_data:
            print(f"✅ 仁村紗和データ存在:")
            print(f"  - account_id: {kimura_data['account_id']}")
            print(f"  - name: {kimura_data['name_full_for_matching']}")
            print(f"  - del_flag: {kimura_data['del_flag']}")
            print(f"  - m_talent_act存在: {'Yes' if kimura_data['talent_act_id'] else 'No'}")
            print(f"  - money_max_one_year: {kimura_data['money_max_one_year']}")
            print(f"  - money_min_one_year: {kimura_data['money_min_one_year']}")
        else:
            print("❌ 仁村紗和（account_id=123）のデータが見つかりません")

        print()

        # 4. 現在の予算フィルタで除外されるタレント分析
        print("4️⃣ 予算フィルタ除外分析")

        # 各予算区分での除外状況をチェック
        budget_ranges = [
            ("1,000万円未満", 10000000),
            ("1,000万円～3,000万円未満", 30000000),
            ("3,000万円～1億円未満", 100000000)
        ]

        for budget_name, max_budget in budget_ranges:
            # 現在のフィルタロジックでカウント
            included_current = await conn.fetchval(f"""
                SELECT COUNT(DISTINCT ma.account_id)
                FROM m_account ma
                LEFT JOIN m_talent_act mta ON ma.account_id = mta.account_id
                WHERE ma.del_flag = 0
                  AND (
                    mta.money_max_one_year IS NULL
                    OR ({max_budget} = 'Infinity' OR mta.money_max_one_year <= {max_budget})
                  )
            """)

            # 理想的なフィルタ（NULLも含む）でカウント
            included_ideal = await conn.fetchval(f"""
                SELECT COUNT(*)
                FROM m_account ma
                WHERE ma.del_flag = 0
            """)

            print(f"{budget_name}:")
            print(f"  - 現在のロジック対象: {included_current:,}")
            print(f"  - 理想的な対象: {included_ideal:,}")
            print(f"  - 除外率: {((included_ideal - included_current) / included_ideal * 100):.2f}%")

        print()

        # 5. m_talent_actデータがないタレント一覧（サンプル）
        print("5️⃣ m_talent_actデータ欠損タレント（上位10名）")

        missing_talents = await conn.fetch("""
            SELECT ma.account_id, ma.name_full_for_matching, ma.act_genre
            FROM m_account ma
            LEFT JOIN m_talent_act mta ON ma.account_id = mta.account_id
            WHERE ma.del_flag = 0 AND mta.account_id IS NULL
            ORDER BY ma.account_id
            LIMIT 10
        """)

        if missing_talents:
            for talent in missing_talents:
                print(f"  - ID={talent['account_id']:4}: {talent['name_full_for_matching']} ({talent['act_genre']})")
        else:
            print("  データ欠損タレントは存在しません")

        print()

        # 6. 解決策の提案
        print("6️⃣ 問題と解決策")
        excluded_count = total_accounts - join_count
        if excluded_count > 0:
            print(f"❌ 問題: {excluded_count:,}名のタレントがm_talent_act未登録により")
            print("   予算フィルタで完全除外されています")
            print()
            print("💡 解決策:")
            print("1. ✅ LEFT JOINを使用してm_talent_actがNULLでも対象に含める")
            print("2. ✅ NULLの場合は予算制限なしとして扱う")
            print("3. ✅ おすすめタレントは予算に関係なく表示")
        else:
            print("✅ 全タレントがm_talent_actに登録済みです")

    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(investigate_talent_act_coverage())