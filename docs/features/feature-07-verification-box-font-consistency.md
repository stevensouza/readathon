# Feature 7: Verification Box Font Consistency

**[← Back to Index](../00-INDEX.md)**

---

### Feature 7: Verification Box Font Consistency
**Current Issue:** Different boxes use different font sizes (inconsistent)

**Requirements:**
- Standardize main numbers: **2rem** (white, bold) - matches Top Readers/Classes
- Labels/titles: **0.9-1rem** (light gray, rgba(255,255,255,0.75))
- Secondary numbers: **1.5rem** (white, bold)
- Timestamps: **0.7rem** (lighter gray, rgba(255,255,255,0.65))
- Apply consistent spacing across all boxes
- Box 2 (Minutes breakdown): Use 1.5rem for breakdown numbers

**Implementation:**
- Update CSS in `base.html` styles
- Ensure `.verification-value` is 2rem
- Ensure `.verification-amount` is 2rem (not 2.25rem)
- Test across all 5 boxes

**Note:** Will iterate with UI prototype first before implementing.

---



---

**[← Back to Index](../00-INDEX.md)**
