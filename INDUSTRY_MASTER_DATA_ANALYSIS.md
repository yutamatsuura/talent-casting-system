# Industry Master Data and Purpose Options Analysis

## Executive Summary

This document maps the exact values stored in the form data to understand what the message template expects for industry and purpose fields. The mismatch between frontend form options and backend message template keys is a critical integration issue.

---

## 1. FRONTEND FORM OPTIONS (What Users Select)

### Industry Selection (FormStep1 - q2)
**Source:** API endpoint `GET /api/industries`  
**Data from:** PostgreSQL `industries` table

**Database Query Result:**
```sql
SELECT industry_id, industry_name
FROM industries
ORDER BY industry_id
```

**Typical Industries in the Database:**
Based on the backend code and message templates, the system supports:

1. `美容・化粧品` (Beauty & Cosmetics)
2. `食品・飲料` (Food & Beverage)
3. `自動車・モビリティー` (Automotive & Mobility)
4. `医療・ヘルスケア` (Medical & Healthcare)
5. `金融・保険` (Finance & Insurance)
6. `不動産` (Real Estate)
7. `ファッション・アパレル` (Fashion & Apparel)
8. `IT・テクノロジー` (IT & Technology)
9. `旅行・レジャー` (Travel & Leisure)
10. `教育` (Education)
11. `その他` (Other)

**Source File:** `/Users/lennon/projects/talent-casting-form/backend/app/api/endpoints/industries.py`

---

### Purpose Selection (FormStep3 - q3_2)
**Current Frontend Options (Hardcoded):**

Located in: `/Users/lennon/projects/talent-casting-form/frontend/src/components/diagnosis/FormSteps/FormStep3.tsx`

```typescript
const reasons = [
  '商品サービスの知名度アップ',       // Product/Service Awareness
  '商品サービスの売上拡大',           // Product/Service Sales Expansion
  '商品サービスの特長訴求のため',     // Product/Service Feature Appeal
  '企業知名度アップ',                 // Company Awareness
  '企業好感度アップ',                 // Company Brand Image
  '採用効果アップ',                   // Recruitment Effects
  'その他',                           // Other
];
```

---

## 2. MESSAGE TEMPLATE EXPECTED VALUES

**Source File:** `/Users/lennon/projects/talent-casting-form/frontend/src/lib/personalized-messages.ts`

### Message Template Structure
```typescript
const messageTemplates: Record<string, Record<string, string>> = {
  '業界名': {
    '起用目的': 'メッセージテキスト'
  }
}
```

### Expected Purpose Values in Templates

The message templates use **5 specific purpose keys**:

1. **`認知度向上`** (Awareness Improvement)
2. **`ブランドイメージ向上`** (Brand Image Improvement)
3. **`売上拡大`** (Sales Expansion)
4. **`新規顧客獲得`** (New Customer Acquisition)
5. **`SNS・口コミ拡散`** (SNS/Word-of-Mouth Spread)

### Example Template for Beauty & Cosmetics
```typescript
'美容・化粧品': {
  '認知度向上': 'では、美意識の高い消費者に響く話題性のあるタレントとの協力がおすすめです。...',
  'ブランドイメージ向上': 'では、洗練されたイメージを持つタレントとのコラボレーションが効果的です。...',
  '売上拡大': 'では、購買意欲を高める影響力の強いタレントとの戦略的タイアップがおすすめです。...',
  '新規顧客獲得': 'では、新しい顧客層へのアプローチに長けたタレントとの新鮮な組み合わせが効果的です。...',
  'SNS・口コミ拡散': 'では、SNSでの拡散力に定評のあるタレントとのデジタル戦略が最適です。...'
}
```

---

## 3. DATA FLOW AND MISMATCH IDENTIFICATION

### Current Data Flow

```
User Frontend Input (FormStep3.q3_2)
    ↓
Values: '商品サービスの知名度アップ' / '商品サービスの売上拡大' / etc.
    ↓
API Call (callMatchingApi in api.ts)
    ↓
MatchingApiRequest sends:
  {
    industry: formData.q2,           // e.g., "美容・化粧品"
    purpose: formData.q3_2,          // e.g., "商品サービスの知名度アップ"
    ...
  }
    ↓
Message Generation in ResultsPage.tsx
    ↓
generateDetailedPersonalizedMessage({
  industry: '美容・化粧品',
  purpose: '商品サービスの知名度アップ'  // THIS VALUE IS NOT IN MESSAGE TEMPLATES!
})
```

### THE CRITICAL MISMATCH

**Frontend sends:** `'商品サービスの知名度アップ'`  
**Message template expects:** `'認知度向上'`

**Result:** Message generation falls back to default message because:
```typescript
const detailMessage = industryMessages?.[purpose] || 
                      industryMessages?.['認知度向上'] || 
                      'では、貴社に最適なタレントとの戦略的な協力をご提案いたします。';
```

---

## 4. DETAILED PURPOSE VALUE MAPPING

