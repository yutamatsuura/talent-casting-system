# m_talent_cm テーブル調査報告書

## エグゼクティブサマリー

タレントキャスティングシステムの `m_talent_cm` テーブルについて、実データベースへのアクセスを通じて実施した詳細調査結果を報告します。

**主要結論:**
- `m_talent_cm` テーブルは正常に実装されており、6,687件の高品質なCM出演履歴データを保有
- フロントエンドの `CMHistoryDetail` 型とほぼ対応（product_name の12.2% NULL対応が必要）
- 既存の SQLAlchemy モデル定義には矛盾があり、修正が必須

---

## 1. テーブル構造確認

### 物理テーブル構造（実装状況）

```
テーブル名: m_talent_cm
スキーマ: public
主キー: (account_id, sub_id) - 複合主キー
外部キー: account_id -> m_account.account_id (NO ACTION / NO ACTION)

カラム定義（15カラム）:
```

| # | カラム名 | データ型 | Nullable | 説明 |
|---|---------|---------|---------|------|
| 1 | account_id | INTEGER | NOT NULL | タレントID（FK） |
| 2 | sub_id | INTEGER | NOT NULL | CM出演連番 |
| 3 | client_name | VARCHAR | NULL | クライアント/スポンサー名 |
| 4 | product_name | VARCHAR | NULL | 商品/サービス名 |
| 5 | use_period_start | VARCHAR | NULL | 放映開始日 (YYYY-MM-DD) |
| 6 | use_period_end | VARCHAR | NULL | 放映終了日 (YYYY-MM-DD) |
| 7 | rival_category_type_cd1 | INTEGER | NULL | 競合カテゴリコード1 |
| 8 | rival_category_type_cd2 | INTEGER | NULL | 競合カテゴリコード2 |
| 9 | rival_category_type_cd3 | INTEGER | NULL | 競合カテゴリコード3 |
| 10 | rival_category_type_cd4 | INTEGER | NULL | 競合カテゴリコード4 |
| 11 | agency_name | VARCHAR | NULL | 代理店名 |
| 12 | production_name | VARCHAR | NULL | 制作会社名 |
| 13 | director | VARCHAR | NULL | 監督/演出名 |
| 14 | note | TEXT | NULL | 備考・契約状況等 |
| 15 | regist_date | TIMESTAMP | NULL | 登録日時 |

### インデックス

```sql
CREATE UNIQUE INDEX m_talent_cm_pkey ON public.m_talent_cm USING btree (account_id, sub_id)
```

### 外部キー制約

```
Constraint Name: fk_m_talent_cm_account
  account_id → m_account.account_id
  ON UPDATE: NO ACTION
  ON DELETE: NO ACTION
```

---

## 2. データ投入状況

### レコード数統計

```
総レコード数: 6,687件
対象タレント数: 2,421人
平均CM数/タレント: 2.76件
最多CM数: 26件（川口春奈 account_id=1165）
```

### データ品質指標

```
カラム名                  有値率    NULL件数   品質評価
─────────────────────────────────────────────────
client_name              100.0%        0件      ✓ 優
product_name              87.8%      814件      △ 中（12.2% NULL）
use_period_start           99.6%       26件      ✓ 優
use_period_end             99.2%       56件      ✓ 優
note                       98.4%      107件      ✓ 優
rival_category_type_cd1    99.4%       42件      ✓ 優
rival_category_type_cd[2-4] 99.9%      3-5件     ✓ 優
agency_name                 0.7%     6,643件      ✗ 劣（稀少）
production_name             0.7%     6,641件      ✗ 劣（稀少）
director                    0.5%     6,655件      ✗ 劣（稀少）
regist_date               100.0%        0件      ✓ 優
```

### クライアント・商品統計

```
ユニークなクライアント数: 3,330社
ユニークな商品/サービス: 3,809個
最頻出クライアント: 日本テレビ（年単位での複数商品CM多数）
```

### 日付形式

