#!/usr/bin/env python3
"""
予算フィルタリングロジックの詳細デバッグ
30名中3名しか取得されない原因を特定
"""
import asyncio
import asyncpg
from app.core.config import settings

async def debug_budget_filtering():
    """予算フィルタリングの詳細デバッグ"""
    conn = await asyncpg.connect(settings.database_url)

    try:
        print("=" * 80)
        print("🔍 予算フィルタリング詳細デバッグ")
        print("=" * 80)

        # 1,000万円～3,000万円未満 = 10,000,000円～29,999,999円
        budget_max = 29999999  # 円単位

        # Step 0: 予算フィルタリング前後の数を比較
        print(f"\n📊 Step 0: 予算フィルタリング分析")
        print(f"   条件: 1,000万円～3,000万円未満 (≤{budget_max:,}円)")
        print(f"   万円換算: ≤{budget_max/10000}万円")

        # 全タレント数（有効なもの）
        total_query = """
        SELECT COUNT(*) as total_count
        FROM m_account ma
        LEFT JOIN m_talent_act mta ON ma.account_id = mta.account_id
        WHERE ma.del_flag = 0
          AND mta.account_id IS NOT NULL
        """
        total_result = await conn.fetchrow(total_query)
        total_count = total_result['total_count']
        print(f"   全タレント数（有効）: {total_count:,}名")

        # 修正前のロジック（間違い）での通過数
        wrong_query = """
        SELECT COUNT(*) as count_wrong
        FROM m_account ma
        LEFT JOIN m_talent_act mta ON ma.account_id = mta.account_id
        WHERE ma.del_flag = 0
          AND mta.account_id IS NOT NULL
          AND (
            (mta.money_min_one_year IS NOT NULL AND mta.money_max_one_year IS NOT NULL
             AND mta.money_min_one_year * 10000 <= $1)
            OR
            (mta.money_min_one_year IS NOT NULL AND mta.money_max_one_year IS NULL
             AND mta.money_min_one_year * 10000 <= $1)
            OR
            (mta.money_min_one_year IS NULL AND mta.money_max_one_year IS NOT NULL
             AND mta.money_max_one_year * 10000 <= $1)
          )
        """
        wrong_result = await conn.fetchrow(wrong_query, budget_max)
        wrong_count = wrong_result['count_wrong']
        print(f"   修正前（間違い）通過数: {wrong_count:,}名")

        # 修正後のロジック（正しい）での通過数
        correct_query = """
        SELECT COUNT(*) as count_correct
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
        correct_result = await conn.fetchrow(correct_query, budget_max)
        correct_count = correct_result['count_correct']
        print(f"   修正後（正しい）通過数: {correct_count:,}名")

        # 通過率の計算
        if total_count > 0:
            wrong_rate = (wrong_count / total_count) * 100
            correct_rate = (correct_count / total_count) * 100
            print(f"   修正前通過率: {wrong_rate:.1f}%")
            print(f"   修正後通過率: {correct_rate:.1f}%")

        # 通過するタレントの予算分布を確認
        print(f"\n📈 通過タレントの予算分布:")
        distribution_query = """
        SELECT
            CASE
                WHEN mta.money_min_one_year <= 100 THEN '100万円以下'
                WHEN mta.money_min_one_year <= 500 THEN '101-500万円'
                WHEN mta.money_min_one_year <= 1000 THEN '501-1,000万円'
                WHEN mta.money_min_one_year <= 2000 THEN '1,001-2,000万円'
                WHEN mta.money_min_one_year <= 3000 THEN '2,001-3,000万円'
                ELSE '3,000万円超'
            END as budget_range,
            COUNT(*) as count
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
        GROUP BY
            CASE
                WHEN mta.money_min_one_year <= 100 THEN '100万円以下'
                WHEN mta.money_min_one_year <= 500 THEN '101-500万円'
                WHEN mta.money_min_one_year <= 1000 THEN '501-1,000万円'
                WHEN mta.money_min_one_year <= 2000 THEN '1,001-2,000万円'
                WHEN mta.money_min_one_year <= 3000 THEN '2,001-3,000万円'
                ELSE '3,000万円超'
            END
        ORDER BY MIN(COALESCE(mta.money_min_one_year, 0))
        """
        distribution_results = await conn.fetch(distribution_query, budget_max)
        for row in distribution_results:
            print(f"   {row['budget_range']}: {row['count']}名")

        # ファッション業界 + 女性20-34歳での絞り込み後の数
        print(f"\n🎯 ターゲット条件での絞り込み:")

        # target_segment_idを取得
        segment_query = """
        SELECT target_segment_id FROM target_segments
        WHERE segment_name = '女性20-34歳'
        """
        segment_result = await conn.fetchrow(segment_query)
        if segment_result:
            target_segment_id = segment_result['target_segment_id']
            print(f"   target_segment_id: {target_segment_id}")

            # 業界条件も含めた最終的な数
            final_query = """
            SELECT COUNT(*) as final_count
            FROM m_account ma
            LEFT JOIN m_talent_act mta ON ma.account_id = mta.account_id
            LEFT JOIN talent_scores ts ON ma.account_id = ts.account_id
            WHERE ma.del_flag = 0
              AND mta.account_id IS NOT NULL
              AND ts.target_segment_id = $2
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
            final_result = await conn.fetchrow(final_query, budget_max, target_segment_id)
            final_count = final_result['final_count']
            print(f"   最終候補数（ターゲット条件込み）: {final_count:,}名")

            # アルコール業界チェック（25歳フィルタが効いているか）
            alcohol_query = """
            SELECT industry_id, industry_name FROM industries
            WHERE industry_name = 'ファッション'
            """
            industry_result = await conn.fetchrow(alcohol_query)
            if industry_result:
                print(f"   業界ID: {industry_result['industry_id']} ({industry_result['industry_name']})")

        else:
            print(f"   ❌ target_segmentが見つかりません")

        # 実際のマッチング結果の上位30名を確認
        print(f"\n🏆 実際のマッチング結果（上位30名分析）:")
        matching_query = """
        WITH step0_budget_filter AS (
            SELECT DISTINCT ma.account_id, ma.name_full_for_matching as name, ma.last_name_kana, ma.act_genre
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
        )
        SELECT COUNT(*) as step0_count FROM step0_budget_filter
        """
        step0_result = await conn.fetchrow(matching_query, budget_max)
        step0_count = step0_result['step0_count']
        print(f"   Step0 (予算フィルタ後): {step0_count:,}名")

    except Exception as e:
        print(f"❌ エラー: {e}")
        import traceback
        traceback.print_exc()

    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(debug_budget_filtering())