"""実データ統合インポートスクリプト（Now + VR + TPR）"""
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
    TargetSegment, ImageItem, Industry, IndustryImage, BudgetRange
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


# ターゲット層マッピング（CSVファイル名 → target_segment_id）
TARGET_SEGMENT_MAPPING = {
    "男性12～19": 1,
    "女性12～19": 2,
    "男性20～34": 3,
    "女性20～34": 4,
    "男性35～49": 5,
    "女性35～49": 6,
    "男性50～69": 7,
    "女性50～69": 8,
}

# イメージ項目マッピング（VR列名 → image_item_code）
# VRファイルの実際の列名に合わせて修正
IMAGE_ITEM_MAPPING = {
    "おもしろい": "funny",
    "清潔感がある": "clean",
    "個性的な": "unique",  # VRファイルは「個性的な」
    "信頼できる": "trustworthy",
    "かわいい": "cute",
    "カッコいい": "cool",  # VRファイルは「カッコいい」
    "大人の魅力がある": "mature",  # VRファイルは「大人の魅力がある」
}


async def init_master_data():
    """マスタデータ初期化"""
    print("\n📊 Initializing master data...")

    async with await get_async_session() as session:
        # TRUNCATE CASCADEで高速削除
        await session.execute(text("TRUNCATE TABLE talent_images, talent_scores, talents, industry_images, industries, target_segments, image_items, budget_ranges RESTART IDENTITY CASCADE"))
        await session.commit()
        print("✅ All tables truncated")

        # ターゲット層マスタ
        target_segments = [
            TargetSegment(id=1, code="M1", name="男性12-19歳", gender="男性", age_range="12-19", display_order=1),
            TargetSegment(id=2, code="F1", name="女性12-19歳", gender="女性", age_range="12-19", display_order=2),
            TargetSegment(id=3, code="M2", name="男性20-34歳", gender="男性", age_range="20-34", display_order=3),
            TargetSegment(id=4, code="F2", name="女性20-34歳", gender="女性", age_range="20-34", display_order=4),
            TargetSegment(id=5, code="M3", name="男性35-49歳", gender="男性", age_range="35-49", display_order=5),
            TargetSegment(id=6, code="F3", name="女性35-49歳", gender="女性", age_range="35-49", display_order=6),
            TargetSegment(id=7, code="M4", name="男性50-69歳", gender="男性", age_range="50-69", display_order=7),
            TargetSegment(id=8, code="F4", name="女性50-69歳", gender="女性", age_range="50-69", display_order=8),
        ]

        session.add_all(target_segments)
        await session.commit()
        print(f"✅ Target segments: {len(target_segments)} records")

        # イメージ項目マスタ
        image_items = [
            ImageItem(id=1, code="funny", name="おもしろい", display_order=1),
            ImageItem(id=2, code="clean", name="清潔感がある", display_order=2),
            ImageItem(id=3, code="unique", name="個性的", display_order=3),
            ImageItem(id=4, code="trustworthy", name="信頼できる", display_order=4),
            ImageItem(id=5, code="cute", name="かわいい", display_order=5),
            ImageItem(id=6, code="cool", name="かっこいい", display_order=6),
            ImageItem(id=7, code="mature", name="落ち着きがある", display_order=7),
        ]

        session.add_all(image_items)
        await session.commit()
        print(f"✅ Image items: {len(image_items)} records")

        # 予算区分マスタ
        budget_ranges = [
            BudgetRange(id=1, name="1,000万円未満", min_amount=0, max_amount=10000000, display_order=1),
            BudgetRange(id=2, name="1,000万円～3,000万円未満", min_amount=10000000, max_amount=30000000, display_order=2),
            BudgetRange(id=3, name="3,000万円～5,000万円未満", min_amount=30000000, max_amount=50000000, display_order=3),
            BudgetRange(id=4, name="5,000万円以上", min_amount=50000000, max_amount=None, display_order=4),
        ]

        session.add_all(budget_ranges)
        await session.commit()
        print(f"✅ Budget ranges: {len(budget_ranges)} records")

        # 業種マスタ（サンプル20件）
        industries_data = [
            "化粧品・ヘアケア・オーラルケア", "医薬品・医療機器", "食品", "飲料",
            "アルコール飲料", "自動車", "家電", "ファッション・アパレル",
            "金融・保険", "不動産", "旅行・レジャー", "IT・通信",
            "教育・学習", "流通・小売", "エンターテイメント", "スポーツ",
            "美容・エステ", "家具・インテリア", "日用品・雑貨", "その他"
        ]
        industries = [Industry(name=name, display_order=idx+1) for idx, name in enumerate(industries_data)]

        session.add_all(industries)
        await session.commit()
        print(f"✅ Industries: {len(industries)} records")