```
形式: YYYY-MM-DD（ISO 8601準拠）
例:   2025-12-25 ~ 2026-12-24

全レコードが正規形式で統一されている ✓
```

---

## 3. サンプルデータ解析

### 代表例：川口春奈（account_id=1165）

**基本情報:**
- name_full_for_matching: 川口春奈
- last_name_kana: カワグチ
- first_name_kana: ハルナ
- act_genre: 女優
- company_name: 研音

**CM出演数: 26件**

**最新CM（2025/10 契約確認済み）:**
```
client_name: 総務省統計局
product_name: 令和7年国勢調査
use_period_start: 2025-06-24
use_period_end: 2025-12-01
rival_category_type_cd1: 28
note: ※松平健、川口春奈、藤本美貴、パトリック・ハーラン出演
```

**大型/長期契約の例:**
```
client_name: カルビー
product_name: ポテトチップス系
use_period_start: 2018-04-01
use_period_end: 2026-04-12
agency_name: 博報堂
director: 月田茂
rival_category_type_cd1: 2
note: 【2025/10 契約あり確認】
```

---

## 4. フロントエンド型との対応関係

### フロントエンド期待型（CMHistoryDetail）

```typescript
// frontend/src/types/index.ts から抽出

export interface CMHistoryDetail {
  client_name: string;        // 必須
  product_name: string;       // 必須
  use_period_start: string;   // 必須 (ISO形式)
  use_period_end: string;     // 必須 (ISO形式)
  agency_name?: string;       // オプション
  production_name?: string;   // オプション
  director?: string;          // オプション
  category?: string;          // オプション（※DB に存在しない）
  note?: string;             // オプション
}
```

### マッピング対応表

| フロントエンド | DBカラム | 状態 | 備考 |
|---|---|---|---|
| client_name | client_name | ✓完全対応 | 100% 有値 |
| product_name | product_name | △要対応 | 87.8% 有値（12.2% NULL） |
| use_period_start | use_period_start | ✓完全対応 | 99.6% 有値、ISO形式 |
| use_period_end | use_period_end | ✓完全対応 | 99.2% 有値、ISO形式 |
| agency_name | agency_name | ✓対応可 | 0.7% 有値（稀少） |
| production_name | production_name | ✓対応可 | 0.7% 有値（稀少） |
| director | director | ✓対応可 | 0.5% 有値（稀少） |
| category | ※存在しない | ✗未対応 | 別途実装必要 |
| note | note | ✓完全対応 | 98.4% 有値 |

### 差分分析と対応方案

#### 1. product_name の NULL 対応
**問題:** 814件（12.2%）で NULL
**フロント期待:** 必須フィールド
**推奨対応:**
```python
# APIレスポンス時の変換
product_name: cm.product_name or ''  # NULL → 空文字列

# または代替案
product_name: cm.product_name or cm.client_name  # クライアント名を代替
```

#### 2. category フィールド
**問題:** m_talent_cm テーブルに存在しない
**推奨対応案:**
```python
# 案1: m_account から act_genre を取得
category: talent.act_genre  # 女優、俳優等

# 案2: rival_category_type_cd から推測
# (推奨度低：推測精度が低い)

# 案3: フロントで固定値を使用
# (推奨度低：汎用性欠ける)
```

#### 3. agency_name, production_name, director
**現状:** 0.5～0.7% の稀少フィールド
**推奨対応:**
```python
# 有値時のみ返却
if cm.agency_name:
    response['agency_name'] = cm.agency_name
if cm.production_name:
    response['production_name'] = cm.production_name
if cm.director:
    response['director'] = cm.director
```

#### 4. 日付形式
**DB形式:** VARCHAR (YYYY-MM-DD)
**フロント期待:** string (YYYY-MM-DD)
**対応:** そのまま返却可能（型変換不要）

---

## 5. SQLAlchemyモデル定義

### 現在の問題（backend/app/models/__init__.py）

