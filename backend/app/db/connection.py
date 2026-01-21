"""データベース接続管理（asyncpg + SQLAlchemy 2.0）"""
from typing import Optional
import asyncpg
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.core.config import settings

# SQLAlchemy Base
Base = declarative_base()

# SQLAlchemy Async Engine (global)
engine = None
async_session_maker = None

# asyncpg接続プール (Phase A1最適化)
asyncpg_pool = None


def get_engine():
    """エンジン取得"""
    return engine


def get_session_maker():
    """セッションメーカー取得"""
    return async_session_maker


async def get_asyncpg_connection():
    """asyncpg接続取得（プール使用、Phase A1最適化）"""
    global asyncpg_pool
    try:
        if asyncpg_pool is None:
            # プールが初期化されていない場合は初期化
            await init_asyncpg_pool()

        # プールから接続取得
        return await asyncpg_pool.acquire()
    except Exception as e:
        raise Exception(f"Database connection failed: {str(e)}")


async def release_asyncpg_connection(conn):
    """asyncpg接続返却（プール返却、Phase A1最適化）"""
    global asyncpg_pool
    if asyncpg_pool and conn:
        await asyncpg_pool.release(conn)


async def init_asyncpg_pool():
    """asyncpg接続プール初期化（Phase A1最適化）"""
    global asyncpg_pool
    try:
        # DATABASE_URLからクエリパラメータを除去してasyncpgの引数に変換
        from urllib.parse import urlparse, parse_qs
        parsed = urlparse(settings.database_url)
        query_params = parse_qs(parsed.query)

        # asyncpg接続パラメータ構築
        conn_params = {
            "host": parsed.hostname,
            "port": parsed.port or 5432,
            "user": parsed.username,
            "password": parsed.password,
            "database": parsed.path.lstrip('/'),
        }

        # sslmodeパラメータがある場合はssl='require'に変換
        if query_params.get('sslmode', [''])[0] in ['require', 'verify-ca', 'verify-full']:
            conn_params['ssl'] = 'require'

        # プール作成（Phase A1: 小さなプールサイズで効率化）
        asyncpg_pool = await asyncpg.create_pool(
            **conn_params,
            min_size=2,      # 最小2接続
            max_size=5,      # 最大5接続（設定値と合わせる）
            command_timeout=10  # コマンドタイムアウト
        )
    except Exception as e:
        raise Exception(f"asyncpg pool initialization failed: {str(e)}")


async def check_db_connection() -> bool:
    """データベース接続確認（プール使用、Phase A1最適化）"""
    conn = None
    try:
        conn = await get_asyncpg_connection()
        # 簡易クエリでDB接続確認
        await conn.fetchval("SELECT 1")
        return True
    except Exception as e:
        print(f"DB health check failed: {str(e)}")
        return False
    finally:
        if conn:
            await release_asyncpg_connection(conn)


async def ensure_booking_link_patterns_table():
    """booking_link_patterns テーブルの存在確認と作成"""
    conn = None
    try:
        conn = await get_asyncpg_connection()

        # テーブル存在確認
        exists = await conn.fetchval("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_name = 'booking_link_patterns'
            )
        """)

        if not exists:
            print("📋 booking_link_patterns テーブルが存在しません。作成します...")

            # テーブル作成
            await conn.execute("""
                CREATE TABLE booking_link_patterns (
                    id SERIAL PRIMARY KEY,
                    pattern_key VARCHAR(50) UNIQUE NOT NULL,
                    pattern_name VARCHAR(100) NOT NULL,
                    description TEXT,
                    booking_url TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP
                )
            """)

            # インデックス作成
            await conn.execute("""
                CREATE INDEX idx_booking_link_patterns_key
                ON booking_link_patterns(pattern_key)
            """)

            # 初期データ投入
            await conn.execute("""
                INSERT INTO booking_link_patterns (pattern_key, pattern_name, description, booking_url) VALUES
                ('high_budget', '高予算（1,000万円以上）', '予算が「1,000万～3,000万円未満」「3,000万～5,000万円未満」「5,000万円以上」の場合', 'https://app.spirinc.com/t/W63rJQN01CTXR-FjsFaOr/as/8FtIxQriLEvZxYqBlbzib/confirm'),
                ('low_budget_influencer', '低予算×インフルエンサー', '予算が「500万円未満」「500万～1,000万円未満」かつ希望ジャンルに「インフルエンサー」が含まれる場合', 'https://app.spirinc.com/t/W63rJQN01CTXR-FjsFaOr/as/8FtIxQriLEvZxYqBlbzib/confirm'),
                ('low_budget_other', '低予算×その他', '予算が「500万円未満」「500万～1,000万円未満」かつ希望ジャンルが「インフルエンサー以外」または「ジャンル希望なし」の場合', 'https://app.spirinc.com/t/W63rJQN01CTXR-FjsFaOr/as/8FtIxQriLEvZxYqBlbzib/confirm')
            """)

            print("✅ booking_link_patterns テーブル作成完了（初期データ3件投入）")
        else:
            print("✅ booking_link_patterns テーブル存在確認OK")

    except Exception as e:
        print(f"⚠️  booking_link_patterns テーブル確認エラー: {e}")
        # エラーが発生してもアプリケーション起動は継続
    finally:
        if conn:
            await release_asyncpg_connection(conn)


async def init_db():
    """データベース初期化（アプリケーション起動時、Phase A1最適化）"""
    global engine, async_session_maker

    # PostgreSQL URLをasyncpg用に変換（クエリパラメータを除去）
    from urllib.parse import urlparse
    parsed = urlparse(settings.database_url)
    database_url = f"postgresql+asyncpg://{parsed.username}:{parsed.password}@{parsed.hostname}:{parsed.port or 5432}{parsed.path}"

    # SQLAlchemy 2.0 Async Engine作成 (Phase A1最適化済み設定値使用)
    engine = create_async_engine(
        database_url,
        echo=settings.node_env == "development",
        pool_size=settings.db_pool_size,
        max_overflow=settings.db_max_overflow,
        pool_timeout=settings.db_pool_timeout,
        pool_recycle=settings.db_pool_recycle,
        connect_args={"ssl": "require"} if "neon.tech" in settings.database_url else {},
    )

    # Session Maker作成
    async_session_maker = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    # asyncpgプール初期化 (Phase A1最適化)
    await init_asyncpg_pool()

    # booking_link_patterns テーブルの存在確認と作成
    await ensure_booking_link_patterns_table()


async def get_db_session() -> AsyncSession:
    """データベースセッション取得（依存性注入用）"""
    if async_session_maker is None:
        raise Exception("Database not initialized. Call init_db() first.")

    async with async_session_maker() as session:
        yield session


# エイリアス（後方互換性のため）
get_db = get_db_session


async def close_db():
    """データベース接続クローズ（アプリケーション終了時、Phase A1最適化）"""
    global engine, asyncpg_pool
    if engine:
        await engine.dispose()
    if asyncpg_pool:
        await asyncpg_pool.close()
