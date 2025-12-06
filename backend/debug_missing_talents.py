#!/usr/bin/env python3
"""未発見タレント12件の詳細調査"""

import asyncio
import sys
import pandas as pd
import chardet
from pathlib import Path
import re
import unicodedata

sys.path.insert(0, str(Path(__file__).parent))
from sqlalchemy import text
from app.db.connection import init_db, get_session_maker

async def debug_missing_talents():
    """未発見タレント12件の具体的調査"""
    print("🔍 未発見タレント詳細調査開始")
    print("=" * 50)

    # データベース接続
    await init_db()
    session_maker = get_session_maker()

    # タレントマッピング構築
    async with session_maker() as session:
        result = await session.execute(text("""
            SELECT id, account_id, name, name_normalized
            FROM talents
            WHERE del_flag = 0
            ORDER BY account_id ASC
        """))
        talents = result.fetchall()

        talent_mapping = {}
        for talent in talents:
            talent_id, account_id, name, name_normalized = talent
            if name_normalized:
                talent_mapping[name_normalized] = talent_id

        print(f"📊 データベースタレントマッピング: {len(talent_mapping):,}件")

    # VRファイル分析
    vr_file = "/Users/lennon/projects/talent-casting-form/DB情報/【VR①】C列の人気度と、E～K列の各種イメージを採用する想定です/VR男性タレント_男性20～34_202507.csv"

    # エンコーディング検出
    with open(vr_file, 'rb') as f:
        raw_data = f.read(10000)
        result = chardet.detect(raw_data)
        encoding = 'shift_jis' if result['encoding'] in ['SHIFT_JIS', 'CP932'] else 'utf-8'

    print(f"📄 VRファイル: {Path(vr_file).name}")
    print(f"🔍 検出エンコーディング: {encoding}")

    # CSV読み込み
    df = pd.read_csv(vr_file, encoding=encoding, skiprows=4)
    print(f"📊 VRファイル行数: {len(df)}件")

    # 未発見タレントの特定
    missing_talents = []
    matched_count = 0

    def advanced_normalize_name(name):
        """高度正規化"""
        if pd.isna(name) or name is None:
            return None
        name = str(name)
        name = unicodedata.normalize('NFKC', name)
        name = re.sub(r'[−－─━ー−‐]', 'ー', name)
        name = re.sub(r'[Ａ-Ｚａ-ｚ０-９]', lambda x: chr(ord(x.group()) - 0xFEE0), name)
        name = re.sub(r'[\s\u3000\u00A0\u2000-\u200A\u2028\u2029\u202F\u205F\uFEFF]+', '', name)
        return name.strip()

    # 手動マッピングテーブル
    MANUAL_MAPPING = {
        'チョコレ−トプラネット': 'チョコレートプラネット',
        'ＤＡＩＧＯ': 'DAIGO',
        '所　ジョ−ジ': '所ジョージ',
        # 他の手動マッピングも含める
    }

    for index, row in df.iterrows():
        vr_name = row.get('タレント名')
        if pd.isna(vr_name):
            missing_talents.append(f"行{index+6}: <空白/NaN>")
            continue

        vr_name = str(vr_name).strip()
        normalized_vr = advanced_normalize_name(vr_name)

        # マッチング試行
        found = False
        match_type = ""

        # 1. 直接マッチ
        if normalized_vr and normalized_vr in talent_mapping:
            found = True
            match_type = "直接"

        # 2. 手動マッピング
        elif vr_name in MANUAL_MAPPING and MANUAL_MAPPING[vr_name] in talent_mapping:
            found = True
            match_type = "手動"

        if found:
            matched_count += 1
        else:
            missing_talents.append(f"行{index+6}: 「{vr_name}」 (正規化: 「{normalized_vr}」)")

    print(f"\n📊 分析結果:")
    print(f"   ✅ マッチ成功: {matched_count}件")
    print(f"   ❌ 未発見: {len(missing_talents)}件")

    if missing_talents:
        print(f"\n❌ 未発見タレント詳細 ({len(missing_talents)}件):")
        for i, talent in enumerate(missing_talents, 1):
            print(f"   {i:2d}. {talent}")

    return True

if __name__ == "__main__":
    asyncio.run(debug_missing_talents())