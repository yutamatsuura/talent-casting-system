#!/usr/bin/env python3
"""
STEP 0: 予算フィルタリングの詳細分析
仕様との整合性を確認
"""
import asyncio
from app.db.connection import get_asyncpg_connection

async def analyze_step0_budget_filtering():
    print("🔍 STEP 0: 予算フィルタリング詳細分析")
    print("=" * 70)

    conn = await get_asyncpg_connection()
    try:
        # 1. 仕様確認: 使用データ talents.money_max_one_year
        print("\n1️⃣ 仕様書記載のデータソース確認:")
        print("   仕様: 'talents.money_max_one_year（タレントの年間契約金額上限）'")

        # 実際のテーブル構造確認
        table_check = await conn.fetch("""
            SELECT table_name, column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name IN ('talents', 'm_account', 'm_talent_act')
              AND column_name LIKE '%money%'
            ORDER BY table_name, ordinal_position
        """)

        print("\n   実際のDB構造:")
        current_table = None
        for row in table_check:
            if row['table_name'] != current_table:
                current_table = row['table_name']
                print(f"\n   📋 {current_table}テーブル:")
            print(f"      {row['column_name']} ({row['data_type']}, nullable: {row['is_nullable']})")

        # 2. 実際の実装確認
        print("\n\n2️⃣ 実際の実装データソース確認:")

        # matching.pyから予算フィルタ部分を確認
        print("   実装確認: matching.pyの予算フィルタ部分")

        budget_filter_query = """
        SELECT
            ma.account_id,
            ma.name_full_for_matching,
            mta.money_max_one_year,
            -- 仕様通りの条件チェック
            CASE
                WHEN mta.money_max_one_year IS NULL THEN 'データなし'
                WHEN mta.money_max_one_year <= 30000 THEN '予算内'
                ELSE '予算外'
            END as budget_status
        FROM m_account ma
        LEFT JOIN m_talent_act mta ON ma.account_id = mta.account_id
        WHERE ma.del_flag = 0
        ORDER BY mta.money_max_one_year DESC NULLS LAST
        LIMIT 10
        """

        budget_samples = await conn.fetch(budget_filter_query)
        print("\n   サンプルデータ（予算フィルタ確認）:")
        print("   ID   | Name         | 年間契約上限 | 1000-3000万判定")
        print("   " + "-" * 55)

        for sample in budget_samples:
            name = (sample['name_full_for_matching'] or 'Unknown')[:12].ljust(12)
            amount = sample['money_max_one_year'] or 'NULL'
            status = sample['budget_status']
            print(f"   {sample['account_id']:>4} | {name} | {str(amount):>10} | {status}")

        # 3. 予算区分マスタとの整合性確認
        print("\n\n3️⃣ 予算区分マスタとの整合性確認:")

        budget_ranges = await conn.fetch("SELECT range_name, max_amount FROM budget_ranges ORDER BY max_amount")
        print("   予算区分マスタ:")
        for range_info in budget_ranges:
            print(f"     '{range_info['range_name']}' → 上限: {range_info['max_amount']}")

        # 4. 実際の filtering ロジック検証
        print("\n\n4️⃣ 実際のフィルタリングロジック検証:")

        # 1000万円〜3000万円未満での実際のフィルタリング結果
        actual_filter_query = """
        WITH budget_filtered AS (
            SELECT ma.account_id, ma.name_full_for_matching as name, ma.act_genre as category,
                   CASE
                       WHEN '1,000万円〜3,000万円未満' = '1000万円未満' THEN COALESCE(mta.money_max_one_year, 999999999) <= 10000
                       WHEN '1,000万円〜3,000万円未満' = '1000万円～3000万円未満' THEN COALESCE(mta.money_max_one_year, 999999999) BETWEEN 10000 AND 30000
                       WHEN '1,000万円〜3,000万円未満' = '3000万円～1億円未満' THEN COALESCE(mta.money_max_one_year, 999999999) BETWEEN 30000 AND 100000
                       WHEN '1,000万円〜3,000万円未満' = '1億円以上' THEN COALESCE(mta.money_max_one_year, 999999999) >= 100000
                       ELSE TRUE
                   END as budget_match,
                   mta.money_max_one_year
            FROM m_account ma
            LEFT JOIN m_talent_act mta ON ma.account_id = mta.account_id
            WHERE ma.del_flag = 0
        )
        SELECT
            COUNT(*) as total_talents,
            COUNT(CASE WHEN budget_match = TRUE THEN 1 END) as passed_filter,
            COUNT(CASE WHEN budget_match = FALSE THEN 1 END) as failed_filter,
            MIN(money_max_one_year) as min_amount,
            MAX(money_max_one_year) as max_amount,
            AVG(money_max_one_year) as avg_amount
        FROM budget_filtered
        """

        filter_result = await conn.fetchrow(actual_filter_query)
        print(f"   総タレント数: {filter_result['total_talents']}")
        print(f"   フィルタ通過: {filter_result['passed_filter']}")
        print(f"   フィルタ除外: {filter_result['failed_filter']}")
        print(f"   契約金額範囲: {filter_result['min_amount']} ～ {filter_result['max_amount']} (平均: {filter_result['avg_amount']:.1f})")

        # 5. 仕様との照合確認
        print("\n\n5️⃣ 仕様との照合:")
        print("   ✅ 仕様: 'ユーザーが選んだ予算の上限以下のタレントだけを抽出'")
        print("   ✅ 仕様: '使用データ: talents.money_max_one_year'")
        print("   🔍 実装: 'm_talent_act.money_max_one_year' を使用")
        print()
        print("   ⚠️  検証ポイント:")
        print("      - 仕様では 'talents.money_max_one_year' だが、実装では 'm_talent_act.money_max_one_year'")
        print("      - この差異が意図的なものか確認が必要")

        # 6. テーブル関係の確認
        print("\n\n6️⃣ テーブル関係の確認:")

        table_relation_query = """
        SELECT
            'talents' as table_name,
            COUNT(*) as record_count,
            COUNT(DISTINCT account_id) as unique_ids,
            'タレント基本情報' as description
        UNION ALL
        SELECT
            'm_account' as table_name,
            COUNT(*) as record_count,
            COUNT(DISTINCT account_id) as unique_ids,
            'アカウント情報' as description
        FROM m_account
        UNION ALL
        SELECT
            'm_talent_act' as table_name,
            COUNT(*) as record_count,
            COUNT(DISTINCT account_id) as unique_ids,
            '契約金額情報' as description
        FROM m_talent_act
        """

        table_relations = await conn.fetch(table_relation_query)
        print("   テーブル関係:")
        for relation in table_relations:
            print(f"     {relation['table_name']:>12}: {relation['record_count']:>6}件 (ID: {relation['unique_ids']:>4}種類) - {relation['description']}")

    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(analyze_step0_budget_filtering())