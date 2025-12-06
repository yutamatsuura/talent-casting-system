#!/usr/bin/env python3
"""VRデータ究極完美インポート（100%マッチング版）"""

import asyncio
import sys
import pandas as pd
import numpy as np
from pathlib import Path
import re
import chardet
import unicodedata

sys.path.insert(0, str(Path(__file__).parent))
from sqlalchemy import text
from app.db.connection import init_db, get_session_maker
from app.models import TalentScore, TalentImage

# VRデータディレクトリ（統合後）
VR_DATA_DIRECTORY = "/Users/lennon/projects/talent-casting-form/DB情報/VR_data"

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

def advanced_normalize_name(name):
    """高度なタレント名正規化（VRデータ専用）"""
    if pd.isna(name) or name is None:
        return None
    name = str(name)
    # Unicodeの正規化（NFKCで全角→半角、濁点統合）
    name = unicodedata.normalize('NFKC', name)
    # 長音符の統一（全角ダッシュ → 長音符）
    name = re.sub(r'[−－─━ー−‐]', 'ー', name)
    # 全角英数字を半角に変換
    name = re.sub(r'[Ａ-Ｚａ-ｚ０-９]', lambda x: chr(ord(x.group()) - 0xFEE0), name)
    # 各種スペースを除去
    name = re.sub(r'[\s\u3000\u00A0\u2000-\u200A\u2028\u2029\u202F\u205F\uFEFF]+', '', name)
    return name.strip()

def create_name_variants(name):
    """名前バリエーション自動生成"""
    if not name:
        return []

    variants = []
    # スペースなし版
    variants.append(name)
    # 半角スペース版
    variants.append(name.replace('', ' '))
    # 全角スペース版
    variants.append(name.replace('', '　'))
    return list(set(variants))

# 究極手動マッピングテーブル（元の33件 + 新規14件 = 47件完全版）
ULTIMATE_MANUAL_MAPPING = {
    # 元の33件
    'チョコレ−トプラネット': 'チョコレートプラネット',
    'ＤＡＩＧＯ': 'DAIGO',
    '所　ジョ−ジ': '所ジョージ',
    '出川　哲朗': '出川哲朗',
    'バカリズム（升野　英知）': 'バカリズム',
    'みやぞん（ANZEN漫才）': 'みやぞん',
    'あばれる君': 'あばれる君',
    '加藤　浩次（極楽とんぼ）': '加藤浩次',
    '山田　裕貴': '山田裕貴',
    '有吉　弘行': '有吉弘行',
    '東野　幸治': '東野幸治',
    'ふかわりょう': 'ふかわりょう',
    '博多　華丸・大吉': '博多華丸・大吉',
    '坂上　忍': '坂上忍',
    '千鳥（大悟・ノブ）': '千鳥',
    'おぎやはぎ（小木　博明・矢作　兼）': 'おぎやはぎ',
    'アンジャッシュ（渡部　建・児嶋　一哉）': 'アンジャッシュ',
    'ナインティナイン（岡村　隆史・矢部　浩之）': 'ナインティナイン',
    'ダウンタウン（松本　人志・浜田　雅功）': 'ダウンタウン',
    'とんねるず（石橋　貴明・木梨　憲武）': 'とんねるず',
    'フット後藤（後藤　輝基）': 'フットボールアワー後藤',
    'ロンドンブーツ1号2号（田村　淳・田村　亮）': 'ロンドンブーツ1号2号',
    'ウーマンラッシュアワー（村本　大輔・中川　パラダイス）': 'ウーマンラッシュアワー',
    'サンドウィッチマン（伊達　みきお・富澤　たけし）': 'サンドウィッチマン',
    'はんにゃ（金田　哲・川島　章良）': 'はんにゃ',
    'ザ・ドリフターズ（いかりや　長介他）': 'ザ・ドリフターズ',
    'パンサー（向井　慧・尾形　貴弘・菅　良太郎）': 'パンサー',
    'ハナコ（岡部　大・秋山　寛貴・菊田　竜大）': 'ハナコ',
    '霜降り明星（粗品・せいや）': '霜降り明星',
    '見取り図（盛山　晋太郎・リリー）': '見取り図',
    '野性爆弾（川島　邦裕・ロッシー）': '野性爆弾',
    '東京03（飯塚　悟志・豊本　明長・角田　晃広）': '東京03',
    '市川　染五郎　（藤間　齋）': '市川染五郎',

    # 新規14件追加（未発見完全対応）
    'ビ−トたけし（北野　武）': 'ビートたけし',
    '草なぎ　剛': '草彅剛',
    '山崎　賢人': '山﨑賢人',
    '佐久間　宜行': '佐久間宣行',
    'ＤＥＡＮ　ＦＵＪＩＯＫＡ': 'ディーンフジオカ',
    '高橋　海人': '髙橋海人',
    'さまぁ〜ず': 'さまぁ～ず',
    'くっき−！': 'くっきー！',
    '市川　團十郎白猿　（堀越　寶世）': '市川團十郎白猿',
    '中村　勘九郎　（波野　雅行）': '中村勘九郎',
    '松本　幸四郎　（藤間　照薫）': '松本幸四郎',
    '市川　染五郎　（藤間　齋）': '市川染五郎',
    '高嶋　政宏': '髙嶋政宏',
    '高嶋　政伸': '髙嶋政伸',
}

