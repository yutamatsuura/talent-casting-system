# Nowデータ_20251126.xlsx シート構成 クイックリファレンス

**更新日**: 2025年12月3日

---

## 1. シート機能マップ

### シート全体構図

```
┌─────────────────────────────────────────────────────────────┐
│  Nowデータ_20251126.xlsx                                     │
│  (クライアント所有のタレントDB)                              │
└─────────────────────────────────────────────────────────────┘
                           │
                ┌──────────┴──────────┐
                ▼                     ▼
        ┌─────────────┐      ┌──────────────┐
        │ m_account   │      │ m_talent_act │ ⭐ 金額情報
        │ (マスター)  │      │ (金額・条件) │   STEP 0参照
        │ 4,819件     │      │ 3,225件      │
        └─────────────┘      └──────────────┘
              │                     │
    ┌─────────┼─────────┬─────────┬┘
    │         │         │         │
    ▼         ▼         ▼         ▼
 タレント    その他    スタッフ   メディア
 基本情報    メモ      連絡先     出演情報
 m_account m_talent m_talent  m_talent
           _other   _staff     _media

    ┌─────────┬─────────┬──────────┐
    ▼         ▼         ▼          ▼
   CM契約    契約状態   契約結果   キーワード
m_talent  m_talent  m_talent   m_talent
  _cm      _deal     _deal_     _frequent
          (初期化)   result     _keyword
```

---

## 2. シート別機能一覧表

### マスターシート

| # | シート名 | レコード数 | 主キー | 役割 | 更新頻度 | 完全性 |
|---|---------|----------|--------|------|---------|--------|
| 1 | **m_account** | 4,819 | account_id | タレント基本情報 | 低 | 100% ✓ |

**含有カラム:**
- 名前（last_name, first_name, last_name_kana...）
- 性別、年齢、所属事務所、ジャンル
- SNSアカウント情報（Twitter, Instagram, TikTok, YouTube）
- メタデータ（登録日、更新日、削除フラグ）

**用途:**
- すべてのマッチング処理の基盤
- タレント情報の統一管理

---

### マッチング関連シート

| # | シート名 | レコード数 | 主キー | 役割 | 参照箇所 |
|---|---------|----------|--------|------|---------|
| 7 | **m_talent_act** | 3,225 | account_id | 金額・条件情報 | STEP 0予算フィルタ |

**含有カラム:**
```
年間契約:     money_min_one_year, money_max_one_year ← STEP 0で使用
1クール:      money_min_one_cool, money_max_one_cool
2クール:      money_min_two_cool, money_max_two_cool
制作費:       cost_min/max_one_year, cost_min/max_one_cool, cost_min/max_two_cool
その他:       conditions, event_appearance_flag, lecture_appearance_flag
```

**用途:**
- 予算フィルタリング（money_max_one_year <= ユーザー選択予算）
- 契約金額の見積もり
- イベント出演可否判定

**重要:** このシートの `money_max_one_year` がCLAUDE.mdの「STEP 0」で参照される唯一のカラム

---

### 履歴・実績シート

| # | シート名 | レコード数 | 主キー | 役割 | 関係 |
|---|---------|----------|--------|------|------|
| 3 | m_talent_cm | 6,688 | account_id + sub_id | CM契約履歴 | 1タレント:2.76CM件 |
| 6 | m_talent_deal_result | 28 | account_id + sub_id | 契約成立実績 | 1タレント:1.08件 |

**m_talent_cm のカラム:**
- client_name（クライアント企業）
- product_name（製品名）
- use_period_start/end（出演期間）
- rival_category_type_cd1-4（競合カテゴリ）← 新規案件の競合判定に利用可

**m_talent_deal_result のカラム:**
- job_name（案件名）
- deal_result_cd（成立=1）
- smooth_rating_cd（対応スムーズ度 2-5）
- note（取引メモ）

**用途:**
- タレント実績の可視化
- 営業参考資料
- スムーズ度評価による営業プロセス改善

---

### サポート情報シート

