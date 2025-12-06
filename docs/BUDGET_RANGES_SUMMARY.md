# budget_rangesマスタテーブル サマリーレポート

**作成日**: 2025-12-03  
**ステータス**: 重大な問題を検出

---

## 結論（3行まとめ）

1. ✅ **テーブル構造**: 正常（CLAUDE.md準拠）
2. ✅ **予算区分名称**: 完全一致（ワーカー説明資料と同一）
3. ❌ **重大問題**: 金額の単位が1/10000倍 + talentsテーブルのmoney_max_one_yearが全件NULL

---

## 現在のデータ

```
ID | 名称                         | min_amount | max_amount
───┼──────────────────────────────┼────────────┼──────────
1  | 1,000万円未満                 | 0          | 999
2  | 1,000万円～3,000万円未満       | 1,000      | 2,999
3  | 3,000万円～1億円未満           | 3,000      | 9,999
4  | 1億円以上                     | 10,000     | NULL
```

---

## 重大な問題

### 問題1: 金額の単位が違う

| 区分 | 現在値 | 期待値 | 倍率 |
|------|--------|--------|------|
| レコード#2 min_amount | 1,000 | 10,000,000 | 1/10,000 |
| レコード#2 max_amount | 2,999 | 29,999,999 | 1/10,000 |

**影響**: STEP 0フィルタリングで talentsテーブルのmoney_max_one_yearと比較できない

### 問題2: talentsテーブルのmoney_max_one_yearが全件NULL

```
総タレント数: 4,819人
money_max_one_year > 0: 0人  ← ❌ すべてNULL
```

**影響**: STEP 0フィルタリング実行不可（0件になる）

### 問題3: APIエンドポイント未実装

```
❌ GET /api/budget-ranges が実装されていない
```

**影響**: フロント画面で予算区分を選択できない

---

## 各予算区分に該当するタレント数（現在）

```
✅ 1,000万円未満               0人  ← おかしい
✅ 1,000万円～3,000万円未満     0人  ← おかしい
✅ 3,000万円～1億円未満         0人  ← おかしい
✅ 1億円以上                   0人  ← おかしい
─────────────────────────────────────────
合計                         0人  ← これが問題
```

---

## 修正方法

### ステップ1: budget_rangesの金額を修正

```bash
# 1. insert_budget_ranges.py を開く
# 2. budget_data の値を修正:
budget_data = [
    {"name": "1,000万円未満", "min_amount": 0, "max_amount": 9999999, "display_order": 1},
    {"name": "1,000万円～3,000万円未満", "min_amount": 10000000, "max_amount": 29999999, "display_order": 2},
    {"name": "3,000万円～1億円未満", "min_amount": 30000000, "max_amount": 99999999, "display_order": 3},
    {"name": "1億円以上", "min_amount": 100000000, "max_amount": None, "display_order": 4},
]

# 3. 実行
python3 insert_budget_ranges.py
```

### ステップ2: talentsテーブルのmoney_max_one_yearを設定

```sql
-- VRデータ/TPRデータから金額を取得して設定
UPDATE talents SET money_max_one_year = ... WHERE ...;

-- または、テストデータを手動で設定
UPDATE talents SET money_max_one_year = 15000000 WHERE id = 1;
```

### ステップ3: FastAPI エンドポイントを実装

```python
# backend/app/api/endpoints/budget_ranges.py (新規作成)
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.connection import get_db_session

router = APIRouter()

@router.get("/budget-ranges")
async def get_budget_ranges(session: AsyncSession = Depends(get_db_session)):
    """全予算区分を取得"""
    result = await session.execute(
        "SELECT * FROM budget_ranges ORDER BY display_order"
    )
    return {"success": True, "data": result.fetchall()}
```

**app/main.py に追加**:
```python
from app.api.endpoints import budget_ranges
app.include_router(budget_ranges.router, prefix="/api", tags=["Master Data"])
```

---

## チェックリスト

- [ ] insert_budget_ranges.py の値を修正
- [ ] python3 insert_budget_ranges.py を実行
- [ ] SELECT * FROM budget_ranges; で確認
- [ ] talentsテーブルにmoney_max_one_yearを設定
- [ ] FastAPI エンドポイント実装
- [ ] GET /api/budget-ranges で動作確認
- [ ] フロントエンド対応

---

## ファイル参照

詳細なレポート: `/Users/lennon/projects/talent-casting-form/docs/BUDGET_RANGES_DETAILED_REPORT.md`

---

**対応開始時期**: 即時（STEP 0フィルタリングの実装に必須）
