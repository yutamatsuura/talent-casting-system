#!/usr/bin/env python3
"""
指定されたaccount_idの存在確認
"""
import asyncio
import sys
from pathlib import Path
import os

# 既存のTPRインポーターのコードを流用
os.chdir(Path(__file__).parent.parent)
from scripts.update_tpr_with_name_matching import TPRImporter

async def check_account_ids():
    """指定されたaccount_idの存在確認"""
    importer = TPRImporter()

    print("=" * 80)
    print("🔍 account_id存在確認")
    print("=" * 80)

    # タレント名マッピングを読み込み
    await importer.load_talent_mapping()

    # 逆引き辞書を作成（account_id -> name）
    account_id_to_name = {account_id: name for name, account_id in importer.talent_map.items()}

    # 確認したいaccount_id
    check_ids = {
        1802: "B'z",
        2726: "[ALEXANDROS]",
        404: "SAKURA（宮脇咲良/LE SSERAFIM）",
        274: "ØMI（登坂広臣（三代目 J SOUL BROTHERS））",
        647: "イチロー（成功例）",
        482: "ヒカキン（成功例）"
    }

    print(f"\n📊 読み込まれたタレント数: {len(importer.talent_map)}")
    print("\n🔍 account_id存在確認結果:")
    print("-" * 50)

    for account_id, expected_name in check_ids.items():
        if account_id in account_id_to_name:
            actual_name = account_id_to_name[account_id]
            print(f"ID {account_id}: ✅ 存在")
            print(f"  実際の名前: \"{actual_name}\"")
            print(f"  期待していた名前: \"{expected_name}\"")
            if actual_name != expected_name:
                print(f"  ⚠️  名前が異なります")
            print()
        else:
            print(f"ID {account_id}: ❌ 存在しません")
            print(f"  期待していた名前: \"{expected_name}\"")
            print()

    # 部分マッチ検索
    print("🔍 部分マッチ検索:")
    print("-" * 30)
    search_keywords = ["B'z", "ALEXANDROS", "SAKURA", "ØMI", "登坂", "宮脇"]

    for keyword in search_keywords:
        matches = []
        for name, account_id in importer.talent_map.items():
            if keyword.lower() in name.lower():
                matches.append((account_id, name))

        print(f"\nキーワード '{keyword}':")
        if matches:
            for account_id, name in matches[:3]:  # 上位3件
                print(f"  ID {account_id}: \"{name}\"")
        else:
            print(f"  ❌ 該当なし")

    print("\n" + "=" * 80)

if __name__ == "__main__":
    asyncio.run(check_account_ids())