#!/usr/bin/env python3
"""VRデータのみインポートスクリプト（修正版）"""

import asyncio
import sys
from pathlib import Path
import pandas as pd
from decimal import Decimal

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
            if "女性20" in segment.name and "34" in segment.name:
                mapping["女性20～34"] = segment.id
            elif "女性35" in segment.name and "49" in segment.name:
                mapping["女性35～49"] = segment.id
            elif "女性50" in segment.name:
                mapping["女性50～69"] = segment.id
            elif "男性20" in segment.name and "34" in segment.name:
                mapping["男性20～34"] = segment.id
            elif "男性35" in segment.name and "49" in segment.name:
                mapping["男性35～49"] = segment.id
            elif "男性50" in segment.name:
                mapping["男性50～69"] = segment.id
            elif "Teen" in segment.code or "10代" in segment.name:
                mapping["男性12～19"] = segment.id
                mapping["女性12～19"] = segment.id

        print(f"📊 Target segment mapping: {mapping}")
        return mapping

async def get_image_item_mapping():
    """現在のイメージ項目マスタから正しいマッピングを取得"""
    async with await get_async_session() as session:
        result = await session.execute(select(ImageItem))
        items = result.scalars().all()

        mapping = {}
        for item in items:
            # VRファイルの列名とマッピング（文字化けを考慮）
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
    """VRデータインポート（修正版）"""
    print("\n📥 Importing VR data (Fixed version)...")

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

            # ファイル名からターゲット層を特定
            target_segment_id = None
            for pattern, seg_id in target_mapping.items():
                if pattern.replace("～", "").replace(" ", "") in csv_file.name:
                    target_segment_id = seg_id
                    break

            if target_segment_id is None:
                print(f"⚠️ Could not identify target segment for: {csv_file.name}")
                continue

            print(f"✅ Matched to segment_id: {target_segment_id}")

            try:
                # VRファイルは5行目がヘッダー、6行目からデータ（header=4）
                df = pd.read_csv(csv_file, encoding='shift_jis', header=4)
                print(f"📊 CSV shape: {df.shape}")
                print(f"📊 CSV columns: {list(df.columns)[:10]}...")

            except Exception as e:
                print(f"❌ Failed to read {csv_file.name}: {e}")
                continue

            file_processed_count = 0

            async with await get_async_session() as session:
                for _, row in df.iterrows():
                    # タレント名の取得（複数の列名パターンを試す）
                    talent_name = None
                    for col_name in df.columns:
                        if any(keyword in str(col_name) for keyword in ["タレント", "名前", "talent", "name"]):
                            talent_name = str(row[col_name]).strip()
                            if talent_name and talent_name != "nan":
                                break

                    if not talent_name or talent_name == "nan":
                        continue

                    if talent_name not in talent_map:
                        continue

                    talent_id = talent_map[talent_name].id

                    # 人気度の取得（複数の列名パターンを試す）
                    popularity = None
                    for col_name in df.columns:
                        if any(keyword in str(col_name) for keyword in ["人気度", "人気", "popularity"]):
                            popularity = pd.to_numeric(row[col_name], errors="coerce")
                            if pd.notna(popularity):
                                break

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

                    # イメージデータ処理
                    for image_name, image_id in image_mapping.items():
                        # 列名の検索（文字化け対応）
                        image_score = None
                        for col_name in df.columns:
                            # 部分一致で検索
                            if any(keyword in str(col_name) for keyword in [
                                "おもしろ", "面白", "清潔", "個性", "信頼", "かわいい", "カッコ", "格好", "大人"
                            ]):
                                # 具体的なマッピング
                                if (("おもしろ" in str(col_name) or "面白" in str(col_name)) and image_name == "おもしろい") or \
                                   ("清潔" in str(col_name) and image_name == "清潔感がある") or \
                                   ("個性" in str(col_name) and image_name == "個性的な") or \
                                   ("信頼" in str(col_name) and image_name == "信頼できる") or \
                                   ("かわいい" in str(col_name) and image_name == "かわいい") or \
                                   (("カッコ" in str(col_name) or "格好" in str(col_name)) and image_name == "カッコいい") or \
                                   ("大人" in str(col_name) and image_name == "大人の魅力がある"):

                                    image_score = pd.to_numeric(row[col_name], errors="coerce")
                                    if pd.notna(image_score):
                                        talent_image = TalentImage(
                                            talent_id=talent_id,
                                            target_segment_id=target_segment_id,
                                            image_item_id=image_id,
                                            score=Decimal(str(image_score))
                                        )
                                        session.add(talent_image)
                                        total_image_records += 1
                                        file_processed_count += 1
                                        break

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
    print("🚀 Starting VR data import (Fixed version)...")
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