async def import_now_data():
    """NowデータExcelからタレント基本情報をインポート"""
    print("\n📥 Importing Now data (Excel)...")

    # Excelファイル読み込み
    df = pd.read_excel(NOW_DATA_PATH, sheet_name=0, header=None)

    # ヘッダー検出（最初の数行をスキップ）
    header_row = None
    for i in range(30):  # 検索範囲を拡大
        cell_value = str(df.iloc[i, 0]).lower()
        if "account" in cell_value or "アカウント" in cell_value:
            header_row = i
            break

    if header_row is None:
        print(f"⚠️  First 30 rows:")
        for i in range(min(30, len(df))):
            print(f"Row {i}: {df.iloc[i, 0]}")
        raise ValueError("Header row not found in Excel file")

    # ヘッダー設定
    df.columns = df.iloc[header_row]
    df = df.iloc[header_row + 1:].reset_index(drop=True)

    # Excelのカラム構造に基づいてデータ抽出
    # 姓名を結合してnameカラムを作成
    df["name"] = df["last_name"].fillna("") + df["first_name"].fillna("")
    df["kana"] = df["last_name_kana"].fillna("") + df["first_name_kana"].fillna("")

    # gender_type_cd (1=男性, 2=女性)
    df["gender"] = df["gender_type_cd"].map({1: "男性", 2: "女性"})

    # birthdayから生年を抽出
    df["birthday"] = pd.to_datetime(df["birthday"], errors="coerce")
    df["birth_year"] = df["birthday"].dt.year

    # act_genreをcategoryに
    df["category"] = df["act_genre"]

    # money_max_one_yearがない場合はNoneに設定（後で別途設定する必要がある）
    if "money_max_one_year" not in df.columns:
        df["money_max_one_year"] = None

    df_clean = df[["account_id", "name", "kana", "gender", "birth_year", "category", "money_max_one_year"]].copy()

    # データクレンジング
    df_clean = df_clean.dropna(subset=["account_id", "name"])
    df_clean["account_id"] = df_clean["account_id"].astype(int)
    df_clean["birth_year"] = pd.to_numeric(df_clean["birth_year"], errors="coerce")
    df_clean["money_max_one_year"] = pd.to_numeric(df_clean["money_max_one_year"], errors="coerce")

    # データベースに挿入
    async with await get_async_session() as session:

        talents = []
        for _, row in df_clean.iterrows():
            talent = Talent(
                account_id=int(row["account_id"]),
                name=str(row["name"]),
                kana=str(row["kana"]) if pd.notna(row["kana"]) else None,
                gender=str(row["gender"]) if pd.notna(row["gender"]) else None,
                birth_year=int(row["birth_year"]) if pd.notna(row["birth_year"]) else None,
                category=str(row["category"]) if pd.notna(row["category"]) else None,
                money_max_one_year=Decimal(str(row["money_max_one_year"])) if pd.notna(row["money_max_one_year"]) else None,
            )
            talents.append(talent)

        session.add_all(talents)
        await session.commit()
        print(f"✅ Talents: {len(talents)} records imported")

    return len(talents)


