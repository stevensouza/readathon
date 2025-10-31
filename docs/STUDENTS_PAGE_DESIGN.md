# Students Page Design - Work in Progress

**Status:** ASCII prototype complete, awaiting user review of existing pages before implementation
**Created:** 2025-10-31
**Resume Keyword:** "let's resume our work on the students page"

---

## Context

User requested design for a new **Students** tab that would show individual student-level data across all 411 students. After reviewing project standards (RULES.md, UI_PATTERNS.md, existing School/Teams/Grade Level pages), I designed an ASCII prototype.

**Decision:** User wants to review data on existing pages (School, Teams, Grade Level) first before finalizing Students page design. Also discovered a sponsor metric bug on School page that needs fixing first.

---

## ASCII Prototype (v1)

```
═══════════════════════════════════════════════════════════════════════════════════
                          👨‍🎓 STUDENTS OVERVIEW
═══════════════════════════════════════════════════════════════════════════════════

┌─────────────────────────────────────────────────────────────────────────────────┐
│  📅 Filter Period: [Dropdown: Full Contest (Oct 10 - Oct 19) ▼]  (auto-updates) │
│                                                         [ℹ️ Data Info]            │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────┐
│  HEADLINE BANNER (6 Metrics - Matches School/Teams/Grade Level)                 │
├─────────┬─────────┬─────────┬─────────┬─────────────────┬──────────────────────┤
│ 📅 DAY  │ 💰 FUND │ 📚 MIN  │ 🎁 SPON │ 👥 AVG PART ◐   │ 🎯 GOAL MET ◐        │
│ Day 3   │ $45,678 │ 8,234   │ 28      │ 78.5%           │ 82.0%                │
│ of 10   │ 325/411 │ hours   │ sponsors│ 323/411 active  │ 337/411 students     │
│ Oct 12  │ (79.1%) │ ◐       │ 7/411   │ ◐               │ ◐                    │
│         │         │         │ (17.0%) │                 │                      │
└─────────┴─────────┴─────────┴─────────┴─────────────────┴──────────────────────┘

NOTE: Sponsor count changed to match correct calculation (SUM of all sponsors, not student count)

┌─────────────────────────────────────────────────────────────────────────────────┐
│  🔍 SEARCH & FILTERS                                                            │
├─────────────────────────────────────────────────────────────────────────────────┤
│  Search: [____________] 🔍    Grade: [All ▼]    Team: [All ▼]    Class: [All ▼]│
│  Min. Minutes: [___]    Min. Fundraising: [$___]    Show: [⚪ All ⚫ Active Only]│
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────┐
│  📊 LEADERBOARDS (Top 5 in Each Category)                                      │
├───────────────────────┬───────────────────────┬───────────────────────────────┤
│ 💰 FUNDRAISING LEADERS│ 📚 READING LEADERS ◐  │ 🎯 CONSISTENCY LEADERS ◐      │
│                       │                       │                               │
│ 1. Sarah Chen         │ 1. Marcus Williams    │ 1. Emma Rodriguez             │
│    Grade 5 | KITSKO   │    Grade 4 | STAUB    │    Grade 3 | KITSKO           │
│    $2,624 🥇          │    1,245 min 🥇       │    10/10 days (100%) 🥇       │
│                       │                       │                               │
│ 2. David Park         │ 2. Lily Thompson      │ 2. Jake Martinez              │
│    Grade 4 | STAUB    │    Grade 5 | KITSKO   │    Grade 5 | STAUB            │
│    $1,987             │    1,198 min          │    10/10 days (100%)          │
│                       │                       │                               │
│ 3. Emma Wilson        │ 3. Alex Johnson       │ 3-T. (15 students)            │
│    Grade K | KITSKO   │    Grade 3 | STAUB    │    Various                    │
│    $1,776             │    1,152 min          │    10/10 days (100%)          │
│                       │                       │                               │
│ 4. Noah Garcia        │ 4. Sophie Anderson    │ 18. Ava Brown                 │
│    Grade 2 | STAUB    │    Grade 5 | KITSKO   │    Grade 1 | KITSKO           │
│    $1,654             │    1,089 min          │    9/10 days (90%)            │
│                       │                       │                               │
│ 5. Olivia Kim         │ 5. Ryan Lee           │ 19. Ethan Smith               │
│    Grade 3 | KITSKO   │    Grade 2 | STAUB    │    Grade 4 | STAUB            │
│    $1,543             │    1,034 min          │    9/10 days (90%)            │
└───────────────────────┴───────────────────────┴───────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────┐
│  📋 ALL STUDENTS DETAIL TABLE (Sortable, Filterable)                           │
│  Showing 411 students  |  Export: [📥 CSV] [📊 Excel]                          │
├────┬──────────────┬─────┬──────┬────────┬──────────┬───────────┬──────┬───────┤
│ #  │ NAME ▲       │ GR  │ TEAM │ CLASS  │ FUND 💰  │ READING ◐ │ SPON │ PART ◐│
├────┼──────────────┼─────┼──────┼────────┼──────────┼───────────┼──────┼───────┤
│  1 │ Sarah Chen   │  5  │KITSKO│ ogg    │ ⭕$2,624 │  845 min  │  12  │ 10/10 │
│    │              │     │      │        │          │  (14 hrs) │      │ 100%  │
├────┼──────────────┼─────┼──────┼────────┼──────────┼───────────┼──────┼───────┤
│  2 │ David Park   │  4  │STAUB │ neurohr│ ⭕$1,987 │  723 min  │   9  │ 10/10 │
│    │              │     │      │   pm   │          │  (12 hrs) │      │ 100%  │
├────┼──────────────┼─────┼──────┼────────┼──────────┼───────────┼──────┼───────┤
│  3 │ Emma Wilson  │  K  │KITSKO│ lee am │ ⭕$1,776 │  612 min  │   8  │  9/10 │
│    │              │     │      │        │          │  (10 hrs) │      │  90%  │
├────┼──────────────┼─────┼──────┼────────┼──────────┼───────────┼──────┼───────┤
│... │ (406 more students)                                                       │
├────┼──────────────┼─────┼──────┼────────┼──────────┼───────────┼──────┼───────┤
│411 │ Mia Foster   │  3  │STAUB │ white  │      $0  │    0 min  │   0  │  0/10 │
│    │              │     │      │        │          │   (0 hrs) │      │   0%  │
└────┴──────────────┴─────┴──────┴────────┴──────────┴───────────┴──────┴───────┘

Legend:
  ⭕ = School-wide top 10 (gold highlight)
  ◐ = Metric honors date filter (cumulative through selected date)
  💰 = Fundraising total  |  SPON = Number of sponsors per student  |  PART = Participation %

Pagination: [← Prev]  Page 1 of 9  [Next →]  |  Rows per page: [50 ▼]

┌─────────────────────────────────────────────────────────────────────────────────┐
│  📈 QUICK STATS BY SEGMENT                                                      │
├───────────────────┬───────────────────┬───────────────────┬────────────────────┤
│ BY GRADE ◐        │ BY TEAM ◐         │ BY ACTIVITY ◐     │ BY FUNDRAISING     │
│                   │                   │                   │                    │
│ K:   67 students  │ KITSKO: 206 st.   │ 10/10: 145 st.    │ $1000+: 15 st.     │
│      Avg 320 min  │         Avg 412m  │  9/10:  89 st.    │ $500-$999: 42 st.  │
│                   │                   │  8/10:  67 st.    │ $100-$499: 128 st. │
│ 1:   71 students  │ STAUB: 205 st.    │  7/10:  45 st.    │ $1-$99: 140 st.    │
│      Avg 385 min  │        Avg 398m   │  1-6:   43 st.    │ $0: 86 students    │
│                   │                   │  0:     22 st.    │                    │
│ 2:   68 students  │                   │                   │                    │
│      Avg 412 min  │ LEAD: KITSKO      │ Avg: 7.8 days     │ Avg: $287/student  │
│                   │ +14 min gap       │                   │                    │
│ ... (all grades)  │                   │                   │                    │
└───────────────────┴───────────────────┴───────────────────┴────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────┐
│  [▶ Click to expand] Data Sources & Last Updated                               │
└─────────────────────────────────────────────────────────────────────────────────┘
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
- **Reading minutes:** `SUM(MIN(Daily_Logs.minutes_read, 120))` (◐ honors date filter)
- **Participation %:** `(days_read / total_days) * 100` (◐ honors date filter)

---

## Open Questions / User Decisions Needed

1. **Table columns:** Are these the right columns? Add/remove any?
   - Current: Name, Grade, Team, Class, Fundraising, Reading, Sponsors, Participation
   - Consider adding: Goal Met (Y/N), Days Active, Avg. Minutes/Day?

2. **Leaderboard categories:** Are these the right 3 categories?
   - Current: Fundraising, Reading, Consistency (participation)
   - Consider adding: Most Sponsors, Best Improvement?

3. **Quick Stats segments:** Are these useful?
   - Current: By Grade, By Team, By Activity, By Fundraising
   - Consider adding: By Class, By Goal Achievement?

4. **Student detail view:** Click student name to see:
   - Daily breakdown (reading minutes per day)
   - Sponsor list (if available)
   - Class/grade context
   - Progress charts?

5. **Export format:** CSV only, or also Excel? PDF?

6. **Default sort order:** Alphabetical by name, or by fundraising (descending)?

7. **Pagination:** 50 per page good? Or 25, 100?

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

## Status History

- **2025-10-31 10:31** - ASCII prototype v1 complete
- **2025-10-31 10:31** - Paused for user review of existing pages
- **2025-10-31 10:31** - Discovered School page sponsor bug, fixing separately
- **Next:** Await user feedback after reviewing School/Teams/Grade pages
