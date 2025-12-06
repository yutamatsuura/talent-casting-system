#!/usr/bin/env python3
"""
完全タレントデータインポートスクリプト
Excel m_accountシートから全4,819件をtalentsテーブルにインポート

重要な修正点:
1. 名前マッピングを修正して読みやすくする
   - "有吉" + "弘行" = "有吉 弘行"（空白あり）
   - first_nameが空の場合（911件）はlast_nameのみ使用

2. 完全なデータクリーニングを実行
   - 4,819人すべてのタレント基本情報をインポート
   - account_idが1から順序よく振られることを確認
   - del_flag=1のレコードも含めて全データをインポート

3. データベースの事前準備
   - 既存のtalentsテーブルをTRUNCATEしてからINSERT
   - SERIAL型のaccount_idが正しくリセットされることを確認
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime
import pandas as pd
import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from sqlalchemy import text
from app.db.connection import init_db, get_session_maker

# データディレクトリパス
DB_INFO_DIR = Path(__file__).parent.parent / "DB情報"
NOW_DATA_PATH = DB_INFO_DIR / "Nowデータ_20251126.xlsx"

AsyncSessionLocal = None


async def get_async_session():
    """非同期セッション取得"""
    global AsyncSessionLocal
    if AsyncSessionLocal is None:
        await init_db()
        AsyncSessionLocal = get_session_maker()
    return AsyncSessionLocal()


def safe_str(value, default=None):
    """安全なstr変換（NaN/None対応）"""
    if pd.isna(value) or value is None:
        return default
    return str(value).strip()


def safe_int(value, default=None):
    """安全なint変換（NaN/None対応）"""
    if pd.isna(value) or value is None:
        return default
    try:
        return int(float(value))
    except (ValueError, TypeError):
        return default


def safe_date(value, default=None):
    """安全な日付変換（NaN/None対応）"""
    if pd.isna(value) or value is None:
        return default
    try:
        if isinstance(value, datetime):
            return value
        return pd.to_datetime(value)
    except Exception:
        return default


def build_full_name(last_name, first_name):
    """
    フルネーム構築（空白入り）

    重要なロジック:
    - first_nameがある場合: "姓 名"（空白入り）
    - first_nameがない場合: "姓"のみ

    例:
    - "有吉" + "弘行" = "有吉 弘行"
    - "ローラ" + NaN = "ローラ"
    """
    last = safe_str(last_name, "")
    first = safe_str(first_name, "")

    if first:
        return f"{last} {first}"
    return last


async def truncate_talents_table():
    """talentsテーブルをTRUNCATEしてIDをリセット"""
    print("\n🧹 Truncating talents table...")

    async with await get_async_session() as session:
        try:
            # 依存テーブルをクリア
            dependent_tables = [
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
                "talent_scores"
            ]

            for table in dependent_tables:
                try:
                    await session.execute(text(f"DELETE FROM {table}"))
                    print(f"   ✅ Cleared: {table}")
                except Exception as e:
                    print(f"   ⚠️  Failed to clear {table}: {e}")

            # talentsテーブルをTRUNCATEしてIDをリセット
            await session.execute(text("TRUNCATE TABLE talents RESTART IDENTITY CASCADE"))
            await session.commit()
            print("✅ Talents table truncated successfully (ID reset to 1)")

        except Exception as e:
            print(f"❌ Error truncating talents table: {e}")
            await session.rollback()
            raise


async def import_talents_from_excel():
    """m_accountシートから全タレントデータをインポート"""
    print("\n📥 Importing all talent data from m_account sheet...")

    if not NOW_DATA_PATH.exists():
        raise FileNotFoundError(f"Excel file not found: {NOW_DATA_PATH}")

    # m_accountシート読み込み
    print(f"📖 Reading {NOW_DATA_PATH.name}...")
    df = pd.read_excel(NOW_DATA_PATH, sheet_name="m_account")
    total_records = len(df)
    print(f"   Total records in Excel: {total_records:,}")

    # del_flag統計
    if 'del_flag' in df.columns:
        active_count = (df['del_flag'] == 0).sum()
        deleted_count = (df['del_flag'] == 1).sum()
        print(f"   Active records (del_flag=0): {active_count:,}")
        print(f"   Deleted records (del_flag=1): {deleted_count:,}")

    # first_name統計
    first_name_null_count = df['first_name'].isna().sum()
    print(f"   Records with first_name: {total_records - first_name_null_count:,}")
    print(f"   Records without first_name: {first_name_null_count:,}")

    # データインポート準備
    print("\n🔄 Processing talent records...")
    async with await get_async_session() as session:
        imported_count = 0
        skipped_count = 0
        errors = []

        for idx, row in df.iterrows():
            try:
                # account_idは必須
                account_id = safe_int(row.get('account_id'))
                if not account_id:
                    skipped_count += 1
                    errors.append(f"Row {idx}: Missing account_id")
                    continue

                # 名前フィールド構築（空白入り）
                last_name = safe_str(row.get('last_name'), "")
                first_name = safe_str(row.get('first_name'), "")
                full_name = build_full_name(last_name, first_name)

                if not full_name:
                    skipped_count += 1
                    errors.append(f"Row {idx}: Missing name (account_id={account_id})")
                    continue

                # その他のフィールド
                last_name_kana = safe_str(row.get('last_name_kana'))
                first_name_kana = safe_str(row.get('first_name_kana'))
                image_name = safe_str(row.get('image_name'))
                birthday = safe_date(row.get('birthday'))
                gender_type_cd = safe_int(row.get('gender_type_cd'))
                pref_cd = safe_int(row.get('pref_cd'))
                company_name = safe_str(row.get('company_name'))
                official_url = safe_str(row.get('official_url'))
                act_genre = safe_str(row.get('act_genre'))

                # SNSフラグとアカウント
                twitter_flag = safe_int(row.get('twitter_account_have_flag'), 0)
                twitter_name = safe_str(row.get('twitter_name'))
                instagram_flag = safe_int(row.get('instagram_account_have_flag'), 0)
                instagram_name = safe_str(row.get('instagram_name'))
                tiktok_flag = safe_int(row.get('tiktok_account_have_flag'), 0)
                tiktok_name = safe_str(row.get('tiktok_name'))
                youtube_flag = safe_int(row.get('youtube_account_have_flag'), 0)
                youtube_channel_id = safe_str(row.get('youtube_channel_id'))

                # 内部管理用フィールド
                upload_last_name = safe_str(row.get('upload_last_name'))
                upload_first_name = safe_str(row.get('upload_first_name'))
                sort_last_name_kana = safe_str(row.get('sort_last_name_kana'))
                sort_first_name_kana = safe_str(row.get('sort_first_name_kana'))
                del_flag = safe_int(row.get('del_flag'), 0)
                regist_date = safe_date(row.get('regist_date'))
                up_date = safe_date(row.get('up_date'))

                # SQLインサート実行
                insert_sql = text("""
                    INSERT INTO talents (
                        account_id, name, last_name, first_name,
                        last_name_kana, first_name_kana, image_name,
                        birthday, gender_type_cd, pref_cd,
                        company_name, official_url, act_genre,
                        twitter_account_have_flag, twitter_name,
                        instagram_account_have_flag, instagram_name,
                        tiktok_account_have_flag, tiktok_name,
                        youtube_account_have_flag, youtube_channel_id,
                        upload_last_name, upload_first_name,
                        sort_last_name_kana, sort_first_name_kana,
                        del_flag, regist_date, up_date, created_at, updated_at
                    ) VALUES (
                        :account_id, :name, :last_name, :first_name,
                        :last_name_kana, :first_name_kana, :image_name,
                        :birthday, :gender_type_cd, :pref_cd,
                        :company_name, :official_url, :act_genre,
                        :twitter_flag, :twitter_name,
                        :instagram_flag, :instagram_name,
                        :tiktok_flag, :tiktok_name,
                        :youtube_flag, :youtube_channel_id,
                        :upload_last_name, :upload_first_name,
                        :sort_last_name_kana, :sort_first_name_kana,
                        :del_flag, :regist_date, :up_date, NOW(), NOW()
                    )
                """)

                await session.execute(insert_sql, {
                    'account_id': account_id,
                    'name': full_name,
                    'last_name': last_name,
                    'first_name': first_name if first_name else None,
                    'last_name_kana': last_name_kana,
                    'first_name_kana': first_name_kana,
                    'image_name': image_name,
                    'birthday': birthday,
                    'gender_type_cd': gender_type_cd,
                    'pref_cd': pref_cd,
                    'company_name': company_name,
                    'official_url': official_url,
                    'act_genre': act_genre,
                    'twitter_flag': twitter_flag,
                    'twitter_name': twitter_name,
                    'instagram_flag': instagram_flag,
                    'instagram_name': instagram_name,
                    'tiktok_flag': tiktok_flag,
                    'tiktok_name': tiktok_name,
                    'youtube_flag': youtube_flag,
                    'youtube_channel_id': youtube_channel_id,
                    'upload_last_name': upload_last_name,
                    'upload_first_name': upload_first_name,
                    'sort_last_name_kana': sort_last_name_kana,
                    'sort_first_name_kana': sort_first_name_kana,
                    'del_flag': del_flag,
                    'regist_date': regist_date,
                    'up_date': up_date
                })

                imported_count += 1

                # 進捗表示（100件ごと）
                if imported_count % 100 == 0:
                    print(f"   Progress: {imported_count:,}/{total_records:,} records")

            except Exception as e:
                skipped_count += 1
                errors.append(f"Row {idx} (account_id={row.get('account_id')}): {str(e)}")

        # コミット
        await session.commit()

        print(f"\n✅ Import completed!")
        print(f"   Total records: {total_records:,}")
        print(f"   Imported: {imported_count:,}")
        print(f"   Skipped: {skipped_count:,}")

        if errors:
            print(f"\n⚠️ Errors encountered: {len(errors)}")
            for error in errors[:10]:  # 最初の10件のみ表示
                print(f"      {error}")
            if len(errors) > 10:
                print(f"      ... and {len(errors) - 10} more errors")

        return imported_count, skipped_count


async def verify_import():
    """インポート結果の検証"""
    print("\n🔍 Verifying import results...")

    async with await get_async_session() as session:
        # 総レコード数
        result = await session.execute(text("SELECT COUNT(*) FROM talents"))
        total_count = result.scalar()
        print(f"   Total talents: {total_count:,}")

        # del_flag統計
        result = await session.execute(text("""
            SELECT del_flag, COUNT(*)
            FROM talents
            GROUP BY del_flag
            ORDER BY del_flag
        """))
        del_flag_stats = result.fetchall()
        print("\n   Del flag statistics:")
        for flag, count in del_flag_stats:
            status = "Active" if flag == 0 else "Deleted"
            print(f"      {status} (del_flag={flag}): {count:,}")

        # first_name統計
        result = await session.execute(text("""
            SELECT
                COUNT(*) FILTER (WHERE first_name IS NOT NULL) as with_first,
                COUNT(*) FILTER (WHERE first_name IS NULL) as without_first
            FROM talents
        """))
        name_stats = result.fetchone()
        print("\n   Name statistics:")
        print(f"      With first_name: {name_stats[0]:,}")
        print(f"      Without first_name: {name_stats[1]:,}")

        # サンプルレコード表示（最初の5件）
        result = await session.execute(text("""
            SELECT account_id, name, last_name, first_name, del_flag
            FROM talents
            ORDER BY account_id
            LIMIT 5
        """))
        samples = result.fetchall()
        print("\n   Sample records (first 5):")
        for record in samples:
            print(f"      ID:{record[0]:4d} | Name: {record[1]:<20s} | "
                  f"Last: {record[2]:<10s} | First: {str(record[3]):<10s} | "
                  f"Del: {record[4]}")

        # account_idの連続性チェック
        result = await session.execute(text("""
            SELECT MIN(account_id), MAX(account_id)
            FROM talents
        """))
        min_id, max_id = result.fetchone()
        print(f"\n   Account ID range: {min_id} - {max_id}")

        # 重複チェック
        result = await session.execute(text("""
            SELECT account_id, COUNT(*)
            FROM talents
            GROUP BY account_id
            HAVING COUNT(*) > 1
        """))
        duplicates = result.fetchall()
        if duplicates:
            print(f"\n   ⚠️ Warning: Found {len(duplicates)} duplicate account_ids")
        else:
            print("\n   ✅ No duplicate account_ids found")


async def main():
    """メイン実行"""
    print("=" * 80)
    print("タレントデータ完全インポートスクリプト")
    print("=" * 80)
    print(f"Excel file: {NOW_DATA_PATH}")
    print(f"Sheet: m_account")
    print()

    try:
        # ステップ1: talentsテーブルをTRUNCATEしてIDをリセット
        await truncate_talents_table()

        # ステップ2: 全タレントデータをインポート
        imported, skipped = await import_talents_from_excel()

        # ステップ3: インポート結果を検証
        await verify_import()

        print("\n" + "=" * 80)
        print("✅ All operations completed successfully!")
        print("=" * 80)

    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
