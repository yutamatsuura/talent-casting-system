#!/usr/bin/env python3
"""VRインポートでスキップされたタレント名の詳細調査"""

import pandas as pd
import re
from pathlib import Path
import chardet
import asyncio
from sqlalchemy import text
import sys

sys.path.insert(0, str(Path(__file__).parent))
from app.db.connection import init_db, get_session_maker

AsyncSessionLocal = None

async def get_async_session():
    global AsyncSessionLocal
    if AsyncSessionLocal is None:
        await init_db()
        AsyncSessionLocal = get_session_maker()
    return AsyncSessionLocal()

def detect_encoding(file_path):
    """ファイルのエンコーディングを自動検出"""
    with open(file_path, 'rb') as file:
        raw_data = file.read(10000)
        result = chardet.detect(raw_data)
        encoding = result['encoding']

        if encoding in ['SHIFT_JIS', 'CP932', 'Shift_JIS']:
            return 'shift_jis'
        elif encoding in ['UTF-8', 'utf-8']:
            return 'utf-8'
        else:
            return 'shift_jis'

def normalize_name(name):
    """タレント名の正規化（スペース除去）"""
    if pd.isna(name) or name is None:
        return None
    normalized = re.sub(r'[\s\u3000\u00A0\u2000-\u200A\u2028\u2029\u202F\u205F]+', '', str(name))
    return normalized.strip()

async def analyze_skipped_talents():
    """スキップされたタレントの詳細分析"""
    print("🔍 VRスキップタレント詳細調査開始")
    print("=" * 50)

    # CSVファイル読み込み
    vr_file = "/Users/lennon/projects/talent-casting-form/DB情報/【VR①】C列の人気度と、E～K列の各種イメージを採用する想定です/VR男性タレント_男性20～34_202507.csv"

    encoding = detect_encoding(vr_file)
    df = pd.read_csv(vr_file, encoding=encoding, skiprows=4)
    print(f"📊 CSV読み込み完了: {len(df)}行")

    # タレントマッピング取得
    async with await get_async_session() as session:
        result = await session.execute(text("SELECT id, account_id, name_normalized FROM talents"))
        talent_mapping = {}
        for row in result:
            if row[2]:  # name_normalizedが存在する場合
                talent_mapping[row[2]] = row[0]
        print(f"📊 データベースタレント数: {len(talent_mapping)}")

    # スキップされたタレントの分析
    found_count = 0
    skipped_count = 0
    skipped_talents = []

    print(f"\n📋 タレント名チェック:")
    for index, row in df.iterrows():
        talent_name_raw = row.get('タレント名')
        talent_name = normalize_name(talent_name_raw)

        if not talent_name:
            print(f"  ⚠️  空のタレント名 (行{index+6}): '{talent_name_raw}'")
            skipped_count += 1
            skipped_talents.append(f"行{index+6}: 空名前 '{talent_name_raw}'")
        elif talent_name not in talent_mapping:
            print(f"  ❌ 未登録タレント (行{index+6}): '{talent_name_raw}' -> '{talent_name}'")
            skipped_count += 1
            skipped_talents.append(f"行{index+6}: '{talent_name_raw}' (正規化: '{talent_name}')")
        else:
            found_count += 1

    print(f"\n📊 集計結果:")
    print(f"   ✅ 登録済み: {found_count}件")
    print(f"   ❌ スキップ: {skipped_count}件")
    print(f"   📈 登録率: {(found_count / len(df) * 100):.1f}%")

    if skipped_talents:
        print(f"\n❌ スキップされたタレント ({len(skipped_talents)}件):")
        for talent in skipped_talents[:10]:  # 最初の10件のみ表示
            print(f"   {talent}")
        if len(skipped_talents) > 10:
            print(f"   ... 他{len(skipped_talents) - 10}件")

    return True

async def main():
    try:
        await analyze_skipped_talents()
        return True
    except Exception as e:
        print(f"❌ エラー: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)