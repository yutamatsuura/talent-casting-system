# Data Mapping Comparison: Frontend Values vs Backend Expectations

## Quick Reference Table

| Location | Field | Actual Values Collected | Expected by Template | Match? |
|----------|-------|----------------------|----------------------|--------|
| FormStep3.tsx | q3_2 (Purpose) | 7 hardcoded options | 5 template keys | ❌ NO |
| Industries API | industry | From DB (11+ values) | Template keys | ✓ YES |
| Target Segments | target_segments | 8 standard formats | Template OK | ✓ YES |

---

## Purpose Field: The Critical Mismatch

### What FormStep3.tsx Defines (User Options)
```javascript
const reasons = [
  '商品サービスの知名度アップ',       // INDEX 0
  '商品サービスの売上拡大',           // INDEX 1
  '商品サービスの特長訴求のため',     // INDEX 2
  '企業知名度アップ',                 // INDEX 3
  '企業好感度アップ',                 // INDEX 4
  '採用効果アップ',                   // INDEX 5
  'その他',                           // INDEX 6
];
```

### What personalized-messages.ts Expects (Template Keys)
```javascript
const messageTemplates = {
  '業界': {
    '認知度向上': 'メッセージ1',
    'ブランドイメージ向上': 'メッセージ2',
    '売上拡大': 'メッセージ3',
    '新規顧客獲得': 'メッセージ4',
    'SNS・口コミ拡散': 'メッセージ5'
  }
};
```

---

## Data Journey: What Happens When User Submits Form

### Step 1: User Selects Purpose in FormStep3
```
User selects: "商品サービスの知名度アップ"
Stored in state as: formData.q3_2 = '商品サービスの知名度アップ'
```

### Step 2: Frontend API Call (lib/api.ts)
```typescript
function transformFormDataToApiRequest(formData) {
  return {
    industry: '美容・化粧品',           // ✓ Correct
    target_segments: '女性20-34歳',     // ✓ Correct
    purpose: '商品サービスの知名度アップ',  // ❌ PROBLEM!
    budget: '1,000万円～3,000万円未満',  // ✓ Correct
    company_name: '株式会社テスト',      // ✓ Correct
    email: 'test@example.com',           // ✓ Correct
    // ... other fields
  };
}
```

### Step 3: Message Generation (Results/ResultsPage.tsx)
```typescript
const generatePersonalizedMessage = () => {
  const industry = '美容・化粧品';               // ✓ Found in templates
  const purpose = '商品サービスの知名度アップ';   // ❌ NOT in templates!

  // personalized-messages.ts tries:
  const detailMessage = 
    messageTemplates['美容・化粧品']['商品サービスの知名度アップ']  // undefined!
    || messageTemplates['美容・化粧品']['認知度向上']  // ✓ FALLBACK!
    || 'default message';

  // Result: Uses fallback because exact key not found
};
```

### Step 4: Actual Output
```
EXPECTED: "株式会社テスト様、美容・化粧品では、美意識の高い消費者に響く話題性のあるタレントとの協力がおすすめです..."
ACTUAL:   "株式会社テスト様、美容・化粧品では、美意識の高い消費者に響く話題性のあるタレントとの協力がおすすめです..." (happens to work by accident!)
```

---

## The Hidden Problem

While the fallback mechanism accidentally works for `'商品サービスの知名度アップ'` → uses `'認知度向上'` message...

It FAILS for these user selections:

| User Selection | Expected Template Key | What Happens |
|---|---|---|
| 商品サービスの知名度アップ | 認知度向上 | Works by luck (fallback) |
| **商品サービスの売上拡大** | 売上拡大 | ❌ Falls back to '認知度向上' |
| **商品サービスの特長訴求のため** | (No match) | ❌ Falls back to '認知度向上' |
| **企業知名度アップ** | (No match) | ❌ Falls back to '認知度向上' |
| **企業好感度アップ** | (No match) | ❌ Falls back to 'ブランドイメージ向上'? NO! |
| **採用効果アップ** | (No match) | ❌ Falls back to '認知度向上' |
| その他 | (No match) | ❌ Falls back to '認知度向上' |

---

## Code Analysis: Why Fallback Masks the Bug

