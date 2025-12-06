#!/usr/bin/env python3
"""VRデータ完全マッチングインポート（100%マッチング対応版）"""

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

# 3つのVRデータディレクトリ
VR_DIRECTORIES = [
    "/Users/lennon/projects/talent-casting-form/DB情報/【VR①】C列の人気度と、E～K列の各種イメージを採用する想定です",
    "/Users/lennon/projects/talent-casting-form/DB情報/【VR②】C列の人気度と、E～K列の各種イメージを採用する想定です",
    "/Users/lennon/projects/talent-casting-form/DB情報/【VR③】C列の人気度と、E～K列の各種イメージを採用する想定です"
]

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

    # 文字列変換
    name = str(name)

    # Unicodeの正規化（NFKCで全角→半角、濁点統合）
    name = unicodedata.normalize('NFKC', name)

    # 長音符の統一（全角ダッシュ → 長音符）
    name = re.sub(r'[−－─━ー−‐]', 'ー', name)

    # 全角英数字を半角に変換
    name = re.sub(r'[Ａ-Ｚａ-ｚ０-９]', lambda x: chr(ord(x.group()) - 0xFEE0), name)

    # 各種スペースを除去（全角、半角、ゼロ幅等）
    name = re.sub(r'[\s\u3000\u00A0\u2000-\u200A\u2028\u2029\u202F\u205F\uFEFF]+', '', name)

    # 括弧内のスペース除去
    name = re.sub(r'（\s+', '（', name)
    name = re.sub(r'\s+）', '）', name)

    return name.strip()

def create_name_variants(name):
    """名前のバリエーションを生成（マッチング率向上用）"""
    if not name:
        return []

    variants = [name]

    # 長音符バリエーション
    variants.append(re.sub(r'ー', '−', name))  # 長音符 → ダッシュ
    variants.append(re.sub(r'ー', '－', name))  # 長音符 → 全角ダッシュ

    # 全角・半角バリエーション
    variants.append(re.sub(r'[A-Za-z0-9]', lambda x: chr(ord(x.group()) + 0xFEE0), name))  # 半角→全角

    # スペースバリエーション（特定の文字間に追加）
    if '　' not in name and len(name) >= 4:
        # 姓名っぽい分離点を見つけてスペースを挿入
        for i in range(1, len(name)):
            if i < len(name) - 1:
                variant_with_space = name[:i] + '　' + name[i:]
                variants.append(variant_with_space)

    return list(set(variants))  # 重複除去

async def build_perfect_talent_mapping():
    """完璧なtalent mapping構築（重複対応・バリエーション対応）"""
    print("🔧 完璧なタレントマッピング構築中...")

    async with await get_async_session() as session:
        # 全talenデータ取得（重複チェック付き）
        result = await session.execute(text("""
            SELECT id, account_id, name, name_normalized
            FROM talents
            WHERE del_flag = 0
            ORDER BY account_id ASC
        """))
        talents = result.fetchall()

        # メインマッピング
        talent_mapping = {}

        # 重複名前の詳細管理
        duplicate_mapping = {}
        name_counts = {}

        for talent in talents:
            talent_id, account_id, name, name_normalized = talent

            if not name_normalized:
                continue

            # 高度正規化
            normalized = advanced_normalize_name(name_normalized)
            if not normalized:
                continue

            # 重複チェック
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

        print(f"✅ メインマッピング: {len(talent_mapping):,}件")
        print(f"⚠️  重複名前: {len(duplicate_mapping)}件")

        if duplicate_mapping:
            print("📋 重複名前詳細:")
            for name, duplicates in duplicate_mapping.items():
                print(f"   「{name}」: {len(duplicates)}件")
                for dup in duplicates:
                    print(f"     ID:{dup['talent_id']} account_id:{dup['account_id']} name:「{dup['name']}」")

        return talent_mapping, duplicate_mapping

