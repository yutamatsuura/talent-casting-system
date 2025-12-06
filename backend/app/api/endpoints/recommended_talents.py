"""おすすめタレント管理APIエンドポイント"""
from fastapi import APIRouter, HTTPException, status
from typing import List, Dict, Optional
from pydantic import BaseModel
from app.db.connection import get_asyncpg_connection

router = APIRouter()


class RecommendedTalentRequest(BaseModel):
    """おすすめタレント設定リクエスト"""
    industry_name: str
    talent_id_1: Optional[int] = None
    talent_id_2: Optional[int] = None
    talent_id_3: Optional[int] = None


class RecommendedTalentResponse(BaseModel):
    """おすすめタレント設定レスポンス"""
    id: int
    industry_name: str
    talent_id_1: Optional[int]
    talent_id_2: Optional[int]
    talent_id_3: Optional[int]
    talent_1_name: Optional[str]
    talent_2_name: Optional[str]
    talent_3_name: Optional[str]
    created_at: str
    updated_at: str


class TalentOption(BaseModel):
    """タレント選択肢"""
    account_id: int
    name: str
    category: Optional[str]


@router.get(
    "/recommended-talents",
    response_model=List[RecommendedTalentResponse],
    summary="おすすめタレント設定一覧取得",
    description="全業界のおすすめタレント設定を取得"
)
async def get_recommended_talents():
    """おすすめタレント設定一覧取得"""
    conn = await get_asyncpg_connection()
    try:
        query = """
            SELECT
                rt.id,
                rt.industry_name,
                rt.talent_id_1,
                rt.talent_id_2,
                rt.talent_id_3,
                t1.name_full_for_matching as talent_1_name,
                t2.name_full_for_matching as talent_2_name,
                t3.name_full_for_matching as talent_3_name,
                rt.created_at::text,
                rt.updated_at::text
            FROM recommended_talents rt
            LEFT JOIN m_account t1 ON rt.talent_id_1 = t1.account_id
            LEFT JOIN m_account t2 ON rt.talent_id_2 = t2.account_id
            LEFT JOIN m_account t3 ON rt.talent_id_3 = t3.account_id
            ORDER BY rt.industry_name
        """
        rows = await conn.fetch(query)

        return [RecommendedTalentResponse(**dict(row)) for row in rows]

    finally:
        await conn.close()


@router.get(
    "/recommended-talents/{industry_name}",
    response_model=RecommendedTalentResponse,
    summary="業界別おすすめタレント取得",
    description="指定業界のおすすめタレント設定を取得"
)
async def get_recommended_talent_by_industry(industry_name: str):
    """業界別おすすめタレント取得"""
    conn = await get_asyncpg_connection()
    try:
        query = """
            SELECT
                rt.id,
                rt.industry_name,
                rt.talent_id_1,
                rt.talent_id_2,
                rt.talent_id_3,
                t1.name_full_for_matching as talent_1_name,
                t2.name_full_for_matching as talent_2_name,
                t3.name_full_for_matching as talent_3_name,
                rt.created_at::text,
                rt.updated_at::text
            FROM recommended_talents rt
            LEFT JOIN m_account t1 ON rt.talent_id_1 = t1.account_id
            LEFT JOIN m_account t2 ON rt.talent_id_2 = t2.account_id
            LEFT JOIN m_account t3 ON rt.talent_id_3 = t3.account_id
            WHERE rt.industry_name = $1
        """
        row = await conn.fetchrow(query, industry_name)

        if not row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"業界 '{industry_name}' のおすすめタレント設定が見つかりません"
            )

        return RecommendedTalentResponse(**dict(row))

    finally:
        await conn.close()


