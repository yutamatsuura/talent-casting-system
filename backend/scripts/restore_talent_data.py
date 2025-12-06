#!/usr/bin/env python3
"""
完全タレントデータ復旧スクリプト
元データ（TPR + VRファイル）から全タレントデータを復元
"""

import asyncio
import asyncpg
import pandas as pd
import os
import sys
from pathlib import Path
from typing import Dict, List, Tuple
import hashlib
import re

# プロジェクトルートを追加
sys.path.insert(0, str(Path(__file__).parent.parent))

# データベース接続関数
async def get_db_connection():
    """データベース接続を取得"""
    # 環境変数からDATABASE_URLを取得
    env_path = Path(__file__).parent.parent.parent / ".env.local"
    database_url = None

    with open(env_path, "r") as f:
        for line in f:
            if line.startswith("DATABASE_URL="):
                database_url = line.strip().split("=", 1)[1]
                break

    if not database_url:
        raise ValueError("DATABASE_URL not found in .env.local")

    # PostgreSQL URLをasyncpg用に変換
    database_url = database_url.replace("postgresql://", "postgresql+asyncpg://")
    from urllib.parse import urlparse, urlunparse
    parsed = urlparse(database_url)
    # asyncpg用にスキームを戻す
    asyncpg_url = database_url.replace("postgresql+asyncpg://", "postgresql://")

    return await asyncpg.connect(asyncpg_url)

# 元データディレクトリ
BACKUP_BASE_DIR = "/Users/lennon/projects/talent-casting-form-backup-2025-11-30_詳細ページ実行前/DB情報"
TPR_DIR = f"{BACKUP_BASE_DIR}/【TPR】G列のパワースコアを採用する想定です"
VR_DIR_1 = f"{BACKUP_BASE_DIR}/【VR①】C列の人気度と、E～K列の各種イメージを採用する想定です"
VR_DIR_2 = f"{BACKUP_BASE_DIR}/【VR②】C列の人気度と、E～K列の各種イメージを採用する想定です"
VR_DIR_3 = f"{BACKUP_BASE_DIR}/【VR③】C列の人気度と、E～K列の各種イメージを採用する想定です"

# ターゲットセグメント マッピング
TARGET_SEGMENTS = {
    '男性10～19': 1,   # M1
    '男性20～34': 2,   # M2
    '男性35～49': 3,   # M3
    '男性50～69': 4,   # M4
    '女性10～19': 5,   # F1
    '女性20～34': 6,   # F2
    '女性35～49': 7,   # F3
    '女性50～69': 8    # F4
}

# イメージアイテム マッピング (image_items.idに対応)
IMAGE_ITEMS = {
    '若々しい': 1,
    '上品な': 2,
    '親しみやすい': 3,
    '信頼できる': 4,
    '知的な': 5,
    'さわやかな': 6,
    'かっこいい': 7
}

async def read_csv_safe(file_path: str) -> pd.DataFrame:
    """CSVファイルを安全に読み込み（文字化け対応）"""
    try:
        # まずUTF-8で試行
        df = pd.read_csv(file_path, encoding='utf-8')
        print(f"✅ UTF-8で読み込み成功: {os.path.basename(file_path)}")
        return df
    except UnicodeDecodeError:
        try:
            # Shift_JISで試行
            df = pd.read_csv(file_path, encoding='shift_jis')
            print(f"✅ Shift_JISで読み込み成功: {os.path.basename(file_path)}")
            return df
        except Exception as e:
            print(f"❌ CSVファイル読み込みエラー: {file_path}")
            print(f"エラー詳細: {e}")
            return pd.DataFrame()

