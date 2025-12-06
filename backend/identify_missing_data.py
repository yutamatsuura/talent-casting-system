#!/usr/bin/env python3
"""
VR処理で未処理となったデータの特定
"""
import asyncio
import asyncpg
import os
import pandas as pd
import chardet
from glob import glob

async def identify_missing_data():
    """未処理データを特定して分析"""

    database_url = os.getenv('DATABASE_URL')
    conn = await asyncpg.connect(database_url)

    try:
        print("=== VR処理未処理データの特定 ===")
        print()

        # 1. データベースに既存のtalent_scoresを取得
        existing_talent_ids = await conn.fetch("""
            SELECT DISTINCT ts.talent_id, t.name, t.account_id
            FROM talent_scores ts
            INNER JOIN talents t ON t.id = ts.talent_id
            ORDER BY ts.talent_id
        """)

        existing_talent_names = {record['name']: record['talent_id'] for record in existing_talent_ids}
        print(f"1. データベース既存タレント数: {len(existing_talent_names):,}人")

        # 2. VRファイルから全タレント名を収集
        vr_directories = [
            "/Users/lennon/projects/talent-casting-form/DB情報/【VR①】C列の人気度と、E～K列の各種イメージを採用する想定です",
            "/Users/lennon/projects/talent-casting-form/DB情報/【VR②】C列の人気度と、E～K列の各種イメージを採用する想定です",
            "/Users/lennon/projects/talent-casting-form/DB情報/【VR③】C列の人気度と、E～K列の各種イメージを採用する想定です"
        ]

        all_vr_talents = set()
        file_count = 0

        for directory in vr_directories:
            if os.path.exists(directory):
                csv_files = glob(os.path.join(directory, "*.csv"))
                for csv_file in csv_files:
                    try:
                        # エンコーディング検出
                        with open(csv_file, 'rb') as f:
                            raw_data = f.read(10000)
                            result = chardet.detect(raw_data)
                            encoding = 'shift_jis' if result['encoding'] in ['SHIFT_JIS', 'CP932'] else 'utf-8'

                        # CSVファイル読み込み（B列＝タレント名）
                        df = pd.read_csv(csv_file, encoding=encoding)
                        if len(df.columns) > 1:
                            # 4行目以降からB列のタレント名を取得（ヘッダー行をスキップ）
                            talent_names = df.iloc[3:, 1].dropna().unique()  # B列のタレント名（4行目から）
                            all_vr_talents.update(talent_names)
                            file_count += 1

                    except Exception as e:
                        filename = os.path.basename(csv_file)
                        print(f"❌ {filename}: 読み込みエラー: {e}")

        print(f"2. VRファイルから読み込み: {len(all_vr_talents):,}人（{file_count}ファイル）")

        # 3. 未処理タレントの特定
        missing_talents = []
        for vr_talent_name in all_vr_talents:
            if vr_talent_name not in existing_talent_names:
                missing_talents.append(vr_talent_name)

        print(f"3. 未処理タレント数: {len(missing_talents)}人")
        print()

        # 4. 未処理タレントの詳細分析
        if missing_talents:
            print("=== 未処理タレント詳細 ===")

            # データベース内でのタレント検索（部分一致）
            print("データベース内での名前検索結果:")
            for i, missing_name in enumerate(missing_talents[:10], 1):  # 最初の10人
                print(f"{i}. VR表記: '{missing_name}'")

                # データベース内で類似名検索
                similar_talents = await conn.fetch("""
                    SELECT name, account_id
                    FROM talents
                    WHERE name ILIKE $1 OR name ILIKE $2
                    LIMIT 3
                """, f"%{missing_name}%", f"%{missing_name.replace('　', ' ')}%")

                if similar_talents:
                    print("   データベース内類似名:")
                    for st in similar_talents:
                        print(f"     - {st['name']} (ID: {st['account_id']})")
                else:
                    print("   データベース内に類似名なし")
                print()

            if len(missing_talents) > 10:
                print(f"... 他{len(missing_talents) - 10}人")

        # 5. 重複・データベース不整合の確認
        print("\n=== データ整合性確認 ===")

        # talent_scoresの重複確認
        duplicates = await conn.fetch("""
            SELECT talent_id, target_segment_id, COUNT(*) as count
            FROM talent_scores
            GROUP BY talent_id, target_segment_id
            HAVING COUNT(*) > 1
            LIMIT 5
        """)

        if duplicates:
            print(f"talent_scores重複レコード: {len(duplicates)}件")
            for dup in duplicates:
                print(f"  talent_id={dup['talent_id']}, segment_id={dup['target_segment_id']}, 重複数={dup['count']}")
        else:
            print("talent_scores重複レコード: なし")

        print()
        print("=== 調査結果サマリ ===")
        print(f"📊 VRファイル総タレント数: {len(all_vr_talents):,}人")
        print(f"📊 データベース処理済み: {len(existing_talent_names):,}人")
        print(f"🚨 未処理データ: {len(missing_talents)}人")
        print()

        if len(missing_talents) > 0:
            print("次のステップ:")
            print("1. 未処理タレントの名前正規化・マッピング確認")
            print("2. データベース内での正確な名前検索")
            print("3. 手動でのマッピング修正・データ追加")

    except Exception as e:
        print(f"❌ エラー: {e}")
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(identify_missing_data())