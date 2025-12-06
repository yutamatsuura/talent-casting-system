"""マスターデータ初期投入スクリプト（industries + image_items + industry_images）

実行方法:
    cd backend
    python -m scripts.seed_master_data

注意:
    - .env.local のDATABASE_URLを使用
    - 既存データは削除されます（開発環境専用）
"""
import asyncio
import sys
from pathlib import Path

# プロジェクトルートをパスに追加
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models import Base, Industry, ImageItem, IndustryImage


# 7つのイメージ項目マスタデータ（requirements.md準拠）
IMAGE_ITEMS_DATA = [
    {"id": 1, "code": "funny", "name": "おもしろい", "description": "ユーモアや親しみやすさを感じさせる", "display_order": 1},
    {"id": 2, "code": "clean", "name": "清潔感がある", "description": "清潔で爽やかな印象を与える", "display_order": 2},
    {"id": 3, "code": "unique", "name": "個性的", "description": "独自性や個性が際立つ", "display_order": 3},
    {"id": 4, "code": "trustworthy", "name": "信頼できる", "description": "信頼感や安心感を与える", "display_order": 4},
    {"id": 5, "code": "cute", "name": "可愛い", "description": "愛らしく魅力的な印象", "display_order": 5},
    {"id": 6, "code": "cool", "name": "カッコいい", "description": "洗練されたカッコよさを持つ", "display_order": 6},
    {"id": 7, "code": "mature", "name": "大人っぽい", "description": "成熟した落ち着いた雰囲気", "display_order": 7},
]

# 20業種マスタデータ（frontend/FormStep1.tsx準拠）
INDUSTRIES_DATA = [
    {"id": 1, "name": "食品", "display_order": 1},
    {"id": 2, "name": "菓子・氷菓", "display_order": 2},
    {"id": 3, "name": "乳製品", "display_order": 3},
    {"id": 4, "name": "清涼飲料水", "display_order": 4},
    {"id": 5, "name": "アルコール飲料", "display_order": 5},
    {"id": 6, "name": "フードサービス", "display_order": 6},
    {"id": 7, "name": "医薬品・医療・健康食品", "display_order": 7},
    {"id": 8, "name": "化粧品・ヘアケア・オーラルケア", "display_order": 8},
    {"id": 9, "name": "トイレタリー", "display_order": 9},
    {"id": 10, "name": "自動車関連", "display_order": 10},
    {"id": 11, "name": "家電", "display_order": 11},
    {"id": 12, "name": "通信・IT", "display_order": 12},
    {"id": 13, "name": "ゲーム・エンターテイメント・アプリ", "display_order": 13},
    {"id": 14, "name": "流通・通販", "display_order": 14},
    {"id": 15, "name": "ファッション", "display_order": 15},
    {"id": 16, "name": "貴金属", "display_order": 16},
    {"id": 17, "name": "金融・不動産", "display_order": 17},
    {"id": 18, "name": "エネルギー・輸送・交通", "display_order": 18},
    {"id": 19, "name": "教育・出版・公共団体", "display_order": 19},
    {"id": 20, "name": "観光", "display_order": 20},
]

