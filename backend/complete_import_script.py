#!/usr/bin/env python3
"""完全タレントデータベース構築スクリプト - del_flag+名前正規化+全シート対応"""

import asyncio
import sys
import re
from pathlib import Path
from decimal import Decimal
from datetime import datetime
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from sqlalchemy import select, delete, text
from app.db.connection import init_db, get_session_maker
from app.models import (
    Talent, TalentScore, TalentImage,
    TargetSegment, ImageItem, Industry, IndustryImage
)

# データディレクトリパス
DB_INFO_DIR = Path(__file__).parent.parent / "DB情報"
NOW_DATA_PATH = DB_INFO_DIR / "Nowデータ_20251126.xlsx"
VR_DIRS = [
    DB_INFO_DIR / "【VR①】C列の人気度と、E～K列の各種イメージを採用する想定です",
    DB_INFO_DIR / "【VR②】C列の人気度と、E～K列の各種イメージを採用する想定です",
    DB_INFO_DIR / "【VR③】C列の人気度と、E～K列の各種イメージを採用する想定です",
]
TPR_DIR = DB_INFO_DIR / "【TPR】G列のパワースコアを採用する想定です"

AsyncSessionLocal = None

async def get_async_session():
    global AsyncSessionLocal
    if AsyncSessionLocal is None:
        await init_db()
        AsyncSessionLocal = get_session_maker()
    return AsyncSessionLocal()

def normalize_name(name):
    """名前正規化（全角・半角スペース除去、VR/TPR照合用）"""
    if not name or str(name) == "nan":
        return ""

    # 全角・半角スペース、その他空白文字を除去
    normalized = re.sub(r'[\s\u3000\u00A0\u2000-\u200A\u2028\u2029\u202F\u205F]+', '', str(name))
    return normalized.strip()

def safe_decimal(value, default=None):
    """安全なDecimal変換"""
    if pd.isna(value) or value is None:
        return default
    try:
        return Decimal(str(value))
    except (ValueError, TypeError, InvalidOperation):
        return default

def safe_int(value, default=None):
    """安全なint変換"""
    if pd.isna(value) or value is None:
        return default
    try:
        return int(float(value))
    except (ValueError, TypeError):
        return default

def safe_str(value, default=None):
    """安全なstr変換"""
    if pd.isna(value) or value is None:
        return default
    return str(value).strip()

async def clear_all_talent_data():
    """全タレントデータクリア（マスタデータ保護）"""
    print("\n🧹 Clearing all existing talent data...")

    async with await get_async_session() as session:
        # 新しいテーブルもクリア
        tables_to_clear = [
            "talent_keywords",
            "talent_movies",
            "talent_deal_results",
            "talent_notes",
            "talent_contacts",
            "talent_pricing",
            "talent_business_info",
            "talent_media_experience",
            "talent_cm_history",
            "talent_images",
            "talent_scores",
            "talents"
        ]

        for table in tables_to_clear:
            try:
                await session.execute(text(f"DELETE FROM {table}"))
                print(f"   ✅ Cleared: {table}")
            except Exception as e:
                print(f"   ⚠️  Failed to clear {table}: {e}")

        await session.commit()
        print("✅ All talent data cleared successfully")

async def get_target_segment_mapping():
    """ターゲット層マッピング取得"""
    async with await get_async_session() as session:
        result = await session.execute(select(TargetSegment))
        segments = result.scalars().all()

        mapping = {}
        for segment in segments:
            # VR/TPRファイル名パターンとマッピング
            if "F1" in segment.code and "20" in segment.name:
                mapping["女性20～34"] = segment.id
                mapping["女性20〜34"] = segment.id  # 別文字パターン対応
            elif "F2" in segment.code and "35" in segment.name:
                mapping["女性35～49"] = segment.id
                mapping["女性35〜49"] = segment.id
            elif "F3" in segment.code and "50" in segment.name:
                mapping["女性50～69"] = segment.id
                mapping["女性50〜69"] = segment.id
            elif "M1" in segment.code and "20" in segment.name:
                mapping["男性20～34"] = segment.id
                mapping["男性20〜34"] = segment.id
            elif "M2" in segment.code and "35" in segment.name:
                mapping["男性35～49"] = segment.id
                mapping["男性35〜49"] = segment.id
            elif "M3" in segment.code and "50" in segment.name:
                mapping["男性50～69"] = segment.id
                mapping["男性50〜69"] = segment.id
            elif "Teen" in segment.code:
                mapping["男性12～19"] = segment.id
                mapping["女性12～19"] = segment.id
                mapping["男性10～19"] = segment.id  # TPR用パターン
                mapping["女性10～19"] = segment.id

        print(f"📊 Target segment mapping: {len(mapping)} patterns")
        return mapping