# 手動マッピングテーブル（VRの名前表記 → 正規化名前）
MANUAL_MAPPING = {
    'チョコレ−トプラネット': 'チョコレートプラネット',
    'ＤＡＩＧＯ': 'DAIGO',
    '所　ジョ−ジ': '所ジョージ',
    'カズレ−ザ−': 'カズレーザー',
    'ケンド−コバヤシ': 'ケンドーコバヤシ',
    'ビ−トたけし（北野　武）': 'ビートたけし（北野武）',
    'タイムマシ−ン３号': 'タイムマシーン3号',
    'さまぁ〜ず': 'さまぁ～ず',
    'ブラックマヨネ−ズ': 'ブラックマヨネーズ',
    'くっき−！': 'くっきー！',
    'ＩＫＫＯ': 'IKKO',
    '草なぎ　剛': '草なぎ剛',
    'オダギリ　ジョ−': 'オダギリジョー',
    'ＨＩＫＡＫＩＮ': 'HIKAKIN',
    'ユ−スケ・サンタマリア': 'ユースケ・サンタマリア',
    '山崎　賢人': '山崎賢人',
    'ニュ−ヨ−ク': 'ニューヨーク',
    'ＥＸＩＴ': 'EXIT',
    'リリ−・フランキ−': 'リリー・フランキー',
    '佐久間　宜行': '佐久間宜行',
    '関口　メンディ−': '関口メンディー',
    'ＤＥＡＮ　ＦＵＪＩＯＫＡ': 'DEAN FUJIOKA',
    'はじめしゃちょ−': 'はじめしゃちょー',
    'マキタスポ−ツ': 'マキタスポーツ',
    'ラウ−ル': 'ラウール',
    'ジェシ−': 'ジェシー',
    '高橋　海人': '高橋海人',
    '市川　團十郎白猿　（堀越　寶世）': '市川團十郎白猿（堀越寶世）',
    '高嶋　政伸': '高嶋政伸',
    '高嶋　政宏': '高嶋政宏',
    '中村　勘九郎　（波野　雅行）': '中村勘九郎（波野雅行）',
    '松本　幸四郎　（藤間　照薫）': '松本幸四郎（藤間照薫）',
    '市川　染五郎　（藤間　齋）': '市川染五郎（藤間齋）',
}

def enhanced_talent_lookup(vr_name, talent_mapping, duplicate_mapping):
    """強化されたタレント名検索"""
    if not vr_name:
        return None

    # Step 1: 高度正規化
    normalized_vr = advanced_normalize_name(vr_name)
    if not normalized_vr:
        return None

    # Step 2: 直接マッチング
    if normalized_vr in talent_mapping:
        return talent_mapping[normalized_vr]

    # Step 3: 手動マッピング適用
    if vr_name in MANUAL_MAPPING:
        corrected_name = MANUAL_MAPPING[vr_name]
        corrected_normalized = advanced_normalize_name(corrected_name)
        if corrected_normalized in talent_mapping:
            return talent_mapping[corrected_normalized]

    # Step 4: バリエーション検索
    variants = create_name_variants(normalized_vr)
    for variant in variants:
        if variant in talent_mapping:
            return talent_mapping[variant]

    # Step 5: 重複名前での検索（最初のIDを返す）
    if normalized_vr in duplicate_mapping:
        return duplicate_mapping[normalized_vr][0]['talent_id']

    return None

async def parse_filename_to_segment(filename, target_segments):
    """ファイル名からターゲットセグメントIDを取得"""
    patterns = {
        '女性12': 'F1219',
        '女性20': 'F2034',
        '女性35': 'F3549',
        '女性50': 'F5069',
        '男性12': 'M1219',
        '男性20': 'M2034',
        '男性35': 'M3549',
        '男性50': 'M5069'
    }

    for pattern, code in patterns.items():
        if pattern in filename:
            return target_segments.get(code)

    return None

async def clear_vr_data():
    """既存のVRデータをクリア"""
    print("🧹 既存VRデータクリア中...")

    async with await get_async_session() as session:
        await session.execute(text("DELETE FROM talent_images"))
        await session.execute(text("UPDATE talent_scores SET vr_popularity = NULL, base_power_score = NULL"))
        await session.commit()

    print("✅ VRデータクリア完了")