def extract_target_from_filename(filename: str) -> str:
    """ファイル名からターゲット層を抽出"""
    # TPRファイル: TPR_女性20～34_202508.csv
    # VRファイル: VR男性タレント_女性20～34_202507.csv

    patterns = [
        r'_([男女]性\d+～\d+)_',  # TPR形式
        r'_([男女]性\d+～\d+)\.csv',  # VR形式（最後）
    ]

    for pattern in patterns:
        match = re.search(pattern, filename)
        if match:
            return match.group(1)

    print(f"⚠️ ファイル名からターゲット層抽出失敗: {filename}")
    return ""

def generate_talent_id(name: str, kana: str = "") -> int:
    """タレント名から一意のIDを生成"""
    # 名前 + よみがなでハッシュ生成、数値に変換
    combined = f"{name}_{kana}".strip('_')
    hash_obj = hashlib.md5(combined.encode('utf-8'))
    # ハッシュの先頭8文字を16進数として解釈し整数に変換
    return int(hash_obj.hexdigest()[:8], 16) % 2147483647  # PostgreSQL INT範囲内

async def load_tpr_data() -> Tuple[Dict[int, dict], Dict[Tuple[int, int], float]]:
    """TPRデータ（パワースコア）を読み込み"""
    talents = {}  # talent_id -> {name, kana, etc.}
    scores = {}   # (talent_id, target_segment_id) -> power_score

    print("\n🔄 TPRデータ読み込み開始...")

    tpr_files = [
        "TPR_男性10～19_202508.csv",
        "TPR_男性20～34_202508.csv",
        "TPR_男性35～49_202508.csv",
        "TPR_男性50～69_202508.csv",
        "TPR_女性10～19_202508.csv",
        "TPR_女性20～34_202508.csv",
        "TPR_女性35～49_202508.csv",
        "TPR_女性50～69_202508.csv"
    ]

    for filename in tpr_files:
        file_path = f"{TPR_DIR}/{filename}"
        if not os.path.exists(file_path):
            print(f"⚠️ TPRファイル見つからず: {filename}")
            continue

        target_key = extract_target_from_filename(filename)
        if target_key not in TARGET_SEGMENTS:
            print(f"⚠️ ターゲット層マッピング失敗: {target_key}")
            continue

        target_segment_id = TARGET_SEGMENTS[target_key]

        df = await read_csv_safe(file_path)
        if df.empty:
            continue

        print(f"📊 TPRファイル: {filename} - {len(df)}件")

        for _, row in df.iterrows():
            # TPR実際のカラム構造: 順位,前回,前々回,タレント名,タレント名(全角カナ),年齢,スコア,認知度,誘引率
            try:
                name = str(row.iloc[3]).strip()  # 4列目: タレント名
                kana = str(row.iloc[4]).strip()  # 5列目: タレント名(全角カナ)
                power_score = row.iloc[6]        # 7列目: スコア
                age = row.iloc[5]                # 6列目: 年齢
            except (IndexError, KeyError):
                # カラム名でも試行
                name = str(row.get('タレント名', '')).strip()
                kana = str(row.get('タレント名(全角カナ)', '')).strip()
                power_score = row.get('スコア', 0)
                age = row.get('年齢', 0)

            if not name or name == 'nan':
                continue

            talent_id = generate_talent_id(name, kana)

            # タレント基本情報登録
            if talent_id not in talents:
                # 事務所情報の取得（TPRファイルには含まれていない可能性が高い）
                company_name = ""
                # 年齢の処理
                try:
                    age_value = int(float(age)) if age and str(age) != 'nan' else None
                except (ValueError, TypeError):
                    age_value = None

                talents[talent_id] = {
                    'name': name,
                    'kana': kana,
                    'company_name': company_name,
                    'age': age_value
                }

            # スコア登録
            try:
                power_score = float(power_score)
                scores[(talent_id, target_segment_id)] = power_score
            except (ValueError, TypeError):
                print(f"⚠️ パワースコア変換エラー: {name} - {power_score}")

    print(f"✅ TPRデータ読み込み完了: タレント{len(talents)}人, スコア{len(scores)}件")
    return talents, scores

