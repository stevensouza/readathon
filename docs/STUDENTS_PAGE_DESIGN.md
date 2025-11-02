# Students Page Design - Work in Progress

**Status:** HTML prototype complete with all refinements applied
**Created:** 2025-10-31
**Last Updated:** 2025-11-01 (HTML Prototype Session - All refinements documented)
**Resume Keyword:** "let's continue with the students page" or "students page design"

## Resume Instructions for Next Session

**To resume this work, say:** "Let's continue with the students page" or "students page design"

**What to do when resuming:**
1. Read this entire file (STUDENTS_PAGE_DESIGN.md) - especially "Design Decisions (2025-11-01 Session)" section
2. Review 11 documented design decisions (lines 186-370+)
3. Note special focus on:
   - Banner consistency (exact labels/icons)
   - Filter order: All Grades → By Team → K, 1, 2, 3, 4, 5
   - ALL data honors BOTH date filter AND grade/team filters
   - Filter stickiness across pages (sessionStorage)
4. Review open questions
5. Create revised ASCII prototype incorporating all decisions
6. Get user approval before moving to HTML prototype phase

---

## Context

User requested design for a new **Students** tab that would show individual student-level data across all 411 students. After reviewing project standards (RULES.md, UI_PATTERNS.md, existing School/Teams/Grade Level pages), I designed an ASCII prototype.

**Decision:** User wants to review data on existing pages (School, Teams, Grade Level) first before finalizing Students page design. Also discovered a sponsor metric bug on School page that needs fixing first.

---

## ASCII Prototype (v2 - APPROVED 2025-11-01)

### Master View (Students Table)

```
═══════════════════════════════════════════════════════════════════════════════════
                          👨‍🎓 STUDENTS OVERVIEW
═══════════════════════════════════════════════════════════════════════════════════

┌─────────────────────────────────────────────────────────────────────────────────┐
│  📅 Filter Period: [Full Contest (Oct 10 - Oct 19) ▼]                          │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────┐
│  HEADLINE BANNER (6 Metrics - Exact Match with School/Teams/Grade Level)       │
├─────────┬─────────┬─────────┬─────────┬───────────────────┬────────────────────┤
│ 📅 DAY  │💰 FUND  │📚 MIN   │🎁 SPON  │👥 AVG PART (◐)    │🎯 GOAL MET (◐)     │
│Campaign │Fundrais-│Minutes  │Sponsors │Avg. Participation │Goal Met (≥1 Day)   │
│   Day   │  ing    │  Read   │         │   (With Color)    │                    │
├─────────┼─────────┼─────────┼─────────┼───────────────────┼────────────────────┤
│ Day 3   │ $45,678 │ 8,234   │   28    │      78.5%        │      82.0%         │
│ of 10   │325/411  │ hours   │sponsors │   323/411 active  │  337/411 students  │
│ Oct 12  │(79.1%)  │   ◐     │7/411    │        ◐          │        ◐           │
│         │         │         │(1.7%)   │                   │                    │
└─────────┴─────────┴─────────┴─────────┴───────────────────┴────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────┐
│  FILTERS                                                                        │
├─────────────────────────────────────────────────────────────────────────────────┤
│  [All Grades] [K] [1] [2] [3] [4] [5]          Team: [All Teams ▼]            │
│                                                                                  │
│  Showing 411 students  |  [📋 Copy] [💾 Export CSV]                            │
└─────────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│  📊 ALL STUDENTS TABLE (Click any row for daily breakdown)                                                  │
├────────────┬──────┬────────┬────────────┬───────────┬────────┬────────┬────────┬────────┬──────┬──────┬──────┬──────┤
│ STUDENT    │GRADE │ TEAM   │ CLASS      │ TEACHER   │FUNDRAIS│SPONSORS│MINUTES │MINUTES │DAYS  │PARTIC│DAYS  │GOAL  │
│ NAME ▲     │      │        │ NAME       │ NAME      │ ING💰  │  🎁    │CAPPED◐ │UNCAPPED│PARTIC│  % ◐ │GOAL  │MET % │
│            │      │        │            │           │        │        │   📚   │  📚    │  ◐   │      │ ◐    │  ◐   │
├────────────┼──────┼────────┼────────────┼───────────┼────────┼────────┼────────┼────────┼──────┼──────┼──────┼──────┤
│Sarah Chen  │  5   │KITSKO  │ogg         │ogg        │⭕$2,624│   12   │ ⭕1,200│ 1,245  │ 10/10│ 100% │  10  │ 100% │
│            │      │        │            │           │        │        │  min   │  min   │      │      │      │      │
├────────────┼──────┼────────┼────────────┼───────────┼────────┼────────┼────────┼────────┼──────┼──────┼──────┼──────┤
│David Park  │  4   │STAUB   │neurohr pm  │neurohr    │⭕$1,987│    9   │  1,176 │ 1,198  │ 10/10│ 100% │  10  │ 100% │
│            │      │        │            │           │        │        │  min   │  min   │      │      │      │      │
├────────────┼──────┼────────┼────────────┼───────────┼────────┼────────┼────────┼────────┼──────┼──────┼──────┼──────┤
│Emma Wilson │  K   │KITSKO  │lee am      │lee        │⭕$1,776│    8   │  1,152 │ 1,152  │  9/10│  90% │   9  │ 100% │
│            │      │        │            │           │        │        │  min   │  min   │      │      │      │      │
├────────────┼──────┼────────┼────────────┼───────────┼────────┼────────┼────────┼────────┼──────┼──────┼──────┼──────┤
│Noah Garcia │  2   │STAUB   │white       │white      │ $1,654 │    7   │    960 │   960  │  8/10│  80% │   8  │ 100% │
│            │      │        │            │           │        │        │  min   │  min   │      │      │      │      │
├────────────┼──────┼────────┼────────────┼───────────┼────────┼────────┼────────┼────────┼──────┼──────┼──────┼──────┤
│...         │      │        │            │           │        │        │        │        │      │      │      │      │
│(407 more)  │      │        │            │           │        │        │        │        │      │      │      │      │
├────────────┼──────┼────────┼────────────┼───────────┼────────┼────────┼────────┼────────┼──────┼──────┼──────┼──────┤
│Mia Foster  │  3   │STAUB   │white       │white      │     $0 │    0   │      0 │     0  │  0/10│   0% │   0  │   0% │
│            │      │        │            │           │        │        │  min   │  min   │      │      │      │      │
└────────────┴──────┴────────┴────────────┴───────────┴────────┴────────┴────────┴────────┴──────┴──────┴──────┴──────┘

Legend:
  ⭕ = Gold oval (school-wide winner for this metric)
  🥈 = Silver oval (grade/team winner when filters applied)
  ◐ = Honors date filter (recalculates when date range changes)
  💰 = Total fundraising (NOT filtered by date)
  🎁 = Number of sponsors per student (NOT filtered by date)
  📚 = Reading minutes (Capped = max 120/day for contest, Uncapped = actual total)

Notes:
  - Click any row to see daily breakdown
  - All columns sortable (click header)
  - Export exports only visible/filtered students
  - Gold highlights based on full school (411 students)
  - Silver highlights appear when grade/team filter active

┌─────────────────────────────────────────────────────────────────────────────────┐
│  [▶ Click to expand] Data Sources & Last Updated                               │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### Detail View (Click Student Row)

```
═══════════════════════════════════════════════════════════════════════════════════
                   📋 STUDENT DETAIL: Sarah Chen
═══════════════════════════════════════════════════════════════════════════════════