| # | シート名 | レコード数 | 主キー | 役割 | 完全性 |
|---|---------|----------|--------|------|--------|
| 2 | m_talent_other | 4,488 | account_id | その他メモ | 93% |
| 4 | m_talent_media | 4,305 | account_id | メディア出演情報 | 89% |
| 5 | m_talent_deal | 3,698 | account_id | 契約フラグ | 77% (初期化済) |
| 8 | m_talent_staff | 4,232 | account_id | スタッフ連絡先 | 1% (未入力) |
| 10 | m_talent_frequent_keyword | 1,726 | account_id + sub_id | SNS分析キーワード | 25% |

**m_talent_other:**
- スキャンダル情報、個人情報（配偶者等）
- 営業判断の参考情報

**m_talent_media:**
- ドラマ出演履歴
- 映画出演履歴
- 舞台出演履歴
- バラエティ出演フォーマット
- プロフィール（自由テキスト）
  **注:** 改行で複数行テキスト（正規化が必要）

**m_talent_deal:**
- decision_flag（契約決定フラグ）
- contact_flag（連絡フラグ）
- smooth_rating（スムーズ度 0-5）
  **現状:** ほぼすべて 0（初期化済み、未運用）

**m_talent_staff:**
- staff_name, staff_tel1/2/3, staff_mail
  **現状:** 99%未入力（今後の実装予定）

**m_talent_frequent_keyword:**
- frequent_category_type_cd（分類 1-5）
- source（参考URL）
  **用途:** SNS分析による話題キーワード抽出

---

### 未実装シート

| # | シート名 | レコード数 | 状態 |
|---|---------|----------|------|
| 9 | m_talent_movie | 1 | テストデータのみ |

**用途:** ポートフォリオ動画URL（未実装）

---

## 3. 現在のtalentsテーブルとの対応

### talents テーブルの構成源

```
talents テーブル
├── m_account から抽出
│   ├── account_id
│   ├── last_name, first_name
│   ├── gender_type_cd
│   ├── company_name
│   ├── official_url
│   ├── birthday
│   ├── act_genre
│   ├── del_flag
│   ├── regist_date
│   └── up_date
│
└── m_talent_act から抽出（外部キー結合）
    ├── money_min_one_year ← STEP 0 予算フィルタで参照
    └── money_max_one_year ← STEP 0 予算フィルタで参照
```

### マッチングロジック STEP 0 での参照

```sql
SELECT *
FROM talents
LEFT JOIN talents_pricing ON talents.account_id = talents_pricing.account_id
WHERE talents_pricing.money_max_one_year <= ? -- ユーザー選択予算
  AND talents.del_flag = 0
  AND talents_pricing.target_segment_id = ? -- ユーザー選択ターゲット層
```

---

## 4. データ品質状況

### 入力率表

| シート | 入力率 | 理由・注記 |
|--------|--------|----------|
| m_account | 100% | すべてのタレント |
| m_talent_act | 67% | 3224/4819（有料契約タレントのみ） |
| m_talent_cm | 50% | 2421/4819（活動中タレント） |
| m_talent_media | 89% | 4305/4819（定期更新） |
| m_talent_deal | 77% | 3698/4819（初期化済み） |
| m_talent_other | 93% | 4488/4819（補足あり） |
| m_talent_staff | 88% | 4232/4819（ほぼ未入力） |
| m_talent_movie | 0.02% | 1/4819（未実装） |
| m_talent_frequent_keyword | 25% | 1214/4819（SNS分析中） |

### 実装優先度（推奨）

```
Phase 6（即座）:
  m_account     → talents テーブル化
  m_talent_act  → talents_pricing テーブル化（foreign key）

Phase 7（1-2ヶ月）:
  m_talent_cm   → talent_cm_contracts テーブル化
  m_talent_deal → talent_deals テーブル化

Phase 8（3-6ヶ月）:
  m_talent_media     → media_appearances テーブル化（正規化）
  m_talent_deal_result → deal_results テーブル化（履歴管理）
  m_talent_frequent_keyword → keywords テーブル化
  
Phase 9（6-12ヶ月）:
  m_talent_staff → staff_contacts テーブル化（実装後）
  m_talent_movie → portfolio_videos テーブル化（実装後）
  m_talent_other → talent_notes テーブル化（オプション）
```

---

## 5. 注意事項

### 必須チェックリスト

