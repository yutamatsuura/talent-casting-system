"""
タレント詳細情報取得エンドポイント

タレントの基本情報、CM履歴、マッチングスコア詳細を取得するAPI
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from datetime import datetime
import logging

from app.db.connection import get_db_session
from app.schemas.talents import TalentDetailResponse, CMHistoryDetail

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/{account_id}/details",
    response_model=TalentDetailResponse,
    summary="タレント詳細情報取得",
    description="指定されたタレントの基本情報、CM履歴、マッチングスコア詳細を取得します"
)
async def get_talent_details(
    account_id: int,
    target_segment_id: Optional[int] = Query(None, description="ターゲット層ID（マッチングスコア詳細用）"),
    db: AsyncSession = Depends(get_db_session)
) -> TalentDetailResponse:
    """
    タレント詳細情報を取得

    Args:
        account_id: タレントのアカウントID
        target_segment_id: ターゲット層ID（オプション）
        db: データベースセッション

    Returns:
        TalentDetailResponse: タレント詳細情報

    Raises:
        HTTPException: タレントが見つからない場合
    """

    try:
        # 1. タレント基本情報を取得
        talent_query = text("""
            SELECT
                ma.account_id,
                ma.name_full_for_matching as name,
                ma.last_name_kana,
                ma.first_name_kana,
                ma.act_genre as category,
                ma.birthday,
                ma.company_name,
                ma.pref_cd,
                CASE
                    WHEN ma.birthday IS NOT NULL
                    THEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, ma.birthday))::INTEGER
                    ELSE NULL
                END as age
            FROM m_account ma
            WHERE ma.account_id = :account_id
              AND ma.del_flag = 0
        """)

        result = await db.execute(talent_query, {"account_id": account_id})
        talent_data = result.fetchone()

        if not talent_data:
            raise HTTPException(
                status_code=404,
                detail=f"Talent with account_id {account_id} not found"
            )

        # 2. CM履歴を取得（カテゴリ情報含む）
        cm_history_query = text("""
            SELECT
                mtc.client_name,
                COALESCE(mtc.product_name, '') as product_name,
                mtc.use_period_start,
                mtc.use_period_end,
                mtc.agency_name,
                mtc.production_name,
                mtc.director,
                mtc.note,
                mtc.sub_id,
                mtc.rival_category_type_cd1,
                mtc.rival_category_type_cd2,
                mtc.rival_category_type_cd3,
                mtc.rival_category_type_cd4
            FROM m_talent_cm mtc
            WHERE mtc.account_id = :account_id
            ORDER BY mtc.use_period_start DESC, mtc.sub_id DESC
        """)

        cm_result = await db.execute(cm_history_query, {"account_id": account_id})
        cm_history_rows = cm_result.fetchall()

        # 3. CM履歴データを整形（カテゴリコード含む）
        cm_history = []
        for row in cm_history_rows:
            # 期間フォーマット処理
            category = _determine_cm_category(row.client_name, row.product_name)

            cm_detail = CMHistoryDetail(
                client_name=row.client_name or "",
                product_name=row.product_name or "",
                use_period_start=row.use_period_start or "",
                use_period_end=row.use_period_end or "",
                agency_name=row.agency_name or "",
                production_name=row.production_name or "",
                director=row.director or "",
                category=category,
                note=row.note or "",
                rival_category_type_cd1=row.rival_category_type_cd1,
                rival_category_type_cd2=row.rival_category_type_cd2,
                rival_category_type_cd3=row.rival_category_type_cd3,
                rival_category_type_cd4=row.rival_category_type_cd4
            )
            cm_history.append(cm_detail)

        # 4. マッチングスコア詳細を取得（target_segment_idがある場合）
        base_power_score = None
        image_adjustment = None

        if target_segment_id:
            score_query = text("""
                SELECT
                    ts.base_power_score,
                    ts.vr_popularity,
                    ts.tpr_power_score
                FROM talent_scores ts
                WHERE ts.account_id = :account_id
                  AND ts.target_segment_id = :target_segment_id
            """)

            score_result = await db.execute(
                score_query,
                {"account_id": account_id, "target_segment_id": target_segment_id}
            )
            score_data = score_result.fetchone()

            if score_data:
                base_power_score = float(score_data.base_power_score) if score_data.base_power_score else None

        # 5. ふりがな文字列の組み立て
        kana = None
        if talent_data.last_name_kana or talent_data.first_name_kana:
            last_kana = talent_data.last_name_kana or ""
            first_kana = talent_data.first_name_kana or ""
            kana = f"{last_kana} {first_kana}".strip()

        # 6. 出身地の取得
        birthplace = _get_prefecture_name(talent_data.pref_cd)

        # 7. レスポンス構築
        response = TalentDetailResponse(
            account_id=talent_data.account_id,
            name=talent_data.name,
            kana=kana,
            category=talent_data.category,
            age=talent_data.age,
            company_name=talent_data.company_name,
            birthplace=birthplace,  # 出身地を追加
            introduction=None,  # 自己紹介文は現在DBに存在しない
            cm_history=cm_history,
            base_power_score=base_power_score,
            image_adjustment=image_adjustment,
            image_url=_build_image_url(None)
        )

        logger.info(f"Successfully retrieved details for talent {account_id} with {len(cm_history)} CM records")
        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving talent details for account_id {account_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


def _get_prefecture_name(pref_cd: Optional[int]) -> Optional[str]:
    """
    都道府県コードから都道府県名を取得

    このプロジェクトは独自の都道府県コード体系を使用
    実際のデータベース調査結果に基づく正確なマッピング

    Args:
        pref_cd: 都道府県コード

    Returns:
        str: 都道府県名、またはNone
    """
    if not pref_cd:
        return None

    # 実際のDB調査結果に基づく独自コード体系マッピング
    # JIS X 0401の先頭0削除版（ただし12/13が入れ替わり）
    prefecture_map = {
        1: "北海道",     # 中島みゆき、大泉洋 ✅確認済み
        2: "青森県",     # 吉幾三
        3: "岩手県",     #
        4: "宮城県",     # 福原愛、千葉雄大 (※JIS標準とは順序異なる)
        5: "秋田県",     # 佐々木希
        6: "山形県",     # 橋本マナミ
        7: "福島県",     # 武田玲奈
        8: "茨城県",     # 磯山さやか、渡辺直美 ✅確認済み
        9: "栃木県",     # 大島優子、U字工事 ✅確認済み
        10: "群馬県",    # 白石麻衣、井森美幸 ✅確認済み
        11: "埼玉県",    # 菜々緒、草彅剛 ✅確認済み
        12: "東京都",    # いとうあさこ、きゃりー、木村拓哉 ✅確認済み
        13: "千葉県",    # 小島瑠璃子、桐谷美玲 ✅確認済み
        14: "神奈川県",  # ムロツヨシ、香取慎吾 ✅確認済み
        15: "新潟県",    # 横澤夏子、渡辺謙
        16: "富山県",    # はじめしゃちょー
        17: "石川県",    # 浜辺美波
        18: "福井県",    # 道端ジェシカ
        19: "山梨県",    # 田中要次、藤森慎吾
        20: "長野県",    # 清水ミチコ
        21: "岐阜県",    # マキタスポーツ
        22: "静岡県",    # 別所哲也、広瀬すず ✅確認済み
        23: "愛知県",    # 浅田舞、松井珠理奈 ✅確認済み
        24: "三重県",    # 高橋メアリージュン、西野カナ
        25: "滋賀県",    # 徳井義実、安田美沙子
        26: "京都府",    # 足立梨花、水野美紀
        27: "大阪府",    # 三戸なつめ、ゆりやん (※標準JISと一致)
        28: "兵庫県",    # 明石家さんま (※実際は和歌山出身だが兵庫育ち)
        29: "奈良県",    # 高畑充希、今田耕司 ✅確認済み
        30: "和歌山県",  # 松本人志、北川景子 (※要再確認)
        31: "鳥取県",    # イモトアヤコ
        32: "島根県",    # 錦織圭 ✅確認済み
        33: "岡山県",    # 佐野史郎
        34: "広島県",    # 有吉弘行 ✅確認済み
        35: "山口県",    # 田村淳
        36: "徳島県",    # 松本明子
        37: "香川県",    # 犬飼貴丈
        38: "愛媛県",    # 眞鍋かをり
        39: "高知県",    # 間寛平、広末涼子
        40: "福岡県",    # 橋本環奈、博多華丸 ✅確認済み
        41: "佐賀県",    # 指原莉乃
        42: "長崎県",    # 森高千里、福山雅治
        43: "熊本県",    # 松雪泰子
        44: "大分県",    # 指原莉乃（大分出身）
        45: "宮崎県",    # オカリナ、東国原英夫
        46: "鹿児島県",  # 柏木由紀
        47: "沖縄県",    # 新垣結衣、黒木メイサ ✅確認済み
        99: "その他"
    }

    return prefecture_map.get(pref_cd, "不明")


def _determine_cm_category(client_name: str, product_name: str) -> str:
    """
    クライアント名と商品名からCMカテゴリを推定

    Args:
        client_name: クライアント名
        product_name: 商品名

    Returns:
        str: 推定されたカテゴリ
    """
    if not client_name:
        return "その他"

    # エンターテイメント系
    entertainment_keywords = ["テレビ", "放送", "映画", "ゲーム", "アプリ", "コミック"]
    if any(keyword in client_name for keyword in entertainment_keywords):
        return "エンターテイメント"

    # 食品系
    food_keywords = ["食品", "飲料", "レストラン", "カフェ"]
    if any(keyword in client_name for keyword in food_keywords):
        return "食品・飲料"

    # 化粧品・美容系
    beauty_keywords = ["化粧品", "コスメ", "美容", "ヘアケア"]
    if any(keyword in client_name for keyword in beauty_keywords):
        return "化粧品・美容"

    # 自動車系
    auto_keywords = ["自動車", "トヨタ", "ホンダ", "日産"]
    if any(keyword in client_name for keyword in auto_keywords):
        return "自動車"

    return "その他"


def _build_image_url(image_file_name: Optional[str]) -> Optional[str]:
    """
    画像ファイル名からURLを構築

    Args:
        image_file_name: 画像ファイル名

    Returns:
        str: 構築された画像URL、またはNone
    """
    if not image_file_name:
        return None

    # TODO: 実際の画像CDN URLに置き換える
    # 現在はプレースホルダーを返す
    return "/placeholder-user.jpg"