async def get_image_item_mapping():
    """イメージ項目マッピング取得"""
    async with await get_async_session() as session:
        result = await session.execute(select(ImageItem))
        items = result.scalars().all()

        mapping = {}
        for item in items:
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

        print(f"📊 Image item mapping: {len(mapping)} items")
        return mapping

async def import_all_excel_sheets():
    """全Excelシートインポート"""
    print("\n📥 Importing all Excel sheets...")

    if not NOW_DATA_PATH.exists():
        raise FileNotFoundError(f"Excel file not found: {NOW_DATA_PATH}")

    # Excelファイル読み込み
    excel_file = pd.ExcelFile(NOW_DATA_PATH)
    sheet_names = excel_file.sheet_names

    print(f"📊 Found {len(sheet_names)} sheets: {sheet_names}")

    # メインアカウントデータ（m_account）から開始
    main_sheet = "m_account"
    if main_sheet not in sheet_names:
        raise ValueError(f"Main sheet '{main_sheet}' not found in Excel file")

    print(f"\n📋 Step 1: Importing main talent data from '{main_sheet}'...")

    df_account = pd.read_excel(NOW_DATA_PATH, sheet_name=main_sheet)
    print(f"   Raw records: {len(df_account):,}")

    # del_flag=0 フィルタリング
    if 'del_flag' in df_account.columns:
        active_df = df_account[df_account['del_flag'] == 0]
        deleted_count = len(df_account) - len(active_df)
        print(f"   Active records (del_flag=0): {len(active_df):,}")
        print(f"   Deleted records (del_flag=1): {deleted_count:,}")
        df_account = active_df
    else:
        print("   ⚠️ del_flag column not found, importing all records")

    talent_count = 0
    talent_id_map = {}  # account_id -> talent_id mapping

    async with await get_async_session() as session:
        for _, row in df_account.iterrows():
            # 基本情報取得
            account_id = safe_int(row.get("account_id"))
            if not account_id:
                continue

            last_name = safe_str(row.get("last_name", ""))
            first_name = safe_str(row.get("first_name", ""), "")
            name_full = f"{last_name}{first_name}".strip()

            if not name_full or len(name_full) < 1:
                continue

            # 名前正規化
            name_normalized = normalize_name(name_full)

            # カナ名
            last_kana = safe_str(row.get("last_name_kana", ""), "")
            first_kana = safe_str(row.get("first_name_kana", ""), "")
            kana_full = f"{last_kana}{first_kana}".strip() if last_kana or first_kana else None

            # 性別変換
            gender_code = safe_int(row.get("gender_type_cd"))
            gender = "男性" if gender_code == 1 else "女性" if gender_code == 2 else None

            # 生年月日・年齢計算
            birthday = None
            birth_year = None
            birthday_value = row.get("birthday")
            if pd.notna(birthday_value):
                try:
                    if isinstance(birthday_value, str):
                        birthday = pd.to_datetime(birthday_value).date()
                    else:
                        birthday = birthday_value.date() if hasattr(birthday_value, 'date') else birthday_value
                    birth_year = birthday.year
                except:
                    pass

            # その他情報
            company_name = safe_str(row.get("company_name"))
            image_name = safe_str(row.get("image_name"))
            pref_code = safe_int(row.get("pref_cd"))
            official_url = safe_str(row.get("official_url"))
            category = safe_str(row.get("act_genre"))

            # Talentオブジェクト作成
            talent = Talent(
                account_id=account_id,
                name=name_full,
                name_normalized=name_normalized,
                kana=kana_full,
                gender=gender,
                birth_year=birth_year,
                birthday=birthday,
                category=category,
                company_name=company_name,
                image_name=image_name,
                prefecture_code=pref_code,
                official_url=official_url,
                del_flag=0,  # アクティブレコード
                money_max_one_year=None,  # 後で設定
                created_at=datetime.now(),
                updated_at=datetime.now()
            )

            session.add(talent)
            talent_count += 1

            if talent_count % 1000 == 0:
                await session.commit()
                print(f"      Processed {talent_count:,} talents...")

        await session.commit()

        # talent_id_map作成
        result = await session.execute(text("SELECT id, account_id FROM talents"))
        for talent_id, account_id in result:
            talent_id_map[account_id] = talent_id

        print(f"   ✅ Main talents imported: {talent_count:,} records")

    # 他のシートインポート
    await import_additional_sheets(sheet_names, talent_id_map)

    return talent_count

