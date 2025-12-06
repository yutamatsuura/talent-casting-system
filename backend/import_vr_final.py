#!/usr/bin/env python3
"""VRデータ完全インポート（全16ファイル+構造修正対応版）"""

import asyncio
import sys
import pandas as pd
import numpy as np
from pathlib import Path
import re
import chardet

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
        raw_data = file.read(10000)  # 最初の10KB読み取り
        result = chardet.detect(raw_data)
        encoding = result['encoding']

        # 日本語ファイルの一般的なパターン
        if encoding in ['SHIFT_JIS', 'CP932', 'Shift_JIS']:
            return 'shift_jis'
        elif encoding in ['UTF-8', 'utf-8']:
            return 'utf-8'
        else:
            # デフォルトで試す順序
            return 'shift_jis'

def parse_filename_to_segment(filename):
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
            return code

    print(f"⚠️  Unknown segment pattern in filename: {filename}")
    return None

def normalize_name(name):
    """タレント名の正規化（スペース除去）"""
    if pd.isna(name) or name is None:
        return None
    normalized = re.sub(r'[\s\u3000\u00A0\u2000-\u200A\u2028\u2029\u202F\u205F]+', '', str(name))
    return normalized.strip()

async def clear_vr_data():
    """既存のVRデータをクリア"""
    print("🧹 Clearing existing VR data...")

    async with await get_async_session() as session:
        # talent_imagesテーブル完全クリア（VRイメージデータ）
        await session.execute(text("DELETE FROM talent_images"))

        # talent_scoresのVR関連カラムのみNULLに設定
        await session.execute(text("UPDATE talent_scores SET vr_popularity = NULL, base_power_score = NULL"))

        await session.commit()

    print("✅ VR data cleared")

