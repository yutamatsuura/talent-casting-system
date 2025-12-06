# 緊急課題サマリー：データベース再構築に伴う重大な修正項目

**作成日**: 2025-12-03
**優先度**: ⚠️ 高

---

## ⚠️ 重大な不一致（必須修正）

### 1. Talent テーブルのカラム名不一致

| 項目 | ワーカー説明資料 | 現在のコード | 状態 |
|------|----------------|-----------|------|
| タレント名 | `name_full` | `name` | ❌ 不一致 |
| 年間最小金額 | `money_min_one_year` | （未実装） | ❌ 欠落 |

**影響範囲**:
- SQL クエリでの SELECT 句: `talents.name` → `talents.name_full`
- VR/TPRデータの照合ロジック: name_full で文字列マッチング
- マイグレーション: 既存の `name` を `name_full` へリネーム

**修正難易度**: 低
**推定作業時間**: 30分

---

### 2. STEP 2 マッチングロジックの加減点誤り

**ワーカー説明資料（p.3 加減点表）**:
```
順位帯       加減点
上位15%     +12点
16～30%     +6点
31～50%     +3点   ← ⚠️ 現在: 0点（不正）
51～70%     -3点   ← ⚠️ 現在: -6点（不正）
71～85%     -6点
86～100%    -12点
```

**現在のコード**（matching.py 行118-126）:
```python
CASE
  WHEN percentile_rank <= 0.15 THEN 12.0  ✅ OK
  WHEN percentile_rank <= 0.30 THEN 6.0   ✅ OK
  WHEN percentile_rank <= 0.50 THEN 0.0   ❌ 誤り: +3点であるべき
  WHEN percentile_rank <= 0.70 THEN -6.0  ❌ 誤り: -3点であるべき
  ELSE -12.0                               ✅ OK
END
```

**修正内容**:
```python
CASE
  WHEN percentile_rank <= 0.15 THEN 12.0
  WHEN percentile_rank <= 0.30 THEN 6.0
  WHEN percentile_rank <= 0.50 THEN 3.0   ← 修正
  WHEN percentile_rank <= 0.70 THEN -3.0  ← 修正
  ELSE -12.0
END
```

**影響範囲**:
- マッチング結果の順位が変動
- 特に31～70%帯のタレントの順位が大幅に変わる可能性
- クライアント提案結果が変更される

**修正難易度**: 低
**推定作業時間**: 15分

---

### 3. talent_images スキーマの根本的な構造差異

**ワーカー説明資料の期待値（p.4）**:
```
【データテーブル】
└── talent_images    : イメージスコア7項目（約16,000件）
    主なカラム：
    - account_id        : タレントID
    - target_segment_id : ターゲット層ID
    - image_funny       : おもしろい
    - image_clean       : 清潔感がある
    - image_unique      : 個性的な
    - image_trustworthy : 信頼できる
    - image_cute        : かわいい
    - image_cool        : カッコいい
    - image_mature      : 大人の魅力がある
```

**現在の実装（models/__init__.py）**:
```python
class TalentImage(Base):
    __tablename__ = "talent_images"
    
    id = Column(Integer, primary_key=True)
    talent_id = Column(Integer, ForeignKey("talents.id"))
    target_segment_id = Column(Integer, ForeignKey("target_segments.id"))
    image_item_id = Column(Integer, ForeignKey("image_items.id"))  # ← 正規化
    score = Column(Numeric(5, 2))  # ← 正規化
```

**根本的な差異**:
| 側面 | ワーカー説明資料 | 現在の実装 |
|------|----------------|---------|
| スキーマ形式 | 非正規化（カラムに7項目） | 正規化（行で7項目） |
| 1レコード | タレント × ターゲット層 | タレント × ターゲット層 × イメージ項目 |
| 件数 | 約 2,000 × 8 = 16,000 | 約 2,000 × 8 × 7 = 112,000 |
| 現在のDB | - | 56,448 件（4.8%） |

**修正の判断分岐**:

**選択肢A: 現在の正規化形式を保持**
- 利点: データ整合性、拡張性、インデックス効率
- 欠点: ワーカー説明資料の形式と異なる
- 対応: STEP 2 のクエリを正規化形式に合わせて実装（現在既に対応）
- 難易度: 低
- 推定作業時間: 10分（確認のみ）

**選択肢B: スキーマを完全に再設計**
- 利点: ワーカー説明資料に完全一致
- 欠点: 大規模な構造変更、既存クエリの全面修正必要
- 対応: テーブル再作成、全データ移行、クエリ全面修正
- 難易度: 高
- 推定作業時間: 4～8時間

**推奨**: **選択肢A（現在の正規化形式保持）**
理由: 現在の実装が データベース設計のベストプラクティスに従っており、マッチングロジックも既に正規化形式に対応している。

---

## ⚠️ データカバー率の問題

**2025-12-02 調査結果**:

| テーブル | 期待値 | 実際 | カバー率 | 状態 |
|---------|--------|------|---------|------|
| talents | ~2,000 | 4,810 | 240% | ✅ 超過（OK） |
| talent_scores | ~16,000 | 6,118 | 38% | 🚨 不足 |
| talent_images | ~16,000 | 2,688 | 17% | 🚨 深刻 |