async def load_vr_data() -> Tuple[Dict[Tuple[int, int], float], Dict[Tuple[int, int, int], float]]:
    """VRデータ（人気度・イメージスコア）を読み込み"""
    popularity_scores = {}  # (talent_id, target_segment_id) -> popularity
    image_scores = {}       # (talent_id, target_segment_id, image_item_id) -> score

    print("\n🔄 VRデータ読み込み開始...")

    vr_directories = [VR_DIR_1, VR_DIR_2, VR_DIR_3]

    for vr_dir in vr_directories:
        if not os.path.exists(vr_dir):
            print(f"⚠️ VRディレクトリ見つからず: {vr_dir}")
            continue

        for filename in os.listdir(vr_dir):
            if not filename.endswith('.csv'):
                continue

            file_path = f"{vr_dir}/{filename}"
            target_key = extract_target_from_filename(filename)

            if target_key not in TARGET_SEGMENTS:
                print(f"⚠️ ターゲット層マッピング失敗: {target_key} ({filename})")
                continue

            target_segment_id = TARGET_SEGMENTS[target_key]

            df = await read_csv_safe(file_path)
            if df.empty:
                continue

            print(f"📊 VRファイル: {filename} - {len(df)}件")

            for _, row in df.iterrows():
                # VR実際のカラム構造: 順位,タレント名,人気度,認知度,若々しい,上品な,親しみやすい,信頼できる,知的な,さわやかな,かっこいい
                try:
                    if len(df.columns) < 4:  # ヘッダー行をスキップ
                        continue
                    name = str(row.iloc[1]).strip()  # 2列目: タレント名
                    popularity = row.iloc[2]         # 3列目: 人気度
                except (IndexError, KeyError):
                    # カラム名でも試行
                    name = str(row.get('タレント名', '')).strip()
                    popularity = row.get('人気度', 0)

                if not name or name == 'nan':
                    continue

                talent_id = generate_talent_id(name)

                # 人気度スコア
                try:
                    popularity = float(popularity)
                    popularity_scores[(talent_id, target_segment_id)] = popularity
                except (ValueError, TypeError):
                    pass

                # イメージスコア（5～11列目）
                image_mappings = [
                    (4, '若々しい'),      # 5列目
                    (5, '上品な'),        # 6列目
                    (6, '親しみやすい'),  # 7列目
                    (7, '信頼できる'),    # 8列目
                    (8, '知的な'),        # 9列目
                    (9, 'さわやかな'),    # 10列目
                    (10, 'かっこいい')    # 11列目
                ]

                for col_index, image_name in image_mappings:
                    if image_name not in IMAGE_ITEMS:
                        continue

                    image_item_id = IMAGE_ITEMS[image_name]

                    try:
                        image_score = row.iloc[col_index] if len(row) > col_index else 0
                        image_score = float(image_score)
                        image_scores[(talent_id, target_segment_id, image_item_id)] = image_score
                    except (ValueError, TypeError, IndexError):
                        pass

    print(f"✅ VRデータ読み込み完了: 人気度{len(popularity_scores)}件, イメージ{len(image_scores)}件")
    return popularity_scores, image_scores