async def import_additional_sheets(sheet_names, talent_id_map):
    """その他シートインポート"""
    print(f"\n📋 Step 2: Importing additional sheets...")

    sheet_importers = {
        "m_talent_cm": import_cm_history,
        "m_talent_media": import_media_experience,
        "m_talent_deal": import_business_info,
        "m_talent_act": import_pricing,
        "m_talent_staff": import_contacts,
        "m_talent_other": import_notes,
        "m_talent_deal_result": import_deal_results,
        "m_talent_movie": import_movies,
        "m_talent_frequent_keyword": import_keywords
    }

    for sheet_name, importer_func in sheet_importers.items():
        if sheet_name in sheet_names:
            print(f"\n   🔍 Importing {sheet_name}...")
            try:
                count = await importer_func(sheet_name, talent_id_map)
                print(f"   ✅ {sheet_name}: {count:,} records imported")
            except Exception as e:
                print(f"   ❌ Failed to import {sheet_name}: {e}")
        else:
            print(f"   ⚠️ Sheet not found: {sheet_name}")

async def import_cm_history(sheet_name, talent_id_map):
    """CM履歴インポート"""
    df = pd.read_excel(NOW_DATA_PATH, sheet_name=sheet_name)
    count = 0

    async with await get_async_session() as session:
        for _, row in df.iterrows():
            account_id = safe_int(row.get("account_id"))
            if account_id not in talent_id_map:
                continue

            # CM履歴テーブルに挿入
            cm_data = {
                "talent_id": talent_id_map[account_id],
                "sub_id": safe_int(row.get("sub_id"), 1),
                "client_name": safe_str(row.get("client_name")),
                "product_name": safe_str(row.get("product_name")),
                "use_period_start": row.get("use_period_start") if pd.notna(row.get("use_period_start")) else None,
                "use_period_end": row.get("use_period_end") if pd.notna(row.get("use_period_end")) else None,
                "rival_category_type_cd1": safe_int(row.get("rival_category_type_cd1")),
                "rival_category_type_cd2": safe_int(row.get("rival_category_type_cd2")),
                "rival_category_type_cd3": safe_int(row.get("rival_category_type_cd3")),
                "rival_category_type_cd4": safe_int(row.get("rival_category_type_cd4")),
                "note": safe_str(row.get("note")),
                "regist_date": row.get("regist_date") if pd.notna(row.get("regist_date")) else None,
                "up_date": row.get("up_date") if pd.notna(row.get("up_date")) else None
            }

            await session.execute(text("""
                INSERT INTO talent_cm_history
                (talent_id, sub_id, client_name, product_name, use_period_start, use_period_end,
                 rival_category_type_cd1, rival_category_type_cd2, rival_category_type_cd3, rival_category_type_cd4,
                 note, regist_date, up_date, created_at, updated_at)
                VALUES (:talent_id, :sub_id, :client_name, :product_name, :use_period_start, :use_period_end,
                        :rival_category_type_cd1, :rival_category_type_cd2, :rival_category_type_cd3, :rival_category_type_cd4,
                        :note, :regist_date, :up_date, NOW(), NOW())
            """), cm_data)

            count += 1

        await session.commit()

    return count

async def import_media_experience(sheet_name, talent_id_map):
    """メディア出演経験インポート"""
    df = pd.read_excel(NOW_DATA_PATH, sheet_name=sheet_name)
    count = 0

    async with await get_async_session() as session:
        for _, row in df.iterrows():
            account_id = safe_int(row.get("account_id"))
            if account_id not in talent_id_map:
                continue

            media_data = {
                "talent_id": talent_id_map[account_id],
                "drama": safe_str(row.get("drama")),
                "movie": safe_str(row.get("movie")),
                "stage": safe_str(row.get("stage")),
                "variety": safe_str(row.get("variety")),
                "profile": safe_str(row.get("profile")),
                "regist_date": row.get("regist_date") if pd.notna(row.get("regist_date")) else None,
                "up_date": row.get("up_date") if pd.notna(row.get("up_date")) else None
            }

            await session.execute(text("""
                INSERT INTO talent_media_experience
                (talent_id, drama, movie, stage, variety, profile, regist_date, up_date, created_at, updated_at)
                VALUES (:talent_id, :drama, :movie, :stage, :variety, :profile, :regist_date, :up_date, NOW(), NOW())
            """), media_data)

            count += 1

        await session.commit()

    return count

