#!/usr/bin/env python3
"""VRデータのみインポートスクリプト（修正版v2）"""

import asyncio
import sys
from pathlib import Path
import pandas as pd
from decimal import Decimal
import re

# backend/appへのパスを追加
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import select, delete, text
from app.db.connection import init_db, get_session_maker
from app.models import (
    Talent, TalentScore, TalentImage,
    TargetSegment, ImageItem
)

# グローバル変数でセッションメーカーを保持
AsyncSessionLocal = None

async def get_async_session():
    """非同期セッション取得"""
    global AsyncSessionLocal
    if AsyncSessionLocal is None:
        await init_db()
        AsyncSessionLocal = get_session_maker()
    return AsyncSessionLocal()

# データディレクトリパス
DB_INFO_DIR = Path(__file__).parent.parent / "DB情報"
VR_DIRS = [
    DB_INFO_DIR / "【VR①】C列の人気度と、E～K列の各種イメージを採用する想定です",
    DB_INFO_DIR / "【VR②】C列の人気度と、E～K列の各種イメージを採用する想定です",
    DB_INFO_DIR / "【VR③】C列の人気度と、E～K列の各種イメージを採用する想定です",
]

async def get_target_segment_mapping():
    """現在のターゲット層マスタから正しいマッピングを取得"""
    async with await get_async_session() as session:
        result = await session.execute(select(TargetSegment))
        segments = result.scalars().all()

        mapping = {}
        for segment in segments:
            print(f"Debug: Segment {segment.id}: {segment.code} - {segment.name}")

            # より柔軟なマッピング
            if "F1" in segment.code:
                mapping["女性20"] = segment.id
                mapping["女性20～34"] = segment.id
            elif "F2" in segment.code:
                mapping["女性35"] = segment.id
                mapping["女性35～49"] = segment.id
            elif "F3" in segment.code:
                mapping["女性50"] = segment.id
                mapping["女性50～69"] = segment.id
            elif "M1" in segment.code:
                mapping["男性20"] = segment.id
                mapping["男性20～34"] = segment.id
            elif "M2" in segment.code:
                mapping["男性35"] = segment.id
                mapping["男性35～49"] = segment.id
            elif "M3" in segment.code:
                mapping["男性50"] = segment.id
                mapping["男性50～69"] = segment.id
            elif "Teen" in segment.code:
                mapping["男性12"] = segment.id
                mapping["女性12"] = segment.id
                mapping["12～19"] = segment.id

        print(f"📊 Target segment mapping: {mapping}")
        return mapping

async def get_image_item_mapping():
    """現在のイメージ項目マスタから正しいマッピングを取得"""
    async with await get_async_session() as session:
        result = await session.execute(select(ImageItem))
        items = result.scalars().all()

        mapping = {}
        for item in items:
            print(f"Debug: Image item {item.id}: {item.name}")
            if "おもしろ" in item.name or "面白" in item.name:
                mapping["おもしろい"] = item.id
            elif "清潔" in item.name:
                mapping["清潔感がある"] = item.id
            elif "個性" in item.name:
                mapping["個性的な"] = item.id
            elif "信頼" in item.name:
                mapping["信頼できる"] = item.id
            elif "かわいい" in item.name:
                mapping["かわいい"] = item.id
            elif "カッコ" in item.name or "格好" in item.name:
                mapping["カッコいい"] = item.id
            elif "大人" in item.name:
                mapping["大人の魅力がある"] = item.id

        print(f"📊 Image item mapping: {mapping}")
        return mapping

def identify_target_segment(filename, target_mapping):
    """ファイル名からターゲット層を特定（改善版）"""
    filename_lower = filename.lower()
    print(f"🔍 Analyzing filename: {filename}")

    # パターンマッチング（より柔軟に）
    patterns = [
        (r"女性20", "女性20"),
        (r"女性35", "女性35"),
        (r"女性50", "女性50"),
        (r"男性20", "男性20"),
        (r"男性35", "男性35"),
        (r"男性50", "男性50"),
        (r"女性12", "女性12"),
        (r"男性12", "男性12"),
    ]

    for pattern, key in patterns:
        if re.search(pattern, filename):
            if key in target_mapping:
                print(f"✅ Matched pattern '{pattern}' to segment_id: {target_mapping[key]}")
                return target_mapping[key]

    print(f"⚠️ No pattern matched for filename: {filename}")
    return None

async def clear_vr_data_only():
    """VRデータのみクリア（TalentImageテーブルとTalentScoreのvr_popularityのみ）"""
    print("\n🧹 Clearing existing VR data only...")

    async with await get_async_session() as session:
        # TalentImageテーブルをクリア
        await session.execute(delete(TalentImage))

        # TalentScoreのvr_popularityをNULLに設定
        await session.execute(text("""
            UPDATE talent_scores SET vr_popularity = NULL, base_power_score = NULL
        """))

        await session.commit()
        print("✅ VR data cleared")