async def restore_data_to_database():
    """データベースに完全復元"""
    print("\n🚀 データベース復元開始...")

    # データ読み込み
    talents, tpr_scores = await load_tpr_data()
    popularity_scores, image_scores = await load_vr_data()

    if not talents:
        print("❌ タレントデータが見つかりません")
        return

    # データベース接続
    conn = await get_db_connection()

    try:
        # トランザクション開始
        await conn.execute("BEGIN")

        # 1. タレントテーブル復元
        print(f"\n📝 タレントデータ投入: {len(talents)}件")
        talent_count = 0

        for talent_id, talent_info in talents.items():
            try:
                await conn.execute("""
                    INSERT INTO talents (id, name, kana, company_name, age)
                    VALUES ($1, $2, $3, $4, $5)
                    ON CONFLICT (id) DO NOTHING
                """, talent_id, talent_info['name'], talent_info['kana'],
                talent_info['company_name'], talent_info['age'])
                talent_count += 1
            except Exception as e:
                print(f"⚠️ タレント登録エラー: {talent_info['name']} - {e}")

        # 2. タレントスコアテーブル復元
        print(f"\n📊 スコアデータ投入開始...")
        score_count = 0

        for (talent_id, target_segment_id), power_score in tpr_scores.items():
            # 対応する人気度スコア取得
            vr_popularity = popularity_scores.get((talent_id, target_segment_id), 0)

            try:
                await conn.execute("""
                    INSERT INTO talent_scores
                    (talent_id, target_segment_id, vr_popularity, tpr_power_score)
                    VALUES ($1, $2, $3, $4)
                    ON CONFLICT (talent_id, target_segment_id) DO UPDATE SET
                    vr_popularity = EXCLUDED.vr_popularity,
                    tpr_power_score = EXCLUDED.tpr_power_score
                """, talent_id, target_segment_id, vr_popularity, power_score)
                score_count += 1
            except Exception as e:
                print(f"⚠️ スコア登録エラー: {talent_id} - {e}")

        # 3. タレントイメージテーブル復元
        print(f"\n🎭 イメージデータ投入開始...")
        image_count = 0

        for (talent_id, target_segment_id, image_item_id), score in image_scores.items():
            try:
                await conn.execute("""
                    INSERT INTO talent_images
                    (talent_id, target_segment_id, image_item_id, score)
                    VALUES ($1, $2, $3, $4)
                    ON CONFLICT (talent_id, target_segment_id, image_item_id) DO UPDATE SET
                    score = EXCLUDED.score
                """, talent_id, target_segment_id, image_item_id, score)
                image_count += 1
            except Exception as e:
                print(f"⚠️ イメージ登録エラー: {talent_id} - {e}")

        # コミット
        await conn.execute("COMMIT")

        print(f"\n🎉 データ復元完了!")
        print(f"   📝 タレント: {talent_count}件")
        print(f"   📊 スコア: {score_count}件")
        print(f"   🎭 イメージ: {image_count}件")

    except Exception as e:
        await conn.execute("ROLLBACK")
        print(f"❌ データ復元エラー: {e}")
        raise
    finally:
        await conn.close()

async def verify_restoration():
    """復元後データ検証"""
    print("\n🔍 データ検証開始...")

    conn = await get_db_connection()
    try:
        # 件数確認
        talent_count = await conn.fetchval("SELECT COUNT(*) FROM talents")
        score_count = await conn.fetchval("SELECT COUNT(*) FROM talent_scores")
        image_count = await conn.fetchval("SELECT COUNT(*) FROM talent_images")

        print(f"📊 復元後データ件数:")
        print(f"   talents: {talent_count:,}件")
        print(f"   talent_scores: {score_count:,}件")
        print(f"   talent_images: {image_count:,}件")

        # サンプルデータ確認
        sample = await conn.fetchrow("""
            SELECT t.name, ts.vr_popularity, ts.tpr_power_score
            FROM talents t
            JOIN talent_scores ts ON t.id = ts.talent_id
            LIMIT 1
        """)

        if sample:
            print(f"\n🔍 サンプル確認:")
            print(f"   タレント: {sample['name']}")
            print(f"   VR人気度: {sample['vr_popularity']}")
            print(f"   TPRパワー: {sample['tpr_power_score']}")

    finally:
        await conn.close()

if __name__ == "__main__":
    print("🚀 タレントデータ完全復旧スクリプト開始")
    print("=" * 60)

    try:
        asyncio.run(restore_data_to_database())
        asyncio.run(verify_restoration())
        print("\n✅ 全ての処理が完了しました!")
    except Exception as e:
        print(f"\n❌ 処理中にエラーが発生: {e}")
        sys.exit(1)