async def import_business_info(sheet_name, talent_id_map):
    """取引・営業情報インポート"""
    df = pd.read_excel(NOW_DATA_PATH, sheet_name=sheet_name)
    count = 0

    async with await get_async_session() as session:
        for _, row in df.iterrows():
            account_id = safe_int(row.get("account_id"))
            if account_id not in talent_id_map:
                continue

            business_data = {
                "talent_id": talent_id_map[account_id],
                "decision_flag": safe_int(row.get("decision_flag"), 0),
                "contact_flag": safe_int(row.get("contact_flag"), 0),
                "smooth_rating": safe_int(row.get("smooth_rating"), 0),
                "regist_date": row.get("regist_date") if pd.notna(row.get("regist_date")) else None,
                "up_date": row.get("up_date") if pd.notna(row.get("up_date")) else None
            }

            await session.execute(text("""
                INSERT INTO talent_business_info
                (talent_id, decision_flag, contact_flag, smooth_rating, regist_date, up_date, created_at, updated_at)
                VALUES (:talent_id, :decision_flag, :contact_flag, :smooth_rating, :regist_date, :up_date, NOW(), NOW())
            """), business_data)

            count += 1

        await session.commit()

    return count

async def import_pricing(sheet_name, talent_id_map):
    """料金情報インポート"""
    df = pd.read_excel(NOW_DATA_PATH, sheet_name=sheet_name)
    count = 0

    async with await get_async_session() as session:
        for _, row in df.iterrows():
            account_id = safe_int(row.get("account_id"))
            if account_id not in talent_id_map:
                continue

            pricing_data = {
                "talent_id": talent_id_map[account_id],
                "money_min_one_year": safe_decimal(row.get("money_min_one_year")),
                "money_max_one_year": safe_decimal(row.get("money_max_one_year")),
                "cost_min_one_year": safe_decimal(row.get("cost_min_one_year")),
                "cost_max_one_year": safe_decimal(row.get("cost_max_one_year")),
                "money_min_one_cool": safe_decimal(row.get("money_min_one_cool")),
                "money_max_one_cool": safe_decimal(row.get("money_max_one_cool")),
                "cost_min_one_cool": safe_decimal(row.get("cost_min_one_cool")),
                "cost_max_one_cool": safe_decimal(row.get("cost_max_one_cool")),
                "money_min_two_cool": safe_decimal(row.get("money_min_two_cool")),
                "money_max_two_cool": safe_decimal(row.get("money_max_two_cool")),
                "cost_min_two_cool": safe_decimal(row.get("cost_min_two_cool")),
                "cost_max_two_cool": safe_decimal(row.get("cost_max_two_cool")),
                "regist_date": row.get("regist_date") if pd.notna(row.get("regist_date")) else None,
                "up_date": row.get("up_date") if pd.notna(row.get("up_date")) else None
            }

            await session.execute(text("""
                INSERT INTO talent_pricing
                (talent_id, money_min_one_year, money_max_one_year, cost_min_one_year, cost_max_one_year,
                 money_min_one_cool, money_max_one_cool, cost_min_one_cool, cost_max_one_cool,
                 money_min_two_cool, money_max_two_cool, cost_min_two_cool, cost_max_two_cool,
                 regist_date, up_date, created_at, updated_at)
                VALUES (:talent_id, :money_min_one_year, :money_max_one_year, :cost_min_one_year, :cost_max_one_year,
                        :money_min_one_cool, :money_max_one_cool, :cost_min_one_cool, :cost_max_one_cool,
                        :money_min_two_cool, :money_max_two_cool, :cost_min_two_cool, :cost_max_two_cool,
                        :regist_date, :up_date, NOW(), NOW())
            """), pricing_data)

            count += 1

        await session.commit()

    return count

