#!/usr/bin/env python3
"""
新垣結衣（talent_id=1265）の予算データ確認スクリプト
予算フィルタリングの問題を特定する
"""
import os
import asyncio
import asyncpg
from dotenv import load_dotenv

# 環境変数の読み込み
# プロジェクトルートの .env.local を読み込む
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
env_file = project_root / '.env.local'
load_dotenv(env_file)

async def check_aragaki_budget():
    """新垣結衣の予算データを詳細確認"""

    # データベース接続
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ ERROR: DATABASE_URL not found in environment variables")
        return

    print(f"📊 Connecting to database...")
    conn = await asyncpg.connect(database_url)

    try:
        print("\n" + "="*80)
        print("🔍 新垣結衣（account_id=30）予算データ確認")
        print("="*80)

        # 1. m_account + m_talent_act テーブルの予算データ確認
        print("\n【1】m_account + m_talent_act テーブルの予算データ")
        print("-" * 80)

        query_talents = """
        SELECT
            ma.account_id,
            ma.name_full_for_matching as talent_name,
            mta.money_min_one_year,
            mta.money_max_one_year
        FROM m_account ma
        LEFT JOIN m_talent_act mta ON ma.account_id = mta.account_id
        WHERE ma.account_id = 30;
        """

        talent_data = await conn.fetchrow(query_talents)

        if talent_data:
            print(f"アカウントID: {talent_data['account_id']}")
            print(f"タレント名: {talent_data['talent_name']}")
            print(f"最低ギャラ (money_min_one_year): {talent_data['money_min_one_year']:,} 円" if talent_data['money_min_one_year'] else "最低ギャラ (money_min_one_year): NULL")
            print(f"最高ギャラ (money_max_one_year): {talent_data['money_max_one_year']:,} 円" if talent_data['money_max_one_year'] else "最高ギャラ (money_max_one_year): NULL")
        else:
            print("⚠️  account_id=1265 が見つかりません")

        # 2. 予算フィルタリング条件での確認
        print("\n【2】予算フィルタリング条件（1,000万円〜3,000万円未満）での確認")
        print("-" * 80)

        budget_max = 30000000  # 3,000万円

        query_filter = """
        SELECT
            ma.account_id,
            ma.name_full_for_matching as talent_name,
            mta.money_min_one_year,
            mta.money_max_one_year,
            CASE
                WHEN mta.money_max_one_year <= $1 THEN 'PASS (フィルタ通過)'
                WHEN mta.money_min_one_year <= $1 THEN 'PASS (フィルタ通過)'
                ELSE 'FAIL (フィルタ除外)'
            END as filter_result
        FROM m_account ma
        LEFT JOIN m_talent_act mta ON ma.account_id = mta.account_id
        WHERE ma.account_id = 30;
        """

        filter_result = await conn.fetchrow(query_filter, budget_max)

        if filter_result:
            print(f"アカウントID: {filter_result['account_id']}")
            print(f"タレント名: {filter_result['talent_name']}")
            if filter_result['money_min_one_year']:
                print(f"最低ギャラ: {filter_result['money_min_one_year']:,} 円")
            else:
                print(f"最低ギャラ: NULL")
            if filter_result['money_max_one_year']:
                print(f"最高ギャラ: {filter_result['money_max_one_year']:,} 円")
            else:
                print(f"最高ギャラ: NULL")
            print(f"予算上限: {budget_max:,} 円")
            print(f"フィルタ結果: {filter_result['filter_result']}")

            # 判定ロジック確認
            min_val = filter_result['money_min_one_year']
            max_val = filter_result['money_max_one_year']

            print(f"\n判定ロジック:")
            if min_val and max_val:
                print(f"  パターン: MIN有・MAX有")
                print(f"  MIN判定: {min_val:,} <= {budget_max:,} → {min_val <= budget_max}")
                print(f"  MAX判定: {max_val:,} <= {budget_max:,} → {max_val <= budget_max}")
                print(f"  結果: {'✅ 通過 (MINで判定)' if min_val <= budget_max else '❌ 除外'}")
            elif min_val:
                print(f"  パターン: MIN有・MAX無")
                print(f"  MIN判定: {min_val:,} <= {budget_max:,} → {min_val <= budget_max}")
                print(f"  結果: {'✅ 通過' if min_val <= budget_max else '❌ 除外'}")
            elif max_val:
                print(f"  パターン: MIN無・MAX有")
                print(f"  MAX判定: {max_val:,} <= {budget_max:,} → {max_val <= budget_max}")
                print(f"  結果: {'✅ 通過' if max_val <= budget_max else '❌ 除外'}")
            else:
                print(f"  パターン: 両方NULL")
                print(f"  結果: ❌ 除外（予算情報なし）")

        # 3. NULL値チェック
        print("\n【3】NULL値チェック")
        print("-" * 80)

        query_null = """
        SELECT
            ma.account_id,
            ma.name_full_for_matching as talent_name,
            mta.money_min_one_year IS NULL as min_is_null,
            mta.money_max_one_year IS NULL as max_is_null,
            COALESCE(mta.money_max_one_year, 0) as max_coalesced,
            COALESCE(mta.money_min_one_year, 0) as min_coalesced
        FROM m_account ma
        LEFT JOIN m_talent_act mta ON ma.account_id = mta.account_id
        WHERE ma.account_id = 30;
        """

        null_check = await conn.fetchrow(query_null)

        if null_check:
            print(f"money_min_one_year が NULL: {null_check['min_is_null']}")
            print(f"money_max_one_year が NULL: {null_check['max_is_null']}")
            print(f"COALESCE(money_min_one_year, 0): {null_check['min_coalesced']:,} 円")
            print(f"COALESCE(money_max_one_year, 0): {null_check['max_coalesced']:,} 円")

            if null_check['min_is_null'] and null_check['max_is_null']:
                print("⚠️  両方の予算値が NULL です！")
                print("   → このタレントは予算フィルタで除外されるべきです")
            elif null_check['min_is_null']:
                print("⚠️  money_min_one_year が NULL です")
                print("   → MAX値のみで判定されます")
            elif null_check['max_is_null']:
                print("⚠️  money_max_one_year が NULL です")
                print("   → MIN値のみで判定されます")

        # 4. 同様の予算帯のタレントを確認
        print("\n【4】同様の予算帯（8,000万円前後）のタレント確認")
        print("-" * 80)

        query_similar = """
        SELECT
            ma.account_id,
            ma.name_full_for_matching as talent_name,
            mta.money_min_one_year,
            mta.money_max_one_year,
            CASE
                WHEN mta.money_max_one_year <= $1 THEN 'PASS (MAX)'
                WHEN mta.money_min_one_year <= $1 THEN 'PASS (MIN)'
                ELSE 'FAIL'
            END as filter_result
        FROM m_account ma
        LEFT JOIN m_talent_act mta ON ma.account_id = mta.account_id
        WHERE (mta.money_max_one_year BETWEEN 70000000 AND 90000000
               OR mta.money_min_one_year BETWEEN 70000000 AND 90000000)
        ORDER BY COALESCE(mta.money_max_one_year, mta.money_min_one_year) DESC
        LIMIT 5;
        """

        similar_talents = await conn.fetch(query_similar, budget_max)

        print(f"予算帯 7,000万円〜9,000万円のタレント（上位5名）:")
        for row in similar_talents:
            min_str = f"{row['money_min_one_year']:,}円" if row['money_min_one_year'] else "NULL"
            max_str = f"{row['money_max_one_year']:,}円" if row['money_max_one_year'] else "NULL"
            print(f"  {row['talent_name']:20s} | MIN: {min_str:15s} | MAX: {max_str:15s} | {row['filter_result']}")

        # 5. 実際のAPIと同じクエリを実行
        print("\n【5】実際のマッチングAPIと同じクエリを実行")
        print("-" * 80)

        # 実際のマッチングAPIで使われているSTEP0ロジックを再現
        query_matching = """
        WITH step0_budget_filter AS (
            SELECT DISTINCT ma.account_id, ma.name_full_for_matching as name,
                   mta.money_min_one_year, mta.money_max_one_year
            FROM m_account ma
            LEFT JOIN m_talent_act mta ON ma.account_id = mta.account_id
            WHERE ma.del_flag = 0
              AND ma.account_id = 30
              AND mta.account_id IS NOT NULL
              AND (
                (mta.money_min_one_year IS NOT NULL AND mta.money_max_one_year IS NOT NULL
                 AND mta.money_min_one_year <= $1)
                OR
                (mta.money_min_one_year IS NOT NULL AND mta.money_max_one_year IS NULL
                 AND mta.money_min_one_year <= $1)
                OR
                (mta.money_min_one_year IS NULL AND mta.money_max_one_year IS NOT NULL
                 AND mta.money_max_one_year <= $1)
              )
        )
        SELECT * FROM step0_budget_filter;
        """

        matching_result = await conn.fetch(query_matching, budget_max)

        print(f"クエリ結果（account_id=30が含まれているか）:")
        if matching_result:
            print("⚠️  含まれています（これは問題です）")
            for row in matching_result:
                min_str = f"{row['money_min_one_year']:,}円" if row['money_min_one_year'] else "NULL"
                max_str = f"{row['money_max_one_year']:,}円" if row['money_max_one_year'] else "NULL"
                print(f"  {row['name']} | MIN: {min_str} | MAX: {max_str}")
        else:
            print("✅ 含まれていません（正常な動作）")

        # 6. データ型確認
        print("\n【6】データ型確認")
        print("-" * 80)

        query_datatype = """
        SELECT
            column_name,
            data_type,
            is_nullable
        FROM information_schema.columns
        WHERE table_name = 'm_talent_act'
          AND column_name IN ('money_min_one_year', 'money_max_one_year')
        ORDER BY column_name;
        """

        datatype_info = await conn.fetch(query_datatype)

        print("カラム情報:")
        for row in datatype_info:
            print(f"  {row['column_name']:25s} | 型: {row['data_type']:15s} | NULL許容: {row['is_nullable']}")

        print("\n" + "="*80)
        print("🔍 診断結果")
        print("="*80)

        if talent_data:
            max_budget_value = talent_data['money_max_one_year']

            if max_budget_value is None:
                print("❌ 問題: money_max_one_year が NULL です")
                print("   → NULL値のハンドリングが不適切な可能性があります")
                print("   → アプリケーション側でNULLを0として扱っている可能性があります")
            elif max_budget_value <= budget_max:
                print(f"❌ 問題: money_max_one_year ({max_budget_value:,}円) が予想より低い値です")
                print(f"   → データベースの値が間違っている可能性があります")
                print(f"   → 期待値: 80,000,000円前後")
                print(f"   → 実際値: {max_budget_value:,}円")
            else:
                print(f"✅ データベースの値は正常です ({max_budget_value:,}円)")
                print(f"   → 問題はアプリケーションロジックにある可能性が高いです")

    finally:
        await conn.close()
        print("\n✅ データベース接続を閉じました")

if __name__ == "__main__":
    asyncio.run(check_aragaki_budget())
