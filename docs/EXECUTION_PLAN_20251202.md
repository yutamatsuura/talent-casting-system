# タレントキャスティングシステム データ統合 実行計画書
**作成日:** 2025年12月2日
**対象:** 完全データ再構築プロジェクト

---

## 🎯 目標
Excelデータ（4,819人）+ VR/TPRデータ（16ファイル）を完全統合し、5段階マッチングロジックが正常動作するシステムを構築する

---

## 📊 現在の状況（2025年12月2日 22:30時点）

### ✅ 完了済み
- [x] データベース構造適合性検証（10シート対応確認）
- [x] Excelシート名とDBテーブル名の対応関係調査
- [x] 予算フィルタリングロジック修正
- [x] VRフォルダ構造整理（16ファイル統合）
- [x] データベースバックアップ作成

### ❌ 現在の問題
- データベース全データ削除状態（talents: 0人、VR: 0件、TPR: 0件）
- 間違ったシート読み込み（m_talent_act ← 本来はm_account）

---

## 🚀 実行計画

### Phase 1: Excelデータ完全インポート（優先度：最高）

#### 1.1 m_accountシート → talentsテーブル（4,819人）
**データ内容:** タレント基本情報
**重要仕様:**
- last_name + first_name → name（スペースなし「有吉弘行」）
- account_id: 1から4,819まで連続
- del_flag=0: 3,971人, del_flag=1: 848人

**列マッピング:**
```
account_id → account_id (1-4819)
last_name + first_name → name (スペースなし結合)
kana → kana
gender → gender
birth_year → birth_year
category → category
money_max_one_year → money_max_one_year
del_flag → del_flag
```

#### 1.2 残り9シートのインポート
| Excelシート | DBテーブル | レコード数 | 用途 |
|------------|-----------|----------|-----|
| m_talent_act | talent_pricing | 3,224件 | ギャラ情報 |
| m_talent_cm | talent_cm_history | 6,687件 | CM履歴 |
| m_talent_media | talent_media_experience | 4,305件 | メディア経験 |
| m_talent_deal | talent_business_info | 3,698件 | ビジネス情報 |
| m_talent_deal_result | talent_deal_results | 27件 | 取引結果 |
| m_talent_staff | talent_contacts | 4,232件 | 連絡先 |
| m_talent_movie | talent_movies | 1件 | 動画情報 |
| m_talent_frequent_keyword | talent_keywords | 1,726件 | キーワード |
| m_talent_other | talent_notes | 4,487件 | その他情報 |

---

### Phase 2: VR/TPRデータ処理（優先度：高）

#### 2.1 VRデータ処理（16ファイル）
**場所:** `/Users/lennon/projects/talent-casting-form/DB情報/VR_data/`
**ファイル構成:**
- VR男性タレント_[ターゲット層]_202507.csv × 8ファイル
- VR女性タレント_[ターゲット層]_202507.csv × 8ファイル

**処理内容:**
1. 名前照合（異体字対応済み）
2. talent_imagesテーブルへ格納
3. 想定レコード数: 約270,000件（4,819人 × 8ターゲット × 7項目）

**VRデータ構造:**
```sql
talent_images {
  talent_id: FK → talents.id
  target_segment_id: 1-8 (8ターゲット層)
  image_item_id: 1-7 (7イメージ項目)
  score: DECIMAL
}
```

**7つのイメージ項目:**
1. おもしろい
2. 清潔感がある
3. 個性的な
4. 信頼できる
5. かわいい
6. カッコいい
7. 大人の魅力がある

#### 2.2 TPRデータ処理
**処理内容:**
1. TPR年齢層マッピング（10-19歳 → 12-19歳等）
2. talent_scoresテーブルへ格納
3. 想定レコード数: 約38,400件（4,819人 × 8ターゲット）

**TPRデータ構造:**
```sql
talent_scores {
  talent_id: FK → talents.id
  target_segment_id: 1-8
  vr_popularity: DECIMAL
  tpr_power_score: DECIMAL
  base_power_score: (vr_popularity + tpr_power_score) / 2
}
```

