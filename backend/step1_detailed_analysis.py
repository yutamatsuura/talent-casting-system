#!/usr/bin/env python3
"""
STEP 1: 基礎パワー得点の詳細分析
修正後の実装確認
"""
import asyncio
from app.db.connection import get_asyncpg_connection

async def analyze_step1_base_power():
    print("🔍 STEP 1: 基礎パワー得点詳細分析")
    print("=" * 70)

    conn = await get_asyncpg_connection()
    try:
        # 1. 仕様確認
        print("\n1️⃣ STEP 1仕様書記載内容:")
        print("   計算式: '基礎パワー得点 = (VR人気度 + TPRパワースコア) / 2'")
        print("   テーブル: 'talent_scores'")
        print("   フィルタ: 'target_segment_id = ユーザー選択ターゲット層'")

        # 2. talent_scoresテーブル詳細確認
        print("\n\n2️⃣ talent_scoresテーブル詳細確認:")

        scores_structure = await conn.fetch("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'talent_scores'
            ORDER BY ordinal_position
        """)

        print("   talent_scoresテーブル:")
        for col in scores_structure:
            print(f"     {col['column_name']} ({col['data_type']}, nullable: {col['is_nullable']})")

        # 3. データサンプル確認
        print("\n\n3️⃣ データサンプル確認:")

        test_target_segment_id = 1  # 女性20-34

        data_sample_query = """
        SELECT
            account_id,
            target_segment_id,
            vr_popularity,
            tpr_power_score,
            base_power_score,
            (COALESCE(vr_popularity, 0) + COALESCE(tpr_power_score, 0)) / 2.0 AS calculated_base_power,
            talent_name_original,
            data_source
        FROM talent_scores
        WHERE target_segment_id = $1
        ORDER BY (COALESCE(vr_popularity, 0) + COALESCE(tpr_power_score, 0)) / 2.0 DESC
        LIMIT 15
        """

        data_samples = await conn.fetch(data_sample_query, test_target_segment_id)

        print(f"\n   データサンプル（ターゲット層ID: {test_target_segment_id}）:")
        print("   ID   | VR人気度 | TPRスコア | 計算値 | 既存base | タレント名")
        print("   " + "-" * 80)

        for sample in data_samples:
            vr_pop = sample['vr_popularity'] or 0
            tpr_score = sample['tpr_power_score'] or 0
            calculated = sample['calculated_base_power']
            existing = sample['base_power_score'] or 0
            name = (sample['talent_name_original'] or 'Unknown')[:12].ljust(12)

            print(f"   {sample['account_id']:>4} | {vr_pop:>8} | {tpr_score:>8} | {calculated:>6.2f} | {existing:>7.2f} | {name}")

        # 4. データ分布確認
        print("\n\n4️⃣ データ分布確認:")

        distribution_query = """
        SELECT
            target_segment_id,
            COUNT(*) as total_records,
            COUNT(CASE WHEN vr_popularity IS NOT NULL THEN 1 END) as vr_data_count,
            COUNT(CASE WHEN tpr_power_score IS NOT NULL THEN 1 END) as tpr_data_count,
            COUNT(CASE WHEN base_power_score IS NOT NULL THEN 1 END) as base_power_data_count,
            AVG(COALESCE(vr_popularity, 0)) as avg_vr,
            AVG(COALESCE(tpr_power_score, 0)) as avg_tpr,
            AVG((COALESCE(vr_popularity, 0) + COALESCE(tpr_power_score, 0)) / 2.0) as avg_calculated_base
        FROM talent_scores
        GROUP BY target_segment_id
        ORDER BY target_segment_id
        """

        distributions = await conn.fetch(distribution_query)

        print("   ターゲット層別データ分布:")
        print("   層ID | 総数 | VRあり | TPRあり | 既存baseあり | VR平均 | TPR平均 | 計算平均")
        print("   " + "-" * 85)

        for dist in distributions:
            print(f"   {dist['target_segment_id']:>4} | {dist['total_records']:>4} | {dist['vr_data_count']:>6} | {dist['tpr_data_count']:>7} | {dist['base_power_data_count']:>11} | {dist['avg_vr']:>6.1f} | {dist['avg_tpr']:>7.1f} | {dist['avg_calculated_base']:>8.2f}")

        # 5. 修正前後の違い確認
        print("\n\n5️⃣ 修正前後の違い確認:")

        # 修正前（base_power_score = vr_popularityのみ）と修正後の違いを確認
        difference_query = """
        SELECT
            account_id,
            vr_popularity,
            tpr_power_score,
            base_power_score as old_calculation,
            (COALESCE(vr_popularity, 0) + COALESCE(tpr_power_score, 0)) / 2.0 AS new_calculation,
            (COALESCE(vr_popularity, 0) + COALESCE(tpr_power_score, 0)) / 2.0 - COALESCE(base_power_score, 0) as difference
        FROM talent_scores
        WHERE target_segment_id = $1
            AND vr_popularity IS NOT NULL
            AND tpr_power_score IS NOT NULL
            AND base_power_score IS NOT NULL
        ORDER BY ABS((COALESCE(vr_popularity, 0) + COALESCE(tpr_power_score, 0)) / 2.0 - COALESCE(base_power_score, 0)) DESC
        LIMIT 10
        """

        differences = await conn.fetch(difference_query, test_target_segment_id)

        print("   修正前後の違いが大きいタレント（上位10名）:")
        print("   ID   | VR人気度 | TPRスコア | 修正前 | 修正後 | 差分")
        print("   " + "-" * 65)

        for diff in differences:
            print(f"   {diff['account_id']:>4} | {diff['vr_popularity']:>8} | {diff['tpr_power_score']:>8} | {diff['old_calculation']:>6.2f} | {diff['new_calculation']:>6.2f} | {diff['difference']:>5.2f}")

        # 6. 実際のmatching.pyでの計算確認
        print("\n\n6️⃣ matching.pyでの計算確認:")

        # 実際のmatching.pyのSTEP1ロジックを実行
        matching_step1_query = """
        SELECT
            ts.account_id,
            ts.target_segment_id,
            (COALESCE(ts.vr_popularity, 0) + COALESCE(ts.tpr_power_score, 0)) / 2.0 AS base_power_score
        FROM talent_scores ts
        WHERE ts.target_segment_id = $1
        ORDER BY (COALESCE(ts.vr_popularity, 0) + COALESCE(ts.tpr_power_score, 0)) / 2.0 DESC
        LIMIT 10
        """

        matching_results = await conn.fetch(matching_step1_query, test_target_segment_id)

        print("   matching.pyの実際の計算結果（上位10名）:")
        print("   ID   | 基礎パワー得点")
        print("   " + "-" * 25)

        for result in matching_results:
            print(f"   {result['account_id']:>4} | {result['base_power_score']:>13.2f}")

    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(analyze_step1_base_power())