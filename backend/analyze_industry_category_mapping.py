#!/usr/bin/env python3
"""業界とCMカテゴリIDのマッピング分析"""
import asyncio
import asyncpg
from app.core.config import settings

async def analyze_industry_category_mapping():
    """業界とCMカテゴリIDのマッピングを分析"""
    print("=== 業界とCMカテゴリIDマッピング分析 ===")

    # フロントエンドの20業界
    industries = [
        "食品", "菓子・氷菓", "乳製品", "清涼飲料水", "アルコール飲料",
        "フードサービス", "医薬品・医療・健康食品", "化粧品・ヘアケア・オーラルケア",
        "トイレタリー", "自動車関連", "家電", "通信・IT",
        "ゲーム・エンターテイメント・アプリ", "流通・通販", "ファッション",
        "貴金属", "金融・不動産", "エネルギー・輸送・交通",
        "教育・出版・公共団体", "観光"
    ]

    conn = await asyncpg.connect(settings.database_url)
    try:
        print("\n📊 業界別CMカテゴリID分析（クライアント名・商品名から推測）:\n")

        for industry in industries:
            print(f"🏭 **{industry}**")

            # 業界キーワードで検索
            keywords = get_industry_keywords(industry)

            if keywords:
                # キーワードでCMデータを検索
                query = f"""
                    SELECT
                        rival_category_type_cd1,
                        COUNT(*) as count,
                        ARRAY_AGG(DISTINCT client_name) as clients,
                        ARRAY_AGG(DISTINCT product_name) as products
                    FROM m_talent_cm
                    WHERE (
                        {' OR '.join([f"client_name ILIKE '%{kw}%' OR product_name ILIKE '%{kw}%'" for kw in keywords])}
                    )
                    AND rival_category_type_cd1 IS NOT NULL
                    GROUP BY rival_category_type_cd1
                    ORDER BY count DESC
                    LIMIT 5
                """

                results = await conn.fetch(query)

                if results:
                    category_scores = {}
                    total_count = sum(r['count'] for r in results)

                    for result in results:
                        category_id = result['rival_category_type_cd1']
                        count = result['count']
                        percentage = (count / total_count * 100)

                        # サンプルクライアント・商品
                        sample_clients = [c for c in result['clients'][:3] if c]
                        sample_products = [p for p in result['products'][:3] if p]

                        category_scores[category_id] = percentage

                        print(f"   カテゴリID **{category_id}**: {count}件 ({percentage:.1f}%)")
                        if sample_clients:
                            print(f"     🏢 クライアント例: {', '.join(sample_clients)}")
                        if sample_products:
                            print(f"     📦 商品例: {', '.join(sample_products)}")

                    # 最も可能性が高いカテゴリID
                    most_likely = max(category_scores.items(), key=lambda x: x[1])
                    print(f"   ➡️ **推定カテゴリID: {most_likely[0]}** ({most_likely[1]:.1f}%)")
                else:
                    print(f"   ❌ マッチするCMデータなし")
            else:
                print(f"   ⚠️ キーワード未定義")

            print()

        # 全カテゴリの使用状況サマリー
        print("\n📈 全カテゴリID使用状況:")
        summary_query = """
            SELECT
                rival_category_type_cd1,
                COUNT(*) as total_count,
                COUNT(CASE WHEN use_period_end::date >= CURRENT_DATE THEN 1 END) as active_count
            FROM m_talent_cm
            WHERE rival_category_type_cd1 IS NOT NULL
            GROUP BY rival_category_type_cd1
            ORDER BY total_count DESC
        """
        summary_results = await conn.fetch(summary_query)

        for result in summary_results:
            category_id = result['rival_category_type_cd1']
            total = result['total_count']
            active = result['active_count']
            active_rate = (active / total * 100) if total > 0 else 0

            print(f"   カテゴリID {category_id:2d}: 総{total:3d}件 (現在{active:2d}件, {active_rate:.1f}%)")

    except Exception as e:
        print(f"エラー: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await conn.close()

def get_industry_keywords(industry_name):
    """業界名に基づいてキーワードリストを取得"""
    keyword_mapping = {
        "食品": ["味の素", "日清", "明治", "森永", "亀田", "永谷園", "マルちゃん", "サトウ食品", "井村屋", "食品", "フード"],
        "菓子・氷菓": ["ロッテ", "グリコ", "カルビー", "森永製菓", "明治製菓", "UHA", "菓子", "チョコ", "グミ", "スナック", "ガム", "キャンディ"],
        "乳製品": ["明治乳業", "森永乳業", "雪印", "小岩井", "よつ葉", "チーズ", "ヨーグルト", "牛乳", "乳製品"],
        "清涼飲料水": ["コカコーラ", "ペプシ", "サントリー", "アサヒ飲料", "キリンビバレッジ", "伊藤園", "ジュース", "お茶", "コーヒー", "清涼飲料"],
        "アルコール飲料": ["アサヒビール", "キリンビール", "サントリー", "サッポロビール", "チューハイ", "ビール", "ワイン", "日本酒", "焼酎"],
        "フードサービス": ["マクドナルド", "吉野家", "すき家", "スターバックス", "ファストフード", "レストラン", "カフェ"],
        "医薬品・医療・健康食品": ["大正製薬", "小林製薬", "エスエス製薬", "武田薬品", "第一三共", "医薬品", "健康食品", "サプリメント", "薬"],
        "化粧品・ヘアケア・オーラルケア": ["資生堂", "カネボウ", "コーセー", "ポーラ", "花王", "ライオン", "化粧品", "シャンプー", "歯磨き", "美容"],
        "トイレタリー": ["花王", "ライオン", "ユニリーバ", "P&G", "洗剤", "柔軟剤", "芳香剤", "トイレタリー"],
        "自動車関連": ["トヨタ", "日産", "ホンダ", "マツダ", "スバル", "ダイハツ", "自動車", "カー用品", "タイヤ", "オイル"],
        "家電": ["パナソニック", "ソニー", "シャープ", "東芝", "日立", "三菱電機", "家電", "テレビ", "冷蔵庫", "エアコン"],
        "通信・IT": ["NTT", "ソフトバンク", "KDDI", "楽天", "通信", "携帯", "スマホ", "インターネット", "IT"],
        "ゲーム・エンターテイメント・アプリ": ["ソニー", "任天堂", "コナミ", "セガ", "バンダイナムコ", "ゲーム", "アプリ", "エンターテイメント"],
        "流通・通販": ["イオン", "セブンイレブン", "楽天", "Amazon", "ヤマト運輸", "通販", "EC", "ショッピング"],
        "ファッション": ["ユニクロ", "しまむら", "ZARA", "H&M", "ファッション", "服", "アパレル", "靴"],
        "貴金属": ["ティファニー", "カルティエ", "貴金属", "ジュエリー", "宝石", "アクセサリー"],
        "金融・不動産": ["三井住友", "みずほ", "三菱UFJ", "りそな", "野村證券", "金融", "銀行", "保険", "証券", "不動産"],
        "エネルギー・輸送・交通": ["JR", "電力", "ガス", "石油", "エネルギー", "輸送", "交通", "鉄道"],
        "教育・出版・公共団体": ["学研", "ベネッセ", "公文", "教育", "出版", "学習", "公共"],
        "観光": ["JTB", "HIS", "観光", "旅行", "ホテル", "航空", "ツアー"]
    }

    return keyword_mapping.get(industry_name, [])

if __name__ == "__main__":
    asyncio.run(analyze_industry_category_mapping())