```python
class TalentCmHistory(Base):
    """CM出演履歴テーブル"""
    __tablename__ = "talent_cm_history"  # ✗ 誤り：実際は m_talent_cm
    
    id = Column(Integer, primary_key=True, autoincrement=True)  # ✗ DBに存在しない
    account_id = Column(Integer, ForeignKey(...), nullable=False)
    sub_id = Column(Integer, nullable=False)
    client_name = Column(String(255), nullable=True)
    product_name = Column(String(255), nullable=True)
    use_period_start = Column(Date, nullable=True)  # ✗ DB は VARCHAR
    use_period_end = Column(Date, nullable=True)    # ✗ DB は VARCHAR
    # ✗ 欠落: agency_name, production_name, director
    note = Column(String, nullable=True)
    # ✗ リレーション未定義
```

**矛盾点:**
1. テーブル名: `talent_cm_history` ≠ 実テーブル `m_talent_cm`
2. 主キー: `id` (単一) ≠ 実構造 `(account_id, sub_id)` (複合)
3. 日付型: `Date` ≠ 実型 `VARCHAR`
4. 欠落カラム: agency_name, production_name, director
5. リレーション: 未定義（talent との1:N関係がない）

### 推奨修正実装

```python
class MTalentCM(Base):
    """CM出演履歴テーブル（m_talent_cm）
    
    タレントのCM出演実績を管理するマスタデータ
    
    Notes:
        - 複合主キー: (account_id, sub_id)
        - 1タレント = 複数のCM出演記録（1:N関係）
        - 日付は VARCHAR(YYYY-MM-DD形式)で保存
    """
    __tablename__ = "m_talent_cm"
    
    # ─────────────────────────────────────
    # 主キー（複合）
    # ─────────────────────────────────────
    account_id = Column(
        Integer, 
        ForeignKey("m_account.account_id", ondelete="NO ACTION"),
        primary_key=True,
        nullable=False,
        index=True,
        doc="タレント ID"
    )
    sub_id = Column(
        Integer, 
        primary_key=True, 
        nullable=False,
        doc="CM出演連番（同一タレント内での採番）"
    )
    
    # ─────────────────────────────────────
    # CM基本情報
    # ─────────────────────────────────────
    client_name = Column(
        String(255), 
        nullable=False,
        index=True,
        doc="クライアント/スポンサー名"
    )
    product_name = Column(
        String(500), 
        nullable=True,
        doc="商品/サービス名（12.2% NULL対応）"
    )
    
    # ─────────────────────────────────────
    # 放映期間（VARCHAR YYYY-MM-DD形式）
    # ─────────────────────────────────────
    use_period_start = Column(
        String(10), 
        nullable=True,
        doc="放映/契約開始日（YYYY-MM-DD）"
    )
    use_period_end = Column(
        String(10), 
        nullable=True,
        doc="放映/契約終了日（YYYY-MM-DD）"
    )
    
    # ─────────────────────────────────────
    # 競合/ライバルカテゴリ（最大4つ）
    # ─────────────────────────────────────
    rival_category_type_cd1 = Column(
        Integer, 
        nullable=True,
        doc="競合カテゴリコード1"
    )
    rival_category_type_cd2 = Column(
        Integer, 
        nullable=True,
        doc="競合カテゴリコード2"
    )
    rival_category_type_cd3 = Column(
        Integer, 
        nullable=True,
        doc="競合カテゴリコード3"
    )
    rival_category_type_cd4 = Column(
        Integer, 
        nullable=True,
        doc="競合カテゴリコード4"
    )
    
    # ─────────────────────────────────────
    # 制作・プロダクション情報（稀少：0.5-0.7%）
    # ─────────────────────────────────────
    agency_name = Column(
        String(255), 
        nullable=True,
        doc="広告代理店名（0.7% の み有値）"
    )
    production_name = Column(
        String(255), 
        nullable=True,
        doc="制作会社名（0.7% のみ有値）"
    )
    director = Column(
        String(255), 
        nullable=True,
        doc="監督/演出名（0.5% のみ有値）"
    )
    
    # ─────────────────────────────────────
    # メタデータ
    # ─────────────────────────────────────
    note = Column(
        Text, 
        nullable=True,
        doc="備考・契約状況確認済みマーク等（98.4% 有値）"
    )
    regist_date = Column(
        DateTime, 
        nullable=True,
        doc="登録日時"
    )
    
    # ─────────────────────────────────────
    # リレーション
    # ─────────────────────────────────────
    talent = relationship(
        "Talent",
        back_populates="cm_history",
        foreign_keys=[account_id],
        doc="タレント基本情報への参照"
    )
    
    # ─────────────────────────────────────
    # インデックス・制約
    # ─────────────────────────────────────
    __table_args__ = (
        Index("idx_m_talent_cm_account", "account_id"),
        Index("idx_m_talent_cm_period", "use_period_start", "use_period_end"),
        Index("idx_m_talent_cm_client", "client_name"),
    )
    
    # ─────────────────────────────────────
    # メソッド
    # ─────────────────────────────────────
    def to_dict(self) -> dict:
        """CMHistoryDetail型への変換用メソッド"""
        return {
            'client_name': self.client_name,
            'product_name': self.product_name or '',  # NULL → 空文字列
            'use_period_start': self.use_period_start,
            'use_period_end': self.use_period_end,
            'agency_name': self.agency_name,
            'production_name': self.production_name,
            'director': self.director,
            'note': self.note,
        }
    
    def get_rival_categories(self) -> list[int]:
        """ライバルカテゴリコードをリスト化"""
        rivals = []
        for cd in [self.rival_category_type_cd1, self.rival_category_type_cd2,
                   self.rival_category_type_cd3, self.rival_category_type_cd4]:
            if cd is not None:
                rivals.append(cd)
        return rivals
    
    def __repr__(self):
        return f"<MTalentCM(account_id={self.account_id}, sub_id={self.sub_id}, client='{self.client_name}')>"
```

