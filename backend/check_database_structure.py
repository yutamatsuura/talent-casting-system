#!/usr/bin/env python3
"""データベーステーブル構成と件数の詳細確認"""

import asyncio
import sys
from pathlib import Path

# backend/appへのパスを追加
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import select, text
from app.db.connection import init_db, get_session_maker

# グローバル変数でセッションメーカーを保持
AsyncSessionLocal = None

async def get_async_session():
    """非同期セッション取得"""
    global AsyncSessionLocal
    if AsyncSessionLocal is None:
        await init_db()
        AsyncSessionLocal = get_session_maker()
    return AsyncSessionLocal()

async def check_database_structure():
    """データベース構造と件数の詳細確認"""
    print("=" * 80)
    print("🔍 DATABASE STRUCTURE VERIFICATION")
    print("=" * 80)
    print("📊 現在のデータベース構成と期待値の比較")
    print("=" * 80)

    async with await get_async_session() as session:
        # 全テーブル一覧取得
        result = await session.execute(text("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            AND table_type = 'BASE TABLE'
            ORDER BY table_name
        """))
        actual_tables = [row[0] for row in result.fetchall()]

        print(f"\n📋 実際のテーブル一覧: {len(actual_tables)}個")
        for table in actual_tables:
            print(f"   • {table}")

        # 期待されるテーブル構成（画像より）
        expected_structure = {
            "talents": {"description": "タレント基本情報（Nowデータ）", "expected_count": "約2,000件", "type": "データテーブル"},
            "talent_scores": {"description": "VR人気度・TPRスコア（ターゲット層別）", "expected_count": "約16,000件", "type": "データテーブル"},
            "talent_images": {"description": "イメージスコア7項目（ターゲット層別）", "expected_count": "約16,000件", "type": "データテーブル"},
            "industries": {"description": "業種マスタ + 求められるイメージ", "expected_count": "20件", "type": "マスタテーブル"},
            "target_segments": {"description": "ターゲット層マスタ", "expected_count": "8件", "type": "マスタテーブル"},
            "budget_ranges": {"description": "予算区分マスタ", "expected_count": "4件", "type": "マスタテーブル"},
            "image_items": {"description": "イメージ項目マスタ", "expected_count": "7件", "type": "マスタテーブル"}
        }

        print("\n" + "=" * 80)
        print("📊 テーブル別詳細確認")
        print("=" * 80)

        table_status = {}

        for table_name, info in expected_structure.items():
            print(f"\n📋 {table_name.upper()}")
            print(f"   説明: {info['description']}")
            print(f"   期待件数: {info['expected_count']}")
            print(f"   種別: {info['type']}")

            if table_name in actual_tables:
                # 実際の件数取得
                count_result = await session.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                actual_count = count_result.scalar()
                print(f"   実際件数: {actual_count:,}件")

                # 期待値との比較
                expected_num = None
                if info['expected_count'] == "約2,000件":
                    expected_num = 2000
                elif info['expected_count'] == "約16,000件":
                    expected_num = 16000
                elif info['expected_count'] == "20件":
                    expected_num = 20
                elif info['expected_count'] == "8件":
                    expected_num = 8
                elif info['expected_count'] == "4件":
                    expected_num = 4
                elif info['expected_count'] == "7件":
                    expected_num = 7

                if expected_num:
                    if info['expected_count'].startswith("約"):
                        # 近似値の場合、±20%の範囲で OK とする
                        tolerance = expected_num * 0.2
                        if abs(actual_count - expected_num) <= tolerance:
                            status = "✅ 正常範囲"
                        else:
                            status = "⚠️ 件数差異"
                    else:
                        # 正確な値の場合
                        if actual_count == expected_num:
                            status = "✅ 完全一致"
                        else:
                            status = "❌ 件数不一致"

                    print(f"   ステータス: {status}")
                    table_status[table_name] = {
                        "exists": True,
                        "count": actual_count,
                        "expected": expected_num,
                        "status": status
                    }
                else:
                    table_status[table_name] = {
                        "exists": True,
                        "count": actual_count,
                        "expected": "不明",
                        "status": "✅ 存在"
                    }
            else:
                print(f"   ステータス: ❌ テーブル不在")
                table_status[table_name] = {
                    "exists": False,
                    "count": 0,
                    "expected": None,
                    "status": "❌ テーブル不在"
                }

        # 余分なテーブル確認
        extra_tables = set(actual_tables) - set(expected_structure.keys())
        if extra_tables:
            print(f"\n🚨 余分なテーブル: {len(extra_tables)}個")
            for table in extra_tables:
                count_result = await session.execute(text(f"SELECT COUNT(*) FROM {table}"))
                count = count_result.scalar()
                print(f"   • {table}: {count:,}件")

        # サマリー
        print("\n" + "=" * 80)
        print("📊 構成確認サマリー")
        print("=" * 80)

        correct_tables = sum(1 for t in table_status.values() if t["status"].startswith("✅"))
        warning_tables = sum(1 for t in table_status.values() if t["status"].startswith("⚠️"))
        error_tables = sum(1 for t in table_status.values() if t["status"].startswith("❌"))

        print(f"✅ 正常: {correct_tables}テーブル")
        print(f"⚠️ 警告: {warning_tables}テーブル")
        print(f"❌ エラー: {error_tables}テーブル")
        print(f"🔍 余分テーブル: {len(extra_tables)}テーブル")

        if error_tables == 0 and warning_tables == 0 and len(extra_tables) == 0:
            print("\n🎉 データベース構成は完全に期待値通りです！")
        elif error_tables == 0 and warning_tables == 0:
            print("\n✅ 基本構成は正常ですが、余分なテーブルがあります")
        else:
            print("\n🚨 データベース構成に問題があります")
            print("🔧 修正が必要な項目があります")

        print("=" * 80)

        return {
            "expected_tables": expected_structure,
            "actual_tables": actual_tables,
            "table_status": table_status,
            "extra_tables": list(extra_tables),
            "summary": {
                "correct": correct_tables,
                "warning": warning_tables,
                "error": error_tables,
                "extra": len(extra_tables)
            }
        }

async def main():
    """メイン処理"""
    try:
        result = await check_database_structure()
        return result
    except Exception as e:
        print(f"\n❌ データベース構成確認中にエラー: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)