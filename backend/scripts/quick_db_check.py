#!/usr/bin/env python3
"""
簡易DB調査スクリプト - 既存のTPRインポーターを利用
"""
import asyncio
import sys
from pathlib import Path

# 既存のTPRインポーターのコードを流用
sys.path.append(str(Path(__file__).parent.parent))

# 既存のupdate_tpr_with_name_matching.pyからインポート
import os
os.chdir(Path(__file__).parent.parent)

from scripts.update_tpr_with_name_matching import TPRImporter

async def quick_db_check():
    """簡易DB調査"""
    importer = TPRImporter()

    print("=" * 80)
    print("🔍 データベース内タレント名調査（簡易版）")
    print("=" * 80)

    # タレント名マッピングを読み込み
    await importer.load_talent_mapping()

    print(f"\n📊 読み込まれたタレント数: {len(importer.talent_map)}")

    # 失敗したタレント名を調査
    failed_names = [
        "B'z",
        "[ALEXANDROS]",
        "SAKURA（宮脇咲良/LE SSERAFIM）",
        "ØMI（登坂広臣（三代目 J SOUL BROTHERS））",
        "スピッツ",
        "EXILE"
    ]

    print(f"\n🔍 DB内での名前検索結果:")
    print("-" * 50)

    for csv_name in failed_names:
        print(f"\nCSV名: \"{csv_name}\"")

        # 完全一致チェック
        if csv_name in importer.talent_map:
            account_id = importer.talent_map[csv_name]
            print(f"  ✅ 完全一致: account_id = {account_id}")
        else:
            print(f"  ❌ 完全一致なし")

            # 部分マッチを探す
            partial_matches = []
            for db_name in importer.talent_map.keys():
                if any(word in db_name.lower() for word in csv_name.lower().split() if len(word) > 2):
                    partial_matches.append((db_name, importer.talent_map[db_name]))

            if partial_matches:
                print(f"  🔍 部分マッチ候補:")
                for db_name, account_id in partial_matches[:3]:  # 上位3件
                    print(f"    ID {account_id}: \"{db_name}\"")
            else:
                print(f"  ❌ 部分マッチも見つからず")

    # 実際に手動マッピングがどう動作するかテスト
    print(f"\n🧪 手動マッピング動作テスト:")
    print("-" * 40)

    from scripts.talent_name_mapping_dictionary import get_manual_mapping

    for csv_name in failed_names:
        manual_result = get_manual_mapping(csv_name)
        if manual_result:
            if manual_result in importer.talent_map:
                account_id = importer.talent_map[manual_result]
                print(f"CSV:\"{csv_name}\" → 手動:\"{manual_result}\" → ✅ DB発見: ID {account_id}")
            else:
                print(f"CSV:\"{csv_name}\" → 手動:\"{manual_result}\" → ❌ DB未発見")
        else:
            print(f"CSV:\"{csv_name}\" → 手動マッピングなし")

    print("\n" + "=" * 80)

if __name__ == "__main__":
    asyncio.run(quick_db_check())