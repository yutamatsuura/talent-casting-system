# Master Data Files Reference Guide

## Quick Navigation Map

This guide shows exactly where each master data definition and business logic is located.

---

## Industry Master Data

### Database Definition
- **Table:** `industries`
- **Location:** PostgreSQL via Neon
- **Query:** `SELECT * FROM industries ORDER BY industry_id;`

### API Endpoint
- **File:** `/Users/lennon/projects/talent-casting-form/backend/app/api/endpoints/industries.py`
- **Endpoint:** `GET /api/industries`
- **Returns:** `IndustryListResponse` with total count and industry array
- **Response Schema:** `/Users/lennon/projects/talent-casting-form/backend/app/schemas/industries.py`

### Message Templates (Frontend)
- **File:** `/Users/lennon/projects/talent-casting-form/frontend/src/lib/personalized-messages.ts`
- **Lines:** 14-92 (messageTemplates object)
- **Industries Referenced:** 11 keys in messageTemplates
- **Export Function:** `generateDetailedPersonalizedMessage()`

### SQLAlchemy Model (Backend)
- **File:** `/Users/lennon/projects/talent-casting-form/backend/app/models/__init__.py`
- **Lines:** 11-39 (Industry class)
- **Table Name:** `industries`
- **Fields:** `industry_id`, `industry_name`, `required_image_id`, `created_at`, `updated_at`

### Admin Page (View/Edit)
- **File:** `/Users/lennon/projects/talent-casting-form/frontend/app/admin/page.tsx`
- **Contains:** Industry selection in admin interface
- **Edit Capability:** None currently (read-only)

---

## Purpose/Reason Master Data

### Frontend Form Definition (PROBLEMATIC)
- **File:** `/Users/lennon/projects/talent-casting-form/frontend/src/components/diagnosis/FormSteps/FormStep3.tsx`
- **Lines:** 23-31 (reasons array)
- **Count:** 7 hardcoded options
- **Field Name:** `formData.q3_2`
- **Issues:** 
  - MISMATCH with template keys (7 options vs 5 template keys)
  - Not synchronized with message templates
  - No validation

```typescript
const reasons = [
  '商品サービスの知名度アップ',
  '商品サービスの売上拡大',
  '商品サービスの特長訴求のため',
  '企業知名度アップ',
  '企業好感度アップ',
  '採用効果アップ',
  'その他',
];
```

### Message Template Definition (AUTHORITATIVE)
- **File:** `/Users/lennon/projects/talent-casting-form/frontend/src/lib/personalized-messages.ts`
- **Lines:** 14-92 (messageTemplates object)
- **Template Keys:** 5 purpose values
- **Industries:** 11 industry keys
- **Valid Purpose Keys:**
  1. `認知度向上`
  2. `ブランドイメージ向上`
  3. `売上拡大`
  4. `新規顧客獲得`
  5. `SNS・口コミ拡散`

### Backend Schema (NO VALIDATION)
- **File:** `/Users/lennon/projects/talent-casting-form/backend/app/schemas/matching.py`
- **Lines:** 7-57 (MatchingFormData class)
- **Field:** `purpose: str = Field(...)`
- **Validation:** NONE! Accepts any string up to 255 characters
- **Risk:** Bad data can be stored in database without warning

### Database Storage
- **Table:** `form_submissions`
- **Column:** `purpose VARCHAR(255)`
- **Stores:** Raw frontend values (not normalized)
- **File:** `/Users/lennon/projects/talent-casting-form/backend/app/models/__init__.py`
- **Lines:** 285-317 (FormSubmission class)

---

## Target Segment Master Data

### Database Definition
- **Table:** `target_segments`
- **Location:** PostgreSQL via Neon
- **Fields:** `target_segment_id`, `segment_name`, `gender`, `age_min`, `age_max`

