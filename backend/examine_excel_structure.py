#!/usr/bin/env python3
"""Excelファイル構造確認"""

import pandas as pd
from pathlib import Path

DB_INFO_DIR = Path("/Users/lennon/projects/talent-casting-form/DB情報")
NOW_DATA_PATH = DB_INFO_DIR / "Nowデータ_20251126.xlsx"

def examine_excel_structure():
    """Excelファイルの構造を確認"""
    print("=" * 80)
    print("🔍 EXCEL FILE STRUCTURE EXAMINATION")
    print("=" * 80)

    if not NOW_DATA_PATH.exists():
        print(f"❌ File not found: {NOW_DATA_PATH}")
        return

    print(f"📂 File: {NOW_DATA_PATH}")

    # Excelファイル読み込み
    df = pd.read_excel(NOW_DATA_PATH)

    print(f"\n📊 Basic Info:")
    print(f"   - Total rows: {len(df):,}")
    print(f"   - Total columns: {len(df.columns)}")

    print(f"\n📋 All Columns ({len(df.columns)} total):")
    for i, col in enumerate(df.columns, 1):
        print(f"   {i:2d}: {col}")

    # del_flag列の確認
    print(f"\n🔍 del_flag Analysis:")
    if 'del_flag' in df.columns:
        print("   ✅ del_flag column found!")
        del_counts = df['del_flag'].value_counts()
        print(f"   📊 Value counts:")
        for value, count in del_counts.items():
            print(f"      del_flag={value}: {count:,} records")

        active_records = len(df[df['del_flag'] == 0])
        deleted_records = len(df[df['del_flag'] == 1])
        total_records = len(df)

        print(f"\n   📈 Summary:")
        print(f"      Active (del_flag=0): {active_records:,} records")
        print(f"      Deleted (del_flag=1): {deleted_records:,} records")
        print(f"      Total: {total_records:,} records")
        print(f"      Active %: {active_records/total_records*100:.1f}%")

    else:
        print("   ❌ del_flag column NOT found!")
        print("   🔍 Similar column names:")
        similar_cols = [col for col in df.columns if 'del' in str(col).lower() or 'flag' in str(col).lower()]
        if similar_cols:
            for col in similar_cols:
                print(f"      - {col}")
        else:
            print("      (No similar columns found)")

    # name_full列の確認
    print(f"\n🔍 name_full Analysis:")
    if 'name_full' in df.columns:
        print("   ✅ name_full column found!")
        sample_names = df['name_full'].dropna().head(10).tolist()
        print(f"   📄 Sample names:")
        for name in sample_names:
            print(f"      - {name}")
    else:
        print("   ❌ name_full column NOT found!")
        name_cols = [col for col in df.columns if 'name' in str(col).lower()]
        print(f"   🔍 Name-related columns:")
        for col in name_cols:
            print(f"      - {col}")

    print("=" * 80)

if __name__ == "__main__":
    examine_excel_structure()