#!/usr/bin/env python3
"""
マッチングロジックの各ステップを詳細デバッグ
30名中3名しか取得されない原因を特定
"""
import asyncio
import asyncpg
from app.core.config import settings

async def debug_matching_steps():
    """マッチングロジックの各ステップを詳細デバッグ"""
    conn = await asyncpg.connect(settings.database_url)

    try:
        print("=" * 80)
        print("🔍 マッチングロジック各ステップ詳細デバッグ")
        print("=" * 80)

        budget_max = 29999999  # 1,000万円～3,000万円未満の上限
        target_segment_id = 12  # 女性20-34歳

        print(f"   条件:")
        print(f"     予算: ≤{budget_max:,}円 (≤{budget_max/10000}万円)")
        print(f"     target_segment_id: {target_segment_id}")

        # Step 0: 予算フィルタリング
        print(f"\n📊 Step 0: 予算フィルタリング")
        step0_query = """
        SELECT COUNT(*) as count
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
        step0_result = await conn.fetchrow(step0_query, budget_max)
        step0_count = step0_result['count']
        print(f"   通過数: {step0_count:,}名")

        # Step 1: talent_scoresとの結合
        print(f"\n📊 Step 1: talent_scoresとの結合")
        step1_query = """
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
        SELECT COUNT(*) as count
        FROM step0_budget_filter bf
        INNER JOIN talent_scores ts ON bf.account_id = ts.account_id
        WHERE ts.target_segment_id = $2
        """
        step1_result = await conn.fetchrow(step1_query, budget_max, target_segment_id)
        step1_count = step1_result['count']
        print(f"   通過数（talent_scores結合後）: {step1_count:,}名")

        # talent_scoresテーブルの状況を確認
        print(f"\n📋 talent_scoresテーブルの状況:")
        ts_total_query = "SELECT COUNT(*) as count FROM talent_scores"
        ts_total = await conn.fetchrow(ts_total_query)
        print(f"   talent_scores総レコード数: {ts_total['count']:,}")

        ts_segment_query = "SELECT COUNT(*) as count FROM talent_scores WHERE target_segment_id = $1"
        ts_segment = await conn.fetchrow(ts_segment_query, target_segment_id)
        print(f"   target_segment_id={target_segment_id}のレコード数: {ts_segment['count']:,}")

        # target_segmentsテーブルも確認
        segments_query = "SELECT * FROM target_segments ORDER BY target_segment_id"
        segments = await conn.fetch(segments_query)
        print(f"\n📋 target_segmentsテーブル:")
        for segment in segments:
            print(f"   ID={segment['target_segment_id']}: {segment['segment_name']}")

        # Step 2: talent_imagesとの結合
        print(f"\n📊 Step 2: talent_imagesとの結合チェック")

        # まずindustries テーブルからrequired_image_idを確認
        industry_query = "SELECT * FROM industries WHERE industry_name = 'ファッション'"
        industry = await conn.fetchrow(industry_query)
        if industry:
            required_image_ids = industry['required_image_id']
            print(f"   ファッション業界のrequired_image_id: {required_image_ids}")

            # talent_imagesとの結合後
            step2_query = """
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
            ),
            step1_base_power AS (
                SELECT
                    ts.account_id,
                    ts.target_segment_id,
                    (COALESCE(ts.vr_popularity, 0) + COALESCE(ts.tpr_power_score, 0)) / 2.0 AS base_power_score
                FROM talent_scores ts
                WHERE ts.target_segment_id = $2
            )
            SELECT COUNT(*) as count
            FROM step0_budget_filter bf
            INNER JOIN step1_base_power bp ON bf.account_id = bp.account_id
            LEFT JOIN talent_images ti ON bp.account_id = ti.account_id AND ti.target_segment_id = $2
            """
            step2_result = await conn.fetchrow(step2_query, budget_max, target_segment_id)
            step2_count = step2_result['count']
            print(f"   通過数（talent_images結合後）: {step2_count:,}名")

        # おすすめタレント機能が影響しているかチェック
        print(f"\n🌟 おすすめタレント機能の確認:")
        recommended_query = """
        SELECT COUNT(*) as count
        FROM recommended_talents
        """
        recommended_result = await conn.fetchrow(recommended_query)
        if recommended_result:
            print(f"   recommended_talentsテーブルのレコード数: {recommended_result['count']}")
        else:
            print(f"   recommended_talentsテーブルが見つかりません")

        # 実際のマッチングロジックと同じクエリを実行してみる
        print(f"\n🎯 実際のマッチングクエリ（簡略版）を実行:")
        actual_query = """
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
        ),
        step1_base_power AS (
            SELECT
                ts.account_id,
                ts.target_segment_id,
                (COALESCE(ts.vr_popularity, 0) + COALESCE(ts.tpr_power_score, 0)) / 2.0 AS base_power_score
            FROM talent_scores ts
            WHERE ts.target_segment_id = $2
        )
        SELECT COUNT(*) as total_candidates
        FROM step0_budget_filter bf
        INNER JOIN step1_base_power bp ON bf.account_id = bp.account_id
        """
        actual_result = await conn.fetchrow(actual_query, budget_max, target_segment_id)
        actual_count = actual_result['total_candidates']
        print(f"   最終候補数: {actual_count:,}名")

    except Exception as e:
        print(f"❌ エラー: {e}")
        import traceback
        traceback.print_exc()

    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(debug_matching_steps())