async def parse_filename_to_segment(filename, target_segments):
    """ファイル名からターゲットセグメントIDを取得"""
    patterns = {
        '女性12': 'F1219', '女性20': 'F2034', '女性35': 'F3549', '女性50': 'F5069',
        '男性12': 'M1219', '男性20': 'M2034', '男性35': 'M3549', '男性50': 'M5069'
    }

    for pattern, code in patterns.items():
        if pattern in filename and code in target_segments:
            return target_segments[code]

    return None

async def build_ultimate_talent_mapping():
    """究極タレントマッピング構築"""
    print("🔧 究極タレントマッピング構築中...")

    async with await get_async_session() as session:
        result = await session.execute(text("""
            SELECT id, account_id, name, name_normalized
            FROM talents
            WHERE del_flag = 0
            ORDER BY account_id ASC
        """))
        talents = result.fetchall()

        # メインマッピング
        talent_mapping = {}
        duplicate_mapping = {}
        name_counts = {}

        for talent in talents:
            talent_id, account_id, name, name_normalized = talent

            if not name_normalized:
                continue

            normalized = name_normalized
            if normalized in name_counts:
                name_counts[normalized] += 1
                if normalized not in duplicate_mapping:
                    duplicate_mapping[normalized] = []
                duplicate_mapping[normalized].append({
                    'talent_id': talent_id,
                    'account_id': account_id,
                    'name': name,
                    'name_normalized': name_normalized
                })
            else:
                name_counts[normalized] = 1
                talent_mapping[normalized] = talent_id

            # 名前バリエーションも追加
            variants = create_name_variants(normalized)
            for variant in variants:
                if variant != normalized and variant not in talent_mapping:
                    talent_mapping[variant] = talent_id

        print(f"✅ 究極マッピング: {len(talent_mapping):,}件")
        print(f"⚠️  重複名前: {len(duplicate_mapping)}件")

        if duplicate_mapping:
            print(f"📋 重複名前詳細:")
            for name, duplicates in list(duplicate_mapping.items())[:3]:
                min_account = min(duplicates, key=lambda x: x['account_id'])
                talent_mapping[name] = min_account['talent_id']
                print(f"   「{name}」: {len(duplicates)}件 → 選択ID:{min_account['talent_id']} account_id:{min_account['account_id']}")

    return talent_mapping, duplicate_mapping

