# Banner Comparison Analysis - School, Teams, Grade Level Pages

**Date:** 2025-10-30
**Purpose:** Identify inconsistencies in headline banner metrics across all three major pages to enable standardization

---

## ✅ RESOLVED - 2025-10-30

**All banner inconsistencies have been addressed through Phases 1-7 of standardization work.**

### Final State (After Standardization):
- ✅ All 3 pages have identical 6-metric structure
- ✅ Metrics use consistent icons, labels, and formatting
- ✅ "Avg. Participation (With Color)" calculation standardized across all pages
- ✅ Detail tables enhanced with new row (Teams) and column (Grade Level)
- ✅ Comprehensive test suite (165 tests) ensures consistency
- ✅ Sponsors icon standardized to 🎁 (not 🤝)
- ✅ Filter indicators (◐) applied consistently

### Standardization Commits:
1. Phase 1-3: Campaign Day, Sponsors metric, Goal Met formatting
2. Phase 4: Switched all banners to "Avg. Participation (With Color)"
3. Phase 5: Added "Avg. Participation (With Color)" to detail tables
4. Phase 6: Verified icon consistency
5. Phase 7: Comprehensive testing suite

**See RULES.md for complete metric definitions and formulas.**

**See test files for verification:**
- `test_banner_standardization_phases1-3.py` (21 tests)
- `test_banner_phase4_avg_participation.py` (15 tests)
- `test_banner_phase5_detail_tables.py` (17 tests)
- `test_banner_comprehensive.py` (29 tests)

---

## Original Analysis (Historical Reference)

The analysis below was created on 2025-10-30 to identify inconsistencies that needed to be resolved. All issues have now been fixed.

---

## Executive Summary