**8つのターゲット層:**
1. 男性12-19歳
2. 男性20-34歳
3. 男性35-49歳
4. 男性50-69歳
5. 女性12-19歳
6. 女性20-34歳
7. 女性35-49歳
8. 女性50-69歳

#### 2.3 base_power_score計算
**計算式:**
```sql
UPDATE talent_scores
SET base_power_score = (vr_popularity + tpr_power_score) / 2
WHERE vr_popularity IS NOT NULL AND tpr_power_score IS NOT NULL
```

---

### Phase 3: システム動作検証（優先度：中）

#### 3.1 5段階マッチングロジックテスト
**STEP 0:** 予算フィルタリング（修正済み）
**STEP 1:** 基礎パワー得点
**STEP 2:** 業種イメージ査定
**STEP 3:** 基礎反映得点
**STEP 4:** ランキング確定
**STEP 5:** マッチングスコア振り分け

#### 3.2 パフォーマンステスト
**目標:** 3秒以内のレスポンス
**設計値:** 242ms

#### 3.3 データ品質検証
- 全4,819人のデータ整合性確認
- VR/TPRデータのカバー率確認

---

### Phase 4: 本格運用準備（優先度：低）

#### 4.1 フロントエンド統合テスト
- Next.js診断システムとの連携確認

#### 4.2 本番環境デプロイ準備
- Google Cloud Run設定
- 環境変数設定

---

## 📈 予想データ規模

| データ種別 | レコード数 | 説明 |
|-----------|----------|------|
| talents | 4,819人 | タレント基本情報 |
| talent_images | 270,000件 | VRイメージデータ |
| talent_scores | 38,400件 | VR/TPRスコア統合 |
| その他テーブル | 約30,000件 | CM履歴等の詳細情報 |
| **合計** | **約340,000件** | 全データ統合 |

---

## ⚠️ 重要な技術的制約

### 名前照合仕様
- VRデータとの照合時は「有吉弘行」（スペースなし）
- 異体字・文字化け対応実装済み

### データ整合性
- account_id: 1-4,819の連続性保証
- del_flag=0: 有効データのみ5段階マッチング対象
- del_flag=1: 保持するがマッチング除外

### パフォーマンス要件
- PostgreSQL PERCENT_RANK()活用
- 複合インデックス最適化済み
- N+1問題回避済み

---

## 🛡️ リスクと対策

### 高リスク
1. **データ消失:** → バックアップ戦略実装済み
2. **名前照合失敗:** → 異体字対応実装済み
3. **パフォーマンス劣化:** → インデックス最適化済み

### 中リスク
1. **メモリ不足:** → バッチ処理で分割実行
2. **ネットワーク接続問題:** → リトライ機構実装

---

## 📅 実行スケジュール（推定）

| Phase | 作業内容 | 予想時間 |
|-------|---------|----------|
| 1.1 | m_accountインポート | 30分 |
| 1.2 | 残り9シートインポート | 90分 |
| 2.1 | VRデータ処理 | 120分 |
| 2.2 | TPRデータ処理 | 60分 |
| 2.3 | base_power_score計算 | 15分 |
| 3.1-3.3 | 動作検証 | 30分 |
| **合計** | | **約6時間** |

---

## ✅ 完了確認チェックリスト

### Phase 1完了条件
- [ ] talents: 4,819人インポート完了
- [ ] 全10テーブルのデータ投入完了
- [ ] account_id 1-4,819の連続性確認

### Phase 2完了条件
- [ ] VR: 約270,000件インポート完了
- [ ] TPR: 約38,400件インポート完了
- [ ] base_power_score計算完了

### Phase 3完了条件
- [ ] 5段階マッチングロジック正常動作
- [ ] レスポンス時間3秒以内達成
- [ ] データ品質100%確認

---

**次回実行時の注意:**
1. 必ずm_accountシートから開始する
2. VRデータ処理前にtalents完全インポート完了を確認
3. 各Phase完了後にデータ整合性チェックを実行