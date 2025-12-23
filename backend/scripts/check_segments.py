#!/usr/bin/env python3
"""
target_segment_idマッピング調査
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from app.db.connection import init_db, get_session_maker
from sqlalchemy import text

async def check_segments():
    """ターゲットセグメントIDを調査"""
    await init_db()
    session_maker = get_session_maker()

    print("=" * 70)
    print("🔍 target_segment_idマッピング調査")
    print("=" * 70)

    async with session_maker() as session:
        # 1. CSVファイル名とtarget_segment_idの対応表を確認
        print(f"\n【1】CSVファイル名パターンとsegment_id推定")
        print("-" * 50)

        csv_files = [
            "TPR_男性12～19_202508.csv",
            "TPR_女性12～19_202508.csv",
            "TPR_男性20～34_202508.csv",
            "TPR_女性20～34_202508.csv",
            "TPR_男性35～49_202508.csv",
            "TPR_女性35～49_202508.csv",
            "TPR_男性50～69_202508.csv",
            "TPR_女性50～69_202508.csv"
        ]

        for i, filename in enumerate(csv_files, 1):
            print(f"ID {i:2d}: {filename}")

        # 2. 実際に存在するターゲットセグメントIDを確認
        print(f"\n【2】データベース内の実在target_segment_id")
        print("-" * 50)

        result = await session.execute(
            text('''
                SELECT DISTINCT target_segment_id
                FROM talent_scores
                ORDER BY target_segment_id
            ''')
        )

        existing_segments = [row[0] for row in result.fetchall()]
        print(f"実在するID: {existing_segments}")

        # 3. サンドウィッチマンのsegment別データ詳細
        print(f"\n【3】サンドウィッチマン segment別詳細分析")
        print("-" * 50)

        result = await session.execute(
            text('''
                SELECT
                    target_segment_id,
                    tpr_power_score,
                    vr_popularity,
                    updated_at
                FROM talent_scores
                WHERE account_id = 729
                ORDER BY target_segment_id
            ''')
        )

        segment_scores = result.fetchall()

        for score in segment_scores:
            segment_id = score[0]
            tpr_score = score[1]
            vr_popularity = score[2]
            updated_at = score[3]

            # 推定対応
            estimated_demo = ""
            if segment_id == 9:
                estimated_demo = "← 25.7 = 診断結果CSV出力値"
            elif segment_id == 10:
                estimated_demo = "← 35.0 ≈ CSVソース35.7"

            print(f"segment_id {segment_id}: TPR={tpr_score}, VR={vr_popularity} {estimated_demo}")
            print(f"  updated: {updated_at}")

        # 4. 診断システムが想定するsegment_idと実際のマッピング検証
        print(f"\n【4】マッピング仮説検証")
        print("-" * 40)

        # 男性12-19歳の診断でsegment_id=1を期待するが、実際にはsegment_id=9を参照している可能性
        expected_mapping = {
            1: "男性12-19歳",
            2: "女性12-19歳",
            3: "男性20-34歳",
            4: "女性20-34歳",
            5: "男性35-49歳",
            6: "女性35-49歳",
            7: "男性50-69歳",
            8: "女性50-69歳"
        }

        actual_mapping = {
            9: "男性12-19歳 (?)",
            10: "女性12-19歳 (?)",
            11: "男性20-34歳 (?)",
            12: "女性20-34歳 (?)",
            13: "男性35-49歳 (?)",
            14: "女性35-49歳 (?)",
            15: "男性50-69歳 (?)",
            16: "女性50-69歳 (?)"
        }

        print("期待されるマッピング:")
        for seg_id, demo in expected_mapping.items():
            print(f"  {seg_id}: {demo}")

        print("\n実際のデータ存在パターン:")
        for seg_id, demo in actual_mapping.items():
            print(f"  {seg_id}: {demo}")

        print(f"\n🔍 結論:")
        print(f"診断システムは target_segment_id = 1 (男性12-19歳) を要求")
        print(f"しかし実際のデータは target_segment_id = 9 から開始")
        print(f"システムがフォールバックで segment_id = 9 のデータ(25.7)を返している")

    print("\n" + "=" * 70)

if __name__ == "__main__":
    asyncio.run(check_segments())