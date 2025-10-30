# Banner Standardization Summary

**Quick Reference for Future Development Sessions**

**Last Updated:** 2025-10-30

**Status:** ✅ Complete (Phases 1-7)

---

## 📋 Complete Metric List

All 3 pages (School, Teams, Grade Level) use these 6 metrics in this exact order:

| # | Icon | Metric | Format | Filter | Notes |
|---|------|--------|--------|--------|-------|
| 1 | 📅 | Campaign Day | "X of Y" | ❌ No | Always shows full campaign status |
| 2 | 💰 | Fundraising | $X,XXX | ❌ No | Cumulative from Reader_Cumulative |
| 3 | 📚/📖 | Minutes Read | X,XXX hrs | ✅ Yes ◐ | Includes color bonus |
| 4 | 🎁 | Sponsors | X,XXX count | ❌ No | NOT 🤝 icon |
| 5 | 👥 | Avg. Participation (With Color) | X.X% | ✅ Yes ◐ | Can exceed 100% |
| 6 | 🎯 | Goal Met (≥1 Day) | X.X% | ✅ Yes ◐ | Students who met goal |

### Filter Behavior Summary

**Metrics that IGNORE date filter:**
- Campaign Day (always shows full contest)
- Fundraising (cumulative total)
- Sponsors (cumulative total)

**Metrics that RESPECT date filter (show ◐):**
- Minutes Read
- Avg. Participation (With Color)
- Goal Met (≥1 Day)

---

## 📊 Two Participation Formulas

### Simple Participation % (Cumulative)
```
(students_who_participated / total_students) * 100
```

**Where used:**
- Grade Level table: "PARTICIPATION %" column
- Teams comparison: "Participation %" row

