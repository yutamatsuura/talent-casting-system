#!/usr/bin/env python3
"""CM履歴データ完全修正インポート（NaN値対応版）"""

import asyncio
import sys
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, date
import re

sys.path.insert(0, str(Path(__file__).parent))
from sqlalchemy import text, insert
from app.db.connection import init_db, get_session_maker
from app.models import TalentCmHistory, Talent

# データファイルパス
EXCEL_PATH = "/Users/lennon/projects/talent-casting-form/DB情報/Nowデータ_20251126.xlsx"

AsyncSessionLocal = None

async def get_async_session():
    global AsyncSessionLocal
    if AsyncSessionLocal is None:
        await init_db()
        AsyncSessionLocal = get_session_maker()
    return AsyncSessionLocal()

def normalize_name(name):
    """タレント名の正規化（スペース除去）"""
    if pd.isna(name) or name is None:
        return None
    normalized = re.sub(r'[\s\u3000\u00A0\u2000-\u200A\u2028\u2029\u202F\u205F]+', '', str(name))
    return normalized.strip()

def convert_date_string(date_str):
    """日付文字列をdateオブジェクトに変換"""
    if pd.isna(date_str) or date_str is None:
        return None

    # 既にdateオブジェクトの場合
    if isinstance(date_str, date):
        return date_str

    # 文字列の場合
    if isinstance(date_str, str):
        date_str = date_str.strip()
        if not date_str:
            return None

        # 一般的な日付フォーマットをパース
        date_formats = [
            '%Y-%m-%d',      # 2020-12-25
            '%Y/%m/%d',      # 2020/12/25
            '%Y年%m月%d日',   # 2020年12月25日
            '%m/%d/%Y',      # 12/25/2020
            '%d/%m/%Y',      # 25/12/2020
        ]

        for fmt in date_formats:
            try:
                return datetime.strptime(date_str, fmt).date()
            except ValueError:
                continue

        print(f"⚠️  Unable to parse date: {date_str}")
        return None

    return None

def safe_int_convert(value):
    """NaN安全な整数変換"""
    if pd.isna(value) or value is None:
        return None

    if isinstance(value, (int, np.integer)):
        return int(value)

    if isinstance(value, (float, np.floating)):
        if np.isnan(value):
            return None
        return int(value)

    if isinstance(value, str):
        value = value.strip()
        if not value:
            return None
        try:
            return int(float(value))
        except (ValueError, TypeError):
            return None

    return None

def safe_str_convert(value):
    """NaN安全な文字列変換"""
    if pd.isna(value) or value is None:
        return None

    if isinstance(value, str):
        value = value.strip()
        return value if value else None

    return str(value).strip() if str(value).strip() != 'nan' else None

