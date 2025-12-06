#!/usr/bin/env python3
"""
VR処理の完了状況詳細調査
"""
import os
import pandas as pd
import chardet
from glob import glob

def investigate_vr_completion():
    """VR処理の完了状況を詳細調査"""

    print("=== VR処理完了状況の詳細調査 ===")
    print()

    # 1. 各VRディレクトリのファイル数確認
    vr_directories = [
        "/Users/lennon/projects/talent-casting-form/DB情報/【VR①】C列の人気度と、E～K列の各種イメージを採用する想定です",
        "/Users/lennon/projects/talent-casting-form/DB情報/【VR②】C列の人気度と、E～K列の各種イメージを採用する想定です",
        "/Users/lennon/projects/talent-casting-form/DB情報/【VR③】C列の人気度と、E～K列の各種イメージを採用する想定です"
    ]

    total_expected_records = 0
    actual_file_count = 0

    for i, directory in enumerate(vr_directories, 1):
        print(f"{i}. VR{i}ディレクトリ: {os.path.basename(directory)}")

        if os.path.exists(directory):
            csv_files = glob(os.path.join(directory, "*.csv"))
            print(f"   ファイル数: {len(csv_files)}個")
            actual_file_count += len(csv_files)

            # 各ファイルのレコード数確認
            directory_total = 0
            for csv_file in csv_files:
                try:
                    # エンコーディング検出
                    with open(csv_file, 'rb') as f:
                        raw_data = f.read(10000)
                        result = chardet.detect(raw_data)
                        encoding = 'shift_jis' if result['encoding'] in ['SHIFT_JIS', 'CP932'] else 'utf-8'

                    # CSVファイル読み込み
                    df = pd.read_csv(csv_file, encoding=encoding)
                    record_count = len(df)
                    directory_total += record_count

                    filename = os.path.basename(csv_file)
                    print(f"     {filename}: {record_count}件")

                except Exception as e:
                    filename = os.path.basename(csv_file)
                    print(f"     {filename}: ❌ 読み込みエラー: {e}")

            print(f"   ディレクトリ合計: {directory_total}件")
            total_expected_records += directory_total
        else:
            print(f"   ❌ ディレクトリが存在しません")
        print()

    print("=== 調査結果まとめ ===")
    print(f"実際のファイル数: {actual_file_count}個")
    print(f"実際の総レコード数: {total_expected_records:,}件")
    print(f"想定レコード数: 8,000件 (500件×16ファイル)")
    print()

    if total_expected_records != 8000:
        print(f"⚠️  想定と実際のレコード数に差異: {total_expected_records - 8000:+}件")
        print("これがVR処理での60件未完了の原因の可能性があります")
    else:
        print("ファイル内容は想定通りです。他の原因を調査する必要があります。")

if __name__ == "__main__":
    investigate_vr_completion()