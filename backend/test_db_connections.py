#!/usr/bin/env python3
"""
データベース接続テスト - 新旧認証情報の比較
"""
import asyncpg
import asyncio

# 00029-c7dで使用中の認証情報（古い）
OLD_DB_URL = "postgresql://neondb_owner:npg_5X1MlRZzVheF@ep-sparkling-smoke-a183z7h8-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require"

# 新規デプロイで使用した認証情報（新しい）
NEW_DB_URL = "postgresql://neondb_owner:npg_AhBGdkFKKnBu5VJa@ep-still-cloud-a1hnz7u1-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require"

async def test_connection(db_url, name):
    """データベース接続テスト"""
    try:
        # URL解析
        from urllib.parse import urlparse, parse_qs
        parsed = urlparse(db_url)
        query_params = parse_qs(parsed.query)

        # 接続パラメータ
        conn_params = {
            "host": parsed.hostname,
            "port": parsed.port or 5432,
            "user": parsed.username,
            "password": parsed.password,
            "database": parsed.path.lstrip('/'),
        }

        # SSL設定
        if query_params.get('sslmode', [''])[0] in ['require', 'verify-ca', 'verify-full']:
            conn_params['ssl'] = 'require'

        print(f"\n🔍 {name}接続テスト:")
        print(f"   Host: {conn_params['host']}")
        print(f"   User: {conn_params['user']}")
        print(f"   Password: {conn_params['password'][:8]}...")

        # 接続試行
        conn = await asyncpg.connect(**conn_params)

        # テストクエリ実行
        result = await conn.fetchval("SELECT 1 as test")
        talent_count = await conn.fetchval("SELECT COUNT(*) FROM m_account")

        await conn.close()

        print(f"   ✅ 接続成功!")
        print(f"   📊 テストクエリ結果: {result}")
        print(f"   👥 タレント総数: {talent_count}")
        return True

    except Exception as e:
        print(f"   ❌ 接続失敗: {str(e)}")
        return False

async def main():
    """メインテスト"""
    print("=" * 60)
    print("🧪 Neonデータベース接続テスト")
    print("=" * 60)

    # 古い認証情報テスト
    old_success = await test_connection(OLD_DB_URL, "旧認証情報")

    # 新しい認証情報テスト
    new_success = await test_connection(NEW_DB_URL, "新認証情報")

    print("\n" + "=" * 60)
    print("📋 テスト結果まとめ:")
    print(f"   旧認証情報（00029-c7d使用中): {'✅ 有効' if old_success else '❌ 無効'}")
    print(f"   新認証情報（デプロイ時使用）: {'✅ 有効' if new_success else '❌ 無効'}")

    if old_success and new_success:
        print("   🤔 結論: 両方の認証情報が有効（異なるデータベース？）")
    elif old_success and not new_success:
        print("   📌 結論: 旧認証情報のみ有効（新認証情報は無効）")
    elif not old_success and new_success:
        print("   📌 結論: 新認証情報のみ有効（旧認証情報は無効）")
    else:
        print("   🚨 結論: 両方とも接続失敗")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())