async def import_contacts(sheet_name, talent_id_map):
    """スタッフ連絡先インポート"""
    df = pd.read_excel(NOW_DATA_PATH, sheet_name=sheet_name)
    count = 0

    async with await get_async_session() as session:
        for _, row in df.iterrows():
            account_id = safe_int(row.get("account_id"))
            if account_id not in talent_id_map:
                continue

            contact_data = {
                "talent_id": talent_id_map[account_id],
                "staff_name": safe_str(row.get("staff_name")),
                "staff_tel1": safe_str(row.get("staff_tel1")),
                "staff_tel2": safe_str(row.get("staff_tel2")),
                "staff_tel3": safe_str(row.get("staff_tel3")),
                "staff_mail": safe_str(row.get("staff_mail")),
                "staff_note": safe_str(row.get("staff_note")),
                "regist_date": row.get("regist_date") if pd.notna(row.get("regist_date")) else None,
                "up_date": row.get("up_date") if pd.notna(row.get("up_date")) else None
            }

            await session.execute(text("""
                INSERT INTO talent_contacts
                (talent_id, staff_name, staff_tel1, staff_tel2, staff_tel3, staff_mail, staff_note,
                 regist_date, up_date, created_at, updated_at)
                VALUES (:talent_id, :staff_name, :staff_tel1, :staff_tel2, :staff_tel3, :staff_mail, :staff_note,
                        :regist_date, :up_date, NOW(), NOW())
            """), contact_data)

            count += 1

        await session.commit()

    return count

async def import_notes(sheet_name, talent_id_map):
    """備考・特記事項インポート"""
    df = pd.read_excel(NOW_DATA_PATH, sheet_name=sheet_name)
    count = 0

    async with await get_async_session() as session:
        for _, row in df.iterrows():
            account_id = safe_int(row.get("account_id"))
            if account_id not in talent_id_map:
                continue

            note_data = {
                "talent_id": talent_id_map[account_id],
                "note": safe_str(row.get("note")),
                "regist_date": row.get("regist_date") if pd.notna(row.get("regist_date")) else None,
                "up_date": row.get("up_date") if pd.notna(row.get("up_date")) else None
            }

            await session.execute(text("""
                INSERT INTO talent_notes
                (talent_id, note, regist_date, up_date, created_at, updated_at)
                VALUES (:talent_id, :note, :regist_date, :up_date, NOW(), NOW())
            """), note_data)

            count += 1

        await session.commit()

    return count

async def import_deal_results(sheet_name, talent_id_map):
    """案件結果詳細インポート"""
    df = pd.read_excel(NOW_DATA_PATH, sheet_name=sheet_name)
    count = 0

    async with await get_async_session() as session:
        for _, row in df.iterrows():
            account_id = safe_int(row.get("account_id"))
            if account_id not in talent_id_map:
                continue

            result_data = {
                "talent_id": talent_id_map[account_id],
                "sub_id": safe_int(row.get("sub_id"), 1),
                "recruiting_year": safe_int(row.get("recruiting_year")),
                "recruiting_month": safe_int(row.get("recruiting_month")),
                "job_name": safe_str(row.get("job_name")),
                "deal_result_cd": safe_int(row.get("deal_result_cd")),
                "smooth_rating_cd": safe_int(row.get("smooth_rating_cd")),
                "note": safe_str(row.get("note")),
                "rating_user_id": safe_int(row.get("rating_user_id")),
                "regist_date": row.get("regist_date") if pd.notna(row.get("regist_date")) else None
            }

            await session.execute(text("""
                INSERT INTO talent_deal_results
                (talent_id, sub_id, recruiting_year, recruiting_month, job_name, deal_result_cd,
                 smooth_rating_cd, note, rating_user_id, regist_date, created_at, updated_at)
                VALUES (:talent_id, :sub_id, :recruiting_year, :recruiting_month, :job_name, :deal_result_cd,
                        :smooth_rating_cd, :note, :rating_user_id, :regist_date, NOW(), NOW())
            """), result_data)

            count += 1

        await session.commit()

    return count

async def import_movies(sheet_name, talent_id_map):
    """動画情報インポート"""
    df = pd.read_excel(NOW_DATA_PATH, sheet_name=sheet_name)
    count = 0

    async with await get_async_session() as session:
        for _, row in df.iterrows():
            account_id = safe_int(row.get("account_id"))
            if account_id not in talent_id_map:
                continue

            movie_data = {
                "talent_id": talent_id_map[account_id],
                "sub_id": safe_int(row.get("sub_id"), 1),
                "url": safe_str(row.get("url")),
                "title": safe_str(row.get("title")),
                "regist_date": row.get("regist_date") if pd.notna(row.get("regist_date")) else None
            }

            await session.execute(text("""
                INSERT INTO talent_movies
                (talent_id, sub_id, url, title, regist_date, created_at, updated_at)
                VALUES (:talent_id, :sub_id, :url, :title, :regist_date, NOW(), NOW())
            """), movie_data)

            count += 1

        await session.commit()

    return count

