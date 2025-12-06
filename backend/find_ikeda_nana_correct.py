#!/usr/bin/env python3
"""
正しい池田菜々の特定とデータ状況調査

方針:
1. recommended_talentsテーブルから3位設定されているタレントを特定
2. 該当タレントのm_talent_actデータ確認
3. 予算フィルタ除外問題の原因特定
"""

import asyncio
from app.db.connection import get_asyncpg_connection

async def find_ikeda_nana_correct():
    print("🔍 正しい池田菜々の特定とデータ調査")
    print("=" * 60)

    conn = await get_asyncpg_connection()
    try:
        # 1. recommended_talentsテーブルから3位設定されているタレント特定
        print("\n1️⃣ おすすめタレント3位設定の確認")

        third_position_talents = await conn.fetch("""
            SELECT DISTINCT
                rt.talent_id_3,
                ma.name_full_for_matching,
                ma.act_genre,
                ma.del_flag,
                COUNT(*) as industries_count
            FROM recommended_talents rt
            INNER JOIN m_account ma ON rt.talent_id_3 = ma.account_id
            WHERE rt.talent_id_3 IS NOT NULL
            GROUP BY rt.talent_id_3, ma.name_full_for_matching, ma.act_genre, ma.del_flag
            ORDER BY industries_count DESC, ma.name_full_for_matching
        """)

        print(f"3位に設定されているタレント一覧:")
        for talent in third_position_talents:
            print(f"  - ID={talent['talent_id_3']:4}: {talent['name_full_for_matching']:15s} ({talent['act_genre']:10s}) - {talent['industries_count']}業界, del_flag={talent['del_flag']}")

        # 池田菜々らしきタレントを特定
        ikeda_candidates = [t for t in third_position_talents if '池田' in t['name_full_for_matching'] or '菜々' in t['name_full_for_matching']]

        if ikeda_candidates:
            ikeda_talent = ikeda_candidates[0]
            ikeda_id = ikeda_talent['talent_id_3']
            print(f"\n✅ 池田菜々と推定: ID={ikeda_id}, 名前={ikeda_talent['name_full_for_matching']}")
        else:
            print(f"\n⚠️ 池田菜々らしき名前が見つからないため、最多設定タレントを調査対象とします")
            if third_position_talents:
                ikeda_talent = third_position_talents[0]
                ikeda_id = ikeda_talent['talent_id_3']
                print(f"調査対象: ID={ikeda_id}, 名前={ikeda_talent['name_full_for_matching']}")
            else:
                print("❌ 3位設定タレントが見つかりません")
                return

        # 2. 該当タレントのm_talent_actデータ確認
        print(f"\n2️⃣ {ikeda_talent['name_full_for_matching']}のm_talent_actデータ確認")

        talent_act_data = await conn.fetchrow("""
            SELECT
                mta.account_id,
                mta.money_max_one_year,
                mta.money_min_one_year
            FROM m_talent_act mta
            WHERE mta.account_id = $1
        """, ikeda_id)

        if talent_act_data:
            print(f"✅ m_talent_actデータ存在:")
            print(f"  - money_max_one_year: {talent_act_data['money_max_one_year']}")
            print(f"  - money_min_one_year: {talent_act_data['money_min_one_year']}")
        else:
            print(f"❌ m_talent_actデータなし (account_id={ikeda_id})")
            print(f"    → これが予算フィルタで除外される原因です！")

        # 3. 設定業界での確認
        print(f"\n3️⃣ おすすめ設定業界確認")

        setting_industries = await conn.fetch("""
            SELECT industry_name, talent_id_1, talent_id_2, talent_id_3
            FROM recommended_talents
            WHERE talent_id_3 = $1
            ORDER BY industry_name
        """, ikeda_id)

        if setting_industries:
            print(f"✅ {len(setting_industries)}業界で3位に設定:")
            for industry in setting_industries[:5]:  # 最初の5業界のみ表示
                print(f"  - {industry['industry_name']}")
            if len(setting_industries) > 5:
                print(f"  ... 他{len(setting_industries) - 5}業界")
        else:
            print(f"❌ おすすめ設定なし")

        # 4. 具体的な業界でのテスト（化粧品業界）
        print(f"\n4️⃣ 化粧品業界での具体的テスト")

        cosmetics_test = await conn.fetchrow("""
            SELECT
                rt.talent_id_1, rt.talent_id_2, rt.talent_id_3,
                t1.name_full_for_matching as talent_1_name,
                t2.name_full_for_matching as talent_2_name,
                t3.name_full_for_matching as talent_3_name
            FROM recommended_talents rt
            LEFT JOIN m_account t1 ON rt.talent_id_1 = t1.account_id
            LEFT JOIN m_account t2 ON rt.talent_id_2 = t2.account_id
            LEFT JOIN m_account t3 ON rt.talent_id_3 = t3.account_id
            WHERE rt.industry_name = '化粧品・ヘアケア・オーラルケア'
        """)

        if cosmetics_test:
            print(f"化粧品業界のおすすめ設定:")
            print(f"  1位: {cosmetics_test['talent_1_name']} (ID: {cosmetics_test['talent_id_1']})")
            print(f"  2位: {cosmetics_test['talent_2_name']} (ID: {cosmetics_test['talent_id_2']})")
            print(f"  3位: {cosmetics_test['talent_3_name']} (ID: {cosmetics_test['talent_id_3']})")

            if cosmetics_test['talent_id_3'] == ikeda_id:
                print(f"  ✅ {ikeda_talent['name_full_for_matching']}が3位に設定されています")
            else:
                print(f"  ⚠️ {ikeda_talent['name_full_for_matching']}は化粧品業界の3位ではありません")

        # 5. 予算フィルタテスト
        print(f"\n5️⃣ 予算フィルタテスト")

        test_budget = 30000000  # 3,000万円未満

        # 現在のロジック（LEFT JOIN）
        current_logic_result = await conn.fetchval("""
            SELECT EXISTS(
                SELECT 1 FROM m_account ma
                LEFT JOIN m_talent_act mta ON ma.account_id = mta.account_id
                WHERE ma.account_id = $1
                  AND ma.del_flag = 0
                  AND (
                    mta.money_max_one_year IS NULL
                    OR mta.money_max_one_year <= $2
                  )
            )
        """, ikeda_id, test_budget)

        # INNER JOINの場合
        inner_join_result = await conn.fetchval("""
            SELECT EXISTS(
                SELECT 1 FROM m_account ma
                INNER JOIN m_talent_act mta ON ma.account_id = mta.account_id
                WHERE ma.account_id = $1
                  AND ma.del_flag = 0
                  AND mta.money_max_one_year <= $2
            )
        """, ikeda_id, test_budget)

        print(f"予算フィルタテスト結果 (予算上限: {test_budget:,}円):")
        print(f"  - 現在のロジック(LEFT JOIN): {'✅通過' if current_logic_result else '❌除外'}")
        print(f"  - 従来ロジック(INNER JOIN): {'✅通過' if inner_join_result else '❌除外'}")

        # 6. talent_scoresデータ確認
        print(f"\n6️⃣ talent_scoresデータ確認")

        scores_count = await conn.fetchval("""
            SELECT COUNT(*) FROM talent_scores WHERE account_id = $1
        """, ikeda_id)

        print(f"talent_scoresデータ: {scores_count}件")

        if scores_count > 0:
            sample_score = await conn.fetchrow("""
                SELECT target_segment_id, base_power_score
                FROM talent_scores
                WHERE account_id = $1
                ORDER BY target_segment_id
                LIMIT 1
            """, ikeda_id)
            print(f"  サンプル: target_segment_id={sample_score['target_segment_id']}, base_power_score={sample_score['base_power_score']}")

        # 7. 問題の根本原因と解決策
        print(f"\n7️⃣ 問題の根本原因と解決策")

        has_talent_act = talent_act_data is not None
        is_active = ikeda_talent['del_flag'] == 0
        has_scores = scores_count > 0

        print(f"問題診断:")
        print(f"  - アカウント有効: {'✅' if is_active else '❌'}")
        print(f"  - m_talent_actデータ: {'✅' if has_talent_act else '❌'}")
        print(f"  - talent_scoresデータ: {'✅' if has_scores else '❌'}")

        if not has_talent_act and is_active:
            print(f"\n🔥 根本問題特定:")
            print(f"  {ikeda_talent['name_full_for_matching']}は有効なタレントですが、")
            print(f"  m_talent_actテーブルにデータがないため、")
            print(f"  おすすめタレントでも予算フィルタで除外されています。")
            print(f"\n💡 解決策:")
            print(f"  1. ✅ get_recommended_talent_details関数でm_talent_act無視")
            print(f"  2. ✅ apply_recommended_talents_integration関数でおすすめは予算除外")
            print(f"  3. ❌ 現在のマッチングクエリがLEFT JOINでもおすすめに影響している")

    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(find_ikeda_nana_correct())