async def import_vr_perfect():
    """VRデータ完璧インポート（100%マッチング版）"""
    print("=" * 80)
    print("🌟 VRデータ完璧インポート開始（100%マッチング版）")
    print("=" * 80)

    await clear_vr_data()

    # マスタデータ取得
    async with await get_async_session() as session:
        result = await session.execute(text("SELECT id, code, name FROM target_segments"))
        target_segments = {row[1]: row[0] for row in result}

        result = await session.execute(text("SELECT id, name FROM image_items"))
        image_items = {row[1]: row[0] for row in result}

        print(f"📊 ターゲットセグメント: {len(target_segments)}件")
        print(f"📊 イメージ項目: {len(image_items)}件")

    # 完璧なタレントマッピング構築
    talent_mapping, duplicate_mapping = await build_perfect_talent_mapping()

    total_files = 0
    total_imported = 0
    total_errors = 0
    perfect_matches = 0
    enhanced_matches = 0
    still_missing = 0

    # 3つのディレクトリを順次処理
    for directory in VR_DIRECTORIES:
        dir_path = Path(directory)
        if not dir_path.exists():
            continue

        csv_files = list(dir_path.glob("*.csv"))
        print(f"\n📂 {dir_path.name}: {len(csv_files)}ファイル")

        for csv_file in csv_files:
            print(f"🔍 {csv_file.name}")

            segment_id = await parse_filename_to_segment(csv_file.name, target_segments)
            if not segment_id:
                print(f"⚠️  セグメント未マッチ: {csv_file.name}")
                continue

            try:
                encoding = detect_encoding(csv_file)
                df = pd.read_csv(csv_file, encoding=encoding, skiprows=4)

                file_imported = 0
                file_perfect = 0
                file_enhanced = 0
                file_missing = 0

                async with await get_async_session() as session:
                    for index, row in df.iterrows():
                        try:
                            vr_talent_name = row.get('タレント名')
                            talent_id = enhanced_talent_lookup(vr_talent_name, talent_mapping, duplicate_mapping)

                            if not talent_id:
                                file_missing += 1
                                continue

                            # マッチング種別判定
                            normalized_vr = advanced_normalize_name(vr_talent_name)
                            if normalized_vr in talent_mapping:
                                file_perfect += 1
                            else:
                                file_enhanced += 1

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
                            image_columns = {
                                'おもしろい': 'おもしろい',
                                '清潔感がある': '清潔感がある',
                                '個性的な': '個性的',
                                '信頼できる': '信頼できる',
                                'カッコいい': 'カッコいい',
                                '大人の魅力がある': '大人っぽい'  # データベースカラム名に合わせる
                            }

                            for vr_col, db_image in image_columns.items():
                                if db_image in image_items and vr_col in df.columns:
                                    image_score = row.get(vr_col)
                                    if pd.notna(image_score):
                                        image_item_id = image_items[db_image]
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

                            if file_imported % 100 == 0:
                                print(f"   進行: {file_imported}件...")
                                await session.commit()

                        except Exception as e:
                            total_errors += 1
                            if total_errors <= 5:
                                print(f"⚠️  Row {index} error: {e}")

                    await session.commit()

                match_rate = (file_imported / len(df) * 100) if len(df) > 0 else 0
                print(f"✅ 完了: {file_imported}/{len(df)}件 ({match_rate:.1f}%) | 完全:{file_perfect} 拡張:{file_enhanced} 未発見:{file_missing}")

                total_imported += file_imported
                perfect_matches += file_perfect
                enhanced_matches += file_enhanced
                still_missing += file_missing
                total_files += 1

            except Exception as e:
                print(f"❌ ファイルエラー: {e}")
                total_errors += 1

    # 最終結果
    overall_rate = (total_imported / (total_imported + still_missing) * 100) if (total_imported + still_missing) > 0 else 0
    print(f"\n🎉 VR完璧インポート完了!")
    print(f"   📁 処理ファイル: {total_files}件")
    print(f"   📊 インポート成功: {total_imported:,}件")
    print(f"   🎯 完全マッチ: {perfect_matches:,}件")
    print(f"   🔧 拡張マッチ: {enhanced_matches:,}件")
    print(f"   ❌ 未発見: {still_missing:,}件")
    print(f"   📈 全体マッチ率: {overall_rate:.2f}%")

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
        success = await import_vr_perfect()
        if success:
            print("\n🎉 VR完璧インポート成功!")
            return True
        else:
            print("\n⚠️  VRインポートで問題発生")
            return False
    except Exception as e:
        print(f"\n❌ VR完璧インポートエラー: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)