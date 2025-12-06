#!/usr/bin/env python3
"""
VR処理進捗をデータベースから確認
"""
import asyncio
import asyncpg
import os
from datetime import datetime

async def check_vr_progress():
    """VR処理進捗をデータベースから確認"""

    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URLが設定されていません")
        return

    try:
        conn = await asyncpg.connect(database_url)

        print("=== VR処理進捗確認 ===")
        print(f"確認時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()

        # 1. talent_scoresテーブルのデータ数
        scores_count = await conn.fetchval("SELECT COUNT(*) FROM talent_scores")
        print(f"📊 talent_scores レコード数: {scores_count:,}件")

        # 2. target_segment別の統計
        print("\n=== ターゲットセグメント別統計 ===")
        segment_stats = await conn.fetch("""
            SELECT
                ts.name as segment_name,
                COUNT(tsc.*) as record_count
            FROM target_segments ts
            LEFT JOIN talent_scores tsc ON ts.id = tsc.target_segment_id
            GROUP BY ts.id, ts.name
            ORDER BY ts.id
        """)

        for stat in segment_stats:
            segment_name = stat['segment_name']
            record_count = stat['record_count'] or 0
            print(f"  {segment_name}: {record_count:,}件")

        # 3. talent_imagesテーブルのデータ数
        images_count = await conn.fetchval("SELECT COUNT(*) FROM talent_images")
        print(f"\n📊 talent_images レコード数: {images_count:,}件")

        # 4. image_item別の統計（VRデータの種類確認）
        print("\n=== イメージ項目別統計（サンプル10項目）===")
        image_stats = await conn.fetch("""
            SELECT
                ii.name as item_name,
                COUNT(ti.*) as record_count
            FROM image_items ii
            LEFT JOIN talent_images ti ON ii.id = ti.image_item_id
            GROUP BY ii.id, ii.name
            ORDER BY record_count DESC
            LIMIT 10
        """)

        for stat in image_stats:
            item_name = stat['item_name']
            record_count = stat['record_count'] or 0
            print(f"  {item_name}: {record_count:,}件")

        # 5. 最近のデータ更新時間（created_atがある場合）
        try:
            latest_score = await conn.fetchrow("""
                SELECT MAX(id) as latest_id, COUNT(*) as total_count
                FROM talent_scores
            """)
            if latest_score:
                print(f"\n📅 talent_scores 最新ID: {latest_score['latest_id']}")
                print(f"📅 talent_scores 総レコード数: {latest_score['total_count']:,}")
        except:
            print("\n📅 最新更新時間の取得ができませんでした")

        # 6. VR処理の期待値と比較
        expected_records_per_file = 500  # 各ファイル500件
        total_files = 16  # 全16ファイル
        expected_total = expected_records_per_file * total_files

        print(f"\n=== 進捗推定 ===")
        print(f"期待総レコード数: {expected_total:,}件 (500件/ファイル × 16ファイル)")

        if scores_count > 0:
            progress_percentage = (scores_count / expected_total) * 100
            estimated_completed_files = scores_count // expected_records_per_file
            print(f"現在の進捗: {progress_percentage:.1f}% ({estimated_completed_files}/16 ファイル完了見込み)")
        else:
            print("まだVRデータが検出されていません")

    except Exception as e:
        print(f"❌ エラー: {e}")
    finally:
        if 'conn' in locals():
            await conn.close()

if __name__ == "__main__":
    asyncio.run(check_vr_progress())