| Frontend Display Value | Current Sent Value | Expected Template Key | Status |
|------------------------|-------------------|----------------------|--------|
| 商品サービスの知名度アップ | 商品サービスの知名度アップ | 認知度向上 | ❌ MISMATCH |
| 商品サービスの売上拡大 | 商品サービスの売上拡大 | 売上拡大 | ❌ MISMATCH |
| 商品サービスの特長訴求のため | 商品サービスの特長訴求のため | (No match) | ❌ NOT FOUND |
| 企業知名度アップ | 企業知名度アップ | (No match) | ❌ NOT FOUND |
| 企業好感度アップ | 企業好感度アップ | (No match) | ❌ NOT FOUND |
| 採用効果アップ | 採用効果アップ | (No match) | ❌ NOT FOUND |
| その他 | その他 | (No match) | ❌ NOT FOUND |

---

## 5. BACKEND SCHEMA VALIDATION

**Source:** `/Users/lennon/projects/talent-casting-form/backend/app/schemas/matching.py`

### MatchingFormData Schema (Backend Expects)
```python
class MatchingFormData(BaseModel):
    industry: str = Field(..., description="業種名")
    target_segments: str = Field(..., min_length=1, description="ターゲット層（単一選択）")
    purpose: str = Field(..., min_length=1, max_length=255, description="起用目的")
    budget: str = Field(..., description="予算区分")
    company_name: str = Field(..., min_length=1, max_length=255, description="企業名")
    email: str = Field(...)
    contact_name: Optional[str] = Field(None, max_length=255, description="担当者名")
    phone: Optional[str] = Field(None, max_length=50, description="電話番号")
```

**Note:** Backend has **NO VALIDATION** on purpose field values! This is dangerous.

---

## 6. DATABASE TABLE STRUCTURE

### industries Table
```sql
CREATE TABLE industries (
    industry_id INTEGER PRIMARY KEY,
    industry_name VARCHAR(255) NOT NULL,
    required_image_id INTEGER,
    created_at DATETIME,
    updated_at DATETIME
);
```

### target_segments Table
```sql
CREATE TABLE target_segments (
    target_segment_id INTEGER PRIMARY KEY,
    segment_name VARCHAR(50) NOT NULL,
    gender VARCHAR(10),
    age_min INTEGER,
    age_max INTEGER,
    created_at DATETIME,
    updated_at DATETIME
);
```

**Valid Target Segments:**
```
1. 男性12-19歳
2. 女性12-19歳
3. 男性20-34歳
4. 女性20-34歳
5. 男性35-49歳
6. 女性35-49歳
7. 男性50-69歳
8. 女性50-69歳
```

---

## 7. FORM SUBMISSION STORAGE

**Source:** `/Users/lennon/projects/talent-casting-form/backend/app/models/__init__.py`

```python
class FormSubmission(Base):
    __tablename__ = "form_submissions"
    
    id = Column(Integer, primary_key=True)
    industry = Column(String(100), nullable=False)
    target_segment = Column(String(50), nullable=False)
    purpose = Column(String(255), nullable=True)  # 起用目的
    budget_range = Column(String(100), nullable=False)
    company_name = Column(String(255), nullable=True)
    contact_name = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
```

**What Gets Stored in `purpose` column:**
- Current: `'商品サービスの知名度アップ'` (raw frontend value)
- Should be: `'認知度向上'` (normalized template key)

---

## 8. IMPLEMENTATION DETAILS

### API Request/Response Flow

**File:** `/Users/lennon/projects/talent-casting-form/frontend/src/lib/api.ts`

```typescript
function transformFormDataToApiRequest(formData: FormData): MatchingApiRequest {
  const apiRequest: MatchingApiRequest = {
    industry: formData.q2,        // Direct mapping
    target_segments: formData.q3, // Direct mapping
    purpose: formData.q3_2,       // Direct mapping - NO TRANSFORMATION!
    budget: formData.q3_3,        // Direct mapping
    company_name: formData.q4,
    email: formData.q6,
    contact_name: formData.q5,
    phone: formData.q7,
  };
  return apiRequest;
}
```

### Message Generation Code

**File:** `/Users/lennon/projects/talent-casting-form/frontend/src/components/diagnosis/Results/ResultsPage.tsx`

```typescript
const generatePersonalizedMessage = (): string => {
  const companyName = formData.q4 || '貴社';
  const industry = formData.q2;
  const purpose = formData.q3_2;  // Raw frontend value!

  if (industry && purpose) {
    return generateDetailedPersonalizedMessage({
      companyName,
      industry,
      purpose  // '商品サービスの知名度アップ' instead of '認知度向上'
    });
  }
  // Falls back to simple message when purpose not found
};
```

---

## 9. ROOT CAUSE ANALYSIS

### Why the Mismatch Exists

1. **Separate Development Streams**
   - Frontend form options were defined independently in FormStep3
   - Backend message templates were created separately
   - No synchronization mechanism

2. **No Data Normalization Layer**
   - Frontend values sent as-is to message template function
   - No transformation: `q3_2` → normalized template key
   - Message template uses `.get()` without strict key matching