### Valid Values (8 total)
```
1. 男性12-19歳 (target_segment_id: 9)
2. 女性12-19歳 (target_segment_id: 10)
3. 男性20-34歳 (target_segment_id: 11)
4. 女性20-34歳 (target_segment_id: 12)
5. 男性35-49歳 (target_segment_id: 13)
6. 女性35-49歳 (target_segment_id: 14)
7. 男性50-69歳 (target_segment_id: 15)
8. 女性50-69歳 (target_segment_id: 16)
```

### API Endpoint
- **File:** `/Users/lennon/projects/talent-casting-form/backend/app/api/endpoints/target_segments.py`
- **Endpoint:** `GET /api/target-segments`
- **Returns:** `TargetSegmentsListResponse`
- **Response Schema:** `/Users/lennon/projects/talent-casting-form/backend/app/schemas/target_segments.py`

### SQLAlchemy Model
- **File:** `/Users/lennon/projects/talent-casting-form/backend/app/models/__init__.py`
- **Lines:** 79-104 (TargetSegment class)

### Backend Validation
- **File:** `/Users/lennon/projects/talent-casting-form/backend/app/schemas/matching.py`
- **Lines:** 22-44 (validate_target_segments function)
- **Hardcoded List:** 8 allowed segment names
- **Status:** CORRECT - validates against known list

---

## Budget Range Master Data

### Database Definition
- **Table:** `budget_ranges`
- **Fields:** `id`, `name`, `min_amount`, `max_amount`, `display_order`

### SQLAlchemy Model
- **File:** `/Users/lennon/projects/talent-casting-form/backend/app/models/__init__.py`
- **Lines:** 106-118 (BudgetRange class)

### Backend Normalization
- **File:** `/Users/lennon/projects/talent-casting-form/backend/app/api/endpoints/matching.py`
- **Lines:** 25-33 (normalize_budget_range_string function)
- **Purpose:** Handle wave dash vs tilde vs fullwidth space variants

---

## Data Flow Files

### Frontend Input to API Request
- **File:** `/Users/lennon/projects/talent-casting-form/frontend/src/lib/api.ts`
- **Lines:** 64-86 (transformFormDataToApiRequest function)
- **Problem:** Direct mapping with NO transformation
- **Issue:** purpose field sent as-is without normalization

### API Request to Message Generation
- **File:** `/Users/lennon/projects/talent-casting-form/frontend/src/components/diagnosis/Results/ResultsPage.tsx`
- **Lines:** 66-102 (generatePersonalizedMessage function)
- **Issue:** Uses raw q3_2 value directly, causes template key mismatch

### Message Template Lookup
- **File:** `/Users/lennon/projects/talent-casting-form/frontend/src/lib/personalized-messages.ts`
- **Lines:** 97-114 (generateDetailedPersonalizedMessage function)
- **Lines:** 104-105 (fallback logic)
- **Danger:** Fallback masks data quality issues

---

## Type Definitions

### Form Data Type
- **File:** `/Users/lennon/projects/talent-casting-form/frontend/src/types/index.ts`
- **Lines:** 7-19 (FormData interface)
- **Field:** `q3_2: string;`
- **Comment:** "タレント起用理由（必須）"
- **No Validation:** Type is just string, no enum or constants

### Matching API Request Type
- **File:** `/Users/lennon/projects/talent-casting-form/frontend/src/lib/api.ts`
- **Lines:** 14-25 (MatchingApiRequest interface)
- **Field:** `purpose: string;`
- **No Validation:** Just string type

### Matching API Response Type
- **File:** `/Users/lennon/projects/talent-casting-form/frontend/src/lib/api.ts`
- **Lines:** 30-49 (MatchingApiResponse interface)
- **Has:** TalentResult array, session_id, timestamp

---

## Component Hierarchy

```
FormStep1 (Industry Selection)
  └─ Fetches from GET /api/industries
  └─ Stores in formData.q2

FormStep2 (Target Segment Selection)
  └─ Fetches from GET /api/target-segments
  └─ Stores in formData.q3

FormStep3 (Purpose Selection) ⚠️ PROBLEMATIC
  └─ Hardcoded reasons array
  └─ Stores in formData.q3_2
  └─ NO connection to message templates!

FormStep4 (Budget Selection)
  └─ Fetches from database
  └─ Stores in formData.q3_3

FormStep5 (Company Info)
  └─ Stores in formData.q4, q5, q6, q7

FormStep6 (Privacy Agreement)
  └─ Stores in formData.privacyAgreed

ResultsPage
  └─ Calls generatePersonalizedMessage()
  └─ Uses formData.q3_2 directly
  └─ Hits personalized-messages.ts template lookup
  └─ Falls back when key not found
```

