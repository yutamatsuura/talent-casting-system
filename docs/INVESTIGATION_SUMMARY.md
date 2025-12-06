# Nowデータ_20251126.xlsx 調査完了レポート

**調査日**: 2025年12月3日  
**調査対象**: `/Users/lennon/projects/talent-casting-form/DB情報/Nowデータ_20251126.xlsx`  
**調査者**: Claude Code (AI)  
**ステータス**: 調査完了 ✓

---

## 概要

Excelファイルに含まれる10個のシート構造を詳細に調査しました。その結果、AIが構築した「talents」テーブルが適切にm_account（マスター）とm_talent_act（金額情報）からデータを取得していることが確認されました。

---

## 主要な発見

### 1. シート構成の明確化

| シート数 | マスター | マッチング関連 | サポート | 未実装 |
|---------|---------|------------|---------|--------|
| 10個 | 1個 | 1個 | 7個 | 1個 |

**マスター**: m_account（4,819タレント）  
**マッチング関連**: m_talent_act（3,225タレント）← STEP 0で参照  
**サポート情報**: m_talent_cm, m_talent_media, m_talent_deal等（品質不均一）  
**未実装**: m_talent_movie（テストデータのみ）

### 2. 金額情報の所在確認（重要発見）

**CLAUDE.md に記載:**
```yaml
STEP 0: 予算フィルタリング
  テーブル: talents.money_max_one_year
  条件: <= ユーザー選択予算上限
```

**実際の所在:**
- `money_min_one_year` → **m_talent_act シート カラム B**
- `money_max_one_year` → **m_talent_act シート カラム C**

**結論**: AIの参照は正確で、テーブル設計方針は適切です。

### 3. データ構造の分離理由

Excelが複数シートに分かれている理由:

| シート分離 | 理由 | 利点 |
|----------|------|------|
| m_account | タレント基本情報 | 変更頻度が低い（安定性） |
| m_talent_act | 金額・条件情報 | 頻繁に更新（柔軟性） |
| m_talent_cm | CM契約履歴 | 1:多関係（正規化） |
| m_talent_media | 出演情報 | テキストが大量（分離） |
| m_talent_deal | 契約フラグ | 運用フラグ（一時的） |

**重要**: これらのシートは「AIが勝手に統合した」のではなく、クライアント側で既に正規化されていたものです。

---

## 各シートの詳細

### 最重要シート: m_talent_act

**レコード数**: 3,225（m_accountの67%）  
**主キー**: account_id  
**用途**: STEP 0 予算フィルタリング

**含有カラム（20個）:**
```
year_contract:  money_min_one_year, money_max_one_year ← ★STEP 0で参照
cool_contract:  money_min_one_cool, money_max_one_cool
other:          cost_min/max_*, event_appearance_flag, conditions等
```

**重要なNULL値処理:**
```
money_max_one_year = NULL
→ 金額上限なし（著名人: 松本人志など）
→ マッチングロジック側で999999万円等で代用する必要あり
```

### 補足シート: m_account

**レコード数**: 4,819（すべてのタレント）  
**主キー**: account_id  
**用途**: タレント基本情報マスター

**含有カラム（27個）:**
- 名前、年齢、性別、所属事務所
- SNSアカウント情報（Twitter, Instagram, TikTok, YouTube）
- 削除フラグ（del_flag）

**削除フラグの重要性:**
```
del_flag = 1 (削除済み)
→ account_id = 5 (テスト) など
→ WHERE del_flag = 0 で必ずフィルタリング
```

---

## 現在のtalentsテーブルの正確性確認

### テーブル構成の検証

```
現在の talents テーブル
│
├── m_account由来のカラム
│   ├── account_id ✓
│   ├── last_name ✓
│   ├── first_name ✓
│   ├── gender_type_cd ✓
│   ├── company_name ✓
│   ├── del_flag ✓
│   └── ...
│
└── m_talent_act由来のカラム
    ├── money_min_one_year ✓ ← STEP 0で参照
    └── money_max_one_year ✓ ← STEP 0で参照
```

**検証結果**: ✓ 構成が正確です

---

## 1:多関係データへの対応

### 複数行を持つシート（正規化されていない）

| シート | 関係 | 処理方法 | 優先度 |
|--------|------|--------|--------|
| m_talent_cm | 1:2.76 | 別テーブル化 | Phase 7 |
| m_talent_deal_result | 1:1.08 | 別テーブル化 | Phase 8 |
| m_talent_frequent_keyword | 1:1.42 | 別テーブル化 | Phase 8 |

**処理前:**
```
1つの talents レコード
  ├── cm_contract_1
  ├── cm_contract_2
  ├── cm_contract_3
  └── ... (最大 2.76件)
```

**処理後:**
```
talents (1件)
  └── FK→ talent_cm_contracts (複数件)
```

---

## データ品質分析結果

### 入力率サマリー

| 優先度 | シート | 入力率 | ステータス |
|--------|--------|--------|----------|
| 必須 | m_account | 100% | ✓ 実装可能 |
| 必須 | m_talent_act | 67% | ⚠ 部分的 |
| 推奨 | m_talent_cm | 50% | ⚠ 部分的 |
| 推奨 | m_talent_media | 89% | ✓ ほぼ完備 |
| 推奨 | m_talent_other | 93% | ✓ ほぼ完備 |
| 今後 | m_talent_staff | 1% | ✗ 未実装 |
| 今後 | m_talent_movie | 0.02% | ✗ 未実装 |

### データ品質上の警告

**1. スタッフ連絡先（m_talent_staff）**
- 現在: 99%が NULL（テンプレートのみ）
- 実装前に事務所から連絡先を取得する必要あり

