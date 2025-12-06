#!/usr/bin/env python3
"""
仁村紗和がおすすめタレントとして表示されない原因の詳細調査

具体的な調査項目:
1. 仁村紗和の完全なデータ状況
2. 現在の予算フィルタリングロジックでの除外状況
3. 各STEPでの抽出状況を追跡
4. 正確な原因の特定
"""

import asyncio
from app.db.connection import get_asyncpg_connection
from app.api.endpoints.matching import get_matching_parameters, normalize_budget_range_string

async def debug_kimura_filtering():
    print("🔍 仁村紗和 フィルタリング詳細デバッグ")
    print("=" * 60)

    conn = await get_asyncpg_connection()
    try:
        kimura_id = 123
        industry = "化粧品・ヘアケア・オーラルケア"
        target_segment = "女性20-34歳"
        budget = "1,000万円～3,000万円未満"

        # 1. 仁村紗和の完全データ状況
        print("\n1️⃣ 仁村紗和の完全データ状況")

        kimura_full_data = await conn.fetchrow(f"""
            SELECT
                ma.account_id,
                ma.name_full_for_matching,
                ma.del_flag,
                ma.birthday,
                ma.act_genre,
                mta.money_max_one_year,
                mta.money_min_one_year,
                ts.target_segment_id as ts_target_segment_id,
                ts.base_power_score,
                ts.vr_popularity,
                ts.tpr_power_score
            FROM m_account ma
            LEFT JOIN m_talent_act mta ON ma.account_id = mta.account_id
            LEFT JOIN talent_scores ts ON ma.account_id = ts.account_id
            WHERE ma.account_id = {kimura_id}
        """)

        if kimura_full_data:
            print(f"✅ 基本データ:")
            print(f"  - account_id: {kimura_full_data['account_id']}")
            print(f"  - name: {kimura_full_data['name_full_for_matching']}")
            print(f"  - del_flag: {kimura_full_data['del_flag']}")
            print(f"  - act_genre: {kimura_full_data['act_genre']}")
            print(f"  - money_max_one_year: {kimura_full_data['money_max_one_year']}")
            print(f"  - talent_scores存在: {'Yes' if kimura_full_data['ts_target_segment_id'] else 'No'}")
            if kimura_full_data['ts_target_segment_id']:
                print(f"  - target_segment_id: {kimura_full_data['ts_target_segment_id']}")
                print(f"  - base_power_score: {kimura_full_data['base_power_score']}")
        else:
            print("❌ データが見つかりません")
            return

        # 2. ターゲット層IDの確認
        print(f"\n2️⃣ ターゲット層マッチング確認")
        target_segment_row = await conn.fetchrow(
            "SELECT target_segment_id FROM target_segments WHERE segment_name = $1",
            target_segment
        )
        if target_segment_row:
            expected_segment_id = target_segment_row['target_segment_id']
            print(f"期待されるtarget_segment_id: {expected_segment_id}")

            # 仁村紗和の該当ターゲット層のデータ確認
            kimura_target_score = await conn.fetchrow(f"""
                SELECT * FROM talent_scores
                WHERE account_id = {kimura_id} AND target_segment_id = {expected_segment_id}
            """)

            if kimura_target_score:
                print(f"✅ ターゲット層データ存在:")
                print(f"  - base_power_score: {kimura_target_score['base_power_score']}")
                print(f"  - vr_popularity: {kimura_target_score['vr_popularity']}")
                print(f"  - tpr_power_score: {kimura_target_score['tpr_power_score']}")
            else:
                print(f"❌ target_segment_id={expected_segment_id}のデータなし")

                # 仁村紗和が持っているターゲット層IDを確認
                all_target_segments = await conn.fetch(f"""
                    SELECT target_segment_id, base_power_score
                    FROM talent_scores
                    WHERE account_id = {kimura_id}
                    ORDER BY target_segment_id
                """)
                print(f"仁村紗和が持つターゲット層: {[row['target_segment_id'] for row in all_target_segments]}")

        # 3. 予算フィルタの詳細確認
        print(f"\n3️⃣ 予算フィルタ詳細確認")

        # 予算区分の正規化確認
        normalized_budget = normalize_budget_range_string(budget)
        print(f"予算区分 (正規化前): {budget}")
        print(f"予算区分 (正規化後): {normalized_budget}")

        # 予算上限値の取得
        try:
            max_budget, target_segment_id, image_item_ids = await get_matching_parameters(
                budget, target_segment, industry
            )
            print(f"予算上限値: {max_budget}")
            print(f"target_segment_id: {target_segment_id}")
            print(f"image_item_ids: {image_item_ids}")
        except Exception as e:
            print(f"❌ パラメータ取得エラー: {e}")
            return

        # 4. 実際のフィルタクエリでの確認
        print(f"\n4️⃣ 実際のフィルタクエリでの確認")

        # アルコール業界かどうか判定
        is_alcohol_industry = industry == "アルコール飲料"
        print(f"アルコール業界: {is_alcohol_industry}")

        # STEP 0のクエリを実行（予算フィルタリング）
        step0_query = f"""
        SELECT DISTINCT ma.account_id, ma.name_full_for_matching as name, ma.last_name_kana, ma.act_genre
        FROM m_account ma
        LEFT JOIN m_talent_act mta ON ma.account_id = mta.account_id
        WHERE (
            mta.money_max_one_year IS NULL
            OR ({max_budget} = 'Infinity'::float8 OR mta.money_max_one_year <= {max_budget})
        ) AND (
            -- アルコール業界の場合のみ25歳以上フィルタ適用
            {is_alcohol_industry} = false OR (
                ma.birthday IS NOT NULL
                AND (EXTRACT(YEAR FROM CURRENT_DATE) - EXTRACT(YEAR FROM ma.birthday)) >= 25
            )
        ) AND ma.account_id = {kimura_id}
        """

        step0_result = await conn.fetch(step0_query)
        print(f"STEP 0 (予算フィルタ) 結果:")
        if step0_result:
            for row in step0_result:
                print(f"  ✅ {row['name']} (ID: {row['account_id']})")
        else:
            print(f"  ❌ 仁村紗和は予算フィルタで除外されました")

            # 原因を特定
            print(f"\n  🔍 除外原因の特定:")

            # money_max_one_year確認
            money_check = await conn.fetchval(f"""
                SELECT mta.money_max_one_year
                FROM m_talent_act mta
                WHERE mta.account_id = {kimura_id}
            """)
            print(f"  - money_max_one_year: {money_check}")
            print(f"  - 予算上限: {max_budget}")
            print(f"  - 予算チェック: {money_check} <= {max_budget} = {money_check <= max_budget if money_check else 'NULL'}")

            # 年齢チェック（アルコール業界の場合）
            if is_alcohol_industry:
                age_check = await conn.fetchval(f"""
                    SELECT (EXTRACT(YEAR FROM CURRENT_DATE) - EXTRACT(YEAR FROM ma.birthday))
                    FROM m_account ma
                    WHERE ma.account_id = {kimura_id}
                """)
                print(f"  - 年齢: {age_check}")
                print(f"  - 年齢チェック: {age_check} >= 25 = {age_check >= 25 if age_check else 'NULL'}")

        # 5. おすすめタレントとしての取得確認
        print(f"\n5️⃣ おすすめタレント設定確認")
        recommended_check = await conn.fetchrow(f"""
            SELECT
                rt.talent_id_1, rt.talent_id_2, rt.talent_id_3,
                CASE
                    WHEN rt.talent_id_1 = {kimura_id} THEN 1
                    WHEN rt.talent_id_2 = {kimura_id} THEN 2
                    WHEN rt.talent_id_3 = {kimura_id} THEN 3
                    ELSE 0
                END as position
            FROM recommended_talents rt
            WHERE rt.industry_name = '{industry}'
        """)

        if recommended_check and recommended_check['position'] > 0:
            print(f"✅ {recommended_check['position']}位におすすめタレントとして設定済み")
        else:
            print(f"❌ おすすめタレントとして設定されていない")
            print(f"    設定タレント: {recommended_check['talent_id_1'] if recommended_check else 'None'}, {recommended_check['talent_id_2'] if recommended_check else 'None'}, {recommended_check['talent_id_3'] if recommended_check else 'None'}")

    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(debug_kimura_filtering())