async def import_cm_history_robust():
    """CM履歴データの完全インポート（堅牢版）"""
    print("🎬 CM履歴データ完全インポート開始（堅牢版）")
    print("=" * 60)

    try:
        # 既存データクリア
        async with await get_async_session() as session:
            await session.execute(text("DELETE FROM talent_cm_history"))
            await session.commit()
            print("🧹 既存CM履歴データクリア完了")

        # Excelファイル読み込み
        df = pd.read_excel(EXCEL_PATH, sheet_name='m_talent_cm')
        print(f"📋 総レコード数: {len(df):,}")

        # 基本情報表示
        print(f"📊 カラム数: {len(df.columns)}")
        print(f"🏷️  カラム名: {list(df.columns)}")

        async with await get_async_session() as session:
            # 既存のtalent_idマッピングを取得
            result = await session.execute(text("SELECT id, account_id FROM talents"))
            talent_mapping = {row[1]: row[0] for row in result}
            print(f"🆔 Talent mapping: {len(talent_mapping)} records")

            # CM履歴データ処理
            imported_count = 0
            error_count = 0
            skipped_count = 0

            print(f"\\n📥 CM履歴データ処理開始...")

            # バッチ処理でより効率的に
            batch_size = 100
            batch_data = []

            for index, row in df.iterrows():
                try:
                    # account_idから対応するtalent_idを取得
                    account_id = safe_int_convert(row.get('account_id'))
                    if account_id is None or account_id not in talent_mapping:
                        skipped_count += 1
                        continue

                    talent_id = talent_mapping[account_id]

                    # 日付フィールドの変換
                    use_period_start = convert_date_string(row.get('use_period_start'))
                    use_period_end = convert_date_string(row.get('use_period_end'))

                    # regist_dateの処理
                    regist_date = None
                    regist_date_raw = row.get('regist_date')
                    if pd.notna(regist_date_raw):
                        if isinstance(regist_date_raw, pd.Timestamp):
                            regist_date = regist_date_raw
                        else:
                            try:
                                regist_date = pd.to_datetime(regist_date_raw)
                            except:
                                pass

                    # up_dateの処理 (up_dateカラムがない可能性もある)
                    up_date = None
                    if 'up_date' in df.columns:
                        up_date_raw = row.get('up_date')
                        if pd.notna(up_date_raw):
                            if isinstance(up_date_raw, pd.Timestamp):
                                up_date = up_date_raw
                            else:
                                try:
                                    up_date = pd.to_datetime(up_date_raw)
                                except:
                                    pass

                    # バッチデータに追加
                    batch_data.append({
                        'talent_id': talent_id,
                        'sub_id': safe_int_convert(row.get('sub_id', 1)) or 1,
                        'client_name': safe_str_convert(row.get('client_name')),
                        'product_name': safe_str_convert(row.get('product_name')),
                        'use_period_start': use_period_start,
                        'use_period_end': use_period_end,
                        'rival_category_type_cd1': safe_int_convert(row.get('rival_category_type_cd1')),
                        'rival_category_type_cd2': safe_int_convert(row.get('rival_category_type_cd2')),
                        'rival_category_type_cd3': safe_int_convert(row.get('rival_category_type_cd3')),
                        'rival_category_type_cd4': safe_int_convert(row.get('rival_category_type_cd4')),
                        'note': safe_str_convert(row.get('note')),
                        'regist_date': regist_date,
                        'up_date': up_date
                    })

                    # バッチサイズに達したら一括インサート
                    if len(batch_data) >= batch_size:
                        await execute_batch_insert(session, batch_data)
                        imported_count += len(batch_data)
                        print(f"   処理済み: {imported_count:,} records...")
                        batch_data = []

                except Exception as e:
                    error_count += 1
                    if error_count <= 5:  # 最初の5エラーのみ表示
                        print(f"⚠️  Row {index} error: {e}")

            # 残りのバッチデータ処理
            if batch_data:
                await execute_batch_insert(session, batch_data)
                imported_count += len(batch_data)

            await session.commit()

            # 最終確認
            result = await session.execute(text("SELECT COUNT(*) FROM talent_cm_history"))
            final_count = result.scalar()

            print(f"\\n✅ CM履歴インポート完了！")
            print(f"   📊 インポート: {imported_count:,} records")
            print(f"   ⚠️  スキップ: {skipped_count:,} records")
            print(f"   ❌ エラー: {error_count:,} records")
            print(f"   💾 最終レコード数: {final_count:,} records")
            print(f"   📈 成功率: {(final_count / len(df) * 100):.1f}%")

            return True

    except Exception as e:
        print(f"❌ CM履歴インポートエラー: {e}")
        import traceback
        traceback.print_exc()
        return False

async def execute_batch_insert(session, batch_data):
    """バッチデータの一括インサート"""
    if not batch_data:
        return

    insert_sql = text("""
        INSERT INTO talent_cm_history
        (talent_id, sub_id, client_name, product_name, use_period_start, use_period_end,
         rival_category_type_cd1, rival_category_type_cd2, rival_category_type_cd3, rival_category_type_cd4,
         note, regist_date, up_date, created_at, updated_at)
        VALUES (:talent_id, :sub_id, :client_name, :product_name, :use_period_start, :use_period_end,
                :rival_category_type_cd1, :rival_category_type_cd2, :rival_category_type_cd3, :rival_category_type_cd4,
                :note, :regist_date, :up_date, NOW(), NOW())
    """)

    for data in batch_data:
        await session.execute(insert_sql, data)

async def main():
    try:
        success = await import_cm_history_robust()

        if success:
            print("\\n🎉 CM履歴データ完全修正完了！")

            # 全体の進捗確認
            async with await get_async_session() as session:
                result = await session.execute(text("""
                    SELECT COUNT(*) as total FROM (
                        SELECT 1 FROM talents
                        UNION ALL
                        SELECT 1 FROM talent_cm_history
                        UNION ALL
                        SELECT 1 FROM talent_media_experience
                        UNION ALL
                        SELECT 1 FROM talent_business_info
                        UNION ALL
                        SELECT 1 FROM talent_pricing
                        UNION ALL
                        SELECT 1 FROM talent_contacts
                        UNION ALL
                        SELECT 1 FROM talent_notes
                        UNION ALL
                        SELECT 1 FROM talent_deal_results
                        UNION ALL
                        SELECT 1 FROM talent_movies
                        UNION ALL
                        SELECT 1 FROM talent_keywords
                    ) combined
                """))
                total_excel_records = result.scalar()
                completion_rate = (total_excel_records / 28387) * 100

                print(f"\\n📊 完成状況:")
                print(f"   Excelデータ: {total_excel_records:,} / 28,387 records")
                print(f"   完成率: {completion_rate:.1f}%")
                print(f"\\n🚀 次のステップ: VR/TPRデータインポート")

            return True
        else:
            print("\\n❌ CM履歴データ修正失敗")
            return False

    except Exception as e:
        print(f"\\n❌ メインエラー: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)