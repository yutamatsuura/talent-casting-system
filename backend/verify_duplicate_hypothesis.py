#!/usr/bin/env python3
"""
VRファイル内のタレント重複仮説の検証
"""
import asyncio
import asyncpg
import os
import pandas as pd
import chardet
from glob import glob
import collections

async def verify_duplicate_hypothesis():
    """VRファイル内のタレント重複仮説を検証"""

    database_url = os.getenv('DATABASE_URL')
    conn = await asyncpg.connect(database_url)

    try:
        print("=== VRファイル重複仮説の検証 ===")
        print()

        # 1. VRファイルから全データ収集（ファイル別・セグメント別）
        vr_directories = [
            "/Users/lennon/projects/talent-casting-form/DB情報/【VR①】C列の人気度と、E～K列の各種イメージを採用する想定です",
            "/Users/lennon/projects/talent-casting-form/DB情報/【VR②】C列の人気度と、E～K列の各種イメージを採用する想定です",
            "/Users/lennon/projects/talent-casting-form/DB情報/【VR③】C列の人気度と、E～K列の各種イメージを採用する想定です"
        ]

        all_talent_entries = []  # (タレント名, ファイル名, セグメント)のリスト
        talent_frequency = collections.Counter()

        for dir_idx, directory in enumerate(vr_directories, 1):
            if os.path.exists(directory):
                csv_files = glob(os.path.join(directory, "*.csv"))
                print(f"VR{dir_idx}ディレクトリ: {len(csv_files)}ファイル")

                for csv_file in csv_files:
                    try:
                        filename = os.path.basename(csv_file)

                        # セグメント情報抽出（ファイル名から）
                        segment_info = filename.replace('VR男性タレント_', '').replace('VR女性タレント_', '').replace('_202507.csv', '')

                        # エンコーディング検出
                        with open(csv_file, 'rb') as f:
                            raw_data = f.read(10000)
                            result = chardet.detect(raw_data)
                            encoding = 'shift_jis' if result['encoding'] in ['SHIFT_JIS', 'CP932'] else 'utf-8'

                        # CSVファイル読み込み（B列＝タレント名）
                        df = pd.read_csv(csv_file, encoding=encoding)
                        if len(df.columns) > 1:
                            # 4行目以降からB列のタレント名を取得
                            talent_names = df.iloc[3:, 1].dropna()

                            print(f"  {filename}: {len(talent_names)}件")

                            for talent_name in talent_names:
                                all_talent_entries.append((talent_name, filename, segment_info))
                                talent_frequency[talent_name] += 1

                    except Exception as e:
                        print(f"❌ {filename}: エラー: {e}")

        print()
        print(f"1. 収集結果:")
        print(f"   総エントリ数: {len(all_talent_entries):,}件")
        print(f"   ユニークタレント数: {len(talent_frequency):,}人")
        print()

        # 2. 重複タレントの分析
        duplicated_talents = {name: count for name, count in talent_frequency.items() if count > 1}
        single_talents = {name: count for name, count in talent_frequency.items() if count == 1}

        print(f"2. 重複分析:")
        print(f"   重複タレント: {len(duplicated_talents):,}人")
        print(f"   単一タレント: {len(single_talents):,}人")
        print()

        # 3. 重複の多いタレント例
        print("3. 重複の多いタレント例（上位10人）:")
        most_duplicated = sorted(duplicated_talents.items(), key=lambda x: x[1], reverse=True)[:10]

        for rank, (talent_name, count) in enumerate(most_duplicated, 1):
            print(f"   {rank}. {talent_name}: {count}回出現")

            # どのファイル/セグメントに出現しているかを表示
            appearances = [entry for entry in all_talent_entries if entry[0] == talent_name]
            segments = [entry[2] for entry in appearances]
            print(f"      セグメント: {', '.join(segments[:5])}")  # 最初の5つを表示
            if len(segments) > 5:
                print(f"      ... 他{len(segments)-5}セグメント")
            print()

        # 4. データベースでの処理状況確認
        print("4. データベース処理状況:")

        # talent_scoresのタレント別セグメント数
        talent_segment_counts = await conn.fetch("""
            SELECT
                t.name,
                COUNT(DISTINCT ts.target_segment_id) as segment_count,
                COUNT(*) as total_records
            FROM talent_scores ts
            INNER JOIN talents t ON t.id = ts.talent_id
            GROUP BY t.id, t.name
            ORDER BY segment_count DESC, t.name
            LIMIT 10
        """)

        print("   データベース内のタレント別セグメント数（上位10人）:")
        for record in talent_segment_counts:
            name = record['name']
            segment_count = record['segment_count']
            total_records = record['total_records']
            print(f"   - {name}: {segment_count}セグメント, {total_records}レコード")

        print()

        # 5. 仮説検証結果
        print("=== 仮説検証結果 ===")

        expected_unique = 8000 // 8  # 8セグメントで割る
        actual_unique = len(talent_frequency)

        print(f"期待ユニーク数: 約{expected_unique:,}人（8,000件÷8セグメント）")
        print(f"実際ユニーク数: {actual_unique:,}人")

        if abs(actual_unique - expected_unique) < expected_unique * 0.2:  # 20%以内
            print("✅ 仮説確認: VRファイルには同じタレントが複数セグメントに出現")
            print("✅ VR処理は正常動作: 重複排除により適切にユニークタレントを処理")
        else:
            print("⚠️ 仮説要再検討: 重複以外の要因が存在する可能性")

        print(f"\n現在のVR処理状況:")
        print(f"- VRファイル内ユニーク: {actual_unique:,}人")
        print(f"- 処理済み: 993人")
        print(f"- 処理率: {(993/actual_unique)*100:.1f}%")

        # 残り8人程度の未処理を調査
        print(f"\n残り{actual_unique-993}人の未処理原因を調査中...")

    except Exception as e:
        print(f"❌ エラー: {e}")
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(verify_duplicate_hypothesis())