**2. メディア出演情報（m_talent_media）**
- drama/movie/stage/variety カラムが改行混在テキスト
- DB化前に別テーブルへの分割処理が必須

**3. 金額データのNULL値**
- money_max_one_year = NULL（金額上限なし）
- マッチングロジック側で「999999万円」等で代用

**4. キーワード分類の未定義**
- m_talent_frequent_keyword の type_cd 1-5の定義がない
- マスタテーブル確認が必要

---

## AIが参照する外部テーブル（要確認）

CLAUDE.md に記載されているが、Excelファイルにはないテーブル:

```
talent_scores
  ├── account_id
  ├── vr_popularity      ← VRデータの出典確認が必要
  ├── tpr_power_score    ← TPRデータの出典確認が必要
  └── target_segment_id

talent_images
  ├── account_id
  ├── industry_id
  └── image_score        ← 業種イメージスコアの算出方法確認が必要

industries
  ├── industry_id
  └── industry_name

target_segments
  ├── target_segment_id
  ├── segment_name
  ├── age_range
  └── gender
```

**確認タスク:**
- [ ] VR/TPRデータの取得元を特定
- [ ] 業種イメージスコアの算出方法を文書化
- [ ] マスタテーブルの定義を明確化

---

## 推奨される実装ロードマップ

### Phase 6（即座実装）

```
m_account + m_talent_act を PostgreSQL に統合
├── talents テーブル化 (m_account)
├── talents_pricing テーブル化 (m_talent_act)
└── 外部キー FK: talents.account_id → talents_pricing.account_id
```

**実装時間**: 1-2日

### Phase 7（1-2ヶ月後）

```
履歴・実績データの正規化
├── talent_cm_contracts テーブル化 (m_talent_cm)
├── talent_deals テーブル化 (m_talent_deal)
└── 外部キー FK: talents.account_id → talent_cm_contracts.account_id
```

### Phase 8（3-6ヶ月後）

```
メディア・キーワード・結果データの分割
├── talent_media_appearances テーブル化 (m_talent_media分割)
├── talent_deal_results テーブル化 (m_talent_deal_result)
├── talent_keywords テーブル化 (m_talent_frequent_keyword分割)
└── 関連するマスタテーブルの統合
```

---

## 重要な実装チェックリスト

- [ ] **削除フラグの処理**: WHERE del_flag = 0 を必ず含める
- [ ] **金額NULL値の処理**: money_max_one_year = NULL を処理
- [ ] **改行テキストの分割**: m_talent_media を別テーブルに分割
- [ ] **gender_type_cdの定義**: 1=男, 2=女, 3=グループ等を明確化
- [ ] **フラグ値の統一**: 1/0/9 の意味を統一
- [ ] **外部キー制約**: talentsテーブルに対する参照整合性を維持
- [ ] **VR/TPRデータ**: 出典を特定し、定期更新方法を確立
- [ ] **スタッフ連絡先**: 事務所に確認後、m_talent_staff を入力

---

## 作成されたドキュメント

### 1. 詳細分析レポート（メイン）

**ファイル**: `/Users/lennon/projects/talent-casting-form/docs/excel_sheet_structure_analysis_20251203.md`  
**サイズ**: 32 KB (883行)  
**内容**:
- 全10シートの詳細構造（カラム一覧、サンプルデータ）
- CLAUDE.md との照合（参照項目の実際の所在確認）
- 金額データの詳細（粒度分類、NULL値処理）
- シート間の関係性（外部キー図）
- データ品質分析
- マッチングロジック実装時の必須確認項目
- SQL実装例

### 2. クイックリファレンス

**ファイル**: `/Users/lennon/projects/talent-casting-form/docs/excel_sheet_mapping_summary.md`  
**内容**:
- シート全体構図（視覚化）
- シート別機能一覧（マトリックス）
- 現在のtalentsテーブルとの対応
- データ品質状況（入力率表）
- 実装優先度（Phase別）
- 注意事項と警告
- Excel活用ガイド
- テーブル設計図

---

## 結論と推奨事項

### 現在のテーブル設計は正確

Excelファイルから確認:
- m_account（4,819タレント）からのマスター情報取得: ✓ 正確
- m_talent_act（3,225タレント）からの金額情報取得: ✓ 正確
- カラム名の一致確認: ✓ money_max_one_year が完全一致

### AIが勝手に統合していない

- シート分離は**クライアント側で既に正規化されたもの**
- 各シートは明確な目的を持つ（変更頻度、データ粒度等）
- AIの役割は正しく「正規化されたデータを参照する」こと

### 次ステップ

1. **即座**: Phase 6 で PostgreSQL への統合実装
2. **1-2ヶ月**: Phase 7 で履歴・実績データの正規化
3. **3-6ヶ月**: Phase 8 でメディア・キーワード・結果データの分割
4. **6-12ヶ月**: Phase 9 で未実装シート（staff, movie）の実装

---

## 参考資料

本調査で参照したExcelファイル:
```
/Users/lennon/projects/talent-casting-form/DB情報/Nowデータ_20251126.xlsx
```

本調査で作成したドキュメント:
```
/Users/lennon/projects/talent-casting-form/docs/excel_sheet_structure_analysis_20251203.md
/Users/lennon/projects/talent-casting-form/docs/excel_sheet_mapping_summary.md
/Users/lennon/projects/talent-casting-form/docs/INVESTIGATION_SUMMARY.md (本ファイル)
```

---

**調査完了**: 2025年12月3日  
**確認**: すべてのシート構造が明確化され、現在のテーブル設計方針が正確であることが確認されました。

