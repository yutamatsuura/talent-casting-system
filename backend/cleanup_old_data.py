#!/usr/bin/env python3
"""
今日以外のフォーム送信履歴と診断結果を直接削除するスクリプト
"""
import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

async def main():
    try:
        # データベースに接続
        db_url = os.getenv('DATABASE_URL')
        if not db_url:
            print("❌ DATABASE_URL環境変数が設定されていません")
            return

        conn = await asyncpg.connect(db_url)

        print("📊 データクリーンアップ開始...")
        print("=" * 60)

        # 1. 現在の状況確認
        print("1. 現在のデータ状況確認中...")
        status_query = """
        SELECT
            DATE(created_at) as submission_date,
            COUNT(*) as count
        FROM form_submissions
        GROUP BY DATE(created_at)
        ORDER BY submission_date;
        """

        results = await conn.fetch(status_query)

        print("📅 日別フォーム送信件数:")
        total_submissions = 0
        today_submissions = 0
        old_submissions = 0

        for row in results:
            count = row['count']
            date = row['submission_date'].strftime('%Y-%m-%d')
            total_submissions += count

            if date == '2025-12-10':
                today_submissions = count
                print(f"   {date}: {count}件 ⭐ (今日・保持対象)")
            else:
                old_submissions += count
                print(f"   {date}: {count}件 (削除対象)")

        print(f"\n📈 集計:")
        print(f"   総送信件数: {total_submissions}件")
        print(f"   今日(2025-12-10): {today_submissions}件 (保持)")
        print(f"   今日以外: {old_submissions}件 (削除予定)")

        if old_submissions == 0:
            print("\n✅ 削除対象のデータはありません。処理を終了します。")
            await conn.close()
            return

        # 2. 確認
        print(f"\n⚠️  {old_submissions}件のデータを削除しようとしています。")
        confirm = input("続行しますか？ (yes/no): ")

        if confirm.lower() != 'yes':
            print("❌ 処理をキャンセルしました。")
            await conn.close()
            return

        print("\n🗑️  データ削除開始...")

        # 3. 診断結果を先に削除（外部キー制約対応）
        print("   古い診断結果を削除中...")
        delete_diagnosis_query = """
            DELETE FROM diagnosis_results
            WHERE form_submission_id IN (
                SELECT id FROM form_submissions
                WHERE DATE(created_at) != '2025-12-10'
            )
        """

        diagnosis_result = await conn.execute(delete_diagnosis_query)
        deleted_diagnosis_count = int(diagnosis_result.split()[-1])
        print(f"   ✅ 診断結果 {deleted_diagnosis_count}件を削除しました")

        # 4. フォーム送信を削除
        print("   古いフォーム送信を削除中...")
        delete_submissions_query = """
            DELETE FROM form_submissions
            WHERE DATE(created_at) != '2025-12-10'
        """

        submission_result = await conn.execute(delete_submissions_query)
        deleted_submissions_count = int(submission_result.split()[-1])
        print(f"   ✅ フォーム送信 {deleted_submissions_count}件を削除しました")

        # 5. 削除後の状況確認
        print("\n📊 削除後の状況確認...")
        final_count_query = """
        SELECT
            'form_submissions' as table_name,
            COUNT(*) as remaining_count
        FROM form_submissions
        UNION ALL
        SELECT
            'diagnosis_results' as table_name,
            COUNT(*) as remaining_count
        FROM diagnosis_results;
        """

        final_results = await conn.fetch(final_count_query)

        for row in final_results:
            table_name = row['table_name']
            count = row['remaining_count']
            print(f"   {table_name}: {count}件 (残存)")

        print("\n✅ データクリーンアップ完了!")
        print(f"   削除されたフォーム送信: {deleted_submissions_count}件")
        print(f"   削除された診断結果: {deleted_diagnosis_count}件")
        print(f"   保持されたデータ: 今日(2025-12-10)のデータのみ")

        await conn.close()

    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())