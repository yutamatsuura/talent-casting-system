#!/usr/bin/env python3
"""
タレントデータ完全インポートスクリプト（VR照合対応・スペースなし名前実装）
m_accountシート→talentsテーブル（4,819人）

VR照合要件：
- 名前形式：「有吉弘行」（スペースなし）
- last_name + first_name（first_nameがNoneの場合はlast_nameのみ）
"""

import pandas as pd
import unicodedata
from sqlalchemy import create_engine, text
from datetime import datetime
import sys
import os

def normalize_name(name):
    """日本語名前の正規化（VR照合用）"""
    if pd.isna(name) or name is None:
        return None

    # 文字列に変換
    name_str = str(name).strip()
    if not name_str:
        return None

    # Unicode正規化（NFKC：濁点統合、全角統一）
    normalized = unicodedata.normalize('NFKC', name_str)

    # 不要な空白除去
    normalized = normalized.strip()

    return normalized if normalized else None

def create_display_name(last_name, first_name):
    """VR照合対応の名前生成（スペースなし）"""
    last = normalize_name(last_name)
    first = normalize_name(first_name)

    # スペースなし連結（VR照合仕様）
    if last and first:
        return f"{last}{first}"  # 例：「有吉弘行」
    elif last:
        return last  # first_nameがない場合
    else:
        return None

