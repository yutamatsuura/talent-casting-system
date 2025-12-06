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


def get_engine():
    """エンジン取得"""
    return engine


def get_session_maker():
    """セッションメーカー取得"""
    return async_session_maker


async def get_asyncpg_connection() -> asyncpg.Connection:
    """asyncpg直接接続取得（高速クエリ用）"""
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

        conn = await asyncpg.connect(**conn_params)
        return conn
    except Exception as e:
        raise Exception(f"Database connection failed: {str(e)}")


async def check_db_connection() -> bool:
    """データベース接続確認（ヘルスチェック用）"""
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
            await conn.close()


async def init_db():
    """データベース初期化（アプリケーション起動時）"""
    global engine, async_session_maker

    # PostgreSQL URLをasyncpg用に変換（クエリパラメータを除去）
    from urllib.parse import urlparse
    parsed = urlparse(settings.database_url)
    database_url = f"postgresql+asyncpg://{parsed.username}:{parsed.password}@{parsed.hostname}:{parsed.port or 5432}{parsed.path}"

    # SQLAlchemy 2.0 Async Engine作成
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


async def get_db_session() -> AsyncSession:
    """データベースセッション取得（依存性注入用）"""
    if async_session_maker is None:
        raise Exception("Database not initialized. Call init_db() first.")

    async with async_session_maker() as session:
        yield session


# エイリアス（後方互換性のため）
get_db = get_db_session


async def close_db():
    """データベース接続クローズ（アプリケーション終了時）"""
    global engine
    if engine:
        await engine.dispose()
