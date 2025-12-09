#!/usr/bin/env python3
"""
STEP 2: 業種イメージ査定の詳細分析
仕様との整合性を確認
"""
import asyncio
from app.db.connection import get_asyncpg_connection

async def analyze_step2_image_assessment():
    print("🔍 STEP 2: 業種イメージ査定詳細分析")
    print("=" * 70)

    conn = await get_asyncpg_connection()
    try:
        # 1. 仕様確認
        print("\n1️⃣ STEP 2仕様書記載内容:")
        print("   処理: 'PostgreSQL PERCENT_RANK()でパーセンタイル算出'")
        print("   加減点: '上位15% +12点、16-30% +6点、31-50% +3点、51-70% -3点、71-85% -6点、86-100% -12点'")
        print("   テーブル: 'talent_images, industries, image_items'")

        # 2. talent_imagesテーブル構造確認
        print("\n\n2️⃣ talent_imagesテーブル構造確認:")

        images_structure = await conn.fetch("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'talent_images'
            ORDER BY ordinal_position
        """)

        print("   talent_imagesテーブル:")
        for col in images_structure:
            print(f"     {col['column_name']} ({col['data_type']}, nullable: {col['is_nullable']})")

        # 3. image_itemsテーブル確認
        print("\n\n3️⃣ image_itemsテーブル確認:")

        image_items = await conn.fetch("SELECT image_id, image_name FROM image_items ORDER BY image_id")
        print("   image_items一覧:")
        for item in image_items:
            print(f"     ID {item['image_id']}: {item['image_name']}")

        # 4. industriesとrequired_image_idの関係確認
        print("\n\n4️⃣ industries.required_image_id確認:")

        industry_images = await conn.fetch("""
            SELECT i.industry_name, i.required_image_id, ii.image_name
            FROM industries i
            LEFT JOIN image_items ii ON i.required_image_id = ii.image_id
            ORDER BY i.industry_id
        """)

        print("   業種別の必要イメージ:")
        for ind in industry_images:
            required = ind['image_name'] if ind['image_name'] else 'なし（全イメージ使用）'
            print(f"     {ind['industry_name']}: {required}")

        # 5. PERCENT_RANK()の実装確認
        print("\n\n5️⃣ PERCENT_RANK()実装確認:")

        # テスト用にSTEP2のロジックを実際に実行
        test_target_segment_id = 1  # 女性20-34
        test_image_ids = [1, 2, 3, 4, 5, 6, 7]  # 全イメージ

        percent_rank_query = """
        SELECT
            unpivot.account_id,
            unpivot.image_id,
            unpivot.score,
            PERCENT_RANK() OVER (
                PARTITION BY unpivot.target_segment_id, unpivot.image_id
                ORDER BY unpivot.score DESC
            ) AS percentile_rank,
            CASE
                WHEN PERCENT_RANK() OVER (
                    PARTITION BY unpivot.target_segment_id, unpivot.image_id
                    ORDER BY unpivot.score DESC
                ) <= 0.15 THEN 12.0
                WHEN PERCENT_RANK() OVER (
                    PARTITION BY unpivot.target_segment_id, unpivot.image_id
                    ORDER BY unpivot.score DESC
                ) <= 0.30 THEN 6.0
                WHEN PERCENT_RANK() OVER (
                    PARTITION BY unpivot.target_segment_id, unpivot.image_id
                    ORDER BY unpivot.score DESC
                ) <= 0.50 THEN 3.0
                WHEN PERCENT_RANK() OVER (
                    PARTITION BY unpivot.target_segment_id, unpivot.image_id
                    ORDER BY unpivot.score DESC
                ) <= 0.70 THEN -3.0
                WHEN PERCENT_RANK() OVER (
                    PARTITION BY unpivot.target_segment_id, unpivot.image_id
                    ORDER BY unpivot.score DESC
                ) <= 0.85 THEN -6.0
                ELSE -12.0
            END AS image_adjustment_points
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
        WHERE unpivot.target_segment_id = $1
            AND unpivot.image_id = ANY($2::int[])
        ORDER BY unpivot.image_id, unpivot.score DESC
        LIMIT 50
        """

        percent_rank_results = await conn.fetch(percent_rank_query, test_target_segment_id, test_image_ids)

        print(f"\n   PERCENT_RANK()実行例（ターゲット層ID: {test_target_segment_id}）:")
        print("   ID   | イメージID | スコア | パーセンタイル | 加減点")
        print("   " + "-" * 60)

        current_image_id = None
        count_per_image = 0

        for result in percent_rank_results:
            if current_image_id != result['image_id']:
                current_image_id = result['image_id']
                count_per_image = 0
                if count_per_image > 0:
                    print()

            if count_per_image < 8:  # 各イメージ項目につき8件まで表示
                percentile = round(result['percentile_rank'], 3)
                points = result['image_adjustment_points']
                print(f"   {result['account_id']:>4} | {result['image_id']:>8} | {result['score']:>5} | {percentile:>11} | {points:>5}")
                count_per_image += 1

        # 6. 実際のmatching.pyの実装との比較
        print("\n\n6️⃣ matching.pyの実装確認:")

        # タレント1人のSTEP2計算例
        sample_talent_query = """
        SELECT
            account_id,
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
            WHERE unpivot.target_segment_id = $1
                AND unpivot.image_id = ANY($2::int[])
        ) sub
        GROUP BY account_id
        ORDER BY image_adjustment DESC
        LIMIT 10
        """

        sample_adjustments = await conn.fetch(sample_talent_query, test_target_segment_id, test_image_ids)

        print("\n   STEP2実装結果サンプル（上位10名）:")
        print("   ID   | イメージ査定調整点")
        print("   " + "-" * 30)

        for sample in sample_adjustments:
            adjustment = round(sample['image_adjustment'], 2)
            print(f"   {sample['account_id']:>4} | {adjustment:>15}")

        # 7. データ整合性チェック
        print("\n\n7️⃣ データ整合性チェック:")

        data_integrity_query = """
        SELECT
            COUNT(DISTINCT ti.account_id) as talents_with_image_data,
            COUNT(DISTINCT ts.account_id) as talents_with_score_data,
            COUNT(DISTINCT ma.account_id) as total_active_talents,
            COUNT(DISTINCT ti.target_segment_id) as image_target_segments,
            COUNT(DISTINCT ts.target_segment_id) as score_target_segments
        FROM m_account ma
        LEFT JOIN talent_images ti ON ma.account_id = ti.account_id AND ma.del_flag = 0
        LEFT JOIN talent_scores ts ON ma.account_id = ts.account_id
        WHERE ma.del_flag = 0
        """

        integrity_result = await conn.fetchrow(data_integrity_query)

        print("   データ整合性:")
        print(f"     有効タレント総数: {integrity_result['total_active_talents']}")
        print(f"     イメージデータありタレント: {integrity_result['talents_with_image_data']}")
        print(f"     スコアデータありタレント: {integrity_result['talents_with_score_data']}")
        print(f"     イメージ対象層数: {integrity_result['image_target_segments']}")
        print(f"     スコア対象層数: {integrity_result['score_target_segments']}")

    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(analyze_step2_image_assessment())