async def import_vr_data():
    """VRデータインポート（修正版v2）"""
    print("\n📥 Importing VR data (Fixed version v2)...")

    target_mapping = await get_target_segment_mapping()
    image_mapping = await get_image_item_mapping()

    async with await get_async_session() as session:
        # タレント名→IDマッピング作成
        result = await session.execute(select(Talent))
        talents = result.scalars().all()
        talent_map = {talent.name: talent for talent in talents}
        print(f"📊 Talent mapping: {len(talent_map)} talents available")

    total_vr_scores = 0
    total_image_records = 0

    for vr_dir in VR_DIRS:
        if not vr_dir.exists():
            print(f"⚠️ VR directory not found: {vr_dir}")
            continue

        csv_files = list(vr_dir.glob("*.csv"))
        print(f"📂 Processing {len(csv_files)} CSV files in {vr_dir.name}")

        for csv_file in csv_files:
            print(f"🔍 Processing file: {csv_file.name}")

            # ファイル名からターゲット層を特定（改善版）
            target_segment_id = identify_target_segment(csv_file.name, target_mapping)

            if target_segment_id is None:
                print(f"⚠️ Could not identify target segment for: {csv_file.name}")
                continue

            print(f"✅ Matched to segment_id: {target_segment_id}")

            try:
                # VRファイルは5行目がヘッダー、6行目からデータ（header=4）
                df = pd.read_csv(csv_file, encoding='shift_jis', header=4)
                print(f"📊 CSV shape: {df.shape}")
                print(f"📊 CSV columns: {list(df.columns)[:10]}...")

                # データが空の場合はスキップ
                if df.empty:
                    print(f"⚠️ Empty CSV file: {csv_file.name}")
                    continue

            except Exception as e:
                print(f"❌ Failed to read {csv_file.name}: {e}")
                continue

            file_processed_count = 0

            async with await get_async_session() as session:
                for _, row in df.iterrows():
                    # タレント名の取得（2列目が一般的にタレント名）
                    talent_name = None
                    if len(df.columns) >= 2:
                        # 2番目の列をタレント名として使用
                        talent_name = str(row.iloc[1]).strip()

                    if not talent_name or talent_name == "nan" or talent_name == "":
                        continue

                    if talent_name not in talent_map:
                        continue

                    talent_id = talent_map[talent_name].id

                    # 人気度の取得（3列目が一般的に人気度）
                    popularity = None
                    if len(df.columns) >= 3:
                        popularity = pd.to_numeric(row.iloc[2], errors="coerce")

                    if pd.notna(popularity):
                        # TalentScore更新（VR人気度）
                        result = await session.execute(
                            select(TalentScore)
                            .filter_by(talent_id=talent_id, target_segment_id=target_segment_id)
                        )
                        talent_score = result.scalar_one_or_none()

                        if talent_score:
                            talent_score.vr_popularity = Decimal(str(popularity))
                            # base_power_scoreの再計算
                            if talent_score.tpr_power_score:
                                talent_score.base_power_score = (
                                    Decimal(str(popularity)) + talent_score.tpr_power_score
                                ) / 2
                        else:
                            talent_score = TalentScore(
                                talent_id=talent_id,
                                target_segment_id=target_segment_id,
                                vr_popularity=Decimal(str(popularity)),
                                tpr_power_score=None,
                                base_power_score=None,
                            )
                            session.add(talent_score)

                        total_vr_scores += 1

                    # イメージデータ処理（4列目以降）
                    image_columns = [
                        ("おもしろい", 4),
                        ("清潔感がある", 5),
                        ("個性的な", 6),
                        ("信頼できる", 7),
                        ("かわいい", 8),
                        ("カッコいい", 9),
                        ("大人の魅力がある", 10)
                    ]

                    for image_name, col_index in image_columns:
                        if image_name in image_mapping and col_index < len(row):
                            image_score = pd.to_numeric(row.iloc[col_index], errors="coerce")
                            if pd.notna(image_score):
                                talent_image = TalentImage(
                                    talent_id=talent_id,
                                    target_segment_id=target_segment_id,
                                    image_item_id=image_mapping[image_name],
                                    score=Decimal(str(image_score))
                                )
                                session.add(talent_image)
                                total_image_records += 1
                                file_processed_count += 1

                await session.commit()

            print(f"  ✅ File {csv_file.name}: {file_processed_count} records processed")

        print(f"  ✅ Completed {vr_dir.name}")

    print(f"✅ VR data import completed:")
    print(f"   - VR popularity scores: {total_vr_scores}")
    print(f"   - Image records: {total_image_records}")
    return total_vr_scores, total_image_records

async def main():
    """メイン処理"""
    print("=" * 60)
    print("🚀 Starting VR data import (Fixed version v2)...")
    print("=" * 60)

    try:
        # VRデータのみクリア
        await clear_vr_data_only()

        # VRデータインポート
        vr_scores, image_records = await import_vr_data()

        print("\n" + "=" * 60)
        print("✅ VR data import completed successfully!")
        print("=" * 60)
        print(f"📊 Summary:")
        print(f"   - VR popularity scores: {vr_scores}")
        print(f"   - Image records: {image_records}")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ Error during import: {e}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    asyncio.run(main())