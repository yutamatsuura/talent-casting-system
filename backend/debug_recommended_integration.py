#!/usr/bin/env python3
"""
おすすめタレント統合機能の詳細デバッグ
なぜ3名しか返されないのかを特定
"""
import asyncio
import asyncpg
from app.core.config import settings
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def debug_recommended_integration():
    """おすすめタレント統合の詳細デバッグ"""
    conn = await asyncpg.connect(settings.database_url)

    try:
        print("=" * 80)
        print("🔍 おすすめタレント統合機能デバッグ")
        print("=" * 80)

        industry = "ファッション"

        # 1. おすすめタレント取得
        print(f"\n1️⃣ おすすめタレント取得 (industry: {industry})")
        recommended_query = """
        SELECT rt.account_id, rt.name, rt.last_name_kana, rt.act_genre, rt.target_industries
        FROM recommended_talents rt
        WHERE rt.is_active = true
        ORDER BY rt.priority_order ASC
        """
        recommended_talents = await conn.fetch(recommended_query)

        print(f"   取得数: {len(recommended_talents)}名")
        for i, talent in enumerate(recommended_talents[:5]):  # 最初の5名表示
            print(f"   [{i+1}] {talent['name']} (ID: {talent['account_id']}, industries: {talent['target_industries']})")

        # 業界フィルタリング後
        filtered_recommended = []
        for talent in recommended_talents:
            if not talent["target_industries"] or industry in talent["target_industries"]:
                filtered_recommended.append(talent)

        print(f"   業界フィルタ後: {len(filtered_recommended)}名")

        # 2. 通常のマッチング結果をシミュレート（簡易版）
        print(f"\n2️⃣ 通常マッチング結果シミュレート")
        budget_max = 29999999  # 1,000万円～3,000万円未満
        target_segment_id = 12  # 女性20-34歳

        standard_query = """
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
                (COALESCE(ts.vr_popularity, 0) + COALESCE(ts.tpr_power_score, 0)) / 2.0 AS base_power_score
            FROM talent_scores ts
            WHERE ts.target_segment_id = $2
        )
        SELECT
            bf.account_id,
            bf.name,
            bf.last_name_kana,
            bf.act_genre,
            bp.base_power_score,
            ROW_NUMBER() OVER (ORDER BY bp.base_power_score DESC, bf.account_id) as ranking
        FROM step0_budget_filter bf
        INNER JOIN step1_base_power bp ON bf.account_id = bp.account_id
        ORDER BY bp.base_power_score DESC, bf.account_id
        LIMIT 30
        """

        standard_results = await conn.fetch(standard_query, budget_max, target_segment_id)
        print(f"   通常マッチング結果: {len(standard_results)}名")

        # 3. 統合処理のシミュレート
        print(f"\n3️⃣ 統合処理シミュレート")

        if not filtered_recommended:
            print("   ケース: おすすめタレントなし → 通常結果をそのまま返却")
            final_count = len(standard_results)
        else:
            print(f"   ケース: おすすめタレントあり ({len(filtered_recommended)}名)")

            # おすすめタレントIDを抽出
            recommended_ids = {talent['account_id'] for talent in filtered_recommended}
            print(f"   おすすめタレントID: {list(recommended_ids)}")

            # 通常結果からおすすめタレントを除去
            filtered_standard = [
                result for result in standard_results
                if result['account_id'] not in recommended_ids
            ]
            print(f"   除去後の通常結果: {len(filtered_standard)}名")

            # おすすめタレントが実際にマッチング対象範囲内にいるかチェック
            recommended_in_scope = []
            for recommended in filtered_recommended[:3]:
                # そのおすすめタレントが予算範囲内かチェック
                scope_check_query = """
                SELECT ma.account_id, ma.name_full_for_matching, mta.money_min_one_year
                FROM m_account ma
                LEFT JOIN m_talent_act mta ON ma.account_id = mta.account_id
                WHERE ma.account_id = $1
                  AND ma.del_flag = 0
                  AND mta.account_id IS NOT NULL
                  AND (
                    (mta.money_min_one_year IS NOT NULL AND mta.money_max_one_year IS NOT NULL
                     AND mta.money_min_one_year <= $2 / 10000)
                    OR
                    (mta.money_min_one_year IS NOT NULL AND mta.money_max_one_year IS NULL
                     AND mta.money_min_one_year <= $2 / 10000)
                    OR
                    (mta.money_min_one_year IS NULL AND mta.money_max_one_year IS NOT NULL
                     AND mta.money_max_one_year <= $2 / 10000)
                  )
                """
                scope_result = await conn.fetchrow(scope_check_query, recommended['account_id'], budget_max)
                if scope_result:
                    recommended_in_scope.append({
                        'account_id': recommended['account_id'],
                        'name': recommended['name'],
                        'budget': scope_result['money_min_one_year']
                    })
                else:
                    print(f"   ⚠️ おすすめタレント「{recommended['name']}」は予算範囲外")

            print(f"   予算範囲内のおすすめタレント: {len(recommended_in_scope)}名")
            for rec in recommended_in_scope:
                print(f"     - {rec['name']} (ID: {rec['account_id']}, 予算: {rec['budget']}万円)")

            # 最終的な結果数を計算
            final_recommended_count = len(recommended_in_scope)
            remaining_standard_count = min(30 - final_recommended_count, len(filtered_standard))
            final_count = final_recommended_count + remaining_standard_count

        print(f"\n🎯 最終結果予測:")
        print(f"   おすすめタレント: {final_recommended_count if 'final_recommended_count' in locals() else 0}名")
        print(f"   通常タレント: {remaining_standard_count if 'remaining_standard_count' in locals() else len(standard_results)}名")
        print(f"   合計: {final_count}名")

        if final_count == 3:
            print(f"   💡 3名しか表示されない理由:")
            print(f"      - おすすめタレントが存在するが、予算範囲外である可能性")
            print(f"      - または、通常マッチング結果が少ない可能性")

    except Exception as e:
        print(f"❌ エラー: {e}")
        import traceback
        traceback.print_exc()

    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(debug_recommended_integration())