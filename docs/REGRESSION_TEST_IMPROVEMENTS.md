# Regression Test Improvements

**Created:** 2025-11-10
**Status:** In Progress

## Overview

This document tracks improvements to regression tests to better validate actual content (not just structure) using the sample database with known values.

## Current State

### Existing Test Coverage

**Structural Tests** (Good coverage):
- Page loads without errors (HTTP 200)
- Expected sections/cards present
- CSS classes exist
- No error messages displayed
- Percentage/currency format validation

**Content Tests** (Limited coverage):
- `test_banner_values_regression.py` - Uses BeautifulSoup to verify exact banner values
- `test_sample_data_integrity` - Verifies team counts match database
- Some tests check for presence of values but not exactness

### Gaps Identified

1. **Top Performer Cards**: Tests check structure exists, but not which student/class names appear
2. **Tie Handling**: Tests check for tie indicators, but not which exact names are tied
3. **"Various Grades" Logic**: No tests verify this text appears when appropriate
4. **Comparison Table Values**: Limited validation of exact totals
5. **Class vs. Teacher Names**: No tests verify class names (not teacher names) displayed

## Proposed Improvements

### New Test File: `test_teams_content_regression.py`

**Purpose:** Verify exact content displayed in Teams page using sample database known values.

**Sample Database Known Values:**

**Team 1 (team1):**
- Students: student11 (K, $10, 1 sponsor), student21 (1, $20, 2 sponsors), student22 (1, $30, 3 sponsors)
- Reading: student11 (120 min - TOP), student21 (50 min), student22 (20 min)
- Classes: class1 (120 min reading), class2 ($50 fundraising)

**Team 2 (team2):**
- Students: student31 (2, $40, 4 sponsors), student32 (2, $50, 5 sponsors), student41 (2, $60, 6 sponsors), student42 (2, $70, 7 sponsors)
- Reading: student31 (60 min - TIE), student41 (60 min - TIE), student32 (30 min), student42 (30 min)
- Classes: class3 (100 min with color bonus), class4 (100 min with color bonus - TIE)

**Ties in Sample Data:**
- Grade 2 reading students: student31 and student41 (60 minutes each)
- Grade 2 top reading classes: class3 and class4 (100 minutes each with color bonus)

### Test Categories

#### 1. Individual Student Leaders (No Ties)
- `test_shows_student22_as_leader` - Verify student22 appears as team1 fundraising leader
- `test_shows_correct_amount_30` - Verify $30 amount displayed
- **Status:** ✅ 2/2 passing

#### 2. Tied Student Leaders
- `test_shows_both_tied_students` - Verify both student31 and student41 appear
- `test_shows_tie_format_with_comma` - Verify "student31, student41" format
- `test_shows_60_minutes` - Verify tied value displayed
- **Status:** ❌ 3/3 failing (card indexing issue - need to fix test)

#### 3. Tied Class Leaders
- `test_team2_top_class_reading_shows_tie` - Verify class3 and class4 appear
- `test_shows_100_minutes_with_color_bonus` - Verify 100 min (with color bonus)
- **Status:** ✅ 1/2 passing (color bonus calculation showing 90 instead of 100 - need investigation)

#### 4. "Various Grades" Logic
- `test_grade_display_single_grade` - Verify no "Various Grades" when all same grade
- **Status:** ✅ 1/1 passing

#### 5. Comparison Table Totals
- `test_fundraising_totals` - Verify $60 (team1) and $220 (team2)
- `test_minutes_totals` - Verify 190 min (team1) and 200 min (team2)
- `test_sponsor_totals` - Verify 28 total sponsors
- **Status:** ✅ 2/3 passing (minutes calculation discrepancy - need investigation)

#### 6. Class Name vs. Teacher Name
- `test_class_names_not_teacher_names` - Verify class names displayed
- **Status:** ✅ 1/1 passing

## Initial Test Run Results

**Summary:** 7 passed, 5 failed (58% pass rate)

**Passing Tests (7):**
- ✅ Team1 fundraising leader shows student22
- ✅ Team1 fundraising shows $30
- ✅ Team2 top class reading shows tied classes
- ✅ "Various Grades" logic works correctly
- ✅ Fundraising totals correct
- ✅ Sponsor totals correct
- ✅ Class names (not teacher names) displayed

**Failing Tests (5):**

### Issue 1: Card Indexing
**Tests affected:** 3 tests for Team2 reading leader tie

**Problem:** Test assumes reading leader is `cards[1]`, but actual HTML structure has different card order.

