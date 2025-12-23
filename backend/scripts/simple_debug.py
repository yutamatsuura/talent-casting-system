#!/usr/bin/env python3
"""
シンプルなサンドウィッチマンTPRスコア調査
"""

import asyncio
import sys
from pathlib import Path

# プロジェクトルートパスを追加
sys.path.insert(0, str(Path(__file__).parent.parent))
from app.db.connection import init_db, get_session_maker
from sqlalchemy import text

async def simple_investigation():
    """シンプルな調査"""
    await init_db()
    session_maker = get_session_maker()

    print("=" * 60)
    print("🔍 サンドウィッチマンTPRスコア簡易調査")
    print("=" * 60)

    async with session_maker() as session:
        # 1. サンドウィッチマン基本情報（account_id=729）
        print(f"\n【1】サンドウィッチマン (account_id: 729) のTPRスコア")
        print("-" * 50)

        result = await session.execute(
            text('''
                SELECT
                    target_segment_id,
                    tpr_power_score,
                    vr_popularity,
                    base_power_score,
                    updated_at
                FROM talent_scores
                WHERE account_id = 729
                ORDER BY target_segment_id
            ''')
        )

        scores = result.fetchall()

        if not scores:
            print("❌ talent_scoresにサンドウィッチマンのデータがありません")
            return

        target_1_tpr = None
        for score in scores:
            segment_id = score[0]
            tpr_score = score[1]
            vr_popularity = score[2]
            base_power = score[3]
            updated_at = score[4]

            print(f"target_segment_id: {segment_id}")
            print(f"  tpr_power_score: {tpr_score}")
            print(f"  vr_popularity: {vr_popularity}")
            print(f"  base_power_score: {base_power}")
            print(f"  updated_at: {updated_at}")

            if segment_id == 1:  # 男性12-19歳
                target_1_tpr = tpr_score
            print()

        # 2. 比較結果
        print(f"【2】データ比較結果")
        print("-" * 30)
        print(f"📄 CSVソースデータ: 35.7")
        print(f"🗄️  DB値 (target_segment_id=1): {target_1_tpr}")
        print(f"📥 診断結果CSV出力値: 25.7")
        print()

        if target_1_tpr and float(target_1_tpr) == 25.7:
            print("🔍 原因: DBのTPRスコアが既に25.7になっています")
            print("   ソースデータ(35.7)が正しく反映されていない可能性")
        elif target_1_tpr and float(target_1_tpr) == 35.7:
            print("🔍 原因: DBは正しい値(35.7)ですが、診断システムが25.7を返している")
            print("   診断システムの別のロジックが影響している可能性")
        else:
            print(f"🔍 原因: 予期しない値({target_1_tpr})が格納されています")

        # 3. 他のコンビ・グループも確認
        print(f"\n【3】他のコンビ・グループの確認")
        print("-" * 40)

        combo_checks = [
            ("チョコレートプラネット", "30.7"),
            ("かまいたち", "25.7"),
            ("千鳥", "24.3")
        ]

        for group_name, csv_score in combo_checks:
            result = await session.execute(
                text('''
                    SELECT ma.account_id, ts.tpr_power_score
                    FROM m_account ma
                    JOIN talent_scores ts ON ma.account_id = ts.account_id
                    WHERE ma.name_full_for_matching LIKE :name
                      AND ts.target_segment_id = 1
                      AND ma.del_flag = 0
                    LIMIT 1
                '''),
                {'name': f'%{group_name}%'}
            )
            db_row = result.fetchone()

            if db_row:
                account_id, db_score = db_row
                print(f"{group_name} (account_id: {account_id}):")
                print(f"  CSVソース: {csv_score}")
                print(f"  DB値: {db_score}")

                if str(db_score) != csv_score:
                    print(f"  ❌ 不一致: {db_score} != {csv_score}")
                else:
                    print(f"  ✅ 一致")
            else:
                print(f"{group_name}: ❌ 見つからず")
            print()

    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(simple_investigation())