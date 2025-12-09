#!/usr/bin/env python3
"""
STEP 3-5: 残りステップの詳細分析
基礎反映得点、ランキング確定、マッチングスコア振り分けの実装確認
"""
import asyncio
from app.db.connection import get_asyncpg_connection

async def analyze_step3_to_5():
    print("🔍 STEP 3-5: 残りステップ詳細分析")
    print("=" * 70)

    conn = await get_asyncpg_connection()
    try:
        # 1. STEP 3: 基礎反映得点の仕様確認
        print("\n1️⃣ STEP 3仕様書記載内容:")
        print("   計算式: 'STEP1 + STEP2'")
        print("   処理: '基礎パワー得点 + イメージ査定調整点 = 基礎反映得点'")

        # 2. STEP 4: ランキング確定の仕様確認
        print("\n2️⃣ STEP 4仕様書記載内容:")
        print("   ソート: '基礎反映得点 DESC, base_power_score DESC, talent_id'")
        print("   抽出: 'LIMIT 30'")
        print("   重複除去: 'DISTINCT ON (account_id) でタレント重複除去'")

        # 3. STEP 5: マッチングスコア振り分けの仕様確認
        print("\n3️⃣ STEP 5仕様書記載内容:")
        print("   1-3位: '97.0-99.7点ランダム'")
        print("   4-10位: '93.0-96.9点ランダム'")
        print("   11-20位: '89.0-92.9点ランダム'")
        print("   21-30位: '86.0-88.9点ランダム'")

        # 4. 実際のmatching.pyの実装確認
        print("\n\n4️⃣ matching.pyの実際の実装確認:")

        # テスト実行（1,000万円〜3,000万円未満、化粧品・ヘアケア・オーラルケア）
        test_budget_max = 2999
        test_target_segment_id = 1  # 女性20-34
        test_image_ids = [2]  # 清潔感がある
        test_industry = "化粧品・ヘアケア・オーラルケア"
        test_is_alcohol = False

        print(f"   テスト条件:")
        print(f"     予算上限: {test_budget_max} (千円)")
        print(f"     ターゲット層ID: {test_target_segment_id}")
        print(f"     業種: {test_industry}")
        print(f"     必要イメージ: {test_image_ids}")

        # 実際のmatching.pyロジックを簡略版で実行
        matching_query = """
        WITH step0_budget_filter AS (
            SELECT DISTINCT ma.account_id, ma.name_full_for_matching as name, ma.last_name_kana, ma.act_genre
            FROM m_account ma
            LEFT JOIN m_talent_act mta ON ma.account_id = mta.account_id
            WHERE ma.del_flag = 0
              AND (
                mta.account_id IS NULL
                OR mta.money_max_one_year IS NULL
                OR mta.money_max_one_year <= $1
              )
        ),
        step1_base_power AS (
            SELECT
                ts.account_id,
                ts.target_segment_id,
                (COALESCE(ts.vr_popularity, 0) + COALESCE(ts.tpr_power_score, 0)) / 2.0 AS base_power_score
            FROM talent_scores ts
            WHERE ts.target_segment_id = $2
        ),
        step2_adjustment AS (
            SELECT
                account_id,
                target_segment_id,
                AVG(
                    CASE
                        WHEN percentile_rank <= 0.15 THEN 12.0
                        WHEN percentile_rank <= 0.30 THEN 6.0
                        WHEN percentile_rank <= 0.50 THEN 3.0
                        WHEN percentile_rank <= 0.70 THEN -3.0
                        WHEN percentile_rank <= 0.85 THEN -6.0
                        ELSE -12.0
                    END
                ) AS image_adjustment
            FROM (
                SELECT
                    unpivot.account_id,
                    unpivot.target_segment_id,
                    unpivot.image_id,
                    PERCENT_RANK() OVER (
                        PARTITION BY unpivot.target_segment_id, unpivot.image_id
                        ORDER BY unpivot.score DESC
                    ) AS percentile_rank
                FROM (
                    SELECT account_id, target_segment_id, 1 AS image_id, image_funny AS score FROM talent_images
                    UNION ALL
                    SELECT account_id, target_segment_id, 2 AS image_id, image_clean AS score FROM talent_images
                    UNION ALL
                    SELECT account_id, target_segment_id, 3 AS image_id, image_unique AS score FROM talent_images
                    UNION ALL
                    SELECT account_id, target_segment_id, 4 AS image_id, image_trustworthy AS score FROM talent_images
                    UNION ALL
                    SELECT account_id, target_segment_id, 5 AS image_id, image_cute AS score FROM talent_images
                    UNION ALL
                    SELECT account_id, target_segment_id, 6 AS image_id, image_cool AS score FROM talent_images
                    UNION ALL
                    SELECT account_id, target_segment_id, 7 AS image_id, image_mature AS score FROM talent_images
                ) unpivot
                WHERE unpivot.target_segment_id = $2
                    AND unpivot.image_id = ANY($3::int[])
            ) sub
            GROUP BY account_id, target_segment_id
        ),
        step3_reflected_score AS (
            SELECT
                bp.account_id,
                bp.target_segment_id,
                bp.base_power_score,
                COALESCE(ia.image_adjustment, 0) AS image_adjustment,
                bp.base_power_score + COALESCE(ia.image_adjustment, 0) AS reflected_score
            FROM step1_base_power bp
            LEFT JOIN step2_adjustment ia
                ON bp.account_id = ia.account_id
                AND bp.target_segment_id = ia.target_segment_id
        ),
        step4_ranking AS (
            SELECT DISTINCT ON (rs.account_id)
                rs.account_id,
                rs.target_segment_id,
                rs.base_power_score,
                rs.image_adjustment,
                rs.reflected_score,
                ROW_NUMBER() OVER (ORDER BY rs.reflected_score DESC, rs.base_power_score DESC, rs.account_id) AS ranking
            FROM step3_reflected_score rs
            INNER JOIN step0_budget_filter bf ON bf.account_id = rs.account_id
            ORDER BY rs.account_id, rs.reflected_score DESC, rs.base_power_score DESC
        )
        SELECT
            r.account_id,
            r.ranking,
            r.base_power_score,
            r.image_adjustment,
            r.reflected_score,
            bf.name
        FROM step4_ranking r
        INNER JOIN step0_budget_filter bf ON bf.account_id = r.account_id
        ORDER BY r.reflected_score DESC, r.base_power_score DESC, r.account_id
        LIMIT 30
        """

        try:
            matching_results = await conn.fetch(matching_query, test_budget_max, test_target_segment_id, test_image_ids)

            print(f"\n   マッチング結果（上位30名）:")
            print("   順位 | ID   | 基礎パワー | イメージ調整 | 反映得点 | タレント名")
            print("   " + "-" * 80)

            if matching_results:
                for result in matching_results:
                    name = (result['name'] or 'Unknown')[:12].ljust(12)
                    print(f"   {result['ranking']:>4} | {result['account_id']:>4} | {result['base_power_score']:>10.2f} | {result['image_adjustment']:>12.2f} | {result['reflected_score']:>8.2f} | {name}")
            else:
                print("   結果なし")

            # 5. STEP 5スコア振り分けのロジック確認
            print(f"\n\n5️⃣ STEP 5スコア振り分け実装確認:")
            print("   ランキング別スコア範囲:")
            print("     1-3位:  97.0-99.7点")
            print("     4-10位: 93.0-96.9点")
            print("     11-20位: 89.0-92.9点")
            print("     21-30位: 86.0-88.9点")

            if matching_results:
                print(f"\n   STEP5適用後のサンプル（上位15名）:")
                print("   順位 | ID   | 反映得点 | マッチングスコア範囲")
                print("   " + "-" * 50)

                for i, result in enumerate(matching_results[:15]):
                    ranking = result['ranking']
                    if 1 <= ranking <= 3:
                        score_range = "97.0-99.7"
                    elif 4 <= ranking <= 10:
                        score_range = "93.0-96.9"
                    elif 11 <= ranking <= 20:
                        score_range = "89.0-92.9"
                    elif 21 <= ranking <= 30:
                        score_range = "86.0-88.9"
                    else:
                        score_range = "80.0-85.9"

                    print(f"   {ranking:>4} | {result['account_id']:>4} | {result['reflected_score']:>8.2f} | {score_range}")

        except Exception as e:
            print(f"   エラー: {e}")

        # 6. おすすめタレント機能の確認
        print(f"\n\n6️⃣ おすすめタレント機能確認:")

        recommended_query = """
        SELECT
            industry_name,
            talent_id_1,
            talent_id_2,
            talent_id_3
        FROM recommended_talents
        WHERE industry_name = $1
        """

        try:
            recommended_results = await conn.fetch(recommended_query, test_industry)

            if recommended_results:
                print(f"   {test_industry}のおすすめタレント:")
                for rec in recommended_results:
                    print(f"     1位: {rec['talent_id_1']}")
                    print(f"     2位: {rec['talent_id_2']}")
                    print(f"     3位: {rec['talent_id_3']}")
            else:
                print(f"   {test_industry}のおすすめタレント設定なし")
        except Exception as e:
            print(f"   エラー: {e}")

    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(analyze_step3_to_5())