#!/usr/bin/env python3
"""
新垣結衣のデータベース値確認スクリプト
"""
import asyncio
import asyncpg
from app.db.connection import get_asyncpg_connection

async def check_gakki_data():
    print("🔍 新垣結衣のデータベース値確認")
    print("=" * 50)

    conn = await get_asyncpg_connection()
    try:
        # 新垣結衣のaccount_id確認
        account_query = """
        SELECT account_id, name_full_for_matching
        FROM m_account
        WHERE name_full_for_matching LIKE '%新垣%'
        AND del_flag = 0
        """
        accounts = await conn.fetch(account_query)

        print("新垣関連のアカウント:")
        for account in accounts:
            print(f"  ID: {account['account_id']}, 名前: {account['name_full_for_matching']}")

        if accounts:
            gakki_id = accounts[0]['account_id']
            print(f"\n新垣結衣のaccount_id: {gakki_id}")

            # talent_scoresのデータ確認
            scores_query = """
            SELECT
                account_id,
                target_segment_id,
                vr_popularity,
                tpr_power_score,
                base_power_score,
                (COALESCE(vr_popularity, 0) + COALESCE(tpr_power_score, 0)) / 2.0 as calculated_base
            FROM talent_scores
            WHERE account_id = $1
            ORDER BY target_segment_id
            """
            scores = await conn.fetch(scores_query, gakki_id)

            print(f"\n新垣結衣のtalent_scoresデータ:")
            for score in scores:
                print(f"  ターゲット: {score['target_segment_id']}")
                print(f"    VR人気度: {score['vr_popularity']}")
                print(f"    TPRスコア: {score['tpr_power_score']}")
                print(f"    既存base_power_score: {score['base_power_score']}")
                print(f"    計算値 (VR+TPR)/2: {score['calculated_base']}")
                print()

            # 「女性20-34歳」のターゲットセグメントIDを確認
            segment_query = """
            SELECT target_segment_id, segment_name
            FROM target_segments
            WHERE segment_name = '女性20-34歳'
            """
            segment = await conn.fetchrow(segment_query)
            if segment:
                target_id = segment['target_segment_id']
                print(f"「女性20-34歳」のID: {target_id}")

                # 該当ターゲットセグメントのデータのみ抽出
                specific_score = next((s for s in scores if s['target_segment_id'] == target_id), None)
                if specific_score:
                    print(f"\n「女性20-34歳」での新垣結衣のスコア:")
                    print(f"  VR人気度: {specific_score['vr_popularity']}")
                    print(f"  TPRスコア: {specific_score['tpr_power_score']}")
                    print(f"  計算値: {specific_score['calculated_base']}")

    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(check_gakki_data())