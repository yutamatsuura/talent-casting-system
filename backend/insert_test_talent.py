#!/usr/bin/env python3
"""最小限のテストタレントデータ投入（マッチング動作確認用）"""
import asyncio
import asyncpg
import os
from dotenv import load_dotenv

# 環境変数をロード
load_dotenv('/Users/lennon/projects/talent-casting-form/.env.local')

async def insert_test_talents():
    """最小限のテストタレントデータを投入"""
    database_url = os.getenv('DATABASE_URL')

    print(f"🔗 データベース接続中...")

    try:
        conn = await asyncpg.connect(database_url)
        print("✅ データベース接続成功")

        # target_segments と image_items の情報を取得
        segments = await conn.fetch("SELECT id, name FROM target_segments ORDER BY id LIMIT 3")
        images = await conn.fetch("SELECT id, name FROM image_items ORDER BY id LIMIT 3")

        if not segments or not images:
            print("❌ target_segments または image_items データが不足しています")
            return

        print(f"📊 利用可能ターゲット層: {len(segments)}件")
        print(f"📊 利用可能イメージ項目: {len(images)}件")

        # 既存データの確認と削除
        existing_talents = await conn.fetchval("SELECT COUNT(*) FROM talents")
        if existing_talents > 0:
            await conn.execute("DELETE FROM talent_images")
            await conn.execute("DELETE FROM talent_scores")
            await conn.execute("DELETE FROM talents")
            print("🗑️  既存テストデータを削除しました")

        # テストタレントデータ（CLAUDE.md準拠の予算内）
        test_talents = [
            {"account_id": 1001, "name": "テスト太郎", "kana": "テストタロウ", "category": "俳優", "money_max_one_year": 25000000},  # 2500万円（範囲内）
            {"account_id": 1002, "name": "サンプル花子", "kana": "サンプルハナコ", "category": "女優", "money_max_one_year": 15000000},  # 1500万円（範囲内）
            {"account_id": 1003, "name": "ダミー次郎", "kana": "ダミージロウ", "category": "歌手", "money_max_one_year": 35000000},  # 3500万円（範囲外・除外確認用）
        ]

        print("\n📥 テストタレントデータを投入中...")

        # talentsテーブルに投入
        talent_ids = []
        for talent in test_talents:
            talent_id = await conn.fetchval("""
                INSERT INTO talents (account_id, name, kana, category, money_max_one_year)
                VALUES ($1, $2, $3, $4, $5)
                RETURNING id
            """, talent["account_id"], talent["name"], talent["kana"], talent["category"], talent["money_max_one_year"])

            talent_ids.append(talent_id)
            print(f"  ✅ {talent['name']} (¥{talent['money_max_one_year']:,}) - ID: {talent_id}")

        print("\n📥 talent_scoresデータを投入中...")

        # talent_scoresテーブルに基本データを投入
        for talent_id in talent_ids:
            for segment in segments:
                vr_score = 70.0 + (talent_id % 15) + (segment["id"] % 5)  # 70-90の範囲でダミーVRスコア
                tpr_score = 75.0 + (talent_id % 12) + (segment["id"] % 8)  # 75-95の範囲でダミーTPRスコア
                base_score = (vr_score + tpr_score) / 2  # 基礎パワー得点は平均値
                await conn.execute("""
                    INSERT INTO talent_scores (talent_id, target_segment_id, vr_popularity, tpr_power_score, base_power_score)
                    VALUES ($1, $2, $3, $4, $5)
                """, talent_id, segment["id"], vr_score, tpr_score, base_score)

        print(f"  ✅ {len(talent_ids)} タレント × {len(segments)} ターゲット層 = {len(talent_ids) * len(segments)} 件")

        print("\n📥 talent_imagesデータを投入中...")

        # talent_imagesテーブルに基本データを投入
        image_count = 0
        for talent_id in talent_ids:
            for segment in segments:
                for image in images:
                    score = 50.0 + (talent_id + segment["id"] + image["id"]) % 40  # 50-90の範囲でダミースコア
                    await conn.execute("""
                        INSERT INTO talent_images (talent_id, target_segment_id, image_item_id, score)
                        VALUES ($1, $2, $3, $4)
                    """, talent_id, segment["id"], image["id"], score)
                    image_count += 1

        print(f"  ✅ {image_count} 件のイメージデータを投入")

        # 投入結果の確認
        print("\n📊 投入結果:")
        final_talents = await conn.fetchval("SELECT COUNT(*) FROM talents")
        final_scores = await conn.fetchval("SELECT COUNT(*) FROM talent_scores")
        final_images = await conn.fetchval("SELECT COUNT(*) FROM talent_images")

        print(f"  - talents: {final_talents}件")
        print(f"  - talent_scores: {final_scores}件")
        print(f"  - talent_images: {final_images}件")

        await conn.close()
        print("\n✅ テストタレントデータの投入が完了しました")
        print("🎯 これでマッチング機能のテストが可能になりました")

    except Exception as e:
        print(f"❌ エラー発生: {str(e)}")

if __name__ == "__main__":
    asyncio.run(insert_test_talents())