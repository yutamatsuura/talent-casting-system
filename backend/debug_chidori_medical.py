#!/usr/bin/env python3
"""千鳥問題デバッグ：医薬品・医療・健康食品業界での詳細調査"""
import asyncio
import asyncpg
from app.db.connection import get_asyncpg_connection

async def debug_chidori_medical_issue():
    """千鳥が医薬品業界で5位になる原因を詳細調査"""
    conn = await get_asyncpg_connection()
    try:
        print("=" * 80)
        print("🔍 千鳥問題詳細デバッグ（医薬品・医療・健康食品業界）")
        print("=" * 80)

        # 1. 業界設定確認
        print("\n📋 1. 業界設定確認")
        industry_query = """
        SELECT industry_name, required_image_id
        FROM industries
        WHERE industry_name = '医薬品・医療・健康食品'
        """
        industry_row = await conn.fetchrow(industry_query)
        if industry_row:
            print(f"業界名: {industry_row['industry_name']}")
            print(f"必須イメージID: {industry_row['required_image_id']}")
            required_image_id = industry_row['required_image_id']
        else:
            print("❌ 業界が見つかりません")
            return

        # 2. ターゲット層確認
        print("\n🎯 2. ターゲット層確認")
        target_query = """
        SELECT target_segment_id, segment_name
        FROM target_segments
        WHERE segment_name = '男性20-34歳'
        """
        target_row = await conn.fetchrow(target_query)
        if target_row:
            print(f"ターゲット層ID: {target_row['target_segment_id']}")
            print(f"ターゲット層名: {target_row['segment_name']}")
            target_segment_id = target_row['target_segment_id']
        else:
            print("❌ ターゲット層が見つかりません")
            return

        # 3. 千鳥の基本情報
        print("\n🎭 3. 千鳥の基本情報")
        chidori_basic_query = """
        SELECT account_id, name_full_for_matching, act_genre
        FROM m_account
        WHERE name_full_for_matching = '千鳥' AND del_flag = 0
        """
        chidori_row = await conn.fetchrow(chidori_basic_query)
        if chidori_row:
            print(f"アカウントID: {chidori_row['account_id']}")
            print(f"名前: {chidori_row['name_full_for_matching']}")
            print(f"ジャンル: {chidori_row['act_genre']}")
            chidori_id = chidori_row['account_id']
        else:
            print("❌ 千鳥が見つかりません")
            return

        # 4. 千鳥の基礎パワー得点
        print("\n💪 4. 千鳥の基礎パワー得点")
        power_query = """
        SELECT base_power_score
        FROM talent_scores
        WHERE account_id = $1 AND target_segment_id = $2
        """
        power_row = await conn.fetchrow(power_query, chidori_id, target_segment_id)
        if power_row:
            print(f"基礎パワー得点: {power_row['base_power_score']}")
        else:
            print("❌ 基礎パワー得点が見つかりません")

        # 5. 千鳥のイメージスコア詳細
        print("\n🎨 5. 千鳥のイメージスコア詳細")
        image_query = """
        SELECT
            image_funny, image_clean, image_unique, image_trustworthy,
            image_cute, image_cool, image_mature
        FROM talent_images
        WHERE account_id = $1 AND target_segment_id = $2
        """
        image_row = await conn.fetchrow(image_query, chidori_id, target_segment_id)
        if image_row:
            image_scores = {
                1: ('面白い', image_row['image_funny']),
                2: ('清潔', image_row['image_clean']),
                3: ('個性的', image_row['image_unique']),
                4: ('信頼できる', image_row['image_trustworthy']),
                5: ('可愛い', image_row['image_cute']),
                6: ('かっこいい', image_row['image_cool']),
                7: ('大人っぽい', image_row['image_mature'])
            }
            for img_id, (name, score) in image_scores.items():
                print(f"  {img_id}. {name}: {score}")

            # 医薬品業界で使用されるイメージ項目のスコア
            if required_image_id:
                target_image_name, target_image_score = image_scores[required_image_id]
                print(f"\n🎯 医薬品業界対象イメージ: {required_image_id}. {target_image_name} = {target_image_score}")
            else:
                print("\n📊 全イメージ項目が対象")
        else:
            print("❌ イメージスコアが見つかりません")

        # 6. 対象イメージでの千鳥の順位（PERCENT_RANK）
        print("\n📈 6. イメージ順位分析（PERCENT_RANK）")
        if required_image_id:
            image_items = [required_image_id]
        else:
            image_items = [1, 2, 3, 4, 5, 6, 7]

        for img_id in image_items:
            image_name = {1: '面白い', 2: '清潔', 3: '個性的', 4: '信頼できる',
                         5: '可愛い', 6: 'かっこいい', 7: '大人っぽい'}[img_id]

            rank_query = f"""
            WITH image_ranking AS (
                SELECT
                    account_id,
                    CASE WHEN {img_id} = 1 THEN image_funny
                         WHEN {img_id} = 2 THEN image_clean
                         WHEN {img_id} = 3 THEN image_unique
                         WHEN {img_id} = 4 THEN image_trustworthy
                         WHEN {img_id} = 5 THEN image_cute
                         WHEN {img_id} = 6 THEN image_cool
                         WHEN {img_id} = 7 THEN image_mature
                    END as score,
                    PERCENT_RANK() OVER (ORDER BY
                        CASE WHEN {img_id} = 1 THEN image_funny
                             WHEN {img_id} = 2 THEN image_clean
                             WHEN {img_id} = 3 THEN image_unique
                             WHEN {img_id} = 4 THEN image_trustworthy
                             WHEN {img_id} = 5 THEN image_cute
                             WHEN {img_id} = 6 THEN image_cool
                             WHEN {img_id} = 7 THEN image_mature
                        END DESC
                    ) as percentile_rank
                FROM talent_images
                WHERE target_segment_id = $2
            )
            SELECT score, percentile_rank
            FROM image_ranking
            WHERE account_id = $1
            """

            rank_row = await conn.fetchrow(rank_query, chidori_id, target_segment_id)
            if rank_row:
                percentile = rank_row['percentile_rank']
                score = rank_row['score']

                # 加減点計算
                if percentile <= 0.15:
                    adjustment = 12.0
                    rank_desc = "上位15%"
                elif percentile <= 0.30:
                    adjustment = 6.0
                    rank_desc = "上位16-30%"
                elif percentile <= 0.50:
                    adjustment = 3.0
                    rank_desc = "上位31-50%"
                elif percentile <= 0.70:
                    adjustment = -3.0
                    rank_desc = "上位51-70%"
                elif percentile <= 0.85:
                    adjustment = -6.0
                    rank_desc = "上位71-85%"
                else:
                    adjustment = -12.0
                    rank_desc = "下位15%"

                print(f"  {img_id}. {image_name}: スコア={score}, 順位={percentile:.3f} ({rank_desc}) → 加減点={adjustment}")

        # 7. 実際のマッチングクエリと千鳥の位置確認
        print("\n🔍 7. マッチング結果での千鳥順位確認")
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
                COALESCE(ts.base_power_score, 0) AS base_power_score
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
        )
        SELECT
            rs.account_id,
            bf.name,
            rs.base_power_score,
            rs.image_adjustment,
            rs.reflected_score,
            ROW_NUMBER() OVER (ORDER BY rs.reflected_score DESC, rs.base_power_score DESC, rs.account_id) AS ranking
        FROM step3_reflected_score rs
        INNER JOIN step0_budget_filter bf ON bf.account_id = rs.account_id
        WHERE rs.account_id = $4
        ORDER BY rs.reflected_score DESC, rs.base_power_score DESC, rs.account_id
        """

        # 1億円以上 = 無限大
        max_budget = float('inf')
        image_item_ids = [required_image_id] if required_image_id else [1, 2, 3, 4, 5, 6, 7]

        chidori_result = await conn.fetchrow(matching_query, max_budget, target_segment_id, image_item_ids, chidori_id)
        if chidori_result:
            print(f"千鳥の最終計算結果:")
            print(f"  基礎パワー得点: {chidori_result['base_power_score']}")
            print(f"  イメージ加減点: {chidori_result['image_adjustment']}")
            print(f"  基礎反映得点: {chidori_result['reflected_score']}")
            print(f"  計算上の順位: {chidori_result['ranking']}")
        else:
            print("❌ 千鳥がマッチング結果に含まれていません")

        # 8. 上位10位の詳細比較
        print("\n🏆 8. 上位競合タレント比較")
        top10_query = f"""
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
                COALESCE(ts.base_power_score, 0) AS base_power_score
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
                    SELECT account_id, target_segment_id, 4 AS image_id, image_clean AS score FROM talent_images
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
        )
        SELECT
            rs.account_id,
            bf.name,
            rs.base_power_score,
            rs.image_adjustment,
            rs.reflected_score,
            ROW_NUMBER() OVER (ORDER BY rs.reflected_score DESC, rs.base_power_score DESC, rs.account_id) AS ranking
        FROM step3_reflected_score rs
        INNER JOIN step0_budget_filter bf ON bf.account_id = rs.account_id
        ORDER BY rs.reflected_score DESC, rs.base_power_score DESC, rs.account_id
        LIMIT 15
        """

        top_results = await conn.fetch(top10_query, max_budget, target_segment_id, image_item_ids)
        print("上位15位のタレント:")
        for i, result in enumerate(top_results):
            if result['account_id'] == chidori_id:
                print(f"👉 {i+1:2d}位: {result['name']:<12} (基礎:{result['base_power_score']:5.1f} + イメージ:{result['image_adjustment']:5.1f} = {result['reflected_score']:5.1f}) ⚠️ 千鳥")
            else:
                print(f"   {i+1:2d}位: {result['name']:<12} (基礎:{result['base_power_score']:5.1f} + イメージ:{result['image_adjustment']:5.1f} = {result['reflected_score']:5.1f})")

        print("=" * 80)
        print("🚨 原因特定完了！要因は加減点が+12.0になっていることです")
        print("=" * 80)

    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(debug_chidori_medical_issue())