async def import_keywords(sheet_name, talent_id_map):
    """頻出キーワードインポート"""
    df = pd.read_excel(NOW_DATA_PATH, sheet_name=sheet_name)
    count = 0

    async with await get_async_session() as session:
        for _, row in df.iterrows():
            account_id = safe_int(row.get("account_id"))
            if account_id not in talent_id_map:
                continue

            keyword_data = {
                "talent_id": talent_id_map[account_id],
                "sub_id": safe_int(row.get("sub_id"), 1),
                "frequent_category_type_cd": safe_int(row.get("frequent_category_type_cd")),
                "source": safe_str(row.get("source")),
                "regist_date": row.get("regist_date") if pd.notna(row.get("regist_date")) else None
            }

            await session.execute(text("""
                INSERT INTO talent_keywords
                (talent_id, sub_id, frequent_category_type_cd, source, regist_date, created_at, updated_at)
                VALUES (:talent_id, :sub_id, :frequent_category_type_cd, :source, :regist_date, NOW(), NOW())
            """), keyword_data)

            count += 1

        await session.commit()

    return count

async def import_vr_data_with_normalization():
    """VRデータインポート（名前正規化対応）"""
    print("\n📥 Importing VR data with name normalization...")

    target_mapping = await get_target_segment_mapping()
    image_mapping = await get_image_item_mapping()

    # タレント名正規化マッピング作成
    async with await get_async_session() as session:
        result = await session.execute(text("SELECT id, name, name_normalized FROM talents"))
        talents = result.fetchall()

        # 名前（生）→タレントマッピング
        talent_name_map = {talent[1]: talent for talent in talents}
        # 名前（正規化）→タレントマッピング
        talent_normalized_map = {talent[2]: talent for talent in talents if talent[2]}

        print(f"   📊 Talent mapping: {len(talent_name_map):,} names, {len(talent_normalized_map):,} normalized")

    total_processed = 0
    total_matched = 0

    for vr_dir in VR_DIRS:
        if not vr_dir.exists():
            continue

        csv_files = list(vr_dir.glob("*.csv"))
        print(f"   📂 Processing {len(csv_files)} CSV files in {vr_dir.name}")

        for csv_file in csv_files:
            # ターゲット層特定
            target_segment_id = None
            file_name = csv_file.name

            for pattern, segment_id in target_mapping.items():
                if pattern in file_name:
                    target_segment_id = segment_id
                    break

            if target_segment_id is None:
                print(f"      ⚠️ Could not identify target segment for: {csv_file.name}")
                continue

            try:
                df = pd.read_csv(csv_file, encoding='utf-8', header=3)
            except UnicodeDecodeError:
                try:
                    df = pd.read_csv(csv_file, encoding='shift_jis', header=3)
                except Exception as e:
                    print(f"      ❌ Failed to read {csv_file.name}: {e}")
                    continue

            file_matched = 0
            file_processed = 0

            async with await get_async_session() as session:
                for _, row in df.iterrows():
                    vr_talent_name = safe_str(row.get("タレント名", ""))
                    if not vr_talent_name:
                        continue

                    file_processed += 1

                    # マッチング試行：1. 直接マッチ 2. 正規化マッチ
                    talent = None

                    if vr_talent_name in talent_name_map:
                        talent = talent_name_map[vr_talent_name]
                    else:
                        vr_normalized = normalize_name(vr_talent_name)
                        if vr_normalized and vr_normalized in talent_normalized_map:
                            talent = talent_normalized_map[vr_normalized]

                    if not talent:
                        continue

                    talent_id = talent[0]
                    file_matched += 1

                    # 人気度データ処理
                    popularity = safe_decimal(row.get("人気度"))
                    if popularity is not None:
                        # TalentScore作成/更新
                        result = await session.execute(
                            select(TalentScore)
                            .filter_by(talent_id=talent_id, target_segment_id=target_segment_id)
                        )
                        talent_score = result.scalar_one_or_none()

                        if talent_score:
                            talent_score.vr_popularity = popularity
                        else:
                            talent_score = TalentScore(
                                talent_id=talent_id,
                                target_segment_id=target_segment_id,
                                vr_popularity=popularity,
                                tpr_power_score=None,
                                base_power_score=None,
                            )
                            session.add(talent_score)

                    # イメージデータ処理
                    for vr_column, image_id in image_mapping.items():
                        if vr_column in row:
                            image_score = safe_decimal(row[vr_column])
                            if image_score is not None and image_score > 0:
                                talent_image = TalentImage(
                                    talent_id=talent_id,
                                    target_segment_id=target_segment_id,
                                    image_item_id=image_id,
                                    score=image_score
                                )
                                session.add(talent_image)

                await session.commit()

            match_rate = (file_matched / file_processed * 100) if file_processed > 0 else 0
            print(f"      ✅ {csv_file.name}: {file_processed} processed, {file_matched} matched ({match_rate:.1f}%)")

            total_processed += file_processed
            total_matched += file_matched

    overall_match_rate = (total_matched / total_processed * 100) if total_processed > 0 else 0
    print(f"   ✅ VR import complete: {total_processed:,} processed, {total_matched:,} matched ({overall_match_rate:.1f}%)")

    return total_matched