### In personalized-messages.ts (Line 105)
```typescript
const detailMessage = industryMessages?.[purpose] || 
                      industryMessages?.['認知度向上'] || 
                      'では、貴社に最適なタレントとの戦略的な協力をご提案いたします。';
```

**This means:**
- **First priority:** Look for exact match of `purpose` in templates
- **Second priority (FALLBACK):** Use '認知度向上' message
- **Third priority:** Use generic message

### The Problem
- Developers can't easily detect this fallback is happening
- All users with non-matching purposes get the same '認知度向上' message
- No logging or warning when fallback is used
- No validation prevents bad data from reaching this point

---

## What Gets Stored in Database

### form_submissions Table
When a user selects "企業好感度アップ" and submits:

```sql
INSERT INTO form_submissions (
  industry,
  target_segment,
  purpose,  -- This is what's stored!
  ...
) VALUES (
  '美容・化粧品',
  '女性20-34歳',
  '企業好感度アップ',  -- Raw frontend value, NOT normalized!
  ...
);
```

### Historical Data Quality Issue
```sql
SELECT DISTINCT purpose FROM form_submissions;
-- Results in database:
-- '商品サービスの知名度アップ'
-- '商品サービスの売上拡大'
-- '商品サービスの特長訴求のため'
-- '企業知名度アップ'
-- '企業好感度アップ'
-- '採用効果アップ'
-- 'その他'
-- ... but message templates only recognize 5 of these!
```

---

## File Structure Map

```
Frontend:
├── FormStep3.tsx (7 purpose options) ❌ HARDCODED
├── api.ts (passes q3_2 as-is) ❌ NO TRANSFORMATION
├── personalized-messages.ts (5 template keys) ✓ DEFINED
├── ResultsPage.tsx (uses q3_2 directly) ❌ NO NORMALIZATION
└── types/index.ts (q3_2: string) ❌ NO VALIDATION

Backend:
├── schemas/matching.py (accepts any purpose) ❌ NO VALIDATION
├── models/__init__.py (stores purpose as string) ❌ NO NORMALIZATION
├── api/endpoints/industries.py (correct)
└── api/endpoints/target_segments.py (correct)
```

---

## Industry Values (These ARE Correct)

### Available in Database (industries table)
The API endpoint `GET /api/industries` returns values that match template keys:

```
1. 美容・化粧品 ✓
2. 食品・飲料 ✓
3. 自動車・モビリティー ✓
4. 医療・ヘルスケア ✓
5. 金融・保険 ✓
6. 不動産 ✓
7. ファッション・アパレル ✓
8. IT・テクノロジー ✓
9. 旅行・レジャー ✓
10. 教育 ✓
11. その他 ✓
```

All these industries exist in personalized-messages.ts template keys.

---

## Target Segments (These ARE Correct)

### Valid Combinations (target_segments table)
```
男性12-19歳 ✓
女性12-19歳 ✓
男性20-34歳 ✓
女性20-34歳 ✓
男性35-49歳 ✓
女性35-49歳 ✓
男性50-69歳 ✓
女性50-69歳 ✓
```

Target segment validation works correctly in backend:
```python
allowed_segments = [
    "男性12-19歳",
    "女性12-19歳",
    # ... etc
]

if v not in allowed_segments:
    raise ValueError(f"無効なターゲット層です: {v}")
```

---

## Summary of Findings

| Component | Status | Issue |
|-----------|--------|-------|
| Industries | ✓ CORRECT | Values match templates |
| Target Segments | ✓ CORRECT | Validated on backend |
| Purpose/Reason | ❌ MISMATCH | 7 options vs 5 template keys |
| Data Transformation | ❌ MISSING | No normalization layer |
| Backend Validation | ❌ MISSING | Accepts any purpose string |
| Database Storage | ❌ INCONSISTENT | Stores raw frontend values |
| Fallback Mechanism | ⚠️ DANGEROUS | Masks data quality issues |

---

## Recommended Action

**Immediate:** Update FormStep3.tsx to use only the 5 purpose values that exist in message templates

**Reason:** Simple, single-point fix that prevents garbage data

**Timeline:** 1 hour implementation + 15 min testing