@router.post(
    "/recommended-talents",
    response_model=RecommendedTalentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="おすすめタレント設定作成/更新",
    description="業界別おすすめタレント設定を作成または更新"
)
async def create_or_update_recommended_talents(request: RecommendedTalentRequest):
    """おすすめタレント設定作成/更新"""
    conn = await get_asyncpg_connection()
    try:
        # UPSERTクエリ（ON CONFLICT DO UPDATE）
        query = """
            INSERT INTO recommended_talents (
                industry_name, talent_id_1, talent_id_2, talent_id_3
            ) VALUES ($1, $2, $3, $4)
            ON CONFLICT (industry_name) DO UPDATE SET
                talent_id_1 = EXCLUDED.talent_id_1,
                talent_id_2 = EXCLUDED.talent_id_2,
                talent_id_3 = EXCLUDED.talent_id_3,
                updated_at = CURRENT_TIMESTAMP
            RETURNING id, industry_name, talent_id_1, talent_id_2, talent_id_3,
                      created_at::text, updated_at::text
        """

        row = await conn.fetchrow(
            query,
            request.industry_name,
            request.talent_id_1,
            request.talent_id_2,
            request.talent_id_3
        )

        if not row:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="おすすめタレント設定の保存に失敗しました"
            )

        # タレント名を取得
        talent_names_query = """
            SELECT
                t1.name_full_for_matching as talent_1_name,
                t2.name_full_for_matching as talent_2_name,
                t3.name_full_for_matching as talent_3_name
            FROM (SELECT 1) dummy
            LEFT JOIN m_account t1 ON t1.account_id = $1
            LEFT JOIN m_account t2 ON t2.account_id = $2
            LEFT JOIN m_account t3 ON t3.account_id = $3
        """

        talent_names = await conn.fetchrow(
            talent_names_query,
            request.talent_id_1,
            request.talent_id_2,
            request.talent_id_3
        )

        result_data = dict(row)
        result_data.update(dict(talent_names) if talent_names else {})

        return RecommendedTalentResponse(**result_data)

    finally:
        await conn.close()


@router.delete(
    "/recommended-talents/{industry_name}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="おすすめタレント設定削除",
    description="指定業界のおすすめタレント設定を削除"
)
async def delete_recommended_talents(industry_name: str):
    """おすすめタレント設定削除"""
    conn = await get_asyncpg_connection()
    try:
        result = await conn.execute(
            "DELETE FROM recommended_talents WHERE industry_name = $1",
            industry_name
        )

        if result == "DELETE 0":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"業界 '{industry_name}' のおすすめタレント設定が見つかりません"
            )

    finally:
        await conn.close()


@router.get(
    "/talent-options",
    response_model=List[TalentOption],
    summary="タレント選択肢取得",
    description="管理画面でのタレント選択用の一覧を取得"
)
async def get_talent_options():
    """タレント選択肢取得（管理画面用）"""
    conn = await get_asyncpg_connection()
    try:
        query = """
            SELECT
                account_id,
                name_full_for_matching as name,
                act_genre as category
            FROM m_account
            WHERE del_flag = 0
            ORDER BY name_full_for_matching
        """
        rows = await conn.fetch(query)

        return [TalentOption(**dict(row)) for row in rows]

    finally:
        await conn.close()


async def get_recommended_talents_for_matching(industry_name: str) -> List[Dict]:
    """マッチングロジック用：業界別おすすめタレント取得"""
    conn = await get_asyncpg_connection()
    try:
        query = """
            SELECT
                ma.account_id,
                ma.name_full_for_matching as name,
                ma.last_name_kana,
                ma.act_genre,
                'recommended' as talent_type
            FROM recommended_talents rt
            INNER JOIN m_account ma ON (
                (rt.talent_id_1 IS NOT NULL AND ma.account_id = rt.talent_id_1)
                OR (rt.talent_id_2 IS NOT NULL AND ma.account_id = rt.talent_id_2)
                OR (rt.talent_id_3 IS NOT NULL AND ma.account_id = rt.talent_id_3)
            )
            WHERE rt.industry_name = $1
                AND ma.del_flag = 0
            ORDER BY
                CASE
                    WHEN ma.account_id = rt.talent_id_1 THEN 1
                    WHEN ma.account_id = rt.talent_id_2 THEN 2
                    WHEN ma.account_id = rt.talent_id_3 THEN 3
                END
        """
        rows = await conn.fetch(query, industry_name)

        return [dict(row) for row in rows]

    finally:
        await conn.close()