#!/usr/bin/env python3
"""Excelファイル全タブ構造確認"""

import pandas as pd
from pathlib import Path

DB_INFO_DIR = Path("/Users/lennon/projects/talent-casting-form/DB情報")
NOW_DATA_PATH = DB_INFO_DIR / "Nowデータ_20251126.xlsx"

def examine_excel_tabs():
    """Excelファイルの全タブ構造確認"""
    print("=" * 80)
    print("🔍 EXCEL FILE TABS STRUCTURE EXAMINATION")
    print("=" * 80)

    if not NOW_DATA_PATH.exists():
        print(f"❌ File not found: {NOW_DATA_PATH}")
        return

    print(f"📂 File: {NOW_DATA_PATH}")

    # 全シート名取得
    excel_file = pd.ExcelFile(NOW_DATA_PATH)
    sheet_names = excel_file.sheet_names

    print(f"\n📋 Total sheets: {len(sheet_names)}")
    for i, sheet_name in enumerate(sheet_names, 1):
        print(f"   {i}: {sheet_name}")

    # 各シートの基本情報確認
    print(f"\n📊 Sheet Details:")
    for sheet_name in sheet_names:
        print(f"\n🔍 Sheet: '{sheet_name}'")

        try:
            df = pd.read_excel(NOW_DATA_PATH, sheet_name=sheet_name)
            print(f"   📊 Rows: {len(df):,}")
            print(f"   📊 Columns: {len(df.columns)}")

            # 列名表示（最初の10列のみ）
            columns_to_show = list(df.columns)[:10]
            if len(df.columns) > 10:
                columns_to_show.append(f"... and {len(df.columns) - 10} more")
            print(f"   📋 Columns: {', '.join(str(col) for col in columns_to_show)}")

            # account_id列の確認
            if 'account_id' in df.columns:
                print(f"   ✅ account_id found")
                unique_account_ids = df['account_id'].nunique()
                total_account_ids = len(df)
                print(f"   📊 Unique account_ids: {unique_account_ids:,} / {total_account_ids:,}")

                # サンプルaccount_id
                sample_ids = df['account_id'].dropna().head(5).tolist()
                print(f"   📄 Sample account_ids: {sample_ids}")
            else:
                print(f"   ❌ account_id NOT found")

            # del_flag列の確認
            if 'del_flag' in df.columns:
                print(f"   ✅ del_flag found")
                del_counts = df['del_flag'].value_counts()
                for value, count in del_counts.items():
                    print(f"      del_flag={value}: {count:,} records")
            else:
                print(f"   ❌ del_flag NOT found")

            # データサンプル（最初の3行）
            print(f"   📄 Sample data (first 3 rows):")
            for i, (_, row) in enumerate(df.head(3).iterrows()):
                row_data = []
                for col in df.columns[:5]:  # 最初の5列のみ
                    value = str(row[col]) if pd.notna(row[col]) else "NaN"
                    if len(value) > 15:
                        value = value[:12] + "..."
                    row_data.append(f"{col}={value}")
                print(f"      Row{i+1}: {' | '.join(row_data)}")

        except Exception as e:
            print(f"   ❌ Error reading sheet: {e}")

    # シート間のaccount_id重複確認
    print(f"\n🔍 Account ID relationships across sheets:")
    account_ids_by_sheet = {}

    for sheet_name in sheet_names:
        try:
            df = pd.read_excel(NOW_DATA_PATH, sheet_name=sheet_name)
            if 'account_id' in df.columns:
                account_ids = set(df['account_id'].dropna().astype(int))
                account_ids_by_sheet[sheet_name] = account_ids
                print(f"   {sheet_name}: {len(account_ids):,} unique account_ids")
        except Exception as e:
            print(f"   {sheet_name}: Error reading - {e}")

    # 共通account_idの確認
    if len(account_ids_by_sheet) > 1:
        sheet_names_with_account_id = list(account_ids_by_sheet.keys())
        print(f"\n🔍 Common account_ids between sheets:")

        for i, sheet1 in enumerate(sheet_names_with_account_id):
            for sheet2 in sheet_names_with_account_id[i+1:]:
                common_ids = account_ids_by_sheet[sheet1] & account_ids_by_sheet[sheet2]
                print(f"   {sheet1} ∩ {sheet2}: {len(common_ids):,} common account_ids")

                if len(common_ids) > 0:
                    sample_common = list(common_ids)[:5]
                    print(f"      Sample: {sample_common}")

    print("=" * 80)

if __name__ == "__main__":
    examine_excel_tabs()