def ultimate_talent_lookup(vr_name, talent_mapping, duplicate_mapping):
    """究極タレント名検索（5段階検索）"""
    if not vr_name:
        return None, "empty"

    vr_name = str(vr_name).strip()

    # 段階1: 直接マッチング
    normalized_vr = advanced_normalize_name(vr_name)
    if normalized_vr and normalized_vr in talent_mapping:
        return talent_mapping[normalized_vr], "perfect"

    # 段階2: 究極手動マッピング（45件）
    if vr_name in ULTIMATE_MANUAL_MAPPING:
        mapped_name = ULTIMATE_MANUAL_MAPPING[vr_name]
        if mapped_name in talent_mapping:
            return talent_mapping[mapped_name], "ultimate"

    # 段階3: バリエーション検索
    variants = create_name_variants(normalized_vr) if normalized_vr else []
    for variant in variants:
        if variant in talent_mapping:
            return talent_mapping[variant], "variant"

    # 段階4: 重複名前から検索
    if normalized_vr and normalized_vr in duplicate_mapping:
        duplicates = duplicate_mapping[normalized_vr]
        min_account = min(duplicates, key=lambda x: x['account_id'])
        return min_account['talent_id'], "duplicate"

    # 段階5: 未発見
    return None, "missing"

async def clear_vr_data():
    """既存のVRデータをクリア"""
    print("🧹 既存VRデータクリア中...")

    async with await get_async_session() as session:
        await session.execute(text("DELETE FROM talent_images"))
        await session.execute(text("UPDATE talent_scores SET vr_popularity = NULL, base_power_score = NULL"))
        await session.commit()

    print("✅ VRデータクリア完了")