### Talent モデルへのリレーション追加

```python
class Talent(Base):
    """タレント基本情報テーブル（m_account）"""
    __tablename__ = "m_account"
    
    account_id = Column(Integer, primary_key=True, autoincrement=True)
    name_full_for_matching = Column(String(255), nullable=False, index=True)
    # ... その他のカラム ...
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # リレーション
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    talent_scores = relationship("TalentScore", back_populates="talent", ...)
    talent_images = relationship("TalentImage", back_populates="talent", ...)
    talent_act = relationship("TalentAct", back_populates="account", ...)
    
    # 新規追加: CM履歴
    cm_history = relationship(
        "MTalentCM",
        back_populates="talent",
        cascade="all, delete-orphan",
        foreign_keys="MTalentCM.account_id",
        doc="CM出演履歴（1:N関係）"
    )
```

---

## 6. m_account との関連設計

### リレーション図

```
m_account (1) ─────────────┬──────────── (*) m_talent_cm
             account_id (PK)   account_id (FK, PK)
                               sub_id (PK)
```

### JOIN 構造の実装例

```python
# SQLAlchemy ORM での取得
from sqlalchemy.orm import Session

def get_talent_detail(session: Session, account_id: int) -> dict:
    """タレント詳細情報（CM履歴を含む）を取得"""
    talent = session.query(Talent).filter(
        Talent.account_id == account_id
    ).options(
        joinedload(Talent.cm_history)
    ).first()
    
    if not talent:
        return None
    
    return {
        'account_id': talent.account_id,
        'name': talent.name_full_for_matching,
        'kana': f"{talent.last_name_kana or ''}{talent.first_name_kana or ''}".strip(),
        'category': talent.act_genre,
        'company_name': talent.company_name,
        'cm_history': [
            cm.to_dict() for cm in sorted(
                talent.cm_history, 
                key=lambda x: x.sub_id
            )
        ]
    }
```

