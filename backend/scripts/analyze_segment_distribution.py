#!/usr/bin/env python3
"""
target_segment_id分布分析 - 統一方針策定用
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from app.db.connection import init_db, get_session_maker
from sqlalchemy import text

async def analyze_segment_distribution():
    """ターゲットセグメント分布を詳細分析"""
    await init_db()
    session_maker = get_session_maker()

    print("=" * 80)
    print("🔍 target_segment_id分布分析 - 統一方針策定")
    print("=" * 80)

    async with session_maker() as session:

        # 1. 全体の分布確認
        print(f"\n【1】target_segment_id別データ件数")
        print("-" * 50)

        result = await session.execute(
            text('''
                SELECT
                    target_segment_id,
                    COUNT(DISTINCT account_id) as タレント数,
                    COUNT(*) as レコード数
                FROM talent_scores
                GROUP BY target_segment_id
                ORDER BY target_segment_id
            ''')
        )

        distribution = result.fetchall()
        total_unique_talents = 0

        for row in distribution:
            segment_id, talent_count, record_count = row
            print(f"segment_id {segment_id:2d}: タレント数 {talent_count:5,}件, レコード数 {record_count:6,}件")
            if segment_id <= 8:
                total_unique_talents += talent_count

        # 2. 重複分析（個人タレントがコンビ分にも存在するか）
        print(f"\n【2】個人タレントとコンビ・グループの重複分析")
        print("-" * 50)

        # segment 1-8に存在するタレント
        result = await session.execute(
            text('''
                SELECT DISTINCT account_id
                FROM talent_scores
                WHERE target_segment_id BETWEEN 1 AND 8
            ''')
        )
        individual_talents = {row[0] for row in result.fetchall()}

        # segment 9-16に存在するタレント
        result = await session.execute(
            text('''
                SELECT DISTINCT account_id
                FROM talent_scores
                WHERE target_segment_id BETWEEN 9 AND 16
            ''')
        )
        combo_talents = {row[0] for row in result.fetchall()}

        overlap = individual_talents & combo_talents

        print(f"個人タレント範囲(1-8)の固有account_id: {len(individual_talents):,}件")
        print(f"コンビ範囲(9-16)の固有account_id: {len(combo_talents):,}件")
        print(f"重複するaccount_id: {len(overlap):,}件")

        if overlap:
            print(f"\n重複例（最初の5件）:")
            overlap_list = list(overlap)[:5]
            for account_id in overlap_list:
                result = await session.execute(
                    text('SELECT name_full_for_matching FROM m_account WHERE account_id = :id'),
                    {'id': account_id}
                )
                name_row = result.fetchone()
                name = name_row[0] if name_row else "不明"
                print(f"  account_id {account_id}: {name}")

        # 3. サンプル分析（コンビ・グループの特徴）
        print(f"\n【3】コンビ・グループの特徴分析")
        print("-" * 40)

        result = await session.execute(
            text('''
                SELECT DISTINCT ma.account_id, ma.name_full_for_matching
                FROM m_account ma
                JOIN talent_scores ts ON ma.account_id = ts.account_id
                WHERE ts.target_segment_id BETWEEN 9 AND 16
                  AND ma.del_flag = 0
                ORDER BY ma.name_full_for_matching
                LIMIT 10
            ''')
        )

        combo_samples = result.fetchall()
        print("コンビ・グループ例（10件）:")
        for account_id, name in combo_samples:
            print(f"  {account_id:4d}: {name}")

        # 4. 統一方針の選択肢とリスク分析
        print(f"\n【4】統一方針の選択肢")
        print("-" * 30)

        print("🔄 選択肢A: 全てを1-8に統一")
        print("  メリット:")
        print("    - 診断システムの修正不要")
        print("    - 既存の個人タレントとの整合性")
        print("  デメリット:")
        print(f"    - コンビ({len(combo_talents):,}件)のsegment_id変更が必要")
        print("    - 大量のUPDATE処理とリスク")

        print("\n🔄 選択肢B: 全てを9-16に統一")
        print("  メリット:")
        print("    - 新しい体系への移行")
        print("    - コンビデータの修正不要")
        print("  デメリット:")
        print(f"    - 個人タレント({len(individual_talents):,}件)のsegment_id変更が必要")
        print("    - 診断システムの修正必要")
        print("    - 更に大量のUPDATE処理")

        print("\n🔄 選択肢C: 診断システムのみ修正")
        print("  メリット:")
        print("    - データ変更不要")
        print("    - 最小限の修正")
        print("  デメリット:")
        print("    - 二重管理の継続")
        print("    - 将来的な混乱リスク")

        # 5. 推奨案の提示
        print(f"\n【5】推奨案")
        print("-" * 20)

        if len(combo_talents) < len(individual_talents):
            print("🎯 推奨: 選択肢A（コンビを1-8に移行）")
            print("理由:")
            print(f"  - 影響範囲が小さい（{len(combo_talents):,}件 vs {len(individual_talents):,}件）")
            print("  - 診断システム修正不要")
            print("  - 標準的な1-8体系に統一")
        else:
            print("🎯 推奨: 選択肢C（診断システム修正）")
            print("理由:")
            print("  - データ変更リスクを回避")
            print("  - 段階的な移行が可能")

        # 6. 実装案
        print(f"\n【6】推奨案の実装手順")
        print("-" * 30)

        print("Phase 1: 一時的対応")
        print("  1. TPR更新スクリプトのsegment_id対応表を9-16に修正")
        print("  2. ドライランで動作確認")
        print("  3. 本番実行")

        print("\nPhase 2: 根本対応（推奨: コンビを1-8に移行）")
        print("  1. コンビ・グループのsegment_id移行スクリプト作成")
        print("  2. ドライラン + バックアップ")
        print("  3. 移行実行")
        print("  4. TPR更新スクリプトを1-8体系に戻す")
        print("  5. 整合性確認")

    print("\n" + "=" * 80)

if __name__ == "__main__":
    asyncio.run(analyze_segment_distribution())