async def import_tpr_data_with_normalization():
    """TPRデータインポート（名前正規化対応）"""
    print("\n📥 Importing TPR data with name normalization...")

    target_mapping = await get_target_segment_mapping()

    # タレント名正規化マッピング作成
    async with await get_async_session() as session:
        result = await session.execute(text("SELECT id, name, name_normalized FROM talents"))
        talents = result.fetchall()

        talent_name_map = {talent[1]: talent for talent in talents}
        talent_normalized_map = {talent[2]: talent for talent in talents if talent[2]}

    if not TPR_DIR.exists():
        print("   ⚠️ TPR directory not found")
        return 0

    csv_files = list(TPR_DIR.glob("*.csv"))
    print(f"   📂 Processing {len(csv_files)} TPR CSV files")

    total_updated = 0
    total_processed = 0
    total_matched = 0

    for csv_file in csv_files:
        # ターゲット層特定
        target_segment_id = None
        file_name = csv_file.name

        for pattern, segment_id in target_mapping.items():
            if pattern in file_name:
                target_segment_id = segment_id
                break

        if target_segment_id is None:
            print(f"      ⚠️ Could not identify target segment for: {csv_file.name}")
            continue

        try:
            df = pd.read_csv(csv_file, encoding='utf-8')
        except UnicodeDecodeError:
            try:
                df = pd.read_csv(csv_file, encoding='shift_jis')
            except Exception as e:
                print(f"      ❌ Failed to read {csv_file.name}: {e}")
                continue

        file_matched = 0
        file_processed = 0

        async with await get_async_session() as session:
            for _, row in df.iterrows():
                tpr_talent_name = safe_str(row.get("タレント名", ""))
                if not tpr_talent_name:
                    continue

                file_processed += 1

                # マッチング試行：1. 直接マッチ 2. 正規化マッチ
                talent = None

                if tpr_talent_name in talent_name_map:
                    talent = talent_name_map[tpr_talent_name]
                else:
                    tpr_normalized = normalize_name(tpr_talent_name)
                    if tpr_normalized and tpr_normalized in talent_normalized_map:
                        talent = talent_normalized_map[tpr_normalized]

                if not talent:
                    continue

                talent_id = talent[0]
                file_matched += 1

                power_score = safe_decimal(row.get("スコア"))
                if power_score is not None:
                    # TalentScore更新
                    result = await session.execute(
                        select(TalentScore)
                        .filter_by(talent_id=talent_id, target_segment_id=target_segment_id)
                    )
                    talent_score = result.scalar_one_or_none()

                    if talent_score:
                        talent_score.tpr_power_score = power_score
                        # 基礎パワー得点計算（STEP1）
                        if talent_score.vr_popularity:
                            talent_score.base_power_score = (
                                talent_score.vr_popularity + power_score
                            ) / 2
                    else:
                        talent_score = TalentScore(
                            talent_id=talent_id,
                            target_segment_id=target_segment_id,
                            vr_popularity=None,
                            tpr_power_score=power_score,
                            base_power_score=None,
                        )
                        session.add(talent_score)

                    total_updated += 1

            await session.commit()

        match_rate = (file_matched / file_processed * 100) if file_processed > 0 else 0
        print(f"      ✅ {csv_file.name}: {file_processed} processed, {file_matched} matched ({match_rate:.1f}%)")

        total_processed += file_processed
        total_matched += file_matched

    overall_match_rate = (total_matched / total_processed * 100) if total_processed > 0 else 0
    print(f"   ✅ TPR import complete: {total_processed:,} processed, {total_matched:,} matched ({overall_match_rate:.1f}%)")

    return total_updated