- [ ] m_account の `del_flag = 0` で有効タレントのみを抽出
- [ ] m_talent_act との LEFT JOIN で金額データを結合
- [ ] `money_max_one_year = NULL` の場合、999999万円等の最大値で代用
- [ ] m_talent_media の改行テキスト（_x000D_）は別テーブルに分割
- [ ] gender_type_cd: 1=男, 2=女, 3=グループ等 で分類
- [ ] *_flag カラム: 1=Yes, 0/9=No (一貫性不均一)

### データ品質の警告

1. **スタッフ連絡先未入力**
   - m_talent_staff はテンプレートのみ（99%NULL）
   - 実装前に事務所に連絡先確認が必須

2. **メディア出演のテキスト正規化**
   - m_talent_media の drama/movie/stage/variety は改行混在
   - DB化前にテキスト分割処理が必須

3. **金額データの NULL 値**
   - 松本人志など著名人は money_max_one_year = NULL
   - マッチングロジック側で「上限なし」判定を実装

4. **キーワード分類体系不明**
   - m_talent_frequent_keyword の type_cd 1-5 の定義がなし
   - マスタテーブル確認が必要

---

## 6. Excelファイル活用ガイド

### 各シートの確認方法

| 確認項目 | 対象シート | 方法 |
|---------|----------|------|
| タレント基本情報 | m_account | 名前やジャンルで検索 |
| 金額・条件確認 | m_talent_act | account_id で検索 |
| CM実績確認 | m_talent_cm | account_id で フィルタ |
| 出演履歴確認 | m_talent_media | account_id で 確認 |
| スキャンダル確認 | m_talent_other | account_id で 検索 |
| 営業フラグ確認 | m_talent_deal | account_id で 確認 |

### Excel での活用 Tips

**並び替え推奨:**
```
SORT BY: last_name_kana ASC, first_name_kana ASC
FILTER: del_flag = 0
```

**検索推奨:**
```
Ctrl+F で sort_last_name_kana で検索
（ひらがな・カタカナ混在対策）
```

---

## 7. テーブル設計図（推奨）

### Phase 6 実装構成

```sql
talents (m_account由来)
  ├── account_id (PK)
  ├── name_full
  ├── gender_type_cd
  ├── company_name
  ├── del_flag
  └── ...27カラム

talents_pricing (m_talent_act由来)
  ├── account_id (PK, FK→talents)
  ├── money_min_one_year
  ├── money_max_one_year ← STEP 0 で参照
  ├── cost_min_one_year
  ├── cost_max_one_year
  ├── event_appearance_flag
  └── ...20カラム

talent_cm_contracts (m_talent_cm由来)
  ├── account_id (PK①, FK→talents)
  ├── sub_id (PK②)
  ├── client_name
  ├── product_name
  ├── use_period_start
  ├── use_period_end
  ├── rival_category_type_cd1
  └── ...15カラム
```

---

## 8. 今後の検討項目

### AI が構築した追加テーブル（要確認）

Excelファイルには存在しないが、CLAUDE.md に記載されている:

```
talent_scores
  ├── account_id
  ├── vr_popularity
  ├── tpr_power_score
  └── target_segment_id ← STEP 1 で使用

talent_images
  ├── account_id
  ├── industry_id
  ├── image_score
  └── ...

industries
  ├── industry_id
  ├── industry_name
  └── ...

target_segments
  ├── target_segment_id
  ├── segment_name
  ├── age_range
  └── gender
```

**確認タスク:**
- [ ] AI が上記テーブルをどこから構築したか確認
- [ ] VR/TPRのデータソースを特定
- [ ] 業種イメージスコアの算出方法を確認

---

## 結論

**Nowデータ_20251126.xlsx は、タレント DB の唯一の真実のソース（Single Source of Truth）です。**

- **m_account**: マスターテーブル（4,819タレント）
- **m_talent_act**: マッチング計算用の金額テーブル（3,225タレント）
- **その他**: サポート・履歴データ（品質・完全性に不均一性）

現在のテーブル設計は「m_account + m_talent_act」を統合するアプローチで正確です。

次フェーズでは各テーブルを正規化して PostgreSQL に移行し、マッチングロジックの実装を進めます。