# 業種-イメージ紐付けデータ（STEP2業種イメージ査定用）
# ※業種ごとに「求められるイメージ」を定義
# 例: 化粧品（id=8）→ 清潔感がある（image_id=2）
INDUSTRY_IMAGES_DATA = [
    # 食品（id=1）→ 清潔感がある、信頼できる
    {"industry_id": 1, "image_item_id": 2},
    {"industry_id": 1, "image_item_id": 4},

    # 菓子・氷菓（id=2）→ 可愛い、おもしろい
    {"industry_id": 2, "image_item_id": 5},
    {"industry_id": 2, "image_item_id": 1},

    # 乳製品（id=3）→ 清潔感がある、信頼できる
    {"industry_id": 3, "image_item_id": 2},
    {"industry_id": 3, "image_item_id": 4},

    # 清涼飲料水（id=4）→ 清潔感がある、おもしろい
    {"industry_id": 4, "image_item_id": 2},
    {"industry_id": 4, "image_item_id": 1},

    # アルコール飲料（id=5）→ カッコいい、大人っぽい
    {"industry_id": 5, "image_item_id": 6},
    {"industry_id": 5, "image_item_id": 7},

    # フードサービス（id=6）→ おもしろい、信頼できる
    {"industry_id": 6, "image_item_id": 1},
    {"industry_id": 6, "image_item_id": 4},

    # 医薬品・医療・健康食品（id=7）→ 信頼できる、清潔感がある
    {"industry_id": 7, "image_item_id": 4},
    {"industry_id": 7, "image_item_id": 2},

    # 化粧品・ヘアケア・オーラルケア（id=8）→ 清潔感がある、可愛い
    {"industry_id": 8, "image_item_id": 2},
    {"industry_id": 8, "image_item_id": 5},

    # トイレタリー（id=9）→ 清潔感がある、信頼できる
    {"industry_id": 9, "image_item_id": 2},
    {"industry_id": 9, "image_item_id": 4},

    # 自動車関連（id=10）→ カッコいい、信頼できる
    {"industry_id": 10, "image_item_id": 6},
    {"industry_id": 10, "image_item_id": 4},

    # 家電（id=11）→ カッコいい、信頼できる
    {"industry_id": 11, "image_item_id": 6},
    {"industry_id": 11, "image_item_id": 4},

    # 通信・IT（id=12）→ カッコいい、個性的
    {"industry_id": 12, "image_item_id": 6},
    {"industry_id": 12, "image_item_id": 3},

    # ゲーム・エンターテイメント・アプリ（id=13）→ おもしろい、個性的
    {"industry_id": 13, "image_item_id": 1},
    {"industry_id": 13, "image_item_id": 3},

    # 流通・通販（id=14）→ 信頼できる、おもしろい
    {"industry_id": 14, "image_item_id": 4},
    {"industry_id": 14, "image_item_id": 1},

    # ファッション（id=15）→ カッコいい、個性的
    {"industry_id": 15, "image_item_id": 6},
    {"industry_id": 15, "image_item_id": 3},

    # 貴金属（id=16）→ カッコいい、大人っぽい
    {"industry_id": 16, "image_item_id": 6},
    {"industry_id": 16, "image_item_id": 7},

    # 金融・不動産（id=17）→ 信頼できる、大人っぽい
    {"industry_id": 17, "image_item_id": 4},
    {"industry_id": 17, "image_item_id": 7},

    # エネルギー・輸送・交通（id=18）→ 信頼できる、カッコいい
    {"industry_id": 18, "image_item_id": 4},
    {"industry_id": 18, "image_item_id": 6},

    # 教育・出版・公共団体（id=19）→ 信頼できる、大人っぽい
    {"industry_id": 19, "image_item_id": 4},
    {"industry_id": 19, "image_item_id": 7},

    # 観光（id=20）→ おもしろい、可愛い
    {"industry_id": 20, "image_item_id": 1},
    {"industry_id": 20, "image_item_id": 5},
]


async def seed_master_data():
    """マスターデータ投入メイン処理"""
    print("🌱 マスターデータ投入開始...")
    print(f"📊 DATABASE_URL: {settings.database_url[:50]}...")

    # asyncpgエンジン作成（postgresql+asyncpg:// プロトコル使用）
    # asyncpgはsslmode/channel_bindingを直接サポートしないため、connect_argsで設定
    database_url = settings.database_url.replace("postgresql://", "postgresql+asyncpg://")
    # パラメータ削除（asyncpg用）
    database_url = database_url.split("?")[0]

    engine = create_async_engine(
        database_url,
        echo=True,  # SQL出力
        future=True,
        connect_args={
            "ssl": "require",  # asyncpg用SSL設定
        },
    )

    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with engine.begin() as conn:
        # テーブル削除・再作成
        print("🗑️  既存テーブル削除中...")
        await conn.run_sync(Base.metadata.drop_all)
        print("✅ テーブル削除完了")

        print("🏗️  テーブル作成中...")
        await conn.run_sync(Base.metadata.create_all)
        print("✅ テーブル作成完了")

    async with async_session() as session:
        # 1. イメージ項目マスタ投入
        print("\n📝 イメージ項目マスタ投入中...")
        for item_data in IMAGE_ITEMS_DATA:
            image_item = ImageItem(**item_data)
            session.add(image_item)
        await session.commit()
        print(f"✅ イメージ項目 {len(IMAGE_ITEMS_DATA)}件 投入完了")

        # 2. 業種マスタ投入
        print("\n📝 業種マスタ投入中...")
        for industry_data in INDUSTRIES_DATA:
            industry = Industry(**industry_data)
            session.add(industry)
        await session.commit()
        print(f"✅ 業種 {len(INDUSTRIES_DATA)}件 投入完了")

        # 3. 業種-イメージ紐付け投入
        print("\n📝 業種-イメージ紐付けデータ投入中...")
        for mapping_data in INDUSTRY_IMAGES_DATA:
            industry_image = IndustryImage(**mapping_data)
            session.add(industry_image)
        await session.commit()
        print(f"✅ 業種-イメージ紐付け {len(INDUSTRY_IMAGES_DATA)}件 投入完了")

    await engine.dispose()
    print("\n🎉 マスターデータ投入完了!")
    print("\n📊 投入サマリー:")
    print(f"   - イメージ項目: {len(IMAGE_ITEMS_DATA)}件")
    print(f"   - 業種: {len(INDUSTRIES_DATA)}件")
    print(f"   - 業種-イメージ紐付け: {len(INDUSTRY_IMAGES_DATA)}件")


if __name__ == "__main__":
    asyncio.run(seed_master_data())