All three pages use the same visual styling (dark blue background #1e3a5f, cyan values #17a2b8), but have **significant differences** in:
- **Metric order** (different priorities on each page)
- **Metric selection** (School has unique "Campaign Day" metric)
- **Subtitle content** (inconsistent detail levels)
- **Filter indicators** (◐) applied inconsistently
- **Team badge display** (School doesn't show team badges in banner)

**Recommendation:** Prioritize consistency in metric order and filter indicator logic across all pages.

---

## 1. Metric-by-Metric Comparison

### Legend:
- ✅ = Metric present
- ❌ = Metric absent
- 🔷 = Different implementation
- ◐ = Filter indicator present

| Metric | School | Teams | Grade Level | Notes |
|--------|--------|-------|-------------|-------|
| **Campaign Day** | ✅ Position 1 | ❌ | ❌ | School-only, shows "Day X of Y" |
| **Fundraising** | ✅ Position 2 | ✅ Position 1 | ✅ Position 1 | Different subtitles |
| **Minutes Read** | ✅ Position 3 ◐ | ✅ Position 2 ◐ | ✅ Position 2 ◐ | Consistent filter indicator |
| **Sponsors** | ❌ | ✅ Position 3 | ✅ Position 3 | School doesn't show sponsors |
| **Participation** | ✅ Position 4 ◐ | ✅ Position 4 ◐ | ✅ Position 4 ◐ | Consistent across all |
| **Goal Met (≥1 Day)** | ✅ Position 5 ◐ | ✅ Position 5 ◐ | ✅ Position 5 ◐ | Consistent across all |

### Key Differences:

1. **School page is unique:**
   - Has "Campaign Day" metric (position 1)
   - Missing "Sponsors" metric
   - Shows 5 metrics total

2. **Teams and Grade Level are similar:**
   - Both start with Fundraising
   - Both show 5 metrics in same order
   - Both show team badges for winners

3. **Metric order inconsistency:**
   - School: Campaign Day → Fundraising → Minutes → Participation → Goal Met
   - Teams: Fundraising → Minutes → Sponsors → Participation → Goal Met
   - Grade: Fundraising → Minutes → Sponsors → Participation → Goal Met

---

## 2. Detailed Metric Comparison

### Metric 1: Campaign Day (School Only)

**School Page:**
```
Icon: 📅
Label: "CAMPAIGN DAY"
Value: "Day X of Y" (e.g., "3 of 6")
Subtitle: Date (e.g., "2025-10-13")
Filter: None
```

**Why unique:** This is a status metric, not a competition metric. Teams and Grade Level focus on competition winners.

---

### Metric 2/1: Fundraising

| Aspect | School | Teams | Grade Level |
|--------|--------|-------|-------------|
| **Icon** | 💰 | 💰 | 💰 |
| **Label** | "FUNDRAISING" | "💰 FUNDRAISING" | "💰 Fundraising" |
| **Winner Badge** | ❌ No | ✅ Yes (team badge) | ✅ Yes (team badge) |
| **Value Format** | `$X,XXX` | `$X,XXX` | `$X,XXX` |
| **Subtitle** | "X of Y Students (Z%)" | "X of Y students (Z%)" or hours | Class name |
| **Extra Line** | ❌ No | ❌ No | ✅ Yes ("🏆 Winner: Grade • Class") |
| **Filter ◐** | ❌ No | ❌ No (cumulative always) | ❌ No |

**Key Difference:** Grade Level shows winning class name + extra "Winner" line. School shows participation count. Teams shows count or hours depending on metric type.

---

### Metric 3/2: Minutes Read

| Aspect | School | Teams | Grade Level |
|--------|--------|-------|-------------|
| **Icon** | 📚 | 📖 | 📖 |
| **Label** | "MINUTES READ" | "💰 MINUTES READ" | "📖 Minutes Read" |
| **Winner Badge** | ❌ No | ✅ Yes (team badge) | ✅ Yes (team badge) |
| **Value Format** | `X,XXX hours` | `X,XXX min` | `X,XXX min` |
| **Subtitle** | "(X,XXX min)" | "(X hours)" | "(X hours)" |
| **Extra Line** | ❌ No | ❌ No | ✅ Yes ("🏆 Winner: Grade • Class") |
| **Filter ◐** | ✅ Yes (if filtered) | ✅ Yes (if filtered) | ✅ Yes (if filtered) |
| **Tooltip** | "Cumulative through {date}" | "Cumulative through {date}" | "Cumulative through {date}" |

**Key Difference:** School shows hours as primary value, Teams/Grade show minutes as primary. All three honor filter indicator consistently.

---

### Metric 4/3: Sponsors

| Aspect | School | Teams | Grade Level |
|--------|--------|-------|-------------|
| **Present?** | ❌ **MISSING** | ✅ Yes | ✅ Yes |
| **Icon** | N/A | 🎁 | 🎁 |
| **Label** | N/A | "🎁 SPONSORS" | "🎁 Sponsors" |
| **Winner Badge** | N/A | ✅ Yes (team badge) | ✅ Yes (team badge) |
| **Value Format** | N/A | `X,XXX` | `X,XXX` |
| **Subtitle** | N/A | "X of Y students (Z%)" or hours | Class name |
| **Extra Line** | N/A | ❌ No | ✅ Yes ("🏆 Winner: Grade • Class") |
| **Filter ◐** | N/A | ❌ No | ❌ No |

**Key Issue:** School page doesn't show sponsors in banner at all.

---

### Metric 5/4: Participation

| Aspect | School | Teams | Grade Level |
|--------|--------|-------|-------------|
| **Icon** | 👥 | 👥 | 👥 |
| **Label** | "PARTICIPATION" | "👥 PARTICIPATION" | "👥 Participation" |
| **Winner Badge** | ❌ No | ✅ Yes (team badge) | ✅ Yes (team badge) |
| **Value Format** | `X%` | `X%` | `X.X%` |
| **Subtitle** | "X of Y Students" (2 lines) | "X of Y students (Z%)" | Class name |
| **Extra Line** | ❌ No | ❌ No | ✅ Yes ("🏆 Winner: Grade • Class") |
| **Filter ◐** | ✅ Yes (if filtered) | ✅ Yes (if filtered) | ✅ Yes (if filtered) |
| **Tooltip** | "Cumulative through {date}" | "Cumulative through {date}" | "Average daily participation through {date}" |

**Key Difference:** Grade Level tooltip says "Average daily" while School/Teams say "Cumulative". All three honor filter consistently.

---

### Metric 6/5: Goal Met (≥1 Day)

| Aspect | School | Teams | Grade Level |
|--------|--------|-------|-------------|
| **Icon** | 🎯 | 🎯 | 🎯 |
| **Label** | "GOAL MET (≥1 DAY)" | "🎯 GOAL MET (≥1 DAY)" | "🎯 Goal Met (≥1 Day)" |
| **Winner Badge** | ❌ No | ✅ Yes (team badge) | ✅ Yes (team badge) |
| **Value Format** | `X%` | `X%` | `X.X%` |
| **Subtitle** | "X of Y Students" (2 lines) | "X of Y students (Z%)" | Class name |
| **Extra Line** | ❌ No | ❌ No | ✅ Yes ("🏆 Winner: Grade • Class") |
| **Filter ◐** | ✅ Yes (if filtered) | ✅ Yes (if filtered) | ✅ Yes (if filtered) |
| **Tooltip** | "Cumulative through {date}" | "Students who met 120 min goal at least once through {date}" | "Students who met 120 min goal at least once through {date}" |

**Key Difference:** School tooltip is generic "Cumulative", while Teams/Grade are more descriptive. All three honor filter consistently.

---

## 3. Visual Structure Comparison

### HTML Structure

| Aspect | School | Teams | Grade Level |
|--------|--------|-------|-------------|
| **Container** | `<div class="headline-banner">` | `<div class="headline-banner">` | `<div class="headline-banner">` |
| **Row Class** | `row align-items-center` | `row g-0` | `row g-0` |
| **Metric Loop** | ❌ Static (5 hardcoded) | ✅ Dynamic (`{% for metric in banner.metrics %}`) | ❌ Static (5 hardcoded) |
| **Column Class** | `col headline-metric` | `col headline-metric` | `col headline-metric` |

**Key Difference:** Teams uses dynamic loop through `banner.metrics`, School and Grade Level hardcode each metric.

---

### CSS Classes Used

| Class | School | Teams | Grade Level | Purpose |
|-------|--------|-------|-------------|---------|
| `headline-banner` | ✅ | ✅ | ✅ | Container (dark blue background) |
| `headline-metric` | ✅ | ✅ | ✅ | Individual metric column |
| `headline-label` | ✅ | ✅ | ✅ | Metric name (uppercase, small) |
| `headline-winner` | ❌ | ✅ | ✅ | Team badge container |
| `headline-value` | ✅ | ✅ | ✅ | Large cyan number |
| `headline-subtitle` | ✅ | ✅ | ✅ | Supporting text below value |
| `headline-extra` | ❌ | ❌ | ✅ | Additional winner info (Grade only) |
| `team-badge` | ❌ | ✅ | ✅ | Team winner badge |
| `team-badge-kitsko` | ❌ | ✅ | ✅ | Team 1 styling (blue) |
| `team-badge-staub` | ❌ | ✅ | ✅ | Team 2 styling (yellow) |
| `filter-indicator` | ✅ | ✅ | ✅ | ◐ symbol with tooltip |

**Key Finding:** School page doesn't use `headline-winner`, `headline-extra`, or team badges in banner (but does use them in body cards).

---

### Styling Consistency

| CSS Property | School | Teams | Grade Level | Status |
|-------------|--------|-------|-------------|--------|
| **Background** | `#1e3a5f` | `#1e3a5f` | `#1e3a5f` | ✅ Consistent |
| **Border Radius** | `0.5rem` | `0.5rem` | `0.5rem` | ✅ Consistent |
| **Padding** | `0.6rem 1rem` | `0.6rem 1rem` | `0.6rem 1rem` | ✅ Consistent |
| **Value Color** | `#17a2b8` (cyan) | `#17a2b8` (cyan) | `#17a2b8` (cyan) | ✅ Consistent |
| **Value Size** | `1.8rem` | `1.8rem` | `1.8rem` | ✅ Consistent |
| **Label Size** | `0.7rem` | `0.7rem` | `0.7rem` | ✅ Consistent |
| **Subtitle Size** | `0.7rem` | `0.7rem` | `0.7rem` | ✅ Consistent |
| **Extra Size** | N/A | N/A | `0.65rem` | 🔷 Grade only |

**Verdict:** Visual styling is highly consistent. Main differences are in content structure, not appearance.

---

## 4. Filter Indicator (◐) Analysis

### When Filter Indicator Appears

| Metric | School | Teams | Grade Level |
|--------|--------|-------|-------------|
| **Campaign Day** | N/A (no filter) | N/A | N/A |
| **Fundraising** | ❌ Never | ❌ Never | ❌ Never |
| **Minutes Read** | ✅ If filtered | ✅ If filtered | ✅ If filtered |
| **Sponsors** | N/A (missing) | ❌ Never | ❌ Never |
| **Participation** | ✅ If filtered | ✅ If filtered | ✅ If filtered |
| **Goal Met** | ✅ If filtered | ✅ If filtered | ✅ If filtered |

### Filter Logic Condition

**School:**
```jinja
{% if request.args.get('date', 'all') != 'all' %}
```

**Teams:**
```jinja
{% if date_filter != 'all' %}
```

**Grade Level:**
```jinja
{% if date_filter != 'all' %}
```

**Verdict:** ✅ Filter indicator logic is **consistent** across all three pages (appears when date filter is active, only on cumulative metrics).

---

### Tooltip Text Comparison

| Metric | School Tooltip | Teams Tooltip | Grade Level Tooltip |
|--------|---------------|---------------|---------------------|
| **Minutes Read** | "Cumulative through {date}" | "Cumulative through {date}" | "Cumulative through {date}" |
| **Participation** | "Cumulative through {date}" | "Cumulative through {date}" | "**Average daily** participation through {date}" |
| **Goal Met** | "Cumulative through {date}" | "Students who met 120 min goal at least once through {date}" | "Students who met 120 min goal at least once through {date}" |

**Issues:**
1. ⚠️ School has generic tooltips, Teams/Grade Level have descriptive ones
2. ⚠️ Grade Level says "Average daily" for Participation, but School/Teams say "Cumulative"

---

## 5. Subtitle Content Patterns

### School Page Subtitles:
- **Campaign Day:** Date string (e.g., "2025-10-13")
- **Fundraising:** "X of Y Students (Z%)" (2 lines with `<br>`)
- **Minutes Read:** "(X,XXX min)" (parentheses)
- **Participation:** "X of Y Students" (2 lines with `<br>`)
- **Goal Met:** "X of Y Students" (2 lines with `<br>`)

### Teams Page Subtitles:
- **Fundraising:** "X of Y students (Z%)" OR "(X hours)" [depends on metric.key]
- **Minutes Read:** "(X hours)"
- **Sponsors:** "X of Y students (Z%)"
- **Participation:** "X of Y students (Z%)"
- **Goal Met:** "X of Y students (Z%)"

**Pattern:** Teams subtitle varies based on metric type (uses conditional logic)

### Grade Level Page Subtitles:
- **Fundraising:** Class name (e.g., "Room 101 - Ms. Spencer")
- **Minutes Read:** "(X hours)"
- **Sponsors:** Class name
- **Participation:** Class name
- **Goal Met:** Class name

**Pattern:** Grade Level always shows winning class name (simpler, more consistent)

---

### Grade Level Extra Line (Unique):

Grade Level has an additional `headline-extra` line below subtitle:
```html
<div class="headline-extra">
    🏆 Winner: {{ format_grade(grade) }} • {{ class_name }}
</div>
```

**Example:** "🏆 Winner: 3rd Grade • Room 101 - Ms. Spencer"

This provides more context than just the class name in subtitle.

---

## 6. Team Badge Display

### School Page:
- ❌ **No team badges in banner**
- ✅ Team badges appear in body cards (Team Competition section)
- Shows numeric values without indicating which team is winning

### Teams Page:
- ✅ **Team badges in banner** showing winner for each metric
- Badge styles:
  - `team-badge-kitsko` (Team 1): Dark blue background, white text
  - `team-badge-staub` (Team 2): Yellow/amber background, dark text
  - `leader-badge-tie`: Gray badge for ties
- Shows team name in uppercase inside badge

### Grade Level Page:
- ✅ **Team badges in banner** showing which team owns winning class
- Same badge styles as Teams page
- Badge indicates team of the winning class (not just class name)

**Inconsistency:** School banner doesn't visually indicate team winners, while Teams and Grade Level do.

---

## 7. Key Inconsistencies Summary

### Priority Issues:

1. **Metric Order** 🔴 HIGH
   - School: Campaign Day first, then Fundraising
   - Teams/Grade: Fundraising first
   - **Impact:** Users expect same metric order across tabs

2. **Missing Sponsors on School** 🔴 HIGH
   - School banner shows 5 metrics but omits Sponsors
   - Teams/Grade both show Sponsors in position 3
   - **Impact:** Incomplete view of competition on School page

3. **No Team Badges on School** 🟡 MEDIUM
   - School doesn't show which team is winning each metric
   - Teams/Grade both show team badges prominently
   - **Impact:** Less visual clarity on School page

4. **Inconsistent Subtitle Content** 🟡 MEDIUM
   - School: Participation counts with percentages
   - Teams: Dynamic based on metric type
   - Grade: Class names only
   - **Impact:** Different information density across pages

5. **Tooltip Inconsistencies** 🟡 MEDIUM
   - School: Generic "Cumulative through {date}"
   - Teams/Grade: Descriptive explanations
   - Grade: Says "Average daily" for Participation (different from others)
   - **Impact:** Less helpful for users on School page

6. **Extra Winner Line** 🟢 LOW
   - Grade Level has `headline-extra` with full winner details
   - School/Teams don't have this
   - **Impact:** Grade Level provides more context (this is actually good)

---

## 8. Recommendations for Standardization

### Option A: Make All Pages Match Teams/Grade Structure

**Changes to School Page:**
1. **Remove "Campaign Day"** metric from banner (or move to page header)
2. **Add "Sponsors"** metric in position 3
3. **Add team badge display** showing winner for each metric
4. **Standardize metric order:** Fundraising → Minutes → Sponsors → Participation → Goal Met
5. **Update tooltips** to be more descriptive (match Teams/Grade Level)
6. **Consider adding** `headline-extra` line like Grade Level for more context

**Pros:**
- ✅ Consistent experience across all three pages
- ✅ Users know where to find each metric
- ✅ Visual clarity with team badges

**Cons:**
- ❌ Lose "Campaign Day" metric from banner (but could keep in page header or cards)
- ❌ More work to implement team winner logic on School page

---

### Option B: Create Unified 6-Metric Banner

**Add "Campaign Day" to all three pages:**
1. All pages show: Campaign Day → Fundraising → Minutes → Sponsors → Participation → Goal Met
2. School gets team badges
3. All pages get descriptive tooltips
4. All pages get `headline-extra` line (Grade Level style)

**Pros:**
- ✅ Campaign Day is valuable context for all pages
- ✅ Complete standardization
- ✅ Most information-dense option

**Cons:**
- ❌ 6 metrics may be too crowded on mobile
- ❌ Campaign Day is status, not competition (doesn't fit Teams/Grade philosophy)

---

### Option C: Minimal Changes (Recommended)

**Goal:** Fix critical inconsistencies, preserve page-specific philosophy

**Changes:**

1. **School Page:**
   - Keep "Campaign Day" (it's valuable status info)
   - Add "Sponsors" metric after Minutes Read
   - Keep 5 metrics total: Campaign Day → Fundraising → Minutes → Sponsors → Participation (remove Goal Met OR keep 6)
   - Add team badges to show winners visually
   - Update tooltips to match Teams/Grade descriptiveness

2. **Teams Page:**
   - Keep current structure (already good)
   - Ensure tooltips match Grade Level where appropriate

3. **Grade Level Page:**
   - Keep current structure (already good)
   - Fix "Average daily" tooltip for Participation to say "Cumulative" (match others)

4. **All Pages:**
   - **Standardize metric order where metrics overlap:**
     - Fundraising always position 1 or 2
     - Minutes Read always position 2 or 3
     - Sponsors always position 3 or 4
     - Participation always position 4 or 5
     - Goal Met always position 5 or 6
   - **Standardize tooltip text** for same metrics
   - **Standardize subtitle patterns** (or document why they differ)

**Pros:**
- ✅ Fixes critical inconsistencies (missing Sponsors, no team badges)
- ✅ Preserves page-specific value (Campaign Day on School)
- ✅ Less work than full standardization
- ✅ Respects different page purposes

**Cons:**
- ❌ School still has different metric order (but justifiable)

---

## 9. Proposed Standard Banner Structure

### Recommended Metric Order (All Pages):

| Position | Metric | Icon | Filter ◐ | Notes |
|----------|--------|------|----------|-------|
| **1** | Campaign Day | 📅 | No | School only (optional for others) |
| **2** | Fundraising | 💰 | No | Always cumulative |
| **3** | Minutes Read | 📖 | Yes | Respects date filter |
| **4** | Sponsors | 🎁 | No | Always cumulative |
| **5** | Participation | 👥 | Yes | Respects date filter |
| **6** | Goal Met (≥1 Day) | 🎯 | Yes | Respects date filter |

**If Campaign Day is School-only:**
- School: 6 metrics (1-6)
- Teams: 5 metrics (2-6)
- Grade Level: 5 metrics (2-6)

---

### Recommended HTML Structure (All Pages):

```html
<div class="headline-banner">
    <div class="row g-0">
        <div class="col headline-metric">
            <div class="headline-label">
                💰 FUNDRAISING
            </div>
            <div class="headline-winner">
                <span class="team-badge team-badge-{team_name}">
                    {TEAM_NAME}
                </span>
            </div>
            <div class="headline-value">
                ${value}
            </div>
            <div class="headline-subtitle">
                {context_text}
            </div>
            <!-- Optional extra line (Grade Level style) -->
            <div class="headline-extra">
                🏆 Winner: {details}
            </div>
        </div>
        <!-- Repeat for each metric -->
    </div>
</div>
```

**Key Elements:**
- ✅ `headline-winner` with team badge (all pages)
- ✅ `headline-extra` for additional context (optional but recommended)
- ✅ Filter indicator `◐` only on filtered metrics
- ✅ Consistent tooltip text for same metrics

---

### Recommended Tooltip Standards:

| Metric | Tooltip Text (When Filtered) |
|--------|------------------------------|
| **Minutes Read** | "Cumulative minutes read through {date}" |
| **Participation** | "Cumulative participation through {date}" |
| **Goal Met** | "Students who met 120 min goal at least once through {date}" |

**All pages should use identical tooltip text for same metrics.**

---

## 10. Implementation Checklist

### School Page Updates:
- [ ] Add "Sponsors" metric to banner (position 4)
- [ ] Add `headline-winner` section with team badges to each metric
- [ ] Update metric order to match standard (if not keeping Campaign Day first)
- [ ] Update tooltips to be more descriptive (match Teams/Grade Level)
- [ ] Consider adding `headline-extra` line for more context
- [ ] Test responsive layout with 6 metrics (if keeping Campaign Day)

### Teams Page Updates:
- [ ] Verify tooltips match Grade Level where appropriate
- [ ] Consider adding `headline-extra` line like Grade Level
- [ ] Ensure metric order matches standard

### Grade Level Page Updates:
- [ ] Fix "Average daily" tooltip for Participation → change to "Cumulative participation through {date}"
- [ ] Verify metric order matches standard
- [ ] Keep `headline-extra` line (it's good!)

### All Pages:
- [ ] Standardize tooltip text for identical metrics
- [ ] Document any intentional differences in subtitle patterns
- [ ] Test filter indicator (◐) behavior consistency
- [ ] Verify team badge styling is identical across pages
- [ ] Test responsive layout on mobile (metrics may need to stack)

---

## 11. Testing Validation

After implementing changes, verify:

1. **Metric Order:**
   - [ ] Same metrics appear in same positions across pages (where applicable)
   - [ ] Users can find metrics in predictable locations

2. **Filter Indicators:**
   - [ ] ◐ appears only on Minutes, Participation, Goal Met
   - [ ] ◐ only appears when date filter is active (not "all")
   - [ ] Tooltips are consistent across pages

3. **Team Badges:**
   - [ ] All pages show team badges for winners
   - [ ] Badge colors are consistent (blue for team 1, yellow for team 2)
   - [ ] Tie badge appears when appropriate

4. **Visual Consistency:**
   - [ ] Banner height is same across pages
   - [ ] Value colors are identical (#17a2b8)
   - [ ] Responsive layout works on mobile

5. **Content Accuracy:**
   - [ ] Values match database queries
   - [ ] Subtitles provide helpful context
   - [ ] Tooltips are descriptive and accurate

---

**Last Updated:** 2025-10-30
**Next Step:** Review this analysis with user, decide on Option A, B, or C for standardization approach
