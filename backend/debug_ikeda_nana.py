#!/usr/bin/env python3
"""
池田菜々の詳細データ調査

調査項目:
1. 池田菜々のaccount_idの特定
2. m_talent_actテーブルデータの存在確認
3. 全業界での3位設定状況の確認
4. 予算フィルタでの除外状況の確認
5. 現在のマッチングロジックでの取得状況
"""

import asyncio
from app.db.connection import get_asyncpg_connection

async def debug_ikeda_nana():
    print("🔍 池田菜々 詳細データ調査")
    print("=" * 60)

    conn = await get_asyncpg_connection()
    try:
        # 1. 池田菜々のaccount_idを特定
        print("\n1️⃣ 池田菜々の基本情報特定")

        ikeda_candidates = await conn.fetch("""
            SELECT account_id, name_full_for_matching, act_genre, del_flag
            FROM m_account
            WHERE name_full_for_matching LIKE '%池田菜々%'
               OR name_full_for_matching LIKE '%菜々%'
               OR name_full_for_matching = '池田菜々'
            ORDER BY account_id
        """)

        if ikeda_candidates:
            print(f"池田菜々候補:")
            for candidate in ikeda_candidates:
                print(f"  - ID={candidate['account_id']:4}: {candidate['name_full_for_matching']} ({candidate['act_genre']}, del_flag={candidate['del_flag']})")

            # 最初の候補を池田菜々として採用
            ikeda_data = ikeda_candidates[0]
            ikeda_id = ikeda_data['account_id']
            print(f"\n✅ 池田菜々として特定: ID={ikeda_id}, 名前={ikeda_data['name_full_for_matching']}")
        else:
            print("❌ 池田菜々が見つかりません")
            return

        # 2. m_talent_actデータの確認
        print(f"\n2️⃣ 池田菜々のm_talent_actデータ確認")

        talent_act_data = await conn.fetchrow(f"""
            SELECT
                mta.account_id,
                mta.money_max_one_year,
                mta.money_min_one_year,
                mta.created_at,
                mta.updated_at
            FROM m_talent_act mta
            WHERE mta.account_id = {ikeda_id}
        """)

        if talent_act_data:
            print(f"✅ m_talent_actデータ存在:")
            print(f"  - money_max_one_year: {talent_act_data['money_max_one_year']}")
            print(f"  - money_min_one_year: {talent_act_data['money_min_one_year']}")
            print(f"  - 作成日: {talent_act_data['created_at']}")
        else:
            print(f"❌ m_talent_actデータなし (account_id={ikeda_id})")
            print(f"    → これが予算フィルタで除外される原因です")

        # 3. 全業界での3位設定状況確認
        print(f"\n3️⃣ 全業界での3位設定状況確認")

        all_recommendations = await conn.fetch(f"""
            SELECT
                industry_name,
                talent_id_1,
                talent_id_2,
                talent_id_3,
                CASE
                    WHEN talent_id_1 = {ikeda_id} THEN 1
                    WHEN talent_id_2 = {ikeda_id} THEN 2
                    WHEN talent_id_3 = {ikeda_id} THEN 3
                    ELSE 0
                END as position
            FROM recommended_talents
            ORDER BY industry_name
        """)

        ikeda_recommendations = [r for r in all_recommendations if r['position'] > 0]

        if ikeda_recommendations:
            print(f"✅ 池田菜々がおすすめ設定されている業界:")
            for rec in ikeda_recommendations:
                print(f"  - {rec['industry_name']}: {rec['position']}位")
        else:
            print(f"❌ 池田菜々はどの業界でもおすすめ設定されていません")

        # 全業界で3位設定されているかチェック
        all_industries = await conn.fetch("SELECT industry_name FROM recommended_talents ORDER BY industry_name")
        third_position_count = len([r for r in all_recommendations if r['talent_id_3'] == ikeda_id])

        print(f"\n業界統計:")
        print(f"  - 総業界数: {len(all_industries)}")
        print(f"  - 池田菜々が3位設定されている業界数: {third_position_count}")
        print(f"  - 全業界3位設定率: {(third_position_count / len(all_industries) * 100):.1f}%")

        # 4. 具体的な予算フィルタテスト
        print(f"\n4️⃣ 予算フィルタテスト")

        test_budgets = [
            ("1,000万円未満", 10000000),
            ("1,000万円～3,000万円未満", 30000000),
            ("3,000万円～1億円未満", 100000000),
            ("1億円以上", float('inf'))
        ]

        for budget_name, max_budget in test_budgets:
            # 現在のフィルタロジック
            filter_result = await conn.fetchval(f"""
                SELECT EXISTS(
                    SELECT 1 FROM m_account ma
                    LEFT JOIN m_talent_act mta ON ma.account_id = mta.account_id
                    WHERE ma.account_id = {ikeda_id}
                      AND ma.del_flag = 0
                      AND (
                        mta.money_max_one_year IS NULL
                        OR mta.money_max_one_year <= {max_budget}
                      )
                )
            """)

            result_mark = "✅" if filter_result else "❌"
            print(f"  {result_mark} {budget_name}: {'通過' if filter_result else '除外'}")

        # 5. talent_scoresデータ確認
        print(f"\n5️⃣ 池田菜々のtalent_scoresデータ確認")

        scores_data = await conn.fetch(f"""
            SELECT
                target_segment_id,
                base_power_score,
                vr_popularity,
                tpr_power_score
            FROM talent_scores
            WHERE account_id = {ikeda_id}
            ORDER BY target_segment_id
        """)

        if scores_data:
            print(f"✅ talent_scoresデータ存在 (ターゲット層数: {len(scores_data)}):")
            for score in scores_data[:3]:  # 最初の3つのみ表示
                print(f"  - target_segment_id={score['target_segment_id']}: base_power={score['base_power_score']}")
        else:
            print(f"❌ talent_scoresデータなし")

        # 6. 問題の特定と解決策
        print(f"\n6️⃣ 問題の特定と解決策")

        has_talent_act = talent_act_data is not None
        has_scores = len(scores_data) > 0
        has_recommendations = len(ikeda_recommendations) > 0

        if not has_talent_act:
            print(f"❌ 主要問題: m_talent_actデータ欠損")
            print(f"   → おすすめタレントでも予算フィルタで除外される")
            print(f"   → 解決策: おすすめタレント用の予算フィルタ完全除外が必要")

        if not has_scores:
            print(f"❌ 副次問題: talent_scoresデータ欠損")
            print(f"   → マッチングスコア計算不可")

        if not has_recommendations:
            print(f"❌ 設定問題: おすすめタレント未設定")
            print(f"   → 管理画面での設定確認が必要")

        if has_talent_act and has_scores and has_recommendations:
            print(f"✅ データ問題なし: 別の原因を調査必要")

    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(debug_ikeda_nana())