### SQL での直接実装例

```sql
-- Raw SQL での取得（パフォーマンス重視）
SELECT 
    ma.account_id,
    ma.name_full_for_matching AS name,
    CONCAT(ma.last_name_kana, ma.first_name_kana) AS kana,
    ma.act_genre AS category,
    ma.company_name,
    mc.sub_id,
    mc.client_name,
    mc.product_name,
    mc.use_period_start,
    mc.use_period_end,
    mc.agency_name,
    mc.production_name,
    mc.director,
    mc.note,
    mc.rival_category_type_cd1,
    mc.rival_category_type_cd2,
    mc.rival_category_type_cd3,
    mc.rival_category_type_cd4
FROM 
    m_account ma
    INNER JOIN m_talent_cm mc ON ma.account_id = mc.account_id
WHERE 
    ma.account_id = $1
ORDER BY 
    mc.sub_id;
```

---

## 7. パフォーマンス最適化

### 必須インデックス

```
✓ 既存:
  - PRIMARY KEY (account_id, sub_id)
  
✓ 推奨追加:
  - idx_m_talent_cm_account (account_id)
    → 特定タレントのCM履歴取得を高速化
  
  - idx_m_talent_cm_period (use_period_start, use_period_end)
    → 期間検索を高速化
  
  - idx_m_talent_cm_client (client_name)
    → クライアント別CM検索に対応
```

### クエリパフォーマンス目標

```
処理内容                    目標時間   実測値  
─────────────────────────────────────────
1タレント (26件CM) 取得      < 50ms   
複数タレント (100件) 取得    < 200ms
全CM検索 (6,687件)         < 500ms
```

---

## 8. API エンドポイント設計

### タレント詳細情報取得

```
エンドポイント: GET /api/talents/{account_id}

レスポンス仕様:
{
  "success": true,
  "data": {
    "account_id": 1165,
    "name": "川口春奈",
    "kana": "カワグチハルナ",
    "category": "女優",
    "company_name": "研音",
    "cm_history": [
      {
        "client_name": "総務省統計局",
        "product_name": "令和7年国勢調査",
        "use_period_start": "2025-06-24",
        "use_period_end": "2025-12-01",
        "agency_name": null,
        "production_name": null,
        "director": null,
        "note": "※松平健、川口春奈、藤本美貴、パトリック・ハーラン出演"
      },
      ...（合計26件）
    ]
  }
}
```

### エラーハンドリング

```
404 Not Found:
{
  "success": false,
  "error_code": "TALENT_NOT_FOUND",
  "error_message": "指定されたタレントが見つかりません"
}

500 Internal Server Error:
{
  "success": false,
  "error_code": "DATABASE_ERROR",
  "error_message": "データベース接続エラーが発生しました"
}
```

---

## 9. フロントエンド実装例

### TalentDetailModal コンポーネントの実装

```typescript
// frontend/src/components/diagnosis/Results/TalentDetailModal.tsx

async function fetchTalentDetail() {
  setLoading(true);
  try {
    const response = await fetch(`/api/talents/${talent.account_id}`);
    
    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }
    
    const { data } = await response.json();
    
    setDetailData({
      account_id: data.account_id,
      name: data.name,
      kana: data.kana,
      category: data.category,
      matching_score: talent.matching_score,
      ranking: talent.ranking,
      cm_history: data.cm_history as CMHistoryDetail[],
    });
  } catch (error) {
    console.error('タレント詳細データ取得失敗:', error);
    // フォールバック処理
  } finally {
    setLoading(false);
  }
}
```

---

## 10. 実装チェックリスト

### Phase 1: モデル定義（優先度 HIGH）
- [ ] `MTalentCM` クラスを定義
  - [ ] テーブル名: `m_talent_cm`
  - [ ] 複合主キー: (account_id, sub_id)
  - [ ] 15カラム全て実装
  - [ ] リレーション: Talent との1:N
  - [ ] ユーティリティメソッド: `to_dict()`, `get_rival_categories()`

