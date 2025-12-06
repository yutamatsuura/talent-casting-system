#!/usr/bin/env python3
"""タレント名マッチングロジック分析"""

import pandas as pd
import asyncio
import sys
import re
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from sqlalchemy import select, text
from app.db.connection import init_db, get_session_maker

# データパス
DB_INFO_DIR = Path(__file__).parent.parent / "DB情報"
NOW_DATA_PATH = DB_INFO_DIR / "Nowデータ_20251126.xlsx"
TPR_DIR = DB_INFO_DIR / "【TPR】G列のパワースコアを採用する想定です"

AsyncSessionLocal = None

async def get_async_session():
    global AsyncSessionLocal
    if AsyncSessionLocal is None:
        await init_db()
        AsyncSessionLocal = get_session_maker()
    return AsyncSessionLocal()

def normalize_name(name):
    """名前正規化（スペース除去）"""
    if not name:
        return ""
    # 全角・半角スペース除去
    normalized = re.sub(r'[\s\u3000]+', '', str(name))
    return normalized.strip()

async def analyze_name_matching():
    """名前マッチング分析"""
    print("=" * 80)
    print("🔍 TALENT NAME MATCHING ANALYSIS")
    print("=" * 80)

    # 1. データベースのタレント名取得
    print("\n📋 Database talent names analysis...")
    async with await get_async_session() as session:
        result = await session.execute(text("SELECT id, name FROM talents LIMIT 20"))
        db_talents = [(row[0], row[1]) for row in result.fetchall()]

        total_count = await session.execute(text("SELECT COUNT(*) FROM talents"))
        total = total_count.scalar()

    print(f"   Total talents in DB: {total:,}")
    print(f"   Sample DB talent names:")
    for talent_id, name in db_talents[:10]:
        print(f"      ID{talent_id}: '{name}' (len={len(name)})")

    # 2. Excelファイルの名前構造確認
    print(f"\n📋 Excel source name structure...")
    if NOW_DATA_PATH.exists():
        df_now = pd.read_excel(NOW_DATA_PATH)
        print(f"   Total Excel records: {len(df_now):,}")
        print(f"   Active records (del_flag=0): {len(df_now[df_now['del_flag']==0]):,}")

        # last_name + first_name の構成を確認
        print(f"   Sample Excel name construction:")
        for i in range(10):
            row = df_now.iloc[i]
            last_name = str(row.get("last_name", "")).strip()
            first_name = str(row.get("first_name", "")).strip() if pd.notna(row.get("first_name")) else ""
            full_name = f"{last_name}{first_name}".strip()
            del_flag = row.get("del_flag")
            print(f"      '{last_name}' + '{first_name}' = '{full_name}' (del_flag={del_flag})")

    # 3. TPRファイルの名前構造確認
    print(f"\n📋 TPR file name structure...")
    tpr_files = list(TPR_DIR.glob("*.csv"))
    if tpr_files:
        sample_file = tpr_files[0]
        print(f"   Sample file: {sample_file.name}")
        try:
            df_tpr = pd.read_csv(sample_file, encoding='utf-8')
        except UnicodeDecodeError:
            df_tpr = pd.read_csv(sample_file, encoding='shift_jis')

        print(f"   TPR records: {len(df_tpr)}")
        print(f"   Sample TPR talent names:")
        for i in range(10):
            if i >= len(df_tpr):
                break
            talent_name = str(df_tpr.iloc[i].get("タレント名", "")).strip()
            print(f"      '{talent_name}' (len={len(talent_name)})")

    # 4. 名前正規化テスト
    print(f"\n📋 Name normalization testing...")
    test_names = [
        "山田 涼介",
        "山田　涼介",  # 全角スペース
        "山田涼介",
        "新垣 結衣",
        "新垣結衣",
        "マツコ・デラックス",
        "マツコ ・ デラックス"
    ]

    for name in test_names:
        normalized = normalize_name(name)
        print(f"      '{name}' → '{normalized}' (スペース除去)")

    # 5. 実際のマッチング問題検出
    print(f"\n📋 Actual matching issues detection...")
    async with await get_async_session() as session:
        # データベースのタレント名を正規化マップ作成
        result = await session.execute(text("SELECT name FROM talents"))
        db_names = [row[0] for row in result.fetchall()]

        # 正規化マップ
        normalized_db = {normalize_name(name): name for name in db_names}

        print(f"   Database names: {len(db_names):,}")
        print(f"   Normalized unique names: {len(normalized_db):,}")

        duplicates_after_normalization = len(db_names) - len(normalized_db)
        if duplicates_after_normalization > 0:
            print(f"   ⚠️  {duplicates_after_normalization} duplicate names after normalization!")

    # 6. TPRマッチング率確認
    if tpr_files:
        print(f"\n📋 TPR matching rate analysis...")
        total_tpr_names = 0
        matched_names = 0
        unmatched_sample = []

        for tpr_file in tpr_files[:2]:  # 最初の2ファイルをテスト
            try:
                df_tpr = pd.read_csv(tpr_file, encoding='utf-8')
            except UnicodeDecodeError:
                df_tpr = pd.read_csv(tpr_file, encoding='shift_jis')

            for _, row in df_tpr.iterrows():
                talent_name = str(row.get("タレント名", "")).strip()
                if not talent_name or talent_name == "nan":
                    continue

                total_tpr_names += 1

                # 直接マッチング
                if talent_name in db_names:
                    matched_names += 1
                # 正規化マッチング
                elif normalize_name(talent_name) in normalized_db:
                    matched_names += 1
                else:
                    if len(unmatched_sample) < 10:
                        unmatched_sample.append(talent_name)

        match_rate = (matched_names / total_tpr_names * 100) if total_tpr_names > 0 else 0
        print(f"   TPR names tested: {total_tpr_names}")
        print(f"   Matched: {matched_names} ({match_rate:.1f}%)")
        print(f"   Unmatched: {total_tpr_names - matched_names}")

        if unmatched_sample:
            print(f"   Sample unmatched names:")
            for name in unmatched_sample:
                normalized = normalize_name(name)
                print(f"      '{name}' → normalized: '{normalized}'")

    print("=" * 80)

async def main():
    try:
        await analyze_name_matching()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())