3. **Fallback Design Masks the Issue**
   - Message templates have fallback logic:
     ```typescript
     industryMessages?.[purpose] || industryMessages?.['認知度向上'] || 'default message'
     ```
   - When purpose key not found, uses '認知度向上' (default)
   - This hides the data mismatch from users

---

## 10. FIXED VALUES REFERENCE

### Correct Industry-Purpose Combinations

**Industries (from messageTemplates keys):**
```
1. 美容・化粧品
2. 食品・飲料
3. 自動車・モビリティー
4. 医療・ヘルスケア
5. 金融・保険
6. 不動産
7. ファッション・アパレル
8. IT・テクノロジー
9. 旅行・レジャー
10. 教育
11. その他
```

**Purposes (from messageTemplates values):**
```
1. 認知度向上
2. ブランドイメージ向上
3. 売上拡大
4. 新規顧客獲得
5. SNS・口コミ拡散
```

---

## 11. RECOMMENDED FIXES

### Option A: Update Frontend Form Options (Recommended)
**Impact:** Low - only frontend change  
**Effort:** 1 hour

Change FormStep3.tsx reasons array to match template keys:
```typescript
const reasons = [
  '認知度向上',           // Awareness
  'ブランドイメージ向上', // Brand Image
  '売上拡大',            // Sales
  '新規顧客獲得',         // Customer Acquisition
  'SNS・口コミ拡散',      // Viral/Spread
  'その他',              // Other
];
```

### Option B: Add Purpose Mapping/Normalization
**Impact:** Medium - requires backend changes  
**Effort:** 2-3 hours

Create mapping dictionary:
```python
PURPOSE_MAPPING = {
    '商品サービスの知名度アップ': '認知度向上',
    '商品サービスの売上拡大': '売上拡大',
    '企業知名度アップ': '認知度向上',
    '企業好感度アップ': 'ブランドイメージ向上',
    # ... etc
}
```

### Option C: Update Message Templates
**Impact:** Medium - affects all templates  
**Effort:** 4-6 hours

Expand templates to accept both frontend and normalized values.

---

## 12. DATABASE VERIFICATION QUERIES

### Check Current Industries in Database
```sql
SELECT * FROM industries ORDER BY industry_id;
```

### Check Current Form Submissions
```sql
SELECT DISTINCT purpose FROM form_submissions 
ORDER BY purpose;
```

### Verify Target Segments Exist
```sql
SELECT * FROM target_segments 
WHERE segment_name IN (
  '男性12-19歳', '女性12-19歳',
  '男性20-34歳', '女性20-34歳',
  '男性35-49歳', '女性35-49歳',
  '男性50-69歳', '女性50-69歳'
);
```

---

## 13. CRITICAL FINDINGS

### Confirmed Issues
1. ✗ Frontend form options for `q3_2` (purpose) are hardcoded and do NOT match message template keys
2. ✗ No data transformation layer between frontend input and message generation
3. ✗ Backend schema accepts any string for `purpose` without validation
4. ✗ Form submissions store raw frontend values, not normalized template keys
5. ✗ Fallback message logic masks the data quality issue

### Data Integrity Concerns
1. Database stores inconsistent purpose values
2. Historical form submissions have non-standardized purpose values
3. No way to track which purposes are actually being used by users
4. Message generation may not work as designed for all purpose values

### Risk Assessment
- **Severity:** MEDIUM
- **User Impact:** Users see generic fallback messages instead of personalized ones
- **Data Quality:** Form submissions table has inconsistent purpose field values
- **Maintenance Risk:** Code is fragile; any new purposes require template updates

---

## 14. FILES INVOLVED

### Frontend Files
- `/Users/lennon/projects/talent-casting-form/frontend/src/components/diagnosis/FormSteps/FormStep3.tsx` - Purpose options
- `/Users/lennon/projects/talent-casting-form/frontend/src/lib/personalized-messages.ts` - Message templates
- `/Users/lennon/projects/talent-casting-form/frontend/src/lib/api.ts` - API request transformation
- `/Users/lennon/projects/talent-casting-form/frontend/src/components/diagnosis/Results/ResultsPage.tsx` - Message generation
- `/Users/lennon/projects/talent-casting-form/frontend/src/types/index.ts` - Type definitions

### Backend Files
- `/Users/lennon/projects/talent-casting-form/backend/app/schemas/matching.py` - Pydantic schema (no validation)
- `/Users/lennon/projects/talent-casting-form/backend/app/models/__init__.py` - FormSubmission model
- `/Users/lennon/projects/talent-casting-form/backend/app/api/endpoints/industries.py` - Industries API
- `/Users/lennon/projects/talent-casting-form/backend/app/api/endpoints/target_segments.py` - Target segments API

---

## Summary

The core issue is a **data mapping mismatch** between what the frontend form collects and what the backend message template expects. The frontend collects 7 different purpose options, but the message templates only recognize 5 keys. No normalization layer exists to bridge this gap, causing message generation to fall back to defaults when the selected purpose is not found in the template dictionary.

This is a classic integration bug that manifests as "users don't see personalized messages" but the underlying issue is poor data pipeline design.