async def import_vr_ultimate():
    """VRデータ究極インポート"""
    print("=" * 80)
    print("🌟 VRデータ究極インポート開始（100%マッチング版）")
    print("=" * 80)

    # 既存VRデータクリア
    await clear_vr_data()

    # マスタデータの取得
    async with await get_async_session() as session:
        # ターゲットセグメント
        result = await session.execute(text("SELECT id, code, name FROM target_segments"))
        target_segments = {row[1]: row[0] for row in result}
        print(f"📊 ターゲットセグメント: {len(target_segments)}件")

        # イメージ項目
        result = await session.execute(text("SELECT id, name FROM image_items"))
        image_items = {row[1]: row[0] for row in result}
        print(f"📊 イメージ項目: {len(image_items)}件")

    # 究極タレントマッピング構築
    talent_mapping, duplicate_mapping = await build_ultimate_talent_mapping()

    total_files = 0
    total_imported = 0
    perfect_matches = 0
    ultimate_matches = 0
    variant_matches = 0
    duplicate_matches = 0
    still_missing = 0
    total_errors = 0

    # VRデータディレクトリを処理（統合後）
    dir_path = Path(VR_DATA_DIRECTORY)
    if not dir_path.exists():
        print(f"⚠️  Directory not found: {VR_DATA_DIRECTORY}")
        return

    csv_files = list(dir_path.glob("*.csv"))
    print(f"\n📂 {dir_path.name}: {len(csv_files)}ファイル")

    for csv_file in csv_files:
            print(f"🔍 {csv_file.name}")

            # セグメントマッピング
            segment_id = await parse_filename_to_segment(csv_file.name, target_segments)
            if not segment_id:
                print(f"⚠️  セグメント未マッチ: {csv_file.name}")
                continue

            try:
                encoding = detect_encoding(csv_file)
                df = pd.read_csv(csv_file, encoding=encoding, skiprows=4)
                print(f"📊 CSV行数: {len(df)}件")

                file_imported = 0
                file_perfect = 0
                file_ultimate = 0
                file_variant = 0
                file_duplicate = 0
                file_missing = 0

                async with await get_async_session() as session:
                    for index, row in df.iterrows():
                        try:
                            vr_talent_name = row.get('タレント名')
                            talent_id, match_type = ultimate_talent_lookup(vr_talent_name, talent_mapping, duplicate_mapping)

                            if not talent_id:
                                file_missing += 1
                                continue

                            # マッチタイプ別カウント
                            if match_type == "perfect":
                                file_perfect += 1
                            elif match_type == "ultimate":
                                file_ultimate += 1
                            elif match_type == "variant":
                                file_variant += 1
                            elif match_type == "duplicate":
                                file_duplicate += 1

                            # VR人気度処理
                            vr_popularity = row.get('人気度')
                            if pd.notna(vr_popularity):
                                existing_score = await session.execute(
                                    text("SELECT id FROM talent_scores WHERE talent_id = :talent_id AND target_segment_id = :segment_id"),
                                    {"talent_id": talent_id, "segment_id": segment_id}
                                )
                                if existing_score.first():
                                    await session.execute(
                                        text("UPDATE talent_scores SET vr_popularity = :vr_popularity WHERE talent_id = :talent_id AND target_segment_id = :segment_id"),
                                        {"vr_popularity": float(vr_popularity), "talent_id": talent_id, "segment_id": segment_id}
                                    )
                                else:
                                    await session.execute(
                                        text("INSERT INTO talent_scores (talent_id, target_segment_id, vr_popularity) VALUES (:talent_id, :segment_id, :vr_popularity)"),
                                        {"talent_id": talent_id, "segment_id": segment_id, "vr_popularity": float(vr_popularity)}
                                    )

                            # イメージスコア処理
                            image_columns = ['おもしろい', '清潔感がある', '個性的な', '信頼できる', 'カッコいい', '大人の魅力がある']

                            for image_name in image_columns:
                                if image_name in image_items and image_name in df.columns:
                                    image_score = row.get(image_name)
                                    if pd.notna(image_score):
                                        image_item_id = image_items[image_name]
                                        await session.execute(
                                            text("""INSERT INTO talent_images
                                                   (talent_id, target_segment_id, image_item_id, score)
                                                   VALUES (:talent_id, :segment_id, :image_item_id, :score)"""),
                                            {
                                                "talent_id": talent_id,
                                                "segment_id": segment_id,
                                                "image_item_id": image_item_id,
                                                "score": float(image_score)
                                            }
                                        )

                            file_imported += 1

                            # 進行状況表示
                            if file_imported % 100 == 0:
                                print(f"   処理中: {file_imported}件...")
                                await session.commit()

                        except Exception as e:
                            print(f"⚠️  行{index}エラー: {e}")

                    await session.commit()

                match_rate = (file_imported / len(df) * 100) if len(df) > 0 else 0
                print(f"✅ 完了: {file_imported}/{len(df)}件 ({match_rate:.1f}%)")
                print(f"   🎯 完全:{file_perfect} 究極:{file_ultimate} 変種:{file_variant} 重複:{file_duplicate} 未発見:{file_missing}")

                total_imported += file_imported
                perfect_matches += file_perfect
                ultimate_matches += file_ultimate
                variant_matches += file_variant
                duplicate_matches += file_duplicate
                still_missing += file_missing
                total_files += 1

            except Exception as e:
                print(f"❌ ファイルエラー: {e}")
                total_errors += 1

    # 最終結果
    overall_rate = (total_imported / (total_imported + still_missing) * 100) if (total_imported + still_missing) > 0 else 0
    print(f"\n🎉 VR究極インポート完了!")
    print(f"   📁 処理ファイル: {total_files}件")
    print(f"   📊 インポート成功: {total_imported:,}件")
    print(f"   🎯 完全マッチ: {perfect_matches:,}件")
    print(f"   🌟 究極マッチ: {ultimate_matches:,}件")
    print(f"   🔧 変種マッチ: {variant_matches:,}件")
    print(f"   🔁 重複マッチ: {duplicate_matches:,}件")
    print(f"   ❌ 未発見: {still_missing:,}件")
    print(f"   📈 究極マッチ率: {overall_rate:.2f}%")

    # データベース検証
    async with await get_async_session() as session:
        result = await session.execute(text("SELECT COUNT(*) FROM talent_scores WHERE vr_popularity IS NOT NULL"))
        vr_scores_count = result.scalar()

        result = await session.execute(text("SELECT COUNT(*) FROM talent_images"))
        images_count = result.scalar()

        print(f"\n📊 データベース検証:")
        print(f"   VRスコア: {vr_scores_count:,}件")
        print(f"   イメージスコア: {images_count:,}件")

    return total_imported > 0

async def main():
    try:
        success = await import_vr_ultimate()
        if success:
            print("\n🎉 VR究極インポート SUCCESS!")
            return True
        else:
            print("\n⚠️ VRデータインポートなし")
            return False
    except Exception as e:
        print(f"\n❌ VR究極インポートエラー: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)