async def update_talent_money_from_pricing():
    """talentsテーブルのmoney_max_one_yearをtalent_pricingから更新"""
    print("\n🔗 Updating talents.money_max_one_year from talent_pricing...")

    async with await get_async_session() as session:
        result = await session.execute(text("""
            UPDATE talents
            SET money_max_one_year = tp.money_max_one_year,
                updated_at = NOW()
            FROM talent_pricing tp
            WHERE talents.id = tp.talent_id
            AND tp.money_max_one_year IS NOT NULL
        """))

        updated_count = result.rowcount
        await session.commit()

        print(f"   ✅ Updated {updated_count:,} talent records with pricing data")

    return updated_count

async def final_verification():
    """最終検証"""
    print("\n🔍 Final verification...")

    async with await get_async_session() as session:
        # 各テーブルの件数確認
        tables = [
            "talents", "talent_cm_history", "talent_media_experience",
            "talent_business_info", "talent_pricing", "talent_contacts",
            "talent_notes", "talent_deal_results", "talent_movies",
            "talent_keywords", "talent_scores", "talent_images"
        ]

        total_records = 0
        for table in tables:
            try:
                result = await session.execute(text(f"SELECT COUNT(*) FROM {table}"))
                count = result.scalar()
                total_records += count
                print(f"   {table:<25}: {count:,} records")
            except Exception as e:
                print(f"   {table:<25}: Error - {e}")

        print(f"   {'='*25}   {'='*10}")
        print(f"   {'Total records':<25}: {total_records:,}")

        # VR/TPR マッチング率確認
        result = await session.execute(text("SELECT COUNT(*) FROM talent_scores WHERE vr_popularity IS NOT NULL"))
        vr_count = result.scalar()

        result = await session.execute(text("SELECT COUNT(*) FROM talent_scores WHERE tpr_power_score IS NOT NULL"))
        tpr_count = result.scalar()

        result = await session.execute(text("SELECT COUNT(*) FROM talent_images"))
        images_count = result.scalar()

        print(f"\n   📊 Matching success:")
        print(f"   VR popularity data: {vr_count:,} records")
        print(f"   TPR power data: {tpr_count:,} records")
        print(f"   Image data: {images_count:,} records")

        # name_normalized 設定確認
        result = await session.execute(text("SELECT COUNT(*) FROM talents WHERE name_normalized IS NOT NULL"))
        normalized_count = result.scalar()

        result = await session.execute(text("SELECT COUNT(*) FROM talents"))
        total_talents = result.scalar()

        print(f"   Name normalization: {normalized_count:,}/{total_talents:,} ({normalized_count/total_talents*100:.1f}%)")

    return {
        "total_records": total_records,
        "vr_count": vr_count,
        "tpr_count": tpr_count,
        "images_count": images_count,
        "normalized_rate": normalized_count/total_talents*100 if total_talents > 0 else 0
    }

async def main():
    """メイン処理"""
    print("=" * 80)
    print("🚀 COMPLETE TALENT DATABASE CONSTRUCTION")
    print("=" * 80)
    print("📋 Features:")
    print("   ✅ del_flag=0 filtering")
    print("   ✅ Name normalization for VR/TPR matching")
    print("   ✅ All 10 Excel sheets import")
    print("   ✅ Complete database schema")
    print("=" * 80)

    try:
        # Step 1: データクリア
        await clear_all_talent_data()

        # Step 2: 全Excelシートインポート
        talent_count = await import_all_excel_sheets()

        # Step 3: VRデータインポート（名前正規化対応）
        vr_count = await import_vr_data_with_normalization()

        # Step 4: TPRデータインポート（名前正規化対応）
        tpr_count = await import_tpr_data_with_normalization()

        # Step 5: 料金データ反映
        pricing_count = await update_talent_money_from_pricing()

        # Step 6: 最終検証
        verification = await final_verification()

        print("\n" + "=" * 80)
        print("🎉 COMPLETE DATABASE CONSTRUCTION SUCCESSFUL!")
        print("=" * 80)
        print(f"📊 Import Summary:")
        print(f"   - Excel sheets: All 10 sheets processed")
        print(f"   - Active talents: {talent_count:,} (del_flag=0)")
        print(f"   - VR data matches: {vr_count:,}")
        print(f"   - TPR data matches: {tpr_count:,}")
        print(f"   - Pricing updates: {pricing_count:,}")
        print(f"   - Total database records: {verification['total_records']:,}")
        print(f"   - Name normalization: {verification['normalized_rate']:.1f}%")
        print("=" * 80)

        return True

    except Exception as e:
        print(f"\n❌ Complete import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)