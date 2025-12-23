#!/usr/bin/env python3
"""
サンドウィッチマンのTPRスコア相違調査スクリプト
"""

import asyncio
import sys
from pathlib import Path
from decimal import Decimal

# プロジェクトルートパスを追加
sys.path.insert(0, str(Path(__file__).parent.parent))
from app.db.connection import init_db, get_session_maker
from sqlalchemy import text

async def investigate_sandwich_man_discrepancy():
    """サンドウィッチマンのTPRスコア相違を詳細調査"""
    await init_db()
    session_maker = get_session_maker()

    print("=" * 80)
    print("🔍 サンドウィッチマンTPRスコア相違原因調査")
    print("=" * 80)

    async with session_maker() as session:
        # 1. サンドウィッチマンの基本情報確認
        print("\n【1】サンドウィッチマン基本情報")
        print("-" * 40)

        result = await session.execute(
            text('''
                SELECT account_id, name_full_for_matching, del_flag, created_at, updated_at
                FROM m_account
                WHERE name_full_for_matching LIKE '%サンドウィッチ%'
            ''')
        )
        talent_info = result.fetchone()

        if not talent_info:
            print("❌ サンドウィッチマンがtalentsテーブルに存在しません")
            return

        account_id = talent_info[0]
        print(f"✅ account_id: {account_id}")
        print(f"✅ 名前: {talent_info[1]}")
        print(f"✅ del_flag: {talent_info[2]}")
        print(f"✅ created_at: {talent_info[3]}")
        print(f"✅ updated_at: {talent_info[4]}")

        # 2. 全ターゲット層のTPRスコア確認
        print(f"\n【2】サンドウィッチマン (account_id: {account_id}) 全ターゲット層TPRスコア")
        print("-" * 60)

        result = await session.execute(
            text('''
                SELECT
                    ts.target_segment_id,
                    tsg.segment_name,
                    ts.tpr_power_score,
                    ts.vr_popularity,
                    ts.base_power_score,
                    ts.updated_at
                FROM talent_scores ts
                LEFT JOIN m_target_segment tsg ON ts.target_segment_id = tsg.target_segment_id
                WHERE ts.account_id = :account_id
                ORDER BY ts.target_segment_id
            '''),
            {'account_id': account_id}
        )
        scores = result.fetchall()

        if not scores:
            print("❌ talent_scoresにデータがありません")
            return

        # ターゲットセグメント1（男性12-19歳）を特定
        target_segment_1_score = None
        for score in scores:
            segment_id = score[0]
            segment_name = score[1] or f"ID_{segment_id}"
            tpr_score = score[2]
            vr_popularity = score[3]
            base_power = score[4]
            updated_at = score[5]

            print(f"segment_id {segment_id} ({segment_name}):")
            print(f"  TPRスコア: {tpr_score}")
            print(f"  VR人気度: {vr_popularity}")
            print(f"  base_power_score: {base_power}")
            print(f"  updated_at: {updated_at}")

            if segment_id == 1:  # 男性12-19歳
                target_segment_1_score = tpr_score
            print()

        # 3. 診断システムで実際に使用されるクエリをテスト
        print("\n【3】診断システム実行シミュレーション（男性12-19歳、乳製品）")
        print("-" * 60)

        # 診断結果のCSVで使われるクエリを再現
        diagnosis_result = await session.execute(
            text('''
                SELECT
                    t.name_full_for_matching as タレント名,
                    ic.category_name as カテゴリー,
                    ts.vr_popularity as "VR人気度",
                    ts.tpr_power_score as "TPRスコア",
                    ts.base_power_score as "従来スコア"
                FROM m_account t
                JOIN talent_scores ts ON t.account_id = ts.account_id
                LEFT JOIN m_industry_category ic ON t.category_id = ic.category_id
                WHERE t.name_full_for_matching = 'サンドウィッチマン'
                  AND ts.target_segment_id = 1
                  AND t.del_flag = 0
            ''')
        )
        diagnosis_row = diagnosis_result.fetchone()

        if diagnosis_row:
            print("診断システムクエリ結果:")
            print(f"  タレント名: {diagnosis_row[0]}")
            print(f"  カテゴリー: {diagnosis_row[1]}")
            print(f"  VR人気度: {diagnosis_row[2]}")
            print(f"  TPRスコア: {diagnosis_row[3]} ← これが問題の値")
            print(f"  従来スコア: {diagnosis_row[4]}")
        else:
            print("❌ 診断システムクエリで結果が取得できません")

        # 4. CSVソースデータとの比較
        print(f"\n【4】ソースデータとの比較")
        print("-" * 30)
        print(f"📄 CSVソースデータ (TPR_男性12～19_202508.csv): 35.7")
        print(f"🗄️  現在のDB値 (target_segment_id=1): {target_segment_1_score}")
        print(f"📥 診断結果CSV出力値: 25.7")

        # 5. 他のコンビ・グループも確認
        print(f"\n【5】他のコンビ・グループの状況確認")
        print("-" * 40)

        combo_groups = [
            ("チョコレートプラネット", "30.7"),
            ("かまいたち", "25.7"),
            ("千鳥", "24.3")
        ]

        for group_name, csv_score in combo_groups:
            result = await session.execute(
                text('''
                    SELECT ts.tpr_power_score
                    FROM m_account t
                    JOIN talent_scores ts ON t.account_id = ts.account_id
                    WHERE t.name_full_for_matching LIKE :name
                      AND ts.target_segment_id = 1
                      AND t.del_flag = 0
                '''),
                {'name': f'%{group_name}%'}
            )
            db_score = result.fetchone()
            db_value = db_score[0] if db_score else "見つからず"

            print(f"{group_name}:")
            print(f"  CSVソース: {csv_score}")
            print(f"  DB値: {db_value}")

    print("\n" + "=" * 80)

if __name__ == "__main__":
    asyncio.run(investigate_sandwich_man_discrepancy())