def main():
    print("=" * 80)
    print("タレントデータ完全インポートスクリプト（VR照合対応・正しい実装）")
    print("=" * 80)

    # データベース接続設定
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL環境変数が設定されていません")
        sys.exit(1)

    excel_file = '/Users/lennon/projects/talent-casting-form/DB情報/Nowデータ_20251126.xlsx'
    sheet_name = 'm_account'

    print(f"Excel file: {excel_file}")
    print(f"Sheet: {sheet_name}")
    print()

    try:
        # SQLAlchemy エンジン作成
        engine = create_engine(database_url)

        print("🧹 Truncating talents table...")

        # 既存データ削除（外部キー制約順序）
        dependent_tables = [
            'talent_keywords',
            'talent_movies',
            'talent_deal_results',
            'talent_notes',
            'talent_contacts',
            'talent_pricing',
            'talent_business_info',
            'talent_media_experience',
            'talent_cm_history',
            'talent_images',
            'talent_scores'
        ]

        with engine.connect() as conn:
            for table in dependent_tables:
                try:
                    result = conn.execute(text(f"DELETE FROM {table}"))
                    print(f"   ✅ Cleared: {table}")
                except Exception as e:
                    print(f"   ⚠️  Warning: {table} - {str(e)}")

            # メインテーブル truncate（ID リセット）
            conn.execute(text("TRUNCATE TABLE talents RESTART IDENTITY CASCADE"))
            conn.commit()
            print("✅ Talents table truncated successfully (ID reset to 1)")
            print()

        print("📥 Importing all talent data from m_account sheet...")
        print("📖 Reading Nowデータ_20251126.xlsx...")

        # Excelファイル読み込み
        df = pd.read_excel(excel_file, sheet_name=sheet_name)
        print(f"   Total records in Excel: {len(df):,}")

        # del_flag分布確認
        active_count = len(df[df['del_flag'] == 0])
        deleted_count = len(df[df['del_flag'] == 1])
        print(f"   Active records (del_flag=0): {active_count:,}")
        print(f"   Deleted records (del_flag=1): {deleted_count:,}")

        # first_name有無確認
        with_first = len(df[df['first_name'].notna()])
        without_first = len(df[df['first_name'].isna()])
        print(f"   Records with first_name: {with_first:,}")
        print(f"   Records without first_name: {without_first:,}")
        print()

        print("🔄 Processing talent records...")

        success_count = 0
        error_count = 0

        # SQLAlchemy bulk insert用のデータ準備
        insert_data = []

        for index, row in df.iterrows():
            try:
                # 基本データ取得
                account_id = int(row['account_id']) if pd.notna(row['account_id']) else None
                last_name = str(row['last_name']).strip() if pd.notna(row['last_name']) else None
                first_name = str(row['first_name']).strip() if pd.notna(row['first_name']) else None

                if not account_id or not last_name:
                    error_count += 1
                    continue

                # VR照合対応の名前生成（スペースなし）
                display_name = create_display_name(last_name, first_name)
                if not display_name:
                    error_count += 1
                    continue

                # その他のフィールド処理
                last_name_kana = str(row['last_name_kana']).strip() if pd.notna(row['last_name_kana']) else None
                first_name_kana = str(row['first_name_kana']).strip() if pd.notna(row['first_name_kana']) else None
                image_name = str(row['image_name']).strip() if pd.notna(row['image_name']) else None

                # 日付処理
                birthday = row['birthday'] if pd.notna(row['birthday']) else None

                # 数値処理
                gender_type_cd = int(row['gender_type_cd']) if pd.notna(row['gender_type_cd']) else None
                pref_cd = int(row['pref_cd']) if pd.notna(row['pref_cd']) else None
                del_flag = int(row['del_flag']) if pd.notna(row['del_flag']) else 0

                # テキスト処理
                company_name = str(row['company_name']).strip() if pd.notna(row['company_name']) else None
                official_url = str(row['official_url']).strip() if pd.notna(row['official_url']) else None
                act_genre = str(row['act_genre']).strip() if pd.notna(row['act_genre']) else None

                # SNS関連
                twitter_account_have_flag = int(row['twitter_account_have_flag']) if pd.notna(row['twitter_account_have_flag']) else 9
                twitter_name = str(row['twitter_name']).strip() if pd.notna(row['twitter_name']) else None
                instagram_account_have_flag = int(row['instagram_account_have_flag']) if pd.notna(row['instagram_account_have_flag']) else 9
                instagram_name = str(row['instagram_name']).strip() if pd.notna(row['instagram_name']) else None
                tiktok_account_have_flag = int(row['tiktok_account_have_flag']) if pd.notna(row['tiktok_account_have_flag']) else 9
                tiktok_name = str(row['tiktok_name']).strip() if pd.notna(row['tiktok_name']) else None
                youtube_account_have_flag = int(row['youtube_account_have_flag']) if pd.notna(row['youtube_account_have_flag']) else 9
                youtube_channel_id = str(row['youtube_channel_id']).strip() if pd.notna(row['youtube_channel_id']) else None

                # アップロード関連
                upload_last_name = str(row['upload_last_name']).strip() if pd.notna(row['upload_last_name']) else None
                upload_first_name = str(row['upload_first_name']).strip() if pd.notna(row['upload_first_name']) else None

                # ソート用カナ
                sort_last_name_kana = str(row['sort_last_name_kana']).strip() if pd.notna(row['sort_last_name_kana']) else None
                sort_first_name_kana = str(row['sort_first_name_kana']).strip() if pd.notna(row['sort_first_name_kana']) else None

                # 日付処理
                regist_date = row['regist_date'] if pd.notna(row['regist_date']) else None
                up_date = row['up_date'] if pd.notna(row['up_date']) else None

                # insertデータ準備
                record_data = {
                    'account_id': account_id,
                    'name': display_name,  # VR照合用（スペースなし）
                    'last_name': last_name,
                    'first_name': first_name,
                    'last_name_kana': last_name_kana,
                    'first_name_kana': first_name_kana,
                    'image_name': image_name,
                    'birthday': birthday,
                    'gender_type_cd': gender_type_cd,
                    'pref_cd': pref_cd,
                    'company_name': company_name,
                    'official_url': official_url,
                    'act_genre': act_genre,
                    'twitter_account_have_flag': twitter_account_have_flag,
                    'twitter_name': twitter_name,
                    'instagram_account_have_flag': instagram_account_have_flag,
                    'instagram_name': instagram_name,
                    'tiktok_account_have_flag': tiktok_account_have_flag,
                    'tiktok_name': tiktok_name,
                    'youtube_account_have_flag': youtube_account_have_flag,
                    'youtube_channel_id': youtube_channel_id,
                    'upload_last_name': upload_last_name,
                    'upload_first_name': upload_first_name,
                    'sort_last_name_kana': sort_last_name_kana,
                    'sort_first_name_kana': sort_first_name_kana,
                    'del_flag': del_flag,
                    'regist_date': regist_date,
                    'up_date': up_date,
                }

                insert_data.append(record_data)
                success_count += 1

                # 進捗表示
                if success_count % 500 == 0:
                    print(f"   Processing talents: {success_count:,}/{len(df):,} ({success_count/len(df)*100:.1f}%)")

            except Exception as e:
                error_count += 1
                if error_count <= 5:
                    print(f"   ❌ Error processing row {index+1}: {str(e)}")

        print()
        print("💾 Bulk inserting to database...")

        # バルクインサート実行
        if insert_data:
            with engine.connect() as conn:
                insert_query = text("""
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
                        :twitter_account_have_flag, :twitter_name,
                        :instagram_account_have_flag, :instagram_name,
                        :tiktok_account_have_flag, :tiktok_name,
                        :youtube_account_have_flag, :youtube_channel_id,
                        :upload_last_name, :upload_first_name,
                        :sort_last_name_kana, :sort_first_name_kana,
                        :del_flag, :regist_date, :up_date, NOW(), NOW()
                    )
                """)

                conn.execute(insert_query, insert_data)
                conn.commit()

        print("✅ Import complete! Verifying results...")
        print()

        # 結果確認
        with engine.connect() as conn:
            # 総数確認
            total_result = conn.execute(text("SELECT COUNT(*) as count FROM talents"))
            total_count = total_result.fetchone()[0]

            # del_flag分布確認
            del_flag_result = conn.execute(text("""
                SELECT del_flag, COUNT(*) as count
                FROM talents
                GROUP BY del_flag
                ORDER BY del_flag
            """))
            del_flag_stats = del_flag_result.fetchall()

            # account_id範囲確認
            range_result = conn.execute(text("""
                SELECT MIN(account_id) as min_id, MAX(account_id) as max_id
                FROM talents
            """))
            id_range = range_result.fetchone()

            # 名前サンプル確認（VR照合形式）
            sample_result = conn.execute(text("""
                SELECT account_id, name, last_name, first_name
                FROM talents
                ORDER BY account_id
                LIMIT 5
            """))
            samples = sample_result.fetchall()

        print("【実行結果】")
        print(f"  処理対象レコード: {len(df):,}件")
        print(f"  成功: {success_count:,}件")
        print(f"  エラー: {error_count}件")
        print(f"  成功率: {success_count/(success_count+error_count)*100:.1f}%")
        print()

        print("【データベース確認結果】")
        print(f"  総レコード数: {total_count:,}人")
        print(f"  account_id範囲: {id_range[0]} - {id_range[1]}")
        print()

        print("📊 del_flag分布:")
        for stat in del_flag_stats:
            flag_name = '有効' if stat[0] == 0 else f'削除フラグ({stat[0]})'
            print(f"  {flag_name}: {stat[1]:,}人")
        print()

        print("🔍 名前サンプル（VR照合形式・スペースなし）:")
        for sample in samples:
            first_name_display = sample[3] if sample[3] else 'None'
            print(f"  ID{sample[0]}: \"{sample[1]}\" (姓: \"{sample[2]}\", 名: \"{first_name_display}\")")
        print()

        # VR照合完了判定
        expected_total = 4819
        completion_rate = (total_count / expected_total) * 100
        print(f"✅ VR照合対応インポート進捗: {total_count:,}/{expected_total:,} ({completion_rate:.1f}%)")

        if completion_rate >= 99.5:
            print("🎉 VR照合対応！m_accountシート完全インポート成功！")
            print("📋 次のステップ: 残り9シートのインポート")
        else:
            print("⚠️ インポートが不完全です。確認が必要です。")

        print()
        print("=" * 80)
        print("インポート完了")
        print("=" * 80)

    except Exception as e:
        print(f"❌ Critical Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()