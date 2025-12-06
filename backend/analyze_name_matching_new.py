#!/usr/bin/env python3
"""
名前マッチングの詳細分析
"""
import asyncio
import asyncpg
import os
import pandas as pd
import chardet
from glob import glob
import unicodedata
import re

def advanced_normalize_name(name):
    """高度なタレント名正規化（引継ぎドキュメントのロジック）"""
    if pd.isna(name) or name is None:
        return None

    name = str(name)

    # Unicode正規化（NFKC: 全角→半角、濁点統合）
    name = unicodedata.normalize('NFKC', name)

    # 長音符統一（各種ダッシュ → ー）
    name = re.sub(r'[−－─━ー−‐]', 'ー', name)

    # 全角英数字 → 半角
    name = re.sub(r'[Ａ-Ｚａ-ｚ０-９]',
                  lambda x: chr(ord(x.group()) - 0xFEE0), name)

    # 各種スペース除去
    name = re.sub(r'[\s\u3000\u00A0\u2000-\u200A\u2028\u2029\u202F\u205F\uFEFF]+',
                  '', name)

    return name.strip()

async def analyze_name_matching():
    """名前マッチングの詳細分析"""

    database_url = os.getenv('DATABASE_URL')
    conn = await asyncpg.connect(database_url)

    try:
        print("=== 名前マッチング詳細分析 ===")
        print()

        # 1. 未マッチタレントの原因分析（サンプル）
        sample_unmatched_names = [
            '中島　裕翔',
            '光石　研',
            '井森　美幸',
            '岸井　ゆきの',
            'ＤＥＡＮ　ＦＵＪＩＯＫＡ',
            '池田　エライザ',
            '関水　渚',
            '森　七菜',
            '秋山　竜次'
        ]

        print("1. サンプル未マッチタレントの分析:")
        for i, vr_name in enumerate(sample_unmatched_names, 1):
            print(f"\n{i}. VR表記: '{vr_name}'")

            # 正規化
            normalized = advanced_normalize_name(vr_name)
            print(f"   正規化後: '{normalized}'")

            # データベース内での正確なマッチング確認
            exact_match = await conn.fetchrow(
                "SELECT name, account_id FROM talents WHERE name_normalized = $1 AND del_flag = 0",
                normalized
            )

            if exact_match:
                print(f"   ✅ 正規化マッチ発見: '{exact_match['name']}' (ID: {exact_match['account_id']})")
            else:
                # 部分マッチング検索
                partial_matches = await conn.fetch("""
                    SELECT name, name_normalized, account_id
                    FROM talents
                    WHERE del_flag = 0 AND (
                        name ILIKE $1 OR
                        name ILIKE $2 OR
                        name_normalized ILIKE $3
                    )
                    LIMIT 5
                """,
                f"%{vr_name.replace('　', '')}%",
                f"%{vr_name.replace('　', ' ')}%",
                f"%{normalized}%")

                if partial_matches:
                    print("   🔍 部分マッチ候補:")
                    for pm in partial_matches:
                        similarity = "高" if pm['name'].replace(' ', '').replace('　', '') == vr_name.replace(' ', '').replace('　', '') else "中"
                        print(f"     - '{pm['name']}' → '{pm['name_normalized']}' (類似度: {similarity})")
                else:
                    print("   ❌ マッチなし - データベースに存在しない可能性")

        # 2. マッピング拡張の必要性確認
        print(f"\n2. マッピング拡張の評価:")

        # データベースのタレント総数
        total_db_talents = await conn.fetchval("SELECT COUNT(*) FROM talents WHERE del_flag = 0")

        # talent_scoresに存在するユニークタレント数
        processed_talents = await conn.fetchval("SELECT COUNT(DISTINCT talent_id) FROM talent_scores")

        print(f"   データベース総タレント数: {total_db_talents:,}人")
        print(f"   VR処理済みタレント数: {processed_talents:,}人")
        print(f"   処理率: {(processed_talents/total_db_talents)*100:.1f}%")

        # 3. 緊急対応の方針提案
        print(f"\n=== 対応方針の提案 ===")
        print("🚨 936人の未処理は大規模問題です")
        print()
        print("対応選択肢:")
        print("A. 大規模マッピング拡張 - 名前正規化ルールの大幅改善")
        print("B. VR処理スクリプトのロジック修正 - 5段階マッチングの改良")
        print("C. 手動マッピング - 重要タレントのみ優先対応")
        print()
        print("推奨: A + C の組み合わせ")

    except Exception as e:
        print(f"❌ エラー: {e}")
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(analyze_name_matching())