async def import_vr_complete():
    """全16ファイルのVRデータを完全インポート"""
    print("=" * 80)
    print("🚀 Starting Complete VR data import (Final Version - Structure Fixed)...")
    print("=" * 80)

    # 既存VRデータクリア
    await clear_vr_data()

    # マスタデータの取得
    async with await get_async_session() as session:
        # ターゲットセグメント
        result = await session.execute(text("SELECT id, code, name FROM target_segments"))
        target_segments = {row[1]: row[0] for row in result}
        print(f"📊 Target segment mapping: {target_segments}")

        # イメージ項目
        result = await session.execute(text("SELECT id, name FROM image_items"))
        image_items = {row[1]: row[0] for row in result}
        print(f"📊 Image item mapping: {image_items}")

        # タレントマッピング
        result = await session.execute(text("SELECT id, account_id, name_normalized FROM talents"))
        talent_mapping = {}
        for row in result:
            if row[2]:  # name_normalizedが存在する場合
                talent_mapping[row[2]] = row[0]
        print(f"📊 Talent mapping: {len(talent_mapping)} talents available")

    total_files = 0
    total_imported = 0
    total_errors = 0

    # 3つのディレクトリを順次処理
    for directory in VR_DIRECTORIES:
        dir_path = Path(directory)
        if not dir_path.exists():
            print(f"⚠️  Directory not found: {directory}")
            continue

        csv_files = list(dir_path.glob("*.csv"))
        print(f"\n📂 Processing {len(csv_files)} files in {dir_path.name}")

        for csv_file in csv_files:
            print(f"🔍 Processing file: {csv_file.name}")

            # ファイル名からセグメントcode取得
            segment_code = parse_filename_to_segment(csv_file.name)
            if segment_code is None or segment_code not in target_segments:
                print(f"⚠️  Skipping file (unmapped segment): {csv_file.name} -> {segment_code}")
                continue

            segment_id = target_segments[segment_code]
            print(f"✅ Matched pattern '{segment_code}' to segment_id: {segment_id}")

            try:
                # エンコーディング自動検出
                encoding = detect_encoding(csv_file)
                print(f"🔍 Detected encoding: {encoding}")

                # CSVファイル読み込み（最初の4行をスキップして5行目をカラム名に）
                df = pd.read_csv(csv_file, encoding=encoding, skiprows=4)
                print(f"📊 CSV shape: {df.shape}")

                # カラム名確認
                print(f"🏷️  Columns: {list(df.columns)}")

                file_imported = 0
                file_errors = 0

                async with await get_async_session() as session:
                    for index, row in df.iterrows():
                        try:
                            # タレント名の正規化とマッピング
                            talent_name = normalize_name(row.get('タレント名'))
                            if not talent_name or talent_name not in talent_mapping:
                                continue

                            talent_id = talent_mapping[talent_name]

                            # VR人気度スコア処理
                            vr_popularity = row.get('人気度')
                            if pd.notna(vr_popularity):
                                # talent_scoresにVR人気度を挿入/更新
                                existing_score = await session.execute(
                                    text("SELECT id FROM talent_scores WHERE talent_id = :talent_id AND target_segment_id = :segment_id"),
                                    {"talent_id": talent_id, "segment_id": segment_id}
                                )
                                if existing_score.first():
                                    # 更新
                                    await session.execute(
                                        text("UPDATE talent_scores SET vr_popularity = :vr_popularity WHERE talent_id = :talent_id AND target_segment_id = :segment_id"),
                                        {"vr_popularity": float(vr_popularity), "talent_id": talent_id, "segment_id": segment_id}
                                    )
                                else:
                                    # 新規挿入
                                    await session.execute(
                                        text("INSERT INTO talent_scores (talent_id, target_segment_id, vr_popularity) VALUES (:talent_id, :segment_id, :vr_popularity)"),
                                        {"talent_id": talent_id, "segment_id": segment_id, "vr_popularity": float(vr_popularity)}
                                    )

                            # イメージスコア処理（実際のカラム名を使用）
                            image_columns = {
                                'おもしろい': 'おもしろい',
                                '清潔感がある': '清潔感がある',
                                '個性的な': '個性的な',
                                '信頼できる': '信頼できる',
                                'カッコいい': 'カッコいい',
                                '大人の魅力がある': '大人の魅力がある'
                            }

                            for image_name, csv_column in image_columns.items():
                                if image_name in image_items and csv_column in df.columns:
                                    image_score = row.get(csv_column)
                                    if pd.notna(image_score):
                                        image_item_id = image_items[image_name]

                                        # talent_imagesに挿入
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
                                print(f"   Processed: {file_imported} records...")
                                await session.commit()

                        except Exception as e:
                            file_errors += 1
                            if file_errors <= 3:  # 最初の3エラーのみ表示
                                print(f"⚠️  Row {index} error: {e}")

                    await session.commit()

                print(f"✅ File completed: {file_imported:,} imported, {file_errors} errors")
                total_imported += file_imported
                total_errors += file_errors
                total_files += 1

            except Exception as e:
                print(f"❌ File processing error: {e}")
                total_errors += 1

    # 最終結果
    print(f"\n🎉 VR Complete Import Finished!")
    print(f"   📁 Total files processed: {total_files}")
    print(f"   📊 Total imported: {total_imported:,} records")
    print(f"   ❌ Total errors: {total_errors}")

    # データベース検証
    async with await get_async_session() as session:
        # talent_scoresのVRデータ件数
        result = await session.execute(text("SELECT COUNT(*) FROM talent_scores WHERE vr_popularity IS NOT NULL"))
        vr_scores_count = result.scalar()

        # talent_imagesの件数
        result = await session.execute(text("SELECT COUNT(*) FROM talent_images"))
        images_count = result.scalar()

        print(f"\n📊 Database verification:")
        print(f"   VR scores: {vr_scores_count:,} records")
        print(f"   Image scores: {images_count:,} records")

        # ターゲットセグメント別統計
        result = await session.execute(text("""
            SELECT ts.code, ts.name, COUNT(*)
            FROM talent_scores sc
            JOIN target_segments ts ON sc.target_segment_id = ts.id
            WHERE sc.vr_popularity IS NOT NULL
            GROUP BY ts.id, ts.code, ts.name
            ORDER BY ts.code
        """))
        segment_stats = result.fetchall()

        print(f"\n📊 VR data by segment:")
        for row in segment_stats:
            print(f"   {row[0]} ({row[1]}): {row[2]:,} records")

    return total_imported > 0

async def main():
    try:
        success = await import_vr_complete()
        if success:
            print("\n🎉 VR Complete Import SUCCESS!")
            return True
        else:
            print("\n⚠️ No VR data imported")
            return False
    except Exception as e:
        print(f"\n❌ VR Complete Import Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)