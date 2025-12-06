"""タレントデータインポート修正版スクリプト（実際のデータ構造対応）"""
import asyncio
import sys
from pathlib import Path
import pandas as pd
from decimal import Decimal
from datetime import datetime

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

        # VRファイル名パターンから正しいsegment_idにマッピング
        mapping = {}
        for segment in segments:
            print(f"Debug: Segment {segment.id}: {segment.code} - {segment.name}")

            # VRファイル名の実際のパターンに合わせて
            if "F1" in segment.code and "20" in segment.name:  # F1: 女性20-34
                mapping["女性20～34"] = segment.id
            elif "F2" in segment.code and "35" in segment.name:  # F2: 女性35-49
                mapping["女性35～49"] = segment.id
            elif "F3" in segment.code and "50" in segment.name:  # F3: 女性50歳以上
                mapping["女性50～69"] = segment.id
            elif "M1" in segment.code and "20" in segment.name:  # M1: 男性20-34
                mapping["男性20～34"] = segment.id
            elif "M2" in segment.code and "35" in segment.name:  # M2: 男性35-49
                mapping["男性35～49"] = segment.id
            elif "M3" in segment.code and "50" in segment.name:  # M3: 男性50歳以上
                mapping["男性50～69"] = segment.id
            elif "Teen" in segment.code:  # Teen: 10代
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
    """Nowデータインポート（実際の列構造に対応）"""
    print("\n📥 Importing Now data...")

    if not NOW_DATA_PATH.exists():
        raise FileNotFoundError(f"Now data file not found: {NOW_DATA_PATH}")

    # Excelファイル読み込み
    df = pd.read_excel(NOW_DATA_PATH)
    print(f"📊 Now data: {len(df)} rows loaded")
    print(f"📊 Columns: {list(df.columns)}")

    talent_count = 0
    skip_count = 0

    async with await get_async_session() as session:
        for _, row in df.iterrows():
            # 基本情報の取得・検証
            last_name = str(row.get("last_name", "")).strip()
            first_name = str(row.get("first_name", "")).strip() if pd.notna(row.get("first_name")) else ""

            # フルネーム作成
            talent_name = f"{last_name}{first_name}".strip()
            if not talent_name or talent_name == "nan" or len(talent_name) < 2:
                skip_count += 1
                continue

            # カナ名の作成
            last_kana = str(row.get("last_name_kana", "")).strip() if pd.notna(row.get("last_name_kana")) else ""
            first_kana = str(row.get("first_name_kana", "")).strip() if pd.notna(row.get("first_name_kana")) else ""
            kana = f"{last_kana}{first_kana}".strip() if last_kana or first_kana else None

            # 性別変換（gender_type_cd: 1=男性, 2=女性）
            gender_code = row.get("gender_type_cd")
            gender = None
            if gender_code == 1:
                gender = "男性"
            elif gender_code == 2:
                gender = "女性"

            # 年齢計算（birthdayから）
            age = None
            birthday = row.get("birthday")
            if pd.notna(birthday):
                try:
                    if isinstance(birthday, str):
                        birth_date = pd.to_datetime(birthday)
                    else:
                        birth_date = birthday

                    today = datetime.now()
                    age = today.year - birth_date.year
                    if (today.month, today.day) < (birth_date.month, birth_date.day):
                        age -= 1
                except:
                    pass

            # その他の情報
            account_id = int(row.get("account_id", 0))
            company = str(row.get("company_name", "")).strip() if pd.notna(row.get("company_name")) else None
            category = str(row.get("act_genre", "")).strip() if pd.notna(row.get("act_genre")) else None

            talent = Talent(
                account_id=account_id,
                name=talent_name,
                kana=kana,
                gender=gender,
                birth_year=birth_date.year if pd.notna(birthday) else None,
                category=category,
                money_max_one_year=None,  # 該当データなし
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            session.add(talent)
            talent_count += 1

            if talent_count % 1000 == 0:
                await session.commit()
                print(f"  ✅ Processed {talent_count} talents...")

        await session.commit()
        print(f"✅ Now data: {talent_count} talents imported, {skip_count} skipped")

    return talent_count


async def import_vr_data():
    """VRデータインポート（実際のファイル名パターン対応）"""
    print("\n📥 Importing VR data...")

    target_mapping = await get_target_segment_mapping()
    image_mapping = await get_image_item_mapping()

    async with await get_async_session() as session:
        # タレント名→IDマッピング作成
        result = await session.execute(select(Talent))
        talents = result.scalars().all()
        talent_map = {talent.name: talent for talent in talents}
        print(f"📊 Talent mapping: {len(talent_map)} talents available")

    total_processed = 0

    for vr_dir in VR_DIRS:
        if not vr_dir.exists():
            print(f"⚠️ VR directory not found: {vr_dir}")
            continue

        csv_files = list(vr_dir.glob("*.csv"))
        print(f"📂 Processing {len(csv_files)} CSV files in {vr_dir.name}")

        for csv_file in csv_files:
            print(f"🔍 Processing file: {csv_file.name}")

            # ファイル名からターゲット層を特定（正確なパターンマッチング）
            target_segment_id = None
            file_name = csv_file.name

            # VRファイル名パターン: VR男性タレント_女性12～19_202507.csv
            if "_女性12～19_" in file_name and "女性12～19" in target_mapping:
                target_segment_id = target_mapping["女性12～19"]
            elif "_女性20～34_" in file_name and "女性20～34" in target_mapping:
                target_segment_id = target_mapping["女性20～34"]
            elif "_女性35～49_" in file_name and "女性35～49" in target_mapping:
                target_segment_id = target_mapping["女性35～49"]
            elif "_女性50～69_" in file_name and "女性50～69" in target_mapping:
                target_segment_id = target_mapping["女性50～69"]
            elif "_男性12～19_" in file_name and "男性12～19" in target_mapping:
                target_segment_id = target_mapping["男性12～19"]
            elif "_男性20～34_" in file_name and "男性20～34" in target_mapping:
                target_segment_id = target_mapping["男性20～34"]
            elif "_男性35～49_" in file_name and "男性35～49" in target_mapping:
                target_segment_id = target_mapping["男性35～49"]
            elif "_男性50～69_" in file_name and "男性50～69" in target_mapping:
                target_segment_id = target_mapping["男性50～69"]

            if target_segment_id is None:
                print(f"⚠️ Could not identify target segment for: {csv_file.name}")
                continue

            print(f"✅ Matched to segment_id: {target_segment_id}")

            try:
                # VRファイルは4行目がヘッダー、5行目からデータ（header=3）
                df = pd.read_csv(csv_file, encoding='utf-8', header=3)
                print(f"📊 CSV columns: {list(df.columns)[:10]}...")  # 最初の10列のみ表示
            except UnicodeDecodeError:
                try:
                    df = pd.read_csv(csv_file, encoding='shift_jis', header=3)
                    print(f"📊 CSV columns: {list(df.columns)[:10]}...")
                except Exception as e:
                    print(f"❌ Failed to read {csv_file.name}: {e}")
                    continue

            processed_in_file = 0

            async with await get_async_session() as session:
                for _, row in df.iterrows():
                    talent_name = str(row.get("タレント名", "")).strip()
                    if not talent_name or talent_name == "nan":
                        continue

                    if talent_name not in talent_map:
                        continue

                    talent_id = talent_map[talent_name].id

                    # 人気度データ処理
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
                            if pd.notna(image_score) and image_score > 0:
                                talent_image = TalentImage(
                                    talent_id=talent_id,
                                    target_segment_id=target_segment_id,
                                    image_item_id=image_id,
                                    score=Decimal(str(image_score))
                                )
                                session.add(talent_image)
                                processed_in_file += 1

                await session.commit()
                print(f"  ✅ File {csv_file.name}: {processed_in_file} records processed")
                total_processed += processed_in_file

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
        talent_map = {talent.name: talent for talent in talents}

    csv_files = list(TPR_DIR.glob("*.csv"))
    print(f"📂 Processing {len(csv_files)} TPR CSV files")

    total_updated = 0

    for csv_file in csv_files:
        print(f"🔍 Processing TPR file: {csv_file.name}")

        # ファイル名からターゲット層を特定
        target_segment_id = None
        file_name = csv_file.name

        # TPRファイル名パターン: TPR_女性20～34_202508.csv, TPR_男性10～19_202508.csv etc.
        if "_女性10～19_" in file_name and "女性12～19" in target_mapping:
            target_segment_id = target_mapping["女性12～19"]
        elif "_女性20～34_" in file_name and "女性20～34" in target_mapping:
            target_segment_id = target_mapping["女性20～34"]
        elif "_女性35～49_" in file_name and "女性35～49" in target_mapping:
            target_segment_id = target_mapping["女性35～49"]
        elif "_女性50～69_" in file_name and "女性50～69" in target_mapping:
            target_segment_id = target_mapping["女性50～69"]
        elif "_男性10～19_" in file_name and "男性12～19" in target_mapping:
            target_segment_id = target_mapping["男性12～19"]
        elif "_男性20～34_" in file_name and "男性20～34" in target_mapping:
            target_segment_id = target_mapping["男性20～34"]
        elif "_男性35～49_" in file_name and "男性35～49" in target_mapping:
            target_segment_id = target_mapping["男性35～49"]
        elif "_男性50～69_" in file_name and "男性50～69" in target_mapping:
            target_segment_id = target_mapping["男性50～69"]

        if target_segment_id is None:
            print(f"⚠️ Could not identify target segment for: {csv_file.name}")
            continue

        try:
            df = pd.read_csv(csv_file, encoding='utf-8')
        except UnicodeDecodeError:
            try:
                df = pd.read_csv(csv_file, encoding='shift_jis')
            except Exception as e:
                print(f"❌ Failed to read {csv_file.name}: {e}")
                continue

        file_updated = 0

        async with await get_async_session() as session:
            for _, row in df.iterrows():
                talent_name = str(row.get("タレント名", "")).strip()
                if not talent_name or talent_name not in talent_map:
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

                    file_updated += 1

            await session.commit()
            print(f"  ✅ File {csv_file.name}: {file_updated} scores updated")
            total_updated += file_updated

    print(f"✅ TPR data: {total_updated} scores updated")
    return total_updated


async def main():
    """メイン処理"""
    print("=" * 60)
    print("🚀 Starting talent data import (Fixed version)...")
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

        # 最終確認
        async with await get_async_session() as session:
            talent_count = await session.execute(text("SELECT COUNT(*) FROM talents"))
            score_count = await session.execute(text("SELECT COUNT(*) FROM talent_scores"))
            image_count = await session.execute(text("SELECT COUNT(*) FROM talent_images"))

            print("\n🔍 Final verification:")
            print(f"   - Talents in DB: {talent_count.scalar()}")
            print(f"   - Scores in DB: {score_count.scalar()}")
            print(f"   - Images in DB: {image_count.scalar()}")

    except Exception as e:
        print(f"\n❌ Error during import: {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    asyncio.run(main())