---

## Key Integration Points

### 1. Industry Selection Pipeline
```
Database (industries)
    ↓
API GET /industries
    ↓
Frontend fetches in FormStep1
    ↓
User selects industry
    ↓
Stored in formData.q2
    ↓
Sent to API in MatchingApiRequest.industry
    ↓
Used in personalized-messages.ts template lookup ✓ WORKS
```

### 2. Target Segment Selection Pipeline
```
Database (target_segments)
    ↓
API GET /target-segments
    ↓
Frontend fetches in FormStep2
    ↓
User selects segment
    ↓
Stored in formData.q3
    ↓
Validated on backend ✓ WORKS
    ↓
Sent to matching logic
    ↓
Used in talent filtering ✓ WORKS
```

### 3. Purpose Selection Pipeline (BROKEN)
```
FormStep3.tsx hardcoded array (7 options) ❌
    ↓
User selects purpose
    ↓
Stored in formData.q3_2 ❌
    ↓
Sent to API as-is (no transformation) ❌
    ↓
Stored in form_submissions.purpose ❌
    ↓
Used in ResultsPage message generation ❌
    ↓
personalized-messages.ts lookup fails ❌
    ↓
Falls back to default message ❌
```

---

## Database Queries for Verification

### Check Industries
```sql
SELECT industry_id, industry_name 
FROM industries 
ORDER BY industry_id;
```

### Check Target Segments
```sql
SELECT target_segment_id, segment_name, gender, age_min, age_max
FROM target_segments
ORDER BY target_segment_id;
```

### Check Budget Ranges
```sql
SELECT id, name, min_amount, max_amount
FROM budget_ranges
ORDER BY id;
```

### Check Form Submissions (Purpose Values)
```sql
SELECT DISTINCT purpose
FROM form_submissions
ORDER BY purpose;
```

### Check Data Quality
```sql
SELECT 
  COUNT(*) as total_submissions,
  COUNT(DISTINCT purpose) as distinct_purposes,
  COUNT(CASE WHEN purpose IN ('認知度向上', 'ブランドイメージ向上', 
                              '売上拡大', '新規顧客獲得', 'SNS・口コミ拡散') 
              THEN 1 END) as valid_purposes,
  COUNT(*) - COUNT(CASE WHEN purpose IN ('認知度向上', 'ブランドイメージ向上', 
                                        '売上拡大', '新規顧客獲得', 'SNS・口コミ拡散') 
                        THEN 1 END) as invalid_purposes
FROM form_submissions;
```

---

## Summary

### Files to Review
1. **CRITICAL:** `/Users/lennon/projects/talent-casting-form/frontend/src/components/diagnosis/FormSteps/FormStep3.tsx`
2. **CRITICAL:** `/Users/lennon/projects/talent-casting-form/frontend/src/lib/personalized-messages.ts`
3. **IMPORTANT:** `/Users/lennon/projects/talent-casting-form/frontend/src/lib/api.ts`
4. **IMPORTANT:** `/Users/lennon/projects/talent-casting-form/backend/app/schemas/matching.py`

### Master Data Summary
| Master Data | Source | Status | Issues |
|---|---|---|---|
| Industries | Database API | CORRECT | - |
| Target Segments | Database API | CORRECT | - |
| Budget Ranges | Database | CORRECT | Tilde normalization needed |
| Purpose/Reason | Hardcoded Form | BROKEN | Mismatch with templates |

### Recommended Next Steps
1. Align FormStep3.tsx reasons with personalized-messages.ts keys
2. Add backend validation for purpose field
3. Add data normalization layer in API request transformation
4. Update database schema comments to document valid values
