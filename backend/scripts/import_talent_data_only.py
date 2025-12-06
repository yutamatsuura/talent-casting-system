"""タレントデータのみインポートスクリプト（マスタデータ保護版）"""
import asyncio
import sys
from pathlib import Path
import pandas as pd
from decimal import Decimal

# backend/appへのパスを追加
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select, delete, text
from app.db.connection import init_db, get_session_maker
from app.models import (
    Talent, TalentScore, TalentImage,
    TargetSegment, ImageItem, Industry, IndustryImage
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
DB_INFO_DIR = Path(__file__).parent.parent.parent / "DB情報"
NOW_DATA_PATH = DB_INFO_DIR / "Nowデータ_20251126.xlsx"
VR_DIRS = [
    DB_INFO_DIR / "【VR①】C列の人気度と、E～K列の各種イメージを採用する想定です",
    DB_INFO_DIR / "【VR②】C列の人気度と、E～K列の各種イメージを採用する想定です",
    DB_INFO_DIR / "【VR③】C列の人気度と、E～K列の各種イメージを採用する想定です",
]
TPR_DIR = DB_INFO_DIR / "【TPR】G列のパワースコアを採用する想定です"


async def clear_talent_data_only():
    """タレント関連データのみクリア（マスタデータ保護）"""
    print("\n🧹 Clearing existing talent data (preserving master data)...")

    async with await get_async_session() as session:
        # タレント関連のみ削除（マスタデータは保護）
        await session.execute(delete(TalentImage))
        await session.execute(delete(TalentScore))
        await session.execute(delete(Talent))
        await session.commit()
        print("✅ Talent-related data cleared (master data preserved)")


async def get_target_segment_mapping():
    """現在のターゲット層マスタから正しいマッピングを取得"""
    async with await get_async_session() as session:
        result = await session.execute(select(TargetSegment))
        segments = result.scalars().all()

        # CSVファイル名パターンから正しいsegment_idにマッピング
        mapping = {}
        for segment in segments:
            # 実際のCSVファイル名に基づいてマッピング
            if "男性20" in segment.name and "34" in segment.name:
                mapping["男性20～34"] = segment.id
            elif "女性20" in segment.name and "34" in segment.name:
                mapping["女性20～34"] = segment.id
            elif "男性35" in segment.name and "49" in segment.name:
                mapping["男性35～49"] = segment.id
            elif "女性35" in segment.name and "49" in segment.name:
                mapping["女性35～49"] = segment.id
            elif "男性50" in segment.name:
                mapping["男性50～69"] = segment.id
            elif "女性50" in segment.name:
                mapping["女性50～69"] = segment.id
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
            # VRファイルの列名とマッピング
            if "おもしろ" in item.name:
                mapping["おもしろい"] = item.id
            elif "清潔" in item.name:
                mapping["清潔感がある"] = item.id
            elif "個性" in item.name:
                mapping["個性的な"] = item.id
            elif "信頼" in item.name:
                mapping["信頼できる"] = item.id
            elif "かわいい" in item.name:
                mapping["かわいい"] = item.id
            elif "カッコ" in item.name:
                mapping["カッコいい"] = item.id
            elif "大人" in item.name:
                mapping["大人の魅力がある"] = item.id

        print(f"📊 Image item mapping: {mapping}")
        return mapping


async def import_now_data():
    """Nowデータインポート"""
    print("\n📥 Importing Now data...")

    if not NOW_DATA_PATH.exists():
        raise FileNotFoundError(f"Now data file not found: {NOW_DATA_PATH}")

    # Excelファイル読み込み
    df = pd.read_excel(NOW_DATA_PATH)
    print(f"📊 Now data: {len(df)} rows loaded")

    talent_count = 0

    async with await get_async_session() as session:
        for _, row in df.iterrows():
            # タレント名のクリーニング
            talent_name = str(row.get("タレント名", "")).strip()
            if not talent_name or talent_name == "nan":
                continue

            # money_max_one_year の処理
            money_value = row.get("お金")
            money_max = None
            if pd.notna(money_value):
                try:
                    if isinstance(money_value, str):
                        # 文字列の場合、数値部分を抽出
                        import re
                        numbers = re.findall(r'\d+', money_value.replace(',', ''))
                        if numbers:
                            money_max = int(numbers[-1]) * 10000  # 万円→円
                    else:
                        money_max = int(float(money_value)) * 10000
                except (ValueError, TypeError):
                    money_max = None

            talent = Talent(
                talent_name=talent_name,
                kana=str(row.get("カナ", "")).strip() if pd.notna(row.get("カナ")) else None,
                gender=str(row.get("性別", "")).strip() if pd.notna(row.get("性別")) else None,
                age=int(row.get("年齢", 0)) if pd.notna(row.get("年齢")) else None,
                company_name=str(row.get("事務所", "")).strip() if pd.notna(row.get("事務所")) else None,
                talent_category=str(row.get("カテゴリ", "")).strip() if pd.notna(row.get("カテゴリ")) else None,
                money_max_one_year=money_max,
                created_at="2024-11-26 00:00:00",
                updated_at="2024-11-26 00:00:00"
            )
            session.add(talent)
            talent_count += 1

            if talent_count % 1000 == 0:
                await session.commit()
                print(f"  ✅ Processed {talent_count} talents...")

        await session.commit()
        print(f"✅ Now data: {talent_count} talents imported")

    return talent_count


async def import_vr_data():
    """VRデータインポート"""
    print("\n📥 Importing VR data...")

    target_mapping = await get_target_segment_mapping()
    image_mapping = await get_image_item_mapping()

    async with await get_async_session() as session:
        # タレント名→IDマッピング作成
        result = await session.execute(select(Talent))
        talents = result.scalars().all()
        talent_map = {talent.talent_name: talent for talent in talents}
        print(f"📊 Talent mapping: {len(talent_map)} talents available")

    total_processed = 0

    for vr_dir in VR_DIRS:
        if not vr_dir.exists():
            print(f"⚠️ VR directory not found: {vr_dir}")
            continue

        csv_files = list(vr_dir.glob("*.csv"))
        print(f"📂 Processing {len(csv_files)} CSV files in {vr_dir.name}")

        for csv_file in csv_files:
            # ファイル名からターゲット層を特定
            target_segment_id = None
            for pattern, seg_id in target_mapping.items():
                if pattern.replace("～", "").replace(" ", "") in csv_file.name:
                    target_segment_id = seg_id
                    break

            if target_segment_id is None:
                print(f"⚠️ Could not identify target segment for: {csv_file.name}")
                continue

            try:
                # CSVファイル読み込み（エンコーディング自動検出）
                df = pd.read_csv(csv_file, encoding='utf-8')
            except UnicodeDecodeError:
                try:
                    df = pd.read_csv(csv_file, encoding='shift_jis')
                except Exception as e:
                    print(f"❌ Failed to read {csv_file.name}: {e}")
                    continue

            async with await get_async_session() as session:
                for _, row in df.iterrows():
                    talent_name = str(row.get("名前", "")).strip()
                    if talent_name not in talent_map:
                        continue

                    talent_id = talent_map[talent_name].id
                    popularity = pd.to_numeric(row.get("人気度", 0), errors="coerce")

                    if pd.notna(popularity):
                        # TalentScore作成/更新
                        result = await session.execute(
                            select(TalentScore)
                            .filter_by(talent_id=talent_id, target_segment_id=target_segment_id)
                        )
                        talent_score = result.scalar_one_or_none()

                        if talent_score:
                            talent_score.vr_popularity = Decimal(str(popularity))
                        else:
                            talent_score = TalentScore(
                                talent_id=talent_id,
                                target_segment_id=target_segment_id,
                                vr_popularity=Decimal(str(popularity)),
                                tpr_power_score=None,
                                base_power_score=None,
                            )
                            session.add(talent_score)

                    # イメージデータ処理
                    for vr_column, image_id in image_mapping.items():
                        if vr_column in row:
                            image_score = pd.to_numeric(row[vr_column], errors="coerce")
                            if pd.notna(image_score):
                                talent_image = TalentImage(
                                    talent_id=talent_id,
                                    target_segment_id=target_segment_id,
                                    image_item_id=image_id,
                                    score=Decimal(str(image_score))
                                )
                                session.add(talent_image)
                                total_processed += 1

                await session.commit()

        print(f"  ✅ Completed {vr_dir.name}")

    print(f"✅ VR data: {total_processed} image records imported")
    return total_processed


async def import_tpr_data():
    """TPRデータインポート"""
    print("\n📥 Importing TPR data...")

    target_mapping = await get_target_segment_mapping()

    if not TPR_DIR.exists():
        print(f"⚠️ TPR directory not found: {TPR_DIR}")
        return 0

    async with await get_async_session() as session:
        # タレント名→IDマッピング作成
        result = await session.execute(select(Talent))
        talents = result.scalars().all()
        talent_map = {talent.talent_name: talent for talent in talents}

    csv_files = list(TPR_DIR.glob("*.csv"))
    print(f"📂 Processing {len(csv_files)} TPR CSV files")

    total_updated = 0

    for csv_file in csv_files:
        # ファイル名からターゲット層を特定
        target_segment_id = None
        for pattern, seg_id in target_mapping.items():
            if pattern.replace("～", "").replace(" ", "") in csv_file.name:
                target_segment_id = seg_id
                break

        if target_segment_id is None:
            continue

        try:
            df = pd.read_csv(csv_file, encoding='utf-8')
        except UnicodeDecodeError:
            try:
                df = pd.read_csv(csv_file, encoding='shift_jis')
            except Exception as e:
                print(f"❌ Failed to read {csv_file.name}: {e}")
                continue

        async with await get_async_session() as session:
            for _, row in df.iterrows():
                talent_name = str(row.get("名前", "")).strip()
                if talent_name not in talent_map:
                    continue

                talent_id = talent_map[talent_name].id
                power_score = pd.to_numeric(row.get("スコア", 0), errors="coerce")

                if pd.notna(power_score):
                    # TalentScore更新
                    result = await session.execute(
                        select(TalentScore)
                        .filter_by(talent_id=talent_id, target_segment_id=target_segment_id)
                    )
                    talent_score = result.scalar_one_or_none()

                    if talent_score:
                        talent_score.tpr_power_score = Decimal(str(power_score))
                        # 基礎パワー得点計算（STEP1）
                        if talent_score.vr_popularity:
                            talent_score.base_power_score = (
                                talent_score.vr_popularity + Decimal(str(power_score))
                            ) / 2
                    else:
                        talent_score = TalentScore(
                            talent_id=talent_id,
                            target_segment_id=target_segment_id,
                            vr_popularity=None,
                            tpr_power_score=Decimal(str(power_score)),
                            base_power_score=None,
                        )
                        session.add(talent_score)

                    total_updated += 1

            await session.commit()

    print(f"✅ TPR data: {total_updated} scores updated")
    return total_updated


async def main():
    """メイン処理"""
    print("=" * 60)
    print("🚀 Starting talent data import (preserving master data)...")
    print("=" * 60)

    try:
        # タレントデータのみクリア
        await clear_talent_data_only()

        # Nowデータインポート
        now_count = await import_now_data()

        # VRデータインポート
        vr_count = await import_vr_data()

        # TPRデータインポート
        tpr_count = await import_tpr_data()

        print("\n" + "=" * 60)
        print("✅ Talent data import completed successfully!")
        print("=" * 60)
        print(f"📊 Summary:")
        print(f"   - Talents: {now_count} records")
        print(f"   - VR data: {vr_count} image records")
        print(f"   - TPR data: {tpr_count} score records")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ Error during import: {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    asyncio.run(main())