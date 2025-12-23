#!/usr/bin/env python3
"""
実際のデータベースから正しい都道府県マッピングを作成
"""

import asyncio
import sys
import os
import json

# backendディレクトリをPATHに追加
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.config import settings

async def main():
    # データベース接続
    DATABASE_URL = settings.database_url
    print(f"🔍 データベース接続: {DATABASE_URL[:50]}...")

    # asyncpg用のURL変換
    from urllib.parse import urlparse
    parsed = urlparse(DATABASE_URL)

    # asyncpg接続パラメータ構築
    conn_params = {
        "host": parsed.hostname,
        "port": parsed.port or 5432,
        "user": parsed.username,
        "password": parsed.password,
        "database": parsed.path.lstrip('/'),
    }

    # SSL設定
    if "neon.tech" in DATABASE_URL or "sslmode=require" in DATABASE_URL:
        conn_params['ssl'] = 'require'

    import asyncpg
    conn = await asyncpg.connect(**conn_params)

    # 都道府県別有名人マップ（出身地が確実にわかる有名人）
    known_celebrities = {
        "北海道": ["大泉洋", "安田美沙子", "鈴木砂羽", "安田忠夫"],
        "青森県": ["新山千春", "成田凌"],
        "岩手県": ["小沢一敬"],
        "宮城県": ["千葉雄大", "サンドウィッチマン"],
        "秋田県": ["佐々木希", "桐沢ゴウ"],
        "山形県": ["佐藤隆太"],
        "福島県": ["西田敏行", "白羽玲子"],
        "茨城県": ["渡辺直美", "磯山さやか"],
        "栃木県": ["U字工事", "薬丸裕英"],
        "群馬県": ["井森美幸", "篠原涼子"],
        "埼玉県": ["菜々緒", "草彅剛", "小嶋陽菜"],
        "千葉県": ["小島瑠璃子", "桐谷美玲", "飯豊まりえ"],
        "東京都": ["いとうあさこ", "きゃりーぱみゅぱみゅ", "木村拓哉", "稲垣吾郎", "吉高由里子", "竹内涼真"],
        "神奈川県": ["香取慎吾", "ムロツヨシ"],
        "新潟県": ["小林麻耶"],
        "富山県": ["藤井フミヤ"],
        "石川県": ["鶴田真由"],
        "福井県": ["長谷川博己"],
        "山梨県": ["中田英寿"],
        "長野県": ["小日向文世"],
        "岐阜県": ["杉本彩"],
        "静岡県": ["広瀬すず", "長澤まさみ"],
        "愛知県": ["松井珠理奈", "浅田舞"],
        "三重県": ["西野カナ"],
        "滋賀県": ["武田真治"],
        "京都府": ["舞妓ちゃん"],
        "大阪府": ["松本人志", "浜田雅功", "鈴木亮平", "北川景子", "有村架純"],
        "兵庫県": ["石田ゆり子"],
        "奈良県": ["高畑充希", "今田耕司"],
        "和歌山県": ["明石家さんま"],
        "鳥取県": ["谷合正明"],
        "島根県": ["錦織圭"],
        "岡山県": ["大本彩乃"],
        "広島県": ["有吉弘行"],
        "山口県": ["西村知美"],
        "徳島県": ["犬飼貴丈"],
        "香川県": ["要潤"],
        "愛媛県": ["真木よう子"],
        "高知県": ["広末涼子"],
        "福岡県": ["橋本環奈", "博多華丸"],
        "佐賀県": ["江頭2:50"],
        "長崎県": ["福山雅治"],
        "熊本県": ["小山力也"],
        "大分県": ["指原莉乃"],
        "宮崎県": ["東国原英夫"],
        "鹿児島県": ["長渕剛"],
        "沖縄県": ["安室奈美恵", "島袋寛子"]
    }

    prefecture_mapping = {}

    try:
        print("\n🔍 有名人の都道府県コードを調査...")

        for prefecture, celebrities in known_celebrities.items():
            found_codes = []

            for celebrity in celebrities:
                query = """
                SELECT DISTINCT pref_cd
                FROM m_account
                WHERE name_full_for_matching LIKE $1 AND del_flag = 0 AND pref_cd IS NOT NULL
                """
                results = await conn.fetch(query, f'%{celebrity}%')

                if results:
                    for row in results:
                        code = row['pref_cd']
                        if code:
                            found_codes.append(code)
                            print(f"  {celebrity} ({prefecture}): pref_cd={code}")

            # 最も多いコードを採用
            if found_codes:
                most_common_code = max(set(found_codes), key=found_codes.count)
                if prefecture not in prefecture_mapping:
                    prefecture_mapping[most_common_code] = prefecture
                    print(f"✅ {prefecture}: pref_cd={most_common_code}")

        print(f"\n📋 確定した都道府県マッピング:")
        for code, pref in sorted(prefecture_mapping.items()):
            print(f"  {code}: {pref}")

        # Pythonのdict形式で出力
        print(f"\n💾 Pythonマッピングコード:")
        print("prefecture_map = {")
        for code in sorted(prefecture_mapping.keys()):
            print(f"    {code}: \"{prefecture_mapping[code]}\",")
        print("}")

    except Exception as e:
        print(f"❌ エラー: {e}")

    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(main())