**原因**: VR/TPRデータのインポートが不完全

**修正アクション**:
- [ ] talent_scores: 残り 4,122 件の TPRデータインポート
- [ ] talent_images: 残り 53,760 件の VRイメージデータインポート

**推定作業時間**: 1～2時間（バッチ処理）

---

## ⚠️ API レスポンス型の不統一

**フロントエンド vs バックエンド間の型名が不統一**:

| フロントエンド型 | バックエンド型 | ステータス |
|----------------|--------------|---------|
| match_score | matching_score | ❌ 不統一 |
| image_adjustment_score | image_adjustment | ❌ 不統一 |
| - | account_id | ⚠️ 未確認 |
| - | kana | ⚠️ 未確認 |
| - | category | ⚠️ 未確認 |

**修正すべき型**:

```typescript
// frontend/src/types/index.ts
export interface TalentResult {
  talent_id: number;
  account_id: number;              // ← 追加確認
  name: string;
  kana?: string;                   // ← 追加確認
  category?: string;               // ← 追加確認
  matching_score: number;          // ← 変更: match_score から
  ranking: number;
  base_power_score?: number;
  image_adjustment?: number;       // ← 変更: image_adjustment_score から
  imageUrl?: string;
}
```

**修正難易度**: 低
**推定作業時間**: 20分

---

## 📋 優先度別修正リスト

### 🔴 P0（ブロッカー・クリティカル）- 修正必須

1. **Talent テーブル name → name_full リネーム**
   - ファイル: backend/app/models/__init__.py
   - ファイル: backend/app/api/endpoints/matching.py
   - 難易度: 低 | 時間: 30分

2. **STEP 2 加減点の修正**
   - ファイル: backend/app/api/endpoints/matching.py
   - 難易度: 低 | 時間: 15分

3. **API レスポンス型の統一**
   - ファイル: frontend/src/types/index.ts
   - ファイル: frontend/src/lib/api.ts
   - 難易度: 低 | 時間: 20分

### 🟡 P1（重要）- 修正推奨

4. **VR/TPRデータインポート完료**
   - ファイル: backend/scripts/import_*.py（インポートスクリプト）
   - 難易度: 中 | 時間: 1～2時間

5. **talent_images スキーマ確認**
   - ファイル: backend/app/models/__init__.py
   - ファイル: backend/app/api/endpoints/matching.py
   - 難易度: 低 | 時間: 10分（確認のみ）

### 🟢 P2（低優先度）- 修正検討

6. **talent_cm_history テーブル削除検討**
   - スコープ外であることを確認
   - 難易度: 低 | 時間: 10分

---

## 修正作業の推奨実行順序

### Day 1（最速修正：1時間）

```
1. Talent name → name_full リネーム（15分）
   └─ models/__init__.py
   └─ matching.py の SELECT 句修正
   
2. STEP 2 加減点修正（15分）
   └─ matching.py の CASE 式修正
   
3. API 型の統一（20分）
   └─ frontend/src/types/index.ts
   └─ frontend/src/lib/api.ts
   
4. ローカル環境テスト（10分）

合計: 1時間
```

### Day 2（データインポート：1～2時間）

```
5. VR/TPRデータインポート再実行（1～2時間）
   └─ talent_scores: 4,122件追加
   └─ talent_images: 53,760件追加
   
6. インポート検証テスト（30分）
```

---

## テスト項目（修正前後での検証）

### 修正前テスト（Baseline）
```bash
# 現在の状態を記録
curl -X POST http://localhost:8432/api/matching \
  -H "Content-Type: application/json" \
  -d '{
    "industry": "化粧品・ヘアケア・オーラルケア",
    "target_segments": ["女性20-34"],
    "budget": "1,000万円～3,000万円未満",
    "company_name": "テスト会社",
    "email": "test@example.com"
  }' | jq '.results[] | {ranking, matching_score, base_power_score, image_adjustment}'
```

### 修正後テスト
```bash
# 修正後の結果を比較
# 期待値：順位帯ごとのスコアが変動する（STEP 2加減点の修正による）
```

---

## リスク評価

### データ整合性リスク（低）
- ✅ name → name_full リネームは安全（新規インポートと既存データ対応で対応可）
- ✅ テーブルスキーマ変更なし（マイグレーションシンプル）

### パフォーマンスリスク（低）
- ✅ STEP 2 の加減点修正はロジックのみ（クエリ構造変更なし）
- ✅ talent_images の正規化形式保持で性能低下なし

### 運用リスク（中）
- ⚠️ VR/TPRデータインポートが大量（56,000件）
- ⚠️ インポート中のダウンタイム対応検討必須
- 対策: バッチ処理、段階的インポート、ロールバック計画

---

## 参考情報

- **ワーカー説明資料**: `/Users/lennon/projects/talent-casting-form/ワーカー説明資料_口頭用.md`
- **現在のDB状況**: `/Users/lennon/projects/talent-casting-form/docs/database_structure_analysis_report.md`
- **CLAUDE.md**: `/Users/lennon/projects/talent-casting-form/CLAUDE.md`

---

**作成者**: Claude Code
**検証ステータス**: 初版完成
**次のアクション**: P0 項目の修正開始