async def import_vr_data():
    """VRデータCSVからVR人気度とイメージスコアをインポート"""
    print("\n📥 Importing VR data (16 CSV files)...")

    # 3ディレクトリから全CSVファイルを取得
    vr_files = []
    for vr_dir in VR_DIRS:
        vr_files.extend(list(vr_dir.glob("*.csv")))

    print(f"📁 Found {len(vr_files)} VR CSV files")
    total_imported = 0
    total_scores_created = 0
    total_images_created = 0
    failed_files = []

    async with await get_async_session() as session:
        # タレントID マッピング取得
        result = await session.execute(select(Talent.id, Talent.account_id, Talent.name))
        talent_map = {row.name: row for row in result.all()}
        print(f"📊 Talent map: {len(talent_map)} talents available")

        # イメージ項目ID マッピング取得
        result = await session.execute(select(ImageItem.id, ImageItem.name))
        image_item_map = {row.name: row.id for row in result.all()}
        print(f"📊 Image item map: {image_item_map}")

        for vr_file in vr_files:
            try:
                # ファイル名からターゲット層を特定
                target_segment_name = None
                for key in TARGET_SEGMENT_MAPPING.keys():
                    if key in vr_file.name:
                        target_segment_name = key
                        break

                if not target_segment_name:
                    print(f"⚠️  Skipping {vr_file.name}: target segment not found")
                    failed_files.append(f"{vr_file.name}: target segment not found")
                    continue

                target_segment_id = TARGET_SEGMENT_MAPPING[target_segment_name]

                # CSV読み込み（Shift_JIS、skiprows=4に修正）
                df = pd.read_csv(vr_file, encoding="shift_jis", header=None, skiprows=4)

                # ヘッダー検出
                header_row = 0
                df.columns = df.iloc[header_row]
                df = df.iloc[header_row + 1:].reset_index(drop=True)

                # タレント名と人気度、イメージスコア抽出
                talent_col = df.columns[1]  # タレント名
                popularity_col = df.columns[2]  # C列: 人気度
                image_cols = df.columns[4:11]  # E~K列: イメージ7項目

                file_success_count = 0
                file_score_count = 0
                file_image_count = 0

                for idx, row in df.iterrows():
                    talent_name = str(row[talent_col]).strip()

                    if talent_name not in talent_map:
                        continue

                    talent_id = talent_map[talent_name].id
                    popularity = pd.to_numeric(row[popularity_col], errors="coerce")

                    # TalentScore作成（VR人気度のみ、TPRは後で統合）
                    talent_score = TalentScore(
                        talent_id=talent_id,
                        target_segment_id=target_segment_id,
                        vr_popularity=Decimal(str(popularity)) if pd.notna(popularity) else None,
                        tpr_power_score=None,  # TPRデータで後で更新
                        base_power_score=None,
                    )
                    session.add(talent_score)
                    file_score_count += 1

                    # TalentImage作成（7項目）
                    for img_col in image_cols:
                        vr_col_name = str(img_col).strip()
                        if vr_col_name not in IMAGE_ITEM_MAPPING:
                            continue

                        # VR列名からcodeを取得
                        img_code = IMAGE_ITEM_MAPPING[vr_col_name]

                        # codeからImageItem IDを直接取得
                        # image_item_mapのキーはImageItem.name（DB上の名前）
                        # IMAGE_ITEM_MAPPINGはVR列名→codeのマッピング
                        # ImageItemマスタの定義: code="funny", name="おもしろい"
                        code_to_name = {
                            "funny": "おもしろい",
                            "clean": "清潔感がある",
                            "unique": "個性的",
                            "trustworthy": "信頼できる",
                            "cute": "かわいい",
                            "cool": "かっこいい",
                            "mature": "落ち着きがある",
                        }

                        img_item_name = code_to_name.get(img_code)
                        if not img_item_name or img_item_name not in image_item_map:
                            continue

                        img_score = pd.to_numeric(row[img_col], errors="coerce")
                        if pd.notna(img_score):
                            talent_image = TalentImage(
                                talent_id=talent_id,
                                target_segment_id=target_segment_id,
                                image_item_id=image_item_map[img_item_name],
                                score=Decimal(str(img_score)),
                            )
                            session.add(talent_image)
                            file_image_count += 1

                    file_success_count += 1

                total_imported += file_success_count
                total_scores_created += file_score_count
                total_images_created += file_image_count
                print(f"✅ {vr_file.name}: {file_success_count} talents, {file_score_count} scores, {file_image_count} images")

            except Exception as e:
                print(f"❌ Error processing {vr_file.name}: {e}")
                failed_files.append(f"{vr_file.name}: {e}")
                continue

        await session.commit()
        print(f"\n✅ VR data import completed:")
        print(f"   - Files processed: {len(vr_files) - len(failed_files)}/{len(vr_files)}")
        print(f"   - Talent records: {total_imported}")
        print(f"   - TalentScore records: {total_scores_created}")
        print(f"   - TalentImage records: {total_images_created}")

        if failed_files:
            print(f"\n⚠️  Failed files ({len(failed_files)}):")
            for failed in failed_files:
                print(f"   - {failed}")

    return total_imported