┌─────────────────────────────────────────────────────────────────────────────────┐
│  STUDENT INFO                                                      [✖ Close]     │
├─────────────────────────────────────────────────────────────────────────────────┤
│  Name: Sarah Chen             Grade: 5             Team: KITSKO                 │
│  Class: ogg                   Teacher: ogg                                      │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────┐
│  SUMMARY METRICS (Contest Period: Oct 10-19, 2025)                             │
├──────────────┬──────────────┬──────────────┬──────────────┬──────────────┬─────┤
│💰 FUNDRAISING│🎁 SPONSORS   │📚 MINUTES    │📚 MINUTES    │👥 PARTICIPATION│🎯 GOAL│
│              │              │   CAPPED     │  UNCAPPED    │               │      │
├──────────────┼──────────────┼──────────────┼──────────────┼──────────────┼─────┤
│  ⭕ $2,624   │      12      │  ⭕ 1,200 min│   1,245 min  │    10/10     │ 10/10│
│  (School #1) │              │  (School #1) │  (+45 over)  │     100%     │ 100% │
└──────────────┴──────────────┴──────────────┴──────────────┴──────────────┴─────┘

Legend: ⭕ = School-wide winner (gold)  |  🥈 = Grade/team winner (silver)

┌─────────────────────────────────────────────────────────────────────────────────┐
│  📅 DAILY READING LOG                                                           │
├─────┬──────────────┬──────────────┬──────────────┬─────────────────────────────┤
│ DAY │ DATE         │ MINUTES READ │ CAPPED       │ STATUS                      │
│     │              │  (ACTUAL)    │ (MAX 120)    │                             │
├─────┼──────────────┼──────────────┼──────────────┼─────────────────────────────┤
│  1  │ Fri, Oct 10  │    127 min   │   120 min    │ ⚠️ Exceeded cap (+7 min)   │
│     │              │              │              │ ✅ Met daily goal           │
├─────┼──────────────┼──────────────┼──────────────┼─────────────────────────────┤
│  2  │ Sat, Oct 11  │    135 min   │   120 min    │ ⚠️ Exceeded cap (+15 min)  │
│     │              │              │              │ ✅ Met daily goal           │
├─────┼──────────────┼──────────────┼──────────────┼─────────────────────────────┤
│  3  │ Sun, Oct 12  │    118 min   │   118 min    │ ✅ Met daily goal           │
├─────┼──────────────┼──────────────┼──────────────┼─────────────────────────────┤
│  4  │ Mon, Oct 13  │    132 min   │   120 min    │ ⚠️ Exceeded cap (+12 min)  │
│     │              │              │              │ ✅ Met daily goal           │
├─────┼──────────────┼──────────────┼──────────────┼─────────────────────────────┤
│  5  │ Tue, Oct 14  │    125 min   │   120 min    │ ⚠️ Exceeded cap (+5 min)   │
│     │              │              │              │ ✅ Met daily goal           │
├─────┼──────────────┼──────────────┼──────────────┼─────────────────────────────┤
│  6  │ Wed, Oct 15  │    128 min   │   120 min    │ ⚠️ Exceeded cap (+8 min)   │
│     │              │              │              │ ✅ Met daily goal           │
├─────┼──────────────┼──────────────┼──────────────┼─────────────────────────────┤
│  7  │ Thu, Oct 16  │    120 min   │   120 min    │ ✅ Met daily goal           │
├─────┼──────────────┼──────────────┼──────────────┼─────────────────────────────┤
│  8  │ Fri, Oct 17  │    115 min   │   115 min    │ ✅ Met daily goal           │
├─────┼──────────────┼──────────────┼──────────────┼─────────────────────────────┤
│  9  │ Sat, Oct 18  │    122 min   │   120 min    │ ⚠️ Exceeded cap (+2 min)   │
│     │              │              │              │ ✅ Met daily goal           │
├─────┼──────────────┼──────────────┼──────────────┼─────────────────────────────┤
│ 10  │ Sun, Oct 19  │    123 min   │   120 min    │ ⚠️ Exceeded cap (+3 min)   │
│     │              │              │              │ ✅ Met daily goal           │
├─────┼──────────────┼──────────────┼──────────────┼─────────────────────────────┤
│TOTAL│              │  1,245 min   │ 1,200 min    │ Days participated: 10/10    │
│     │              │  (20.8 hrs)  │ (20.0 hrs)   │ Days met goal: 10/10 (100%) │
└─────┴──────────────┴──────────────┴──────────────┴─────────────────────────────┘

Notes:
  - ⚠️ indicates day exceeded 120-minute cap (contest uses capped value)
  - ✅ indicates student met their daily reading goal for their grade level
  - Daily goal for Grade 5: 30 minutes/day
  - Total capped minutes used for contest calculations
  - Total uncapped minutes shows actual reading effort
```

---

## Design Principles

### 1. Consistency with Existing Pages
- Same 6-metric banner order (Campaign Day, Fundraising, Minutes, Sponsors, Avg. Participation, Goal Met)
- Same filter period dropdown (sticky via sessionStorage)
- Same collapsible Data Sources footer
- Same color scheme (team badges, winning highlights)

### 2. Student-Focused Features
**Search & Filters:**
- Name search (find specific students quickly)
- Multi-dropdown filters: Grade, Team, Class
- Threshold filters: Min. minutes, Min. fundraising
- Active/All toggle

**Leaderboards:**
- Top 5 Fundraising leaders
- Top 5 Reading leaders (◐ honors date filter)
- Top consistency leaders (students with perfect/near-perfect participation)

**Detail Table:**
- All 411 students (paginated, 50 per page)
- Sortable columns (click header to sort)
- Columns: Name, Grade, Team, Class, Fundraising, Reading, Sponsors (per student), Participation %
- Gold highlights (⭕) for school-wide top 10
- Export to CSV/Excel

**Quick Stats:**
- Segmented views by Grade, Team, Activity Level, Fundraising Tier
- Provides context without cluttering table

### 3. What's Different from School/Teams/Grade
- **Individual focus** (not aggregated by class/team/grade)
- **Search functionality** (find specific students)
- **Leaderboards** (celebrate top performers)
- **Pagination** (411 students = too many for single screen)
- **Export** (teachers want offline analysis)
- **Per-student sponsor count** (not school-wide total)

---

## Data Sources

### Tables Required:
- **Roster** - student_name, grade_level, team_name, class_name, teacher_name
- **Reader_Cumulative** - donation_amount, sponsors (per student), cumulative_minutes
- **Daily_Logs** - log_date, minutes_read (filtered by date_filter, capped at 120/day)
- **Team_Color_Bonus** - bonus_minutes, bonus_participation_points

### Key Calculations:
- **Fundraising:** `Reader_Cumulative.donation_amount` (NOT filtered by date)
- **Sponsors (per student):** `Reader_Cumulative.sponsors` (individual student sponsor count)
- **Reading minutes:** `SUM(MIN(Daily_Logs.minutes_read, 120))` (◐ honors date filter) - **CAPPED at 120/day**
- **Participation %:** `(days_read / total_days) * 100` (◐ honors date filter)

**DECISION (2025-11-01):** Reading column in Students table MUST use **capped minutes** (max 120/day for official contest totals). This matches other pages (School/Teams/Grade Level) for consistency.

---

## Design Decisions (2025-11-01 Session)

### 1. Banner Consistency (MANDATORY)
**DECISION:** Banner must exactly match other pages (School/Teams/Grade Level)

**Exact Labels & Icons (from School page):**
1. 📅 **Campaign Day** (no filter indicator)
2. 💰 **Fundraising** (no filter indicator)
3. 📚 **Minutes Read** ◐ (filter indicator when date filtered)
4. 🎁 **Sponsors** (no filter indicator)
5. 👥 **Avg. Participation (With Color)** ◐ (filter indicator when date filtered)
6. 🎯 **Goal Met (≥1 Day)** ◐ (filter indicator when date filtered)

**Rules:**
- Use EXACT wording (not "AVG PART" or "GOAL MET")
- Use EXACT icons (📚 for minutes, not 📖)
- Use EXACT formatting (parentheses, capitalization)
- ◐ symbol appears when date filter is active (not "all")

✅ **Documented in:** STUDENTS_PAGE_DESIGN.md line 191-206

---

### 2. Date Filter Behavior
**DECISION:** Date filter is honored throughout ENTIRE page

**Affected Elements:**
- Banner metrics (where ◐ appears)
- Table data (all rows update based on date filter)
- Gold/silver highlighting (leaders recalculated for filtered date range)
- All calculations refresh when filter changes

✅ **Documented in:** STUDENTS_PAGE_DESIGN.md line 208-215

---

### 3. Remove Leaderboards Section
**DECISION:** Do NOT include "Top 5 Leaderboards" section

**Reasoning:** Simplifies page, avoids redundancy with table highlighting

✅ **Documented in:** STUDENTS_PAGE_DESIGN.md line 217-220

---

### 4. Filter Interface Layout
**DECISION:** Two independent filters on one row - Approach A2

**Interface Layout:**
```
┌─────────────────────────────────────────────────────────────────┐
│ [All Grades] [K] [1] [2] [3] [4] [5]      Team: [All Teams ▼]  │
└─────────────────────────────────────────────────────────────────┘
```

**Components:**
- **Grade Filter (buttons):** All Grades, K, 1, 2, 3, 4, 5
- **Team Filter (dropdown):** All Teams, KITSKO, STAUB (positioned on right side of same row)

**Why This Layout:**
- ✅ Two separate filters that can be combined (e.g., "5th Grade + KITSKO")
- ✅ Visual clarity: Dropdown makes it obvious team is a separate dimension
- ✅ Clean single-row layout (not too busy)
- ✅ Consistent with existing grade filter pattern
- **Alternative considered:** Two rows (A1) - user's second choice if A2 doesn't work visually

**Filter Combinations Possible:**
- All Grades + All Teams = 411 students
- All Grades + KITSKO = ~206 students
- 5th Grade + All Teams = ~68 students
- 5th Grade + KITSKO = ~34 students
- K + STAUB = ~34 students
- Etc.

**Behavior:**
- Clicking grade button filters table to that grade (or all)
- Selecting team from dropdown filters to that team (or all)
- **Both filters apply simultaneously** (intersection of grade AND team)
- Gold/silver highlighting recalculates for filtered group
- Export buttons export only visible/filtered students
- **Both filters are sticky** (persist via sessionStorage when navigating between pages)

**Cross-Page Filter Persistence:**
- Students page ↔ Grade Level page: Both grade AND team filters persist
- Date filter persists across ALL pages (already implemented)
- Three independent sticky filters: Date + Grade + Team

✅ **Documented in:** STUDENTS_PAGE_DESIGN.md line 242-281

---

### 4.1. Grade Level Page Gets Same Filter Layout
**DECISION:** YES - Add team filter to Grade Level page for consistency

**Same Interface Layout on Grade Level Page:**
```
┌─────────────────────────────────────────────────────────────────┐
│ [All Grades] [K] [1] [2] [3] [4] [5]      Team: [All Teams ▼]  │
└─────────────────────────────────────────────────────────────────┘
```

**Rationale:**
- ✅ Consistency: Both Students and Grade Level pages work identically
- ✅ Filter stickiness: Grade + Team filters persist when navigating between pages
- ✅ Useful: View grade-level class data for one team (e.g., "5th Grade KITSKO classes")
- ✅ Natural UX: Users expect same filtering capability across similar pages

**Impact on Grade Level Page:**
- Same filter row layout (grade buttons + team dropdown)
- Classes table filters to show only classes with students from selected team
- Banner recalculates for filtered team only
- Gold/silver highlighting recalculates for filtered group
- All existing functionality preserved, just adds team dimension

**Implementation:** Will be done alongside Students page (Phase 3) for consistency

✅ **Documented in:** STUDENTS_PAGE_DESIGN.md line 293-315

---

### 4.2. ALL Data Honors Both Filters
**DECISION:** Every element on the page honors BOTH date filter AND grade/team filter selections

**Affected Elements:**
- **Banner metrics** (6 metrics recalculate based on filtered students + date range)
- **Detail table** (shows only students matching grade/team filter)
- **Gold/silver highlighting** (leaders recalculated for filtered group)
- **Export buttons** (export only visible/filtered data)
- **Row counts** (e.g., "Showing 67 students" if K selected, "Showing 411 students" if All Grades)

**Filter Combination Examples:**
- Date Filter: "October 15" + Grade Filter: "K" + Team Filter: "KITSKO"
  - Shows: Kindergarten KITSKO students only
  - Banner: Cumulative through Oct 15 for those ~33 students
  - Table: Only those students, sorted/highlighted accordingly

- Date Filter: "Full Contest" + Grade Filter: "All Grades" + Team Filter: "All Teams"
  - Shows: All 411 students
  - Banner: Full contest metrics for entire school
  - Table: All students

**Stickiness:**
- Date filter: Persists via `sessionStorage.getItem('readathonDateFilter')`
- Grade filter: Persists via `sessionStorage.getItem('gradeFilter')` (new)
- Team filter: Persists via `sessionStorage.getItem('teamFilter')` (new)
- All persist when navigating between pages

✅ **Documented in:** STUDENTS_PAGE_DESIGN.md line 293-320

---

### 5. Gold/Silver Highlighting Rules
**DECISION:** Same as Grade Level page - dual highlighting system

**Gold Ovals (⭕):**
- School-wide leader (across ALL 411 students, regardless of filter)
- Applies to each metric column (Fundraising, Reading, Sponsors, Participation)
- Multiple students can have gold if tied

**Silver Ovals:**
- Leader within FILTERED group (e.g., Kindergarten if "K" tab selected)
- Only shown when a filter tab is active (not "All")
- Multiple students can have silver if tied

**Priority Rule:**
- Gold overrides silver (if student is both school leader AND grade leader, show GOLD only)

✅ **Documented in:** STUDENTS_PAGE_DESIGN.md line 241-256

---

### 6. Export Format
**DECISION:** Match other pages exactly - "Copy" and "Export CSV" buttons

**Buttons (from Grade Level page):**
```html
<button class="btn btn-sm btn-outline-primary" onclick="copyTable()">
    <i class="bi bi-clipboard"></i> Copy
</button>
<button class="btn btn-sm btn-outline-primary" onclick="exportTableToCSV()">
    <i class="bi bi-download"></i> Export CSV
</button>
```

**Behavior:**
- Copy: Copies visible (filtered) table to clipboard
- Export CSV: Downloads visible (filtered) table as CSV file
- NO Excel export, NO PDF export (not "📥 CSV" or "📊 Excel")

✅ **Documented in:** STUDENTS_PAGE_DESIGN.md line 258-271

---

### 7. Summary Metrics Section
**DECISION:** TBD - User uncertain, could be convinced if compelling

**Current Status:** Banner + Filter Tabs + Table (no summary section)

**Possible Ideas (if we add summary):**
- Top 3 students by fundraising (with photos/badges?)
- Progress toward school-wide goals?
- Participation trends over time?
- Achievement badges (100% participation, goal met every day, etc.)?

**Action:** Defer decision - implement core page first, revisit if compelling use case

✅ **Documented in:** STUDENTS_PAGE_DESIGN.md line 273-284

---

### 8. Table Columns
**DECISION:** TBD - Use Grade Level table columns where applicable

**Principles:**
- Include metrics from Grade Level table that apply to individual students
- EXCLUDE: Color points (not student-level), Number of students (N/A)
- INCLUDE: Most other metrics (fundraising, reading, sponsors, participation, goal met, etc.)

**To Be Defined:**
- Exact column list
- Column order
- Format (single-row or two-row like ASCII prototype?)

**Action:** Define in next session

✅ **Documented in:** STUDENTS_PAGE_DESIGN.md line 286-299

---

### 9. Student Detail View
**DECISION:** Click student row → Open detail view with daily breakdown

**Detail View Content (TBD):**
- Daily reading log (date, minutes read, goal met?)
- Sponsor information (if available)
- Progress charts/graphs?
- Other daily details?

**Action:** Design detail view in separate phase (Phase 2 per CLAUDE.md)

✅ **Documented in:** STUDENTS_PAGE_DESIGN.md line 301-310

---

## Open Questions / User Decisions Needed

1. **Additional Filter Tabs:** Besides grades (K-5) and "By Team", what else?
   - By Class? (specific teacher)
   - By Active Status? (active vs inactive students)
   - By Goal Achievement? (met goal at least once vs never)
   - By Fundraising Tier? ($1000+, $500-999, $100-499, $1-99, $0)

2. **Table Columns - Exact List:** Define specific columns and order
   - From Grade Level table: Fundraising, Reading (capped), Sponsors, Participation %, Goal Met %
   - Additional: Days Active, Avg. Minutes/Day, Total Sponsors, Class, Teacher?

3. **Summary Metrics Section:** Keep page simple, or add compelling summary?
   - If added, what metrics would be most valuable?

4. **Student Detail View Content:** What to show when clicking student row?
   - Daily breakdown (definite)
   - Sponsor list? Progress charts? Achievement badges?

5. **Default Sort Order:** Alphabetical by name, or by fundraising (descending)?

6. **Pagination:** 50 per page? 25? 100? All on one page with scroll?

---

## Implementation Notes

### Phase 1: ASCII → HTML Prototype
- Create `/prototypes/students_tab.html`
- Use fictitious student names (already in sample DB)
- Test search, filters, sorting, pagination
- Get user approval on layout/features

### Phase 2: HTML → Production
- Update `app.py` - add `/students` route
- Update `database.py` - add `get_students_data()` method
- Update `queries.py` - add student queries
- Create `templates/students.html` (Jinja2)
- Update `templates/base.html` - add "Students" to nav menu

### Phase 3: Testing
- Create `test_students_page.py`
- Test all filters, sorting, search
- Test pagination
- Test export functionality
- Verify calculations match other pages

---

## Related Work

### Bug Found During Design:
**School page sponsor metric incorrect:**
- Current: Shows COUNT(students with sponsors) = 7
- Should: Show SUM(all sponsors) = 28
- Status: Being fixed separately before Students page implementation

**Teams page sponsor metric:** ✅ CORRECT (uses SUM)
**Grade Level page sponsor metric:** ✅ CORRECT (uses SUM)

---

## Resume Instructions

When user says **"let's resume our work on the students page"**:

1. Load this document (`docs/STUDENTS_PAGE_DESIGN.md`)
2. Review ASCII prototype above
3. Ask user for feedback on:
   - Table columns
   - Leaderboard categories
   - Quick stats segments
   - Student detail view (click name for more info?)
   - Export format
   - Default sort order
4. Adjust ASCII prototype based on feedback
5. Proceed to HTML prototype phase
6. Follow prototype-to-production workflow from CLAUDE.md

---

### 10. Master Table Columns (FINAL)
**DECISION:** 13 columns approved

**Column List (in order):**
1. Student Name (sortable)
2. Grade Level
3. Team Name (badge)
4. Class Name
5. Teacher Name
6. Fundraising 💰 (total $, NOT filtered by date)
7. Sponsors 🎁 (count per student, NOT filtered by date)
8. Minutes Read - Capped 📚 ◐ (max 120/day, honors date filter)
9. Minutes Read - Uncapped 📚 (actual total, honors date filter)
10. Days Participated ◐ (count, honors date filter)
11. Participation % ◐ (days participated / possible days, honors date filter)
12. Days Met Goal ◐ (count of days student met grade-level goal, honors date filter)
13. Goal Met % ◐ (percentage of days met goal, honors date filter)

**Key Notes:**
- Click any row → opens detail view with daily breakdown
- All columns sortable (click header)
- Gold ovals (⭕) = school-wide winners
- Silver ovals (🥈) = grade/team winners when filters active
- ◐ symbol = honors date filter
- Minutes capped vs uncapped shows contest value vs actual effort

✅ **Documented in:** STUDENTS_PAGE_DESIGN.md line 412-437

---

### 11. Detail View Content (FINAL)
**DECISION:** Daily breakdown with clear explanatory notes

**Content Sections:**
1. **Student Info Header:** Name, Grade, Team, Class, Teacher
2. **Summary Metrics:** 6 metrics with gold/silver highlights
   - Fundraising, Sponsors, Minutes Capped, Minutes Uncapped, Participation, Goal Met
3. **Daily Reading Log Table:**
   - Day # + Date
   - Minutes Read (Actual/Uncapped)
   - Minutes Capped (Max 120)
   - Status indicators:
     - ⚠️ = Exceeded 120-minute cap
     - ✅ = Met daily goal for grade level
4. **Totals Row:** Shows cumulative capped vs uncapped, participation stats
5. **Clear Explanatory Notes:**
   - Legend explaining all symbols (⭕, 🥈, ⚠️, ✅, ◐)
   - Data source notes
   - Contest rules (why cap matters)
   - Grade-level daily goals
   - Any other context needed for understanding

**User Emphasis:** "Show clear notes explaining symbols and needed data notes for anything on this page that warrants it"

✅ **Documented in:** STUDENTS_PAGE_DESIGN.md line 439-464

---

---

### 12. HTML Prototype Refinements (Session 2025-11-01)
**DECISION:** Multiple design refinements based on user feedback on HTML prototype

**Initial HTML Prototype Created:**
- File: `/prototypes/students_tab.html`
- 20 fictitious students (sample data)
- All 13 columns implemented
- Grade and team filters functional
- Student detail modal working

**User Feedback & Fixes Applied:**

**1. Remove Pagination - Show All Students**
- **Issue:** Initial prototype had "Showing 10 of 20" with pagination
- **Fix:** Removed pagination, show all students in table
- **Rationale:** Users should see all students at once (411 in production)

**2. Filter Button Labels Must Match Grade Level Page**
- **Issue:** Initial labels were "K", "1", "2", etc.
- **Fix:** Updated to "Kindergarten", "Grade 1", "Grade 2", "Grade 3", "Grade 4", "Grade 5"
- **Reference:** Matched exact labels from `templates/grade_level.html`
- **Consistency:** Same labels across Grade Level and Students pages

**3. Header Layout Consistency**
- **Issue:** Filter period and Data Info button not positioned correctly
- **Fix:** Updated header structure:
  - Page title (👨‍🎓 Students) on LEFT
  - Filter period selector (📅 Filter Period:) in CENTER
  - Data Info button (🔘 Data Info) on RIGHT
- **Reference:** Matched exact layout from Grade Level page

**4. Team Badge Styling - More Oval/Pill Shape**
- **Issue:** Team badges weren't oval enough (border-radius: 0.8rem)
- **Fix:** Increased to `border-radius: 1.5rem` with adjusted padding
- **CSS:**
  ```css
  .team-badge {
      padding: 0.3rem 0.9rem;
      border-radius: 1.5rem;
  }
  ```
- **Result:** Proper oval/pill shape matching other pages

**5. Legend & Data Notes Section - Collapsible & Combined**
- **Issue:** Two separate sections (legend box + student count section)
- **User Request:** "Combine legend and student count info, make it collapsible (collapsed by default)"
- **Fix:** Created single `.legend-section` that combines:
  - 📊 Student Count (total, visible, active filters)
  - 📋 Legend & Data Notes (symbols, explanations)
- **Behavior:** Click to expand/collapse, default state = collapsed
- **JavaScript:** `toggleLegend()` function
- **Rationale:** Cleaner interface, info available but not cluttering main view

**6. Silver Highlighting for Filtered Groups**
- **Issue:** No silver highlighting when filters active
- **Fix:** Implemented `updateSilverHighlighting()` function
- **Logic:**
  - When "All Grades" + "All Teams": No silver (only gold)
  - When filter active: Calculate max values for visible rows
  - Skip cells with gold highlighting (gold overrides silver)
  - Apply silver ovals (🥈) to filtered group winners
- **Columns Highlighted:** Fundraising, Sponsors, Minutes Capped, Minutes Uncapped, Days Participated, Participation %, Days Met Goal, Goal Met %

**7. Banner Update Pattern for Production**
- **Note:** Prototype shows static banner values
- **Production Behavior:** Banner metrics MUST recalculate based on:
  - Date filter (◐ metrics only)
  - Grade filter (all 6 metrics)
  - Team filter (all 6 metrics)
- **Pattern Implemented:** `updateBanner()` function updates subtitles to show "Filtered: [Grade/Team]"
- **User Confirmed:** "This is OK for prototype, production will do full recalculation"

**8. Data Sources Footer**
- **Implemented:** Collapsible footer matching School/Teams/Grade Level pages
- **Content:** Data source notes, last updated timestamps
- **Behavior:** Click to expand, shows database tables used

✅ **Documented in:** STUDENTS_PAGE_DESIGN.md line 629-735
✅ **HTML Prototype:** `/prototypes/students_tab.html` (ready for review)

---

## Status History

- **2025-10-31 10:31** - ASCII prototype v1 complete
- **2025-10-31 10:31** - Paused for user review of existing pages
- **2025-10-31 10:31** - Discovered School page sponsor bug, fixing separately
- **2025-11-01** - v2026.4.0 released (Development Process Improvements, Testing Discipline)
- **2025-11-01** - User reviewed ASCII prototype, provided detailed feedback
- **2025-11-01** - Documented 11 core design decisions:
  1. Banner consistency (exact labels/icons from School page)
  2. Date filter honored throughout page
  3. Remove leaderboards section
  4. Filter tabs: All Grades → By Team → K, 1, 2, 3, 4, 5
  5. Gold/silver highlighting (school-wide vs filtered group)
  6. Export format (Copy + Export CSV)
  7. Summary metrics (defer - keep simple for v1)
  8. Table columns (TBD - use Grade Level columns where applicable)
  9. Student detail view (click row → daily breakdown)
  10. **Add Team filter to Grade Level page?** (recommended YES for consistency)
  11. **ALL data honors BOTH filters** (date + grade/team, sticky across pages)
- **2025-11-01** - **FINAL DECISION:** Filter interface = Approach A2 (one row: grade buttons + team dropdown on right)
  - User chose A2, with A1 (two rows) as backup if A2 doesn't look good
  - Same layout will be added to Grade Level page for consistency
  - Three independent sticky filters: Date + Grade + Team (all persist across pages)
- **2025-11-01** - Master table columns finalized (13 columns)
- **2025-11-01** - Detail view content finalized (daily breakdown + clear explanatory notes)
- **2025-11-01** - ASCII prototypes approved for both master and detail views
- **2025-11-01** - HTML prototype created: `/prototypes/students_tab.html`
- **2025-11-01** - HTML prototype refinements applied:
  - Filter labels updated ("Kindergarten", "Grade 1", etc.)
  - Header layout fixed (title left, filter center, data info right)
  - Team badges made more oval (1.5rem border-radius)
  - Legend section made collapsible and combined with student count
  - Silver highlighting implemented for filtered groups
  - Banner update pattern documented for production
  - All students shown (no pagination)
- **2025-11-01 Evening** - HTML prototype approved, ready for production implementation
- **2025-11-01 Evening** - Production implementation plan created (see below)
- **Next:** Follow production implementation plan (Phase 1: Database queries)

---

# PRODUCTION IMPLEMENTATION PLAN

**Status:** Ready to begin
**Estimated Effort:** 3-4 hours
**Testing Required:** YES - Full test suite before commit

---

## Phase 1: Database Queries (queries.py)

### Query 1: Get All Students Data (Master Table)
**Function:** `get_students_master_data(db_path, date_filter, grade_filter, team_filter)`

**Returns:** List of dicts with 13 columns per student

**SQL Requirements:**
```sql
-- Join tables: Roster, Reader_Cumulative, Daily_Logs
-- Must handle:
--   - Date filter (date_filter = 'all' or 'YYYY-MM-DD' or date range)
--   - Grade filter (grade_filter = 'all' or 'K', '1', '2', '3', '4', '5')
--   - Team filter (team_filter = 'all' or team name)

SELECT
    r.student_name,
    r.grade_level,
    r.team_name,
    r.class_name,
    r.teacher_name,
    rc.donation_amount AS fundraising,
    rc.sponsor_count AS sponsors,
    -- Minutes capped (sum of min(120, daily_logs.minutes) for date range)
    SUM(CASE WHEN dl.minutes_read > 120 THEN 120 ELSE dl.minutes_read END) AS minutes_capped,
    -- Minutes uncapped (sum of actual minutes for date range)
    SUM(dl.minutes_read) AS minutes_uncapped,
    -- Days participated (count of days with >0 minutes in date range)
    COUNT(CASE WHEN dl.minutes_read > 0 THEN 1 END) AS days_participated,
    -- Participation % (days participated / total days in range * 100)
    -- Days met goal (count of days where minutes >= grade goal)
    -- Goal met % (days met goal / days participated * 100)
FROM Roster r
LEFT JOIN Reader_Cumulative rc ON r.student_name = rc.student_name
LEFT JOIN Daily_Logs dl ON r.student_name = dl.student_name
    AND dl.log_date BETWEEN ? AND ?  -- Date filter parameters
WHERE
    (? = 'all' OR r.grade_level = ?)  -- Grade filter
    AND (? = 'all' OR r.team_name = ?)  -- Team filter
GROUP BY r.student_name, r.grade_level, r.team_name, r.class_name, r.teacher_name,
         rc.donation_amount, rc.sponsor_count
ORDER BY r.student_name
```

**Data Transformations:**
- Convert minutes to hours where appropriate
- Calculate participation % = (days_participated / total_days_in_range) * 100
- Calculate goal_met % = (days_met_goal / days_participated) * 100
- Format currency: $X,XXX (no decimals)
- Format percentages: X.X% (1 decimal)

**Edge Cases:**
- Students with no Daily_Logs entries (show 0s)
- Students with no sponsors (show 0)
- Students with $0 fundraising (show $0)
- Date filter = 'all' (use full contest period: Oct 10-19)

---

### Query 2: Get Student Detail (Daily Breakdown)
**Function:** `get_student_detail(db_path, student_name, date_filter)`

**Returns:** Dict with student info + list of daily entries

**SQL Requirements:**
```sql
-- Student summary metrics
SELECT
    r.student_name,
    r.grade_level,
    r.team_name,
    r.class_name,
    r.teacher_name,
    rc.donation_amount,
    rc.sponsor_count,
    SUM(CASE WHEN dl.minutes_read > 120 THEN 120 ELSE dl.minutes_read END) AS total_capped,
    SUM(dl.minutes_read) AS total_uncapped,
    COUNT(CASE WHEN dl.minutes_read > 0 THEN 1 END) AS days_participated,
    COUNT(CASE WHEN dl.minutes_read >= gr.daily_goal THEN 1 END) AS days_met_goal
FROM Roster r
LEFT JOIN Reader_Cumulative rc ON r.student_name = rc.student_name
LEFT JOIN Daily_Logs dl ON r.student_name = dl.student_name
    AND dl.log_date BETWEEN ? AND ?
LEFT JOIN Grade_Rules gr ON r.grade_level = gr.grade_level
WHERE r.student_name = ?
GROUP BY r.student_name, r.grade_level, r.team_name, r.class_name, r.teacher_name,
         rc.donation_amount, rc.sponsor_count

-- Daily log entries
SELECT
    dl.log_date,
    dl.minutes_read AS actual_minutes,
    CASE WHEN dl.minutes_read > 120 THEN 120 ELSE dl.minutes_read END AS capped_minutes,
    CASE WHEN dl.minutes_read > 120 THEN 1 ELSE 0 END AS exceeded_cap,
    CASE WHEN dl.minutes_read >= gr.daily_goal THEN 1 ELSE 0 END AS met_goal,
    gr.daily_goal AS grade_goal
FROM Daily_Logs dl
JOIN Roster r ON dl.student_name = r.student_name
JOIN Grade_Rules gr ON r.grade_level = gr.grade_level
WHERE dl.student_name = ?
    AND dl.log_date BETWEEN ? AND ?
ORDER BY dl.log_date
```

---

### Query 3: Get School-Wide Winners (Gold Highlights)
**Function:** `get_school_winners(db_path, date_filter)`

**Returns:** Dict with winner student names per metric

**SQL Requirements:**
```sql
-- Find max values across ALL 411 students for each metric
-- Return student names who have those max values
-- Metrics: Fundraising, Sponsors, Minutes Capped, Minutes Uncapped,
--          Days Participated, Participation %, Days Met Goal, Goal Met %

-- Example for Fundraising:
WITH max_fundraising AS (
    SELECT MAX(donation_amount) AS max_val
    FROM Reader_Cumulative
)
SELECT student_name
FROM Reader_Cumulative
WHERE donation_amount = (SELECT max_val FROM max_fundraising)

-- Repeat for each metric
```

**Returns:**
```python
{
    'fundraising': ['Sarah Chen'],  # Student(s) with max fundraising
    'sponsors': ['Sarah Chen'],
    'minutes_capped': ['Sarah Chen'],
    'minutes_uncapped': ['David Park'],
    'days_participated': ['Sarah Chen', 'David Park'],  # Multiple if tied
    'participation_pct': ['Sarah Chen', 'David Park'],
    'days_met_goal': ['Sarah Chen'],
    'goal_met_pct': ['Sarah Chen', 'Emma Wilson']
}
```

---

### Query 4: Get Banner Metrics (for Students Page)
**Function:** `get_students_banner_metrics(db_path, date_filter, grade_filter, team_filter)`

**Returns:** Dict with 6 banner metrics (filtered by grade/team)

**SQL Requirements:**
```sql
-- Same 6 metrics as School/Teams/Grade pages, but filtered by grade/team selections
-- 1. Campaign Day (no filtering - always full contest status)
-- 2. Fundraising (SUM of filtered students, no date filter)
-- 3. Minutes Read (SUM of capped minutes for filtered students + date range)
-- 4. Sponsors (SUM of sponsors for filtered students, no date filter)
-- 5. Avg. Participation (With Color) - filtered students + date range
-- 6. Goal Met (≥1 Day) - filtered students + date range

-- Must calculate:
--   - Total students in filtered group
--   - Top student/class for each metric (subtitle)
--   - Percentages where applicable
```

**Key Rules:**
- Campaign Day: Always shows full contest status (ignore filters)
- Fundraising: Total for filtered students (no date filter)
- Minutes: Total capped minutes for filtered students (honors date filter)
- Sponsors: Total sponsors for filtered students (no date filter)
- Avg. Participation: Can exceed 100% if color bonus (honors date filter)
- Goal Met: Students who met goal ≥1 day (honors date filter)

---

### Query 5: Get Filtered Winners (Silver Highlights)
**Function:** `get_filtered_winners(db_path, date_filter, grade_filter, team_filter)`

**Returns:** Dict with winner student names per metric (within filtered group)

**SQL Requirements:**
- Same logic as Query 3, but with WHERE clause for grade/team filters
- Only used when grade_filter != 'all' OR team_filter != 'all'
- Returns silver highlight winners for filtered group

---

## Phase 2: Flask Route (app.py)

### Route: `/students`
**Methods:** GET
**Template:** `templates/students.html`

**Implementation:**
```python
@app.route('/students')
def students_page():
    # Get environment (sample or prod)
    db_path = get_db_path()

    # Get filters from query params (with sticky defaults from session)
    date_filter = request.args.get('date', session.get('date_filter', 'all'))
    grade_filter = request.args.get('grade', session.get('grade_filter', 'all'))
    team_filter = request.args.get('team', session.get('team_filter', 'all'))

    # Save to session for stickiness
    session['date_filter'] = date_filter
    session['grade_filter'] = grade_filter
    session['team_filter'] = team_filter

    # Get database instance
    db = ReadathonDB(db_path)

    # Get all data
    students_data = db.get_students_master_data(date_filter, grade_filter, team_filter)
    banner_metrics = db.get_students_banner_metrics(date_filter, grade_filter, team_filter)
    school_winners = db.get_school_winners(date_filter)
    filtered_winners = db.get_filtered_winners(date_filter, grade_filter, team_filter) if (grade_filter != 'all' or team_filter != 'all') else {}

    # Get team names for dropdown
    teams = db.get_team_names()

    # Get date options for filter dropdown
    date_options = db.get_contest_dates()

    return render_template('students.html',
        students=students_data,
        banner=banner_metrics,
        school_winners=school_winners,
        filtered_winners=filtered_winners,
        teams=teams,
        date_options=date_options,
        date_filter=date_filter,
        grade_filter=grade_filter,
        team_filter=team_filter,
        environment=session.get('environment', 'sample')
    )
```

**Error Handling:**
- Try/except around database calls
- Return user-friendly error page if database error
- Log errors for debugging

---

### Route: `/student/<student_name>`
**Methods:** GET
**Returns:** JSON (for AJAX modal)

**Implementation:**
```python
@app.route('/student/<student_name>')
def student_detail(student_name):
    db_path = get_db_path()
    date_filter = request.args.get('date', session.get('date_filter', 'all'))

    db = ReadathonDB(db_path)
    detail_data = db.get_student_detail(student_name, date_filter)
    school_winners = db.get_school_winners(date_filter)

    return jsonify({
        'student': detail_data,
        'school_winners': school_winners
    })
```

---

## Phase 3: Database Methods (database.py)

### Add to ReadathonDB class:
```python
def get_students_master_data(self, date_filter='all', grade_filter='all', team_filter='all'):
    """Get all students data for master table (13 columns)"""
    query = queries.STUDENTS_MASTER_QUERY
    params = self._build_filter_params(date_filter, grade_filter, team_filter)
    results = self._execute_query(query, params)
    return self._format_students_data(results)

def get_student_detail(self, student_name, date_filter='all'):
    """Get individual student detail with daily breakdown"""
    summary_query = queries.STUDENT_DETAIL_SUMMARY_QUERY
    daily_query = queries.STUDENT_DETAIL_DAILY_QUERY
    # ... implementation

def get_students_banner_metrics(self, date_filter='all', grade_filter='all', team_filter='all'):
    """Get 6 banner metrics filtered by grade/team"""
    # Similar to get_school_metrics but with grade/team filtering
    # ... implementation

def get_school_winners(self, date_filter='all'):
    """Get school-wide winners for gold highlighting"""
    # ... implementation

def get_filtered_winners(self, date_filter='all', grade_filter='all', team_filter='all'):
    """Get filtered group winners for silver highlighting"""
    # ... implementation

def get_team_names(self):
    """Get list of unique team names for dropdown"""
    query = "SELECT DISTINCT team_name FROM Roster ORDER BY team_name"
    results = self._execute_query(query)
    return [row[0] for row in results]
```

---

## Phase 4: Template (templates/students.html)

### Implementation Steps:
1. **Copy prototype HTML structure** from `/prototypes/students_tab.html`
2. **Replace static data with Jinja2 templates:**
   - Banner metrics: `{{ banner.fundraising }}`, etc.
   - Student table rows: `{% for student in students %}`
   - Filter dropdowns: `{% for team in teams %}`
   - Gold/silver highlighting: `{% if student.name in school_winners.fundraising %}`
3. **Add sessionStorage JavaScript:**
   - Restore filters on page load
   - Save filters on change
4. **Add AJAX for student detail modal:**
   - Click row → fetch `/student/<name>` → populate modal
5. **Match existing page patterns:**
   - Same header/footer as grade_level.html
   - Same CSS classes from UI_PATTERNS.md
   - Same filter restoration from School/Teams/Grade pages

### Key Jinja2 Patterns:
```jinja2
<!-- Banner -->
<div class="headline-value">{{ banner.fundraising | format_currency }}</div>

<!-- Student table -->
{% for student in students %}
<tr onclick="openStudentDetail('{{ student.name }}')">
    <td>{{ student.name }}</td>
    <td>{{ student.grade }}</td>
    <td><span class="team-badge team-badge-{{ student.team|lower }}">{{ student.team }}</span></td>
    <td class="text-end">
        {% if student.name in school_winners.fundraising %}
        <span class="winning-value winning-value-school">{{ student.fundraising | format_currency }}</span>
        {% elif student.name in filtered_winners.fundraising %}
        <span class="winning-value winning-value-grade">{{ student.fundraising | format_currency }}</span>
        {% else %}
        {{ student.fundraising | format_currency }}
        {% endif %}
    </td>
    <!-- More columns... -->
</tr>
{% endfor %}

<!-- Team filter dropdown -->
<select id="teamFilter" onchange="applyFilters()">
    <option value="all" {% if team_filter == 'all' %}selected{% endif %}>All Teams</option>
    {% for team in teams %}
    <option value="{{ team }}" {% if team_filter == team %}selected{% endif %}>{{ team }}</option>
    {% endfor %}
</select>
```

---

## Phase 5: Update Navigation (templates/base.html)

### Add Students Link to Nav:
```html
<li class="nav-item">
    <a class="nav-link {% if request.endpoint == 'students_page' %}active{% endif %}"
       href="{{ url_for('students_page') }}">
        👨‍🎓 Students
    </a>
</li>
```

**Position:** After "Grade Level" link, before "Reports" dropdown

---

## Phase 6: Testing (test_students_page.py)

### Test Suite Structure:
```python
import pytest
from app import app
from database import ReadathonDB

@pytest.fixture
def client():
    """Create test client for Students page"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        with app.app_context():
            with client.session_transaction() as sess:
                sess['environment'] = 'sample'
        yield client

@pytest.fixture
def sample_db():
    """Get sample database instance"""
    return ReadathonDB('readathon_sample.db')
```

### Mandatory Tests (from RULES.md):

#### 1. Page Load Tests
```python
def test_page_loads_successfully(client):
    """Verify page loads with HTTP 200"""
    response = client.get('/students')
    assert response.status_code == 200
    assert b'Read-a-Thon System' in response.data
    assert b'Students' in response.data

def test_no_error_messages(client):
    """Scan for error patterns"""
    response = client.get('/students')
    html = response.data.decode('utf-8')
    error_patterns = ['Error:', 'Exception:', 'Traceback', 'error occurred']
    html_lower = html.lower()
    for pattern in error_patterns:
        assert pattern.lower() not in html_lower, f"Found error pattern: {pattern}"
```

#### 2. Data Format Tests
```python
def test_percentage_formats(client):
    """Validate all percentages are properly formatted"""
    response = client.get('/students')
    html = response.data.decode('utf-8')
    import re
    percentages = re.findall(r'(\d+\.?\d*)%', html)
    assert len(percentages) > 0, "No percentages found on page"
    for pct in percentages:
        value = float(pct)
        assert 0 <= value <= 200, f"Percentage out of range: {pct}%"  # Can exceed 100% with color bonus

def test_currency_formats(client):
    """Validate all dollar amounts are properly formatted"""
    response = client.get('/students')
    html = response.data.decode('utf-8')
    import re
    currencies = re.findall(r'\$[\d,]+', html)
    assert len(currencies) > 0, "No currency values found on page"
    for curr in currencies:
        value_str = curr.replace('$', '').replace(',', '')
        value = int(value_str)
        assert value >= 0, f"Negative currency value: {curr}"
```

#### 3. Sample Data Integrity Tests
```python
def test_sample_data_integrity(client, sample_db):
    """Verify displayed values match database calculations"""
    response = client.get('/students')
    html = response.data.decode('utf-8')

    # Get expected values from database
    students = sample_db.get_students_master_data('all', 'all', 'all')

    # Verify student count
    assert len(students) > 0, "No students returned from database"

    # Verify at least one student appears in HTML
    assert students[0]['student_name'] in html, "First student not found in HTML"

    # Verify fundraising totals are present
    total_fundraising = sum(s['fundraising'] for s in students)
    # Check banner shows correct total (formatted as $X,XXX)
    # ... more specific assertions

def test_banner_metrics_correct(client, sample_db):
    """Verify banner shows correct 6 metrics"""
    response = client.get('/students')
    html = response.data.decode('utf-8')

    # Verify all 6 metrics are present
    assert 'Campaign Day' in html
    assert 'Fundraising' in html
    assert 'Minutes Read' in html
    assert 'Sponsors' in html
    assert 'Avg. Participation' in html
    assert 'Goal Met' in html

    # Verify ◐ symbols appear on filtered metrics
    assert '◐' in html

def test_all_13_columns_present(client):
    """Verify table has all 13 required columns"""
    response = client.get('/students')
    html = response.data.decode('utf-8')

    required_headers = [
        'Student Name', 'Grade', 'Team', 'Class', 'Teacher',
        'Fundraising', 'Sponsors', 'Minutes Capped', 'Minutes Uncapped',
        'Days Partic', 'Partic. %', 'Days Goal', 'Goal %'
    ]

    for header in required_headers:
        assert header in html, f"Missing column header: {header}"
```

#### 4. UI Element Tests
```python
def test_team_badges_present(client):
    """Verify team badges appear with correct styling"""
    response = client.get('/students')
    html = response.data.decode('utf-8')
    assert 'team-badge' in html, "No team badges found"
    assert 'team-badge-team1' in html or 'team-badge-kitsko' in html

def test_winning_value_highlights(client):
    """Verify gold/silver ovals appear"""
    response = client.get('/students')
    html = response.data.decode('utf-8')
    assert 'winning-value' in html, "No winning value highlights found"

def test_headline_banner(client):
    """Verify banner structure is present"""
    response = client.get('/students')
    html = response.data.decode('utf-8')
    assert 'headline-banner' in html or 'headline-metric' in html

def test_filter_buttons_present(client):
    """Verify grade filter buttons are present"""
    response = client.get('/students')
    html = response.data.decode('utf-8')

    assert 'All Grades' in html
    assert 'Kindergarten' in html
    assert 'Grade 1' in html
    assert 'Grade 5' in html

def test_team_filter_dropdown_present(client):
    """Verify team dropdown is present"""
    response = client.get('/students')
    html = response.data.decode('utf-8')

    assert 'teamFilter' in html or 'Team:' in html
    assert 'All Teams' in html

def test_legend_section_present(client):
    """Verify legend section exists"""
    response = client.get('/students')
    html = response.data.decode('utf-8')

    assert 'Legend' in html or 'Data Notes' in html
```

#### 5. Filter Tests
```python
def test_grade_filter_works(client, sample_db):
    """Verify grade filter returns only selected grade"""
    response = client.get('/students?grade=K')
    html = response.data.decode('utf-8')

    # Get expected K students from database
    k_students = sample_db.get_students_master_data('all', 'K', 'all')
    assert len(k_students) > 0, "No kindergarten students in database"

    # Verify K students appear
    for student in k_students[:3]:  # Check first 3
        assert student['student_name'] in html

def test_team_filter_works(client, sample_db):
    """Verify team filter returns only selected team"""
    teams = sample_db.get_team_names()
    if len(teams) > 0:
        response = client.get(f'/students?team={teams[0]}')
        assert response.status_code == 200

def test_date_filter_works(client):
    """Verify date filter affects minutes/participation metrics"""
    response = client.get('/students?date=2025-10-15')
    assert response.status_code == 200

    # Verify ◐ symbol appears (indicates filtering active)
    html = response.data.decode('utf-8')
    assert '◐' in html

def test_combined_filters_work(client):
    """Verify grade + team + date filters work together"""
    response = client.get('/students?grade=5&team=team1&date=2025-10-15')
    assert response.status_code == 200
```

#### 6. Student Detail Modal Tests
```python
def test_student_detail_route_works(client, sample_db):
    """Verify student detail route returns JSON"""
    students = sample_db.get_students_master_data('all', 'all', 'all')
    if len(students) > 0:
        student_name = students[0]['student_name']
        response = client.get(f'/student/{student_name}')
        assert response.status_code == 200
        assert response.content_type == 'application/json'

        data = response.get_json()
        assert 'student' in data
        assert 'school_winners' in data

def test_student_detail_has_daily_breakdown(client, sample_db):
    """Verify student detail includes daily log entries"""
    students = sample_db.get_students_master_data('all', 'all', 'all')
    if len(students) > 0:
        student_name = students[0]['student_name']
        response = client.get(f'/student/{student_name}')
        data = response.get_json()

        assert 'daily_logs' in data['student']
        # Should have entries for contest period
```

#### 7. Export Function Tests
```python
def test_copy_button_present(client):
    """Verify copy button exists"""
    response = client.get('/students')
    html = response.data.decode('utf-8')
    assert 'Copy' in html or 'clipboard' in html

def test_export_csv_button_present(client):
    """Verify export CSV button exists"""
    response = client.get('/students')
    html = response.data.decode('utf-8')
    assert 'Export CSV' in html or 'download' in html
```

#### 8. Regression Tests
```python
def test_no_pagination_controls(client):
    """Verify no pagination (show all students)"""
    response = client.get('/students')
    html = response.data.decode('utf-8')

    # Should NOT have pagination controls
    assert 'Previous' not in html or 'pagination' not in html.lower()

def test_banner_honors_filters(client):
    """Verify banner recalculates when filters change"""
    # Get banner with all students
    response_all = client.get('/students?grade=all&team=all')
    html_all = response_all.data.decode('utf-8')

    # Get banner with K students only
    response_k = client.get('/students?grade=K&team=all')
    html_k = response_k.data.decode('utf-8')

    # Banner values should be different (filtered group has fewer students)
    assert html_all != html_k

def test_team_badge_styling(client):
    """Verify team badges use proper oval styling"""
    response = client.get('/students')
    html = response.data.decode('utf-8')

    # Check for border-radius in style or CSS class
    assert 'team-badge' in html
    # In production, verify CSS has border-radius: 1.5rem
```

### Test Execution:
```bash
# Run Students page tests only
pytest test_students_page.py -v

# Run all tests (including regression)
pytest -v

# Run with coverage
pytest test_students_page.py --cov=app --cov=database --cov-report=html

# MANDATORY: All tests must pass before commit
```

---

## Phase 7: Pre-Commit Checklist

**BEFORE creating commit, verify ALL of these:**

- [ ] ✅ All queries in `queries.py` tested with sample database
- [ ] ✅ All database methods in `database.py` tested and working
- [ ] ✅ Flask route `/students` loads successfully
- [ ] ✅ Flask route `/student/<name>` returns correct JSON
- [ ] ✅ Template renders without errors
- [ ] ✅ All 13 columns display correct data
- [ ] ✅ Grade filter works (buttons filter table)
- [ ] ✅ Team filter works (dropdown filters table)
- [ ] ✅ Date filter works (affects ◐ metrics)
- [ ] ✅ Combined filters work (grade + team + date)
- [ ] ✅ Gold highlighting appears for school winners
- [ ] ✅ Silver highlighting appears when filters active
- [ ] ✅ Banner shows correct 6 metrics
- [ ] ✅ Banner recalculates when filters change
- [ ] ✅ Team badges use proper oval styling (1.5rem border-radius)
- [ ] ✅ Legend section is collapsible
- [ ] ✅ Student detail modal opens on click
- [ ] ✅ Daily breakdown shows correct data
- [ ] ✅ Copy and Export CSV buttons work
- [ ] ✅ Filter stickiness works (sessionStorage)
- [ ] ✅ Navigation link added to base.html
- [ ] ✅ All 40+ tests pass (pytest test_students_page.py -v)
- [ ] ✅ No error messages on page
- [ ] ✅ No console errors in browser
- [ ] ✅ Page matches prototype visually
- [ ] ✅ Security review: No SQL injection vulnerabilities
- [ ] ✅ Security review: No XSS vulnerabilities

**Only after ALL boxes checked:**
- Create commit with descriptive message
- Include testing summary in commit message
- Update STUDENTS_PAGE_DESIGN.md status to "Production Complete"

---

## Phase 8: Follow-Up Work (Optional/Future)

### Enhancement Ideas:
1. **Add Team Filter to Grade Level Page** (Decision #4.1)
   - Same filter layout as Students page
   - Filter stickiness across both pages
   - Consistent UX

2. **Export Enhancements**
   - Excel format option?
   - PDF report option?
   - Custom column selection?

3. **Student Detail Enhancements**
   - Progress charts/graphs
   - Comparison to grade average
   - Achievement badges
   - Sponsor list (if available)

4. **Performance Optimization**
   - Cache banner metrics
   - Pagination for very large student lists (>500)
   - Lazy load student detail modal

5. **Additional Filters**
   - By Class (teacher name)
   - By Active Status (has read >0 minutes)
   - By Fundraising Tier ($0, $1-99, $100-499, $500+)
   - By Goal Achievement (met goal ≥1 day, met all days, never met)

---

## Key Success Criteria

**Students page is "done" when:**

1. ✅ Page loads successfully in both sample and prod databases
2. ✅ All 13 columns display accurate data
3. ✅ All 3 filters work (date, grade, team) independently and combined
4. ✅ Banner shows correct 6 metrics and recalculates with filters
5. ✅ Gold/silver highlighting follows RULES.md exactly
6. ✅ Team badges use proper oval styling (matches Grade Level page)
7. ✅ Student detail modal shows daily breakdown
8. ✅ All 40+ automated tests pass
9. ✅ Page matches approved HTML prototype visually
10. ✅ No security vulnerabilities (SQL injection, XSS)
11. ✅ Filters persist via sessionStorage (sticky across pages)
12. ✅ Legend section is collapsible (collapsed by default)
13. ✅ Copy and Export CSV work for filtered data
14. ✅ User can successfully use page without errors or confusion

---

## Estimated Timeline

**Assuming 3-4 hour work session:**

- Phase 1 (Queries): 60-90 minutes
- Phase 2 (Flask routes): 30 minutes
- Phase 3 (Database methods): 30-45 minutes
- Phase 4 (Template): 45-60 minutes
- Phase 5 (Navigation): 5 minutes
- Phase 6 (Testing): 60-90 minutes
- Phase 7 (Pre-commit checklist): 15-30 minutes

**Total: 3.5-5.5 hours**

Recommend breaking into 2 sessions if needed:
- **Session 1:** Phases 1-3 (backend complete)
- **Session 2:** Phases 4-7 (frontend + testing complete)
