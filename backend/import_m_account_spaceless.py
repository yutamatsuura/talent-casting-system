#!/usr/bin/env python3
"""
m_accountシート完全インポートスクリプト（VR照合対応・スペースなし実装）
実行計画書EXECUTION_PLAN_20251202.md準拠

重要仕様:
- 必ずm_accountシート読み込み（4,819人）
- last_name + first_name → name（スペースなし「有吉弘行」）
- VR照合互換性確保
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

    name_str = str(name).strip()
    if not name_str:
        return None

    # Unicode正規化（NFKC：濁点統合、全角統一）
    normalized = unicodedata.normalize('NFKC', name_str)
    normalized = normalized.strip()

    return normalized if normalized else None

def create_display_name_spaceless(last_name, first_name):
    """VR照合対応の名前生成（スペースなし）
    実行計画書仕様: last_name + first_name → name（スペースなし「有吉弘行」）
    """
    last = normalize_name(last_name)
    first = normalize_name(first_name)

    # スペースなし連結（VR照合仕様）
    if last and first:
        return f"{last}{first}"  # 例：「有吉弘行」（スペースなし）
    elif last:
        return last  # first_nameがない場合
    else:
        return None

def main():
    print("=" * 80)
    print("m_accountシート完全インポート（VR照合対応・スペースなし実装）")
    print("実行計画書EXECUTION_PLAN_20251202.md準拠")
    print("=" * 80)

    # データベース接続設定
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL環境変数が設定されていません")
        sys.exit(1)

    excel_file = '/Users/lennon/projects/talent-casting-form/DB情報/Nowデータ_20251126.xlsx'
    sheet_name = 'm_account'  # 実行計画書で明確に指定

    print(f"Excel file: {excel_file}")
    print(f"Sheet: {sheet_name} (4,819人期待)")
    print()

    try:
        # SQLAlchemy エンジン作成
        engine = create_engine(database_url)

        print("🧹 既存データクリア中...")

        # 外部キー制約順序で削除
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

        print(f"📥 m_accountシート読み込み中...")
        print(f"📖 Reading {excel_file}...")

        # Excelファイル読み込み（必ずm_accountシート）
        df = pd.read_excel(excel_file, sheet_name=sheet_name)
        print(f"   Total records: {len(df):,}")

        # データ構造確認
        if len(df) != 4819:
            print(f"⚠️  Warning: Expected 4,819 records, got {len(df):,}")

        # del_flag分布確認
        if 'del_flag' in df.columns:
            active_count = len(df[df['del_flag'] == 0])
            deleted_count = len(df[df['del_flag'] == 1])
            print(f"   Active records (del_flag=0): {active_count:,}")
            print(f"   Deleted records (del_flag=1): {deleted_count:,}")

        # first_name有無確認
        if 'first_name' in df.columns:
            with_first = len(df[df['first_name'].notna()])
            without_first = len(df[df['first_name'].isna()])
            print(f"   Records with first_name: {with_first:,}")
            print(f"   Records without first_name: {without_first:,}")
        print()

        print("🔄 Processing talent records with spaceless names...")

        success_count = 0
        error_count = 0
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
                display_name = create_display_name_spaceless(last_name, first_name)
                if not display_name:
                    error_count += 1
                    continue

                # 最小限のデータ処理（実際のDB schema準拠）
                name_normalized = display_name  # VR照合用

                # 基本データのみ（データベース schema準拠）
                record_data = {
                    'account_id': account_id,
                    'name': display_name,  # スペースなし（VR照合用）
                    'name_normalized': name_normalized,
                    'kana': str(row['last_name_kana']).strip() if pd.notna(row['last_name_kana']) else None,
                    'gender': str(row['gender_type_cd']).strip() if pd.notna(row['gender_type_cd']) else None,
                    'birth_year': None,  # 後で処理
                    'birthday': row['birthday'] if pd.notna(row['birthday']) else None,
                    'category': str(row['act_genre']).strip() if pd.notna(row['act_genre']) else None,
                    'company_name': str(row['company_name']).strip() if pd.notna(row['company_name']) else None,
                    'image_name': str(row['image_name']).strip() if pd.notna(row['image_name']) else None,
                    'del_flag': int(row['del_flag']) if pd.notna(row['del_flag']) else 0,
                }

                # birth_year計算（birthday から）
                if record_data['birthday'] and hasattr(record_data['birthday'], 'year'):
                    record_data['birth_year'] = record_data['birthday'].year

                insert_data.append(record_data)
                success_count += 1

                # 進捗表示
                if success_count % 500 == 0:
                    print(f"   Processing: {success_count:,}/{len(df):,} ({success_count/len(df)*100:.1f}%)")

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
                        account_id, name, name_normalized, kana, gender,
                        birth_year, birthday, category, company_name, image_name,
                        del_flag, created_at, updated_at
                    ) VALUES (
                        :account_id, :name, :name_normalized, :kana, :gender,
                        :birth_year, :birthday, :category, :company_name, :image_name,
                        :del_flag, NOW(), NOW()
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

            # 名前サンプル確認（VR照合形式・スペースなし）
            sample_result = conn.execute(text("""
                SELECT account_id, name, company_name
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
            company = sample[2] if sample[2] else 'N/A'
            print(f"  ID{sample[0]}: \"{sample[1]}\" ({company})")
        print()

        # VR照合完了判定
        expected_total = 4819
        completion_rate = (total_count / expected_total) * 100
        print(f"✅ VR照合対応インポート進捗: {total_count:,}/{expected_total:,} ({completion_rate:.1f}%)")

        if completion_rate >= 99.5:
            print("🎉 VR照合対応！m_accountシート完全インポート成功！")
            print("📋 次のステップ: 残り9シートのインポート（Phase 1.2）")
        else:
            print("⚠️ インポートが不完全です。確認が必要です。")

        print()
        print("=" * 80)
        print("m_accountシートインポート完了（スペースなし名前実装済み）")
        print("=" * 80)

    except Exception as e:
        print(f"❌ Critical Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()