**Error message:**
```
Expected 'student31' in tied reading card, got:
💰 TOP CLASS (FUNDRAISING)
class4's Class
Grade 2
$130
```

**Root cause:** Need to identify cards by content/title, not by index.

**Fix:** Use BeautifulSoup to find card by title text ("READING LEADER"), not by position.

### Issue 2: Color Bonus Calculation
**Test affected:** `test_shows_100_minutes_with_color_bonus`

**Expected:** 100 minutes (90 base + 10 color bonus)
**Actual:** 90 minutes displayed

**Error message:**
```
Expected '100 min' or '1.7 hr' in card, got:
📚 TOP CLASS (READING)
class3, class4's Class
Grade 2
90 minutes
```

**Root cause:** Need to investigate if:
- Color bonus not being applied to TOP CLASS cards
- Different calculation for classes vs. students
- Sample database doesn't have color bonus data for classes

**Fix:** Either:
1. Fix the calculation if it's a bug
2. Update test expectation if 90 is correct

### Issue 3: Minutes Total Discrepancy
**Test affected:** `test_minutes_totals`

**Expected:** 190 minutes for team1
**Actual:** Value not found in page (different format or calculation)

**Root cause:** Need to verify:
- Is comparison table showing hours instead of minutes?
- Is it using uncapped vs. capped minutes?
- Is color bonus included in team totals?

**Fix:** Inspect actual HTML to see what value is displayed, then adjust test.

## Next Steps

### Phase 1: Fix Test Implementation Issues (Priority)
1. ✅ Commit current tests (even with failures) - documents expected behavior
2. Fix card indexing - use content-based selectors instead of positional
3. Investigate actual HTML structure for card order
4. Update tests to match actual card positions or use better selectors

### Phase 2: Investigate Calculation Discrepancies
1. **Color bonus for classes:** Verify if/how color bonus applies to TOP CLASS aggregations
2. **Minutes totals:** Check comparison table actual values and format
3. Document findings - may reveal bugs or misunderstandings

### Phase 3: Expand Coverage
Once initial tests are stable:
1. Add similar content tests for Grade Level page
2. Add tests for School page top performers
3. Add tests for "and X others" format (>3 ties)
4. Add tests for edge cases (no data, zero values)

### Phase 4: Integration with CI/CD
1. Add tests to pre-commit hook (already runs all pytest tests)
2. Document test maintenance process
3. Create test data documentation (sample DB schema and expected values)

## Benefits

### Before (Structural Tests Only)
**Example:** Teams page test
```python
def test_top_performers_structure(self, client):
    html = response.data.decode('utf-8')
    assert 'FUNDRAISING LEADER' in html  # ✅ Pass
    assert 'READING LEADER' in html      # ✅ Pass
```

**Problem:** Tests pass even if:
- Wrong student name displayed
- Ties not shown correctly
- Teacher names instead of class names
- Calculation errors in values

### After (Content Regression Tests)
**Example:** Teams page content test
```python
def test_shows_student22_as_leader(self, client):
    soup = BeautifulSoup(html, 'html.parser')
    cards = soup.find_all('div', class_='zen-card-kitsko')
    fundraising_card = cards[0]
    card_text = fundraising_card.get_text()
    assert 'student22' in card_text  # ✅ Verify EXACT name
    assert '$30' in card_text        # ✅ Verify EXACT amount
```

**Benefits:**
- Catches wrong student/class names
- Catches calculation errors
- Catches tie handling bugs
- Catches class vs. teacher name issues
- Documents expected behavior with sample data

## Lessons Learned

1. **BeautifulSoup is essential** for precise content testing (not just regex on HTML strings)
2. **Card indexing is fragile** - better to find by content/title than by position
3. **Failing tests are valuable** - they reveal mismatches between expectations and reality
4. **Sample database is key** - known, static values enable regression testing
5. **Document expected values** - tests serve as living documentation of sample data behavior

## References

- Original issue: Tie handling bugs on Teams and Grade Level pages
- Commit: aeea757 "Fix tie handling across Teams and Grade Level pages"
- Test file: `tests/test_teams_content_regression.py` (12 tests, 7 passing)
- Sample database: `db/readathon_sample.db` (7 students, 4 classes, 2 teams, 2 contest days)

## Conclusion

Content regression tests provide significantly better coverage than structural tests alone. Initial implementation found 5 areas needing attention (test fixes + potential bugs), demonstrating the value of this approach.

**Current test suite:** 401 passing structural + 7 passing content tests
**Goal:** Add 20-30 content regression tests across all major pages
**Timeline:** Phase 1 fixes by next session, full expansion over 2-3 sessions
