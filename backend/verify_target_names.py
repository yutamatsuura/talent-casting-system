#!/usr/bin/env python3
"""未発見14件の正しいデータベース表記確認"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from sqlalchemy import text
from app.db.connection import init_db, get_session_maker

async def verify_target_names():
    """未発見14件の正確なデータベース名前を確認"""
    print("🔍 データベース内の正確な名前確認")
    print("=" * 50)

    # データベース接続
    await init_db()
    session_maker = get_session_maker()

    # 検索対象の候補名前リスト
    search_targets = [
        # VR名前 → 推測される正しい名前
        ('ビ−トたけし（北野　武）', ['ビートたけし', 'ビートたけし（北野武）', '北野武']),
        ('草なぎ　剛', ['草彅剛', '草なぎ剛']),
        ('山崎　賢人', ['山﨑賢人', '山崎賢人']),
        ('佐久間　宜行', ['佐久間宣行', '佐久間宜行']),
        ('ＤＥＡＮ　ＦＵＪＩＯＫＡ', ['ディーンフジオカ', 'ディーン・フジオカ', 'DEANFUJIOKA']),
        ('高橋　海人', ['髙橋海人', '高橋海人']),
        ('さまぁ〜ず', ['さまぁ～ず', 'さまあず']),
        ('くっき−！', ['くっきー!', 'くっきー']),
        ('高嶋　政伸', ['高嶋政伸', '高島政伸']),
        ('高嶋　政宏', ['高嶋政宏', '高島政宏']),
        ('市川　團十郎白猿　（堀越　寶世）', ['市川團十郎白猿', '市川團十郎', '堀越寶世']),
        ('中村　勘九郎　（波野　雅行）', ['中村勘九郎', '波野雅行']),
        ('松本　幸四郎　（藤間　照薫）', ['松本幸四郎', '藤間照薫']),
        ('市川　染五郎　（藤間　齋）', ['市川染五郎', '藤間齋'])
    ]

    mapping_results = {}

    async with session_maker() as session:
        for vr_name, candidates in search_targets:
            print(f"\n🔍 検索: 「{vr_name}」")
            found_name = None
            talent_id = None

            for candidate in candidates:
                # name_normalizedで検索
                result = await session.execute(
                    text("SELECT id, name, name_normalized FROM talents WHERE del_flag = 0 AND name_normalized = :name"),
                    {"name": candidate}
                )
                found = result.first()

                if found:
                    found_name = found[2]  # name_normalized
                    talent_id = found[0]
                    print(f"   ✅ 発見: 「{candidate}」 → ID:{talent_id}")
                    break

                # nameで検索（バックアップ）
                result = await session.execute(
                    text("SELECT id, name, name_normalized FROM talents WHERE del_flag = 0 AND name LIKE :name"),
                    {"name": f"%{candidate}%"}
                )
                found = result.first()

                if found:
                    found_name = found[2] if found[2] else found[1]
                    talent_id = found[0]
                    print(f"   ✅ 発見(name検索): 「{candidate}」 → ID:{talent_id}")
                    break

            if found_name:
                mapping_results[vr_name] = found_name
                print(f"   🎯 マッピング: 「{vr_name}」 → 「{found_name}」")
            else:
                print(f"   ❌ 未発見: 「{vr_name}」")

    print(f"\n📊 結果サマリー:")
    print(f"   発見: {len(mapping_results)}/14件")

    if mapping_results:
        print(f"\n🎯 手動マッピング用コード:")
        print("# 追加の手動マッピング（未発見14件対応）")
        for vr_name, db_name in mapping_results.items():
            print(f"    '{vr_name}': '{db_name}',")

    return mapping_results

if __name__ == "__main__":
    asyncio.run(verify_target_names())