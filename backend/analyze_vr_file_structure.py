#!/usr/bin/env python3
"""
VRファイルの構造分析
"""
import pandas as pd
import chardet
import os

def analyze_vr_file_structure():
    """VRファイルの実際の構造を分析"""

    print("=== VRファイル構造分析 ===")
    print()

    # サンプルファイルを選択
    sample_file = "/Users/lennon/projects/talent-casting-form/DB情報/【VR①】C列の人気度と、E～K列の各種イメージを採用する想定です/VR男性タレント_男性20～34_202507.csv"

    if not os.path.exists(sample_file):
        print("❌ サンプルファイルが存在しません")
        return

    try:
        # エンコーディング検出
        with open(sample_file, 'rb') as f:
            raw_data = f.read(10000)
            result = chardet.detect(raw_data)
            encoding = 'shift_jis' if result['encoding'] in ['SHIFT_JIS', 'CP932'] else 'utf-8'

        print(f"1. ファイル: {os.path.basename(sample_file)}")
        print(f"2. エンコーディング: {encoding}")
        print()

        # CSVファイル詳細読み込み
        df = pd.read_csv(sample_file, encoding=encoding)

        print("3. ファイル基本情報:")
        print(f"   行数: {len(df)}行")
        print(f"   列数: {len(df.columns)}列")
        print()

        print("4. 列名（ヘッダー）:")
        for i, col in enumerate(df.columns):
            print(f"   {chr(65+i)}列: '{col}'")
        print()

        print("5. 最初の5行データ:")
        print(df.head().to_string())
        print()

        print("6. A列（想定タレント名列）のサンプル:")
        a_column = df.iloc[:, 0] if len(df.columns) > 0 else None
        if a_column is not None:
            print("   タイプ:", a_column.dtype)
            print("   サンプル値:")
            for i, value in enumerate(a_column.head(10)):
                print(f"     {i+1}. '{value}' (type: {type(value).__name__})")

            # NaN値の確認
            nan_count = a_column.isna().sum()
            print(f"   NaN値数: {nan_count}")

            # ユニーク値の数
            unique_count = a_column.nunique()
            print(f"   ユニーク値数: {unique_count}")
        print()

        print("7. B列以降のサンプル:")
        if len(df.columns) > 1:
            for col_idx in range(1, min(6, len(df.columns))):  # B-F列
                col_name = df.columns[col_idx]
                col_data = df.iloc[:, col_idx]
                print(f"   {chr(65+col_idx)}列 '{col_name}': {col_data.head(3).tolist()}")

        print()
        print("8. 想定される問題:")

        # A列が数字の場合
        if a_column is not None and a_column.dtype in ['int64', 'float64']:
            print("   ⚠️ A列が数値型です。タレント名ではない可能性があります。")
            print("   → CSVの列構造が想定と異なる可能性")

        # タレント名らしき列を探す
        print("\n9. タレント名らしき列の検索:")
        for col_idx, col_name in enumerate(df.columns):
            col_data = df.iloc[:, col_idx]
            if col_data.dtype == 'object':  # 文字列っぽい列
                sample_values = col_data.dropna().head(5).tolist()
                print(f"   {chr(65+col_idx)}列 '{col_name}': {sample_values}")

    except Exception as e:
        print(f"❌ ファイル分析エラー: {e}")

if __name__ == "__main__":
    analyze_vr_file_structure()