async def import_tpr_data():
    """TPRデータCSVからTPRパワースコアをインポート（既存TalentScoreに統合）"""
    print("\n📥 Importing TPR data (8 CSV files)...")

    tpr_files = list(TPR_DIR.glob("*.csv"))
    total_updated = 0

    async with await get_async_session() as session:
        # タレントID マッピング取得
        result = await session.execute(select(Talent.id, Talent.account_id, Talent.name))
        talent_map = {row.name: row for row in result.all()}

        for tpr_file in tpr_files:
            # ファイル名からターゲット層を特定（10-19 → 12-19に変換）
            target_segment_name = None
            file_name = tpr_file.name

            # TPRファイル名パターン: TPR_男性10～19_202508.csv
            if "男性10～19" in file_name:
                target_segment_name = "男性12～19"
            elif "女性10～19" in file_name:
                target_segment_name = "女性12～19"
            else:
                for key in ["男性20～34", "女性20～34", "男性35～49", "女性35～49", "男性50～69", "女性50～69"]:
                    if key in file_name:
                        target_segment_name = key
                        break

            if not target_segment_name:
                print(f"⚠️  Skipping {tpr_file.name}: target segment not found")
                continue

            target_segment_id = TARGET_SEGMENT_MAPPING[target_segment_name]

            # CSV読み込み（UTF-8 BOM付き）
            df = pd.read_csv(tpr_file, encoding="utf-8-sig")

            # タレント名とパワースコア抽出（G列）
            if "タレント名" not in df.columns or "スコア" not in df.columns:
                print(f"⚠️  Skipping {tpr_file.name}: required columns not found")
                continue

            for _, row in df.iterrows():
                talent_name = str(row["タレント名"]).strip()

                if talent_name not in talent_map:
                    continue

                talent_id = talent_map[talent_name].id
                power_score = pd.to_numeric(row["スコア"], errors="coerce")

                if pd.notna(power_score):
                    # 既存TalentScoreを更新
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
                        # VRデータがない場合は新規作成
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
        print(f"✅ TPR data: {total_updated} talent scores updated (8 CSV files)")

    return total_updated


async def main():
    """メイン処理"""
    print("=" * 60)
    print("🚀 Starting data import process...")
    print("=" * 60)

    try:
        # マスタデータ初期化
        await init_master_data()

        # Nowデータインポート
        now_count = await import_now_data()

        # VRデータインポート
        vr_count = await import_vr_data()

        # TPRデータインポート
        tpr_count = await import_tpr_data()

        print("\n" + "=" * 60)
        print("✅ Data import completed successfully!")
        print("=" * 60)
        print(f"📊 Summary:")
        print(f"   - Talents: {now_count} records")
        print(f"   - VR data: {vr_count} talent records (16 files)")
        print(f"   - TPR data: {tpr_count} talent scores (8 files)")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ Error during import: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