- [ ] `Talent` モデルに `cm_history` リレーション追加

- [ ] `TalentCmHistory` クラス削除（既存の誤ったモデル）

### Phase 2: API 実装（優先度 HIGH）
- [ ] `GET /api/talents/{account_id}` エンドポイント実装
- [ ] CM履歴取得 SQL / ORM クエリ実装
- [ ] null handling: product_name, agency_name 等
- [ ] エラーハンドリング: 404, 500 等
- [ ] レスポンス仕様書作成

### Phase 3: フロント連携（優先度 MEDIUM）
- [ ] `TalentDetailModal` コンポーネント修正
  - [ ] モックデータ → 実API呼び出しに変更
  - [ ] ローディング状態の表示
  - [ ] エラー時のフォールバック

- [ ] `CMHistoryDetail` 型の検証
  - [ ] product_name: null 許容
  - [ ] agency_name, production_name, director: optional確認

### Phase 4: テスト・検証（優先度 MEDIUM）
- [ ] ユニットテスト: `MTalentCM.to_dict()` 等
- [ ] 統合テスト: API エンドポイント
- [ ] E2E テスト: CM履歴表示フロー
- [ ] パフォーマンステスト: 26件取得時間計測
- [ ] NULL対応テスト: product_name が NULL のレコード確認

### Phase 5: ドキュメント（優先度 LOW）
- [ ] API 仕様書（OpenAPI/Swagger）
- [ ] DB スキーマ図更新
- [ ] 開発ガイド: CM履歴取得パターン集

---

## 11. リスク管理

### リスク: product_name 12.2% NULL

**影響度:** 中
**発生確率:** 高

**対応:**
```python
# APIレベルでの NULL 処理
product_name = cm.product_name or ''
```

### リスク: agency_name 等の稀少フィールド

**影響度:** 低
**発生確率:** 高

**対応:** 有値時のみ返却（フロント側で condition rendering）

### リスク: category フィールド欠落

**影響度:** 中
**発生確率:** 確実

**対応:** `m_account.act_genre` から取得 or フロント側で別途実装

---

## 12. 参考資料

### テーブル作成 DDL（参考）

```sql
CREATE TABLE public.m_talent_cm (
    account_id integer NOT NULL,
    sub_id integer NOT NULL,
    client_name character varying,
    product_name character varying,
    use_period_start character varying,
    use_period_end character varying,
    rival_category_type_cd1 integer,
    rival_category_type_cd2 integer,
    rival_category_type_cd3 integer,
    rival_category_type_cd4 integer,
    agency_name character varying,
    production_name character varying,
    director character varying,
    note text,
    regist_date timestamp without time zone,
    PRIMARY KEY (account_id, sub_id),
    FOREIGN KEY (account_id) REFERENCES m_account(account_id) ON DELETE NO ACTION
);

CREATE INDEX m_talent_cm_account ON public.m_talent_cm (account_id);
CREATE INDEX m_talent_cm_period ON public.m_talent_cm (use_period_start, use_period_end);
CREATE INDEX m_talent_cm_client ON public.m_talent_cm (client_name);
```

---

## 13. まとめ

本調査により、`m_talent_cm` テーブルは高品質なCM出演履歴データを保持していることが確認されました。

主要な対応項目は以下の通りです：

1. **SQLAlchemy モデル修正** - 現在の誤ったモデル定義を正確に修正
2. **API エンドポイント実装** - タレント詳細情報取得機能を提供
3. **NULL/オプション対応** - product_name 12.2% NULL への対応
4. **フロント統合** - TalentDetailModal を実API連携に修正

これらの対応により、タレント詳細情報の表示機能を完成させることができます。

---

**作成日:** 2025-12-05
**調査対象DB:** Neon PostgreSQL (neondb)
**レコード数:** 6,687件
**対象タレント:** 2,421人