**Characteristics:**
- Binary (participated or didn't)
- NO color bonus
- Shows breadth of participation

### Avg. Participation (With Color)
```
base = (total_days_read / (students * days)) * 100
color = (color_war_points / (students * days)) * 100
result = base + color
```

**Where used:**
- All 3 banners
- Teams comparison: "Avg. Participation (With Color)" row
- Grade Level table: "AVG. PARTICIPATION (WITH COLOR)" column

**Characteristics:**
- Continuous (daily average)
- INCLUDES color bonus
- Shows depth/consistency of participation
- **CAN EXCEED 100%** (all students + color points)

**Example:**
- 100% Simple (all students read once)
- 50% Avg. (only read half the days)

---

## 🎨 Banner vs Detail Tables

### Banner Usage

**All 3 pages use:** "Avg. Participation (With Color)"
- Encourages daily consistency
- Rewards team spirit (color bonus)
- Unified metric across application

### Detail Table Usage

**Teams Page:**
- Row 1: "Participation %" (simple)
- Row 2: "Avg. Participation (With Color)" (with bonus)

**Grade Level Page:**
- Column 1: "PARTICIPATION %" (simple)
- Column 2: "AVG. PARTICIPATION (WITH COLOR)" (with bonus)

**Why both?**
- Simple % = engagement level (how many participated)
- Avg. with Color = consistency level (how often + team spirit)

---

## 🧪 Testing Coverage

### Test Files

| File | Tests | Coverage |
|------|-------|----------|
| `test_banner_standardization_phases1-3.py` | 21 | Phases 1-3 (Campaign Day, Sponsors, Goal Met) |
| `test_banner_phase4_avg_participation.py` | 15 | Phase 4 (Banner metric switch) |
| `test_banner_phase5_detail_tables.py` | 17 | Phase 5 (Detail table enhancements) |
| `test_banner_comprehensive.py` | 29 | Phase 7 (All standardization work) |

**Total Banner Tests:** 82 tests

**Pre-Commit Hook:** Runs all 165 tests (including banner tests) before every commit

### Running Tests

```bash
# Run all banner tests
python3 -m pytest test_banner*.py -v

# Run comprehensive suite only
python3 -m pytest test_banner_comprehensive.py -v

# Run all tests (what pre-commit does)
python3 -m pytest test_school_page.py test_teams_page.py \
  test_grade_level_page.py test_data_accuracy.py \
  test_banner_standardization_phases1-3.py \
  test_banner_phase4_avg_participation.py \
  test_banner_phase5_detail_tables.py \
  test_banner_comprehensive.py \
  test_date_filters.py -v
```

---

## ⚠️ Common Pitfalls & Reminders

### 1. Don't Mix Up Participation Metrics
```python
# WRONG - Using simple % in banner
banner_value = (participated_count / total_students) * 100

# CORRECT - Using avg with color in banner
banner_value = (days_read / (students * days)) * 100 + \
               (color_points / (students * days)) * 100
```

### 2. Remember >100% is Valid
```python
# This is NOT a bug!
if avg_participation_with_color > 100:
    # This is EXPECTED when all students read all days + color points
    pass
```

### 3. Filter Indicator Logic
```python
# Fundraising and Sponsors NEVER show ◐
if metric_name in ['Fundraising', 'Sponsors', 'Campaign Day']:
    show_filter_indicator = False
else:
    # Minutes, Participation, Goal Met show ◐ when filtered
    show_filter_indicator = (date_filter != 'all')
```

### 4. Sponsors Icon Must Be 🎁
```python
# WRONG
sponsors_icon = '🤝'

# CORRECT
sponsors_icon = '🎁'
```

### 5. Metric Order is Sacred
```
1. Campaign Day
2. Fundraising
3. Minutes Read
4. Sponsors
5. Avg. Participation (With Color)
6. Goal Met (≥1 Day)

# Do NOT reorder, even if it "makes more sense" contextually
```

---

## 📚 Related Documentation

- **RULES.md** - Complete banner metrics section with formulas and examples
- **UI_PATTERNS.md** - Visual styling patterns and color codes
- **BANNER_COMPARISON_ANALYSIS.md** - Original analysis (now resolved)
- **IMPLEMENTATION_PROMPT.md** - Source of truth for all requirements

---

## 🔍 Quick Reference: File Locations

### Banner Implementation
- **School:** `templates/school.html` lines 454-490
- **Teams:** `templates/teams.html` lines 532-650 (includes dynamic loop)
- **Grade Level:** `templates/grade_level.html` lines 604-650

### Backend Calculations
- **School Banner:** `app.py` lines 233-320
- **Teams Banner:** `app.py` lines 920-1010
- **Grade Level Banner:** `app.py` lines 1540-1630

### SQL Queries
- **Avg. Participation CTE:** `queries.py` lines 1285-1333
- **Team Participation:** `queries.py` lines 740-890
- **Class Participation:** `queries.py` lines 1200-1360

---

## ✅ Verification Checklist

Before modifying any banner-related code:

- [ ] Read RULES.md banner section completely
- [ ] Check existing pages for similar patterns
- [ ] Verify which participation metric to use (simple vs. avg with color)
- [ ] Test with date filter = 'all' and date filter = single date
- [ ] Run banner test suite: `pytest test_banner*.py -v`
- [ ] Verify filter indicators (◐) appear correctly
- [ ] Check that values can exceed 100% for Avg. Participation
- [ ] Test in browser (not just code review)

---

## 🎯 Implementation Phases (Historical)

### Phase 1-3: Foundation (Complete)
- Campaign Day metric added to all pages
- Sponsors metric added to School page
- Goal Met formatting standardized
- Metric order standardized

### Phase 4: Avg. Participation Switch (Complete)
- All banners switched from simple "Participation %" to "Avg. Participation (With Color)"
- Backend calculations updated
- 15 tests added

### Phase 5: Detail Table Enhancements (Complete)
- Teams: Added "Avg. Participation (With Color)" row
- Grade Level: Added "AVG. PARTICIPATION (WITH COLOR)" column
- Both metrics coexist on detail pages
- 17 tests added

### Phase 6: Icon Standardization (Complete)
- Verified all pages use 🎁 for Sponsors
- No 🤝 icons in production code

### Phase 7: Comprehensive Testing (Complete)
- 29 comprehensive tests covering all phases
- Banner structure, calculations, filters, edge cases
- Consistency across pages

### Phase 8: Documentation (Complete)
- RULES.md updated
- BANNER_COMPARISON_ANALYSIS.md marked resolved
- This summary document created

---

## 💡 Future Development Notes

### Adding a New Banner Metric?

**DON'T.** The 6-metric structure is now standard and tested comprehensively. Adding a 7th metric would:
- Break visual balance
- Require updating all 3 pages
- Require updating all 82 banner tests
- Require updating this documentation

**Instead:** Use detail tables or create a new page section.

### Changing Metric Order?

**DON'T.** The current order is tested and documented. Changing order would:
- Break user expectations
- Require updating JavaScript sorting/highlighting logic
- Require updating all test assertions
- Require updating filter indicator logic

**Exception:** Major redesign approved by product owner.

### Adding a Third Participation Metric?

**MAYBE.** We already have two:
1. Simple % (breadth)
2. Avg. with Color (depth + incentive)

If you need a third, ask yourself:
- Does it provide unique insight?
- Where would it live? (banner is full, tables already have both)
- Is it worth the complexity?

---

**Last Review:** 2025-10-30
**Next Review:** When adding new features that interact with banners
