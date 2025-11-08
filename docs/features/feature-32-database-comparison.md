# Feature 32: Database Comparison (Year-Over-Year Analysis)

**Status:** 🚧 IN PROGRESS
**Created:** 2025-01-07
**Last Updated:** 2025-11-07 (Current session)
**Implementation:** Database Comparison tab in Admin page

## Current Status (2025-11-07 - End of Session)

### ✅ Completed
- ✅ Tab integrated into Admin page (5th tab)
- ✅ Form submits to /admin route with comparison parameters
- ✅ Results display in-place within tab (no new window)
- ✅ **17 comparisons working** (up from initial 8)
  - School: 5 metrics (Fundraising, Minutes, Sponsors, Participation, Size)
  - Team: 3 metrics (Fundraising, Minutes, Size)
  - Grade: 3 metrics (Fundraising, Minutes, Size)
  - Class: 3 metrics (Fundraising, Minutes, Size)
  - Student: 3 metrics (Fundraising, Minutes, Sponsors)
- ✅ **Styling fixed** - CSS now renders correctly (was in wrong block)
  - Sort indicators (↕ ↑ ↓) visible and working
  - Winning value ovals showing with correct colors (blue/orange)
  - Table styling matches prototype (dark headers, alternating rows, hover effects)
  - Database selection section has proper card styling with white background
- ✅ **Sort order fixed** - Hierarchical sorting by entity (School→Team→Grade→Class→Student)
- ✅ **"pp" note added** - Explains "pp = percentage points"
- ✅ All references changed from teacher_name to class_name

### ⚠️ Remaining Work
1. **Missing Comparisons:** Only 17 of 55 comparisons (need 38 more)
2. **Sticky Selections:** Not implemented yet (needs sessionStorage)
3. **Testing:** Full functionality test needed (sorting, filtering, searching, exporting)

## Roadmap to 55 Comparisons

### Current: 17 Comparisons Implemented
**Breakdown by Entity:**
- School: 5/11 metrics (45%)
- Team: 3/11 metrics (27%)
- Grade: 3/11 metrics (27%)
- Class: 3/11 metrics (27%)
- Student: 3/11 metrics (27%)

### Target: 55 Comparisons (5 entities × 11 metrics)

**Missing Metrics (38 comparisons):**

#### School Level (Need 6 more):
6. Avg Participation % (With Color)
7. Goal Met (≥1 Day)
8. All N Days Active %
9. Goal Met All Days %
10. Color War Points
11. TBD (entity-specific)

#### Team Level (Need 8 more):
4. Sponsors
5. Total Participating (≥1 Day)
6. Avg Participation % (With Color)
7. Goal Met (≥1 Day)
8. All N Days Active %
9. Goal Met All Days %
10. Color War Points
11. TBD (entity-specific)

#### Grade Level (Need 8 more):
Same as Team level (metrics 4-11)

#### Class Level (Need 8 more):
Same as Team level (metrics 4-11)

#### Student Level (Need 8 more):
4. Total Participating (≥1 Day) - N/A for individual students
5. Avg Participation % (With Color)
6. Goal Met (≥1 Day)
7. All N Days Active %
8. Goal Met All Days %
9. Color War Points
10-11. TBD (maybe top per grade, top per team, etc.)

### Implementation Steps for Next Session

**Step 1: Extend Team/Grade/Class queries in queries.py**
Add implementations for metrics 4-11 in these functions:
- `get_db_comparison_team_top(metric, date_filter)` - Currently only supports fundraising, minutes, size
- `get_db_comparison_grade_top(metric, date_filter)` - Currently only supports fundraising, minutes, size
- `get_db_comparison_class_top(metric, date_filter)` - Currently only supports fundraising, minutes, size

**Step 2: Add School-level queries for metrics 6-11**
Create new query functions in queries.py:
- `get_db_comparison_school_avg_participation()`
- `get_db_comparison_school_goal_met()`
- `get_db_comparison_school_all_days_active()`
- `get_db_comparison_school_goal_met_all_days()`
- `get_db_comparison_school_color_war_points()`

**Step 3: Add Student-level queries for metrics 4-11**
Create new query functions in queries.py:
- `get_db_comparison_student_top_participation()`
- `get_db_comparison_student_top_goal_achievement()`
- etc.

**Step 4: Update database.py**
Extend the `get_database_comparison()` method to use the new queries and generate all 55 comparisons.

**Step 5: Test**
Verify all 55 comparisons display correctly with proper formatting and winner highlighting.

## Quick Reload for Next Session
**Command:** Read this file completely, then review the prototype at `file:///Users/stevesouza/my/data/readathon/v2026_development/prototypes/database_comparison.html`

**Key Files:**
- `/Users/stevesouza/my/data/readathon/v2026_development/docs/features/feature-32-database-comparison.md` (this file - complete requirements)
- `/Users/stevesouza/my/data/readathon/v2026_development/prototypes/database_comparison.html` (visual prototype showing exact styling)
- `/Users/stevesouza/my/data/readathon/v2026_development/templates/admin.html` (Database Comparison tab - lines 800-930)
- `/Users/stevesouza/my/data/readathon/v2026_development/database.py` (get_database_comparison method - line 3345)
- `/Users/stevesouza/my/data/readathon/v2026_development/app.py` (admin route - line 2618)

**Technical Details:**

**Existing Query Functions (queries.py lines 2132-2601):**
- `get_db_comparison_school_fundraising()` - Returns: total_fundraising, class_name, teacher_name, grade_level, team_name
- `get_db_comparison_school_minutes()` - Returns: total_minutes, class_name, teacher_name, grade_level, team_name
- `get_db_comparison_school_sponsors()` - Returns: total_sponsors, class_name, teacher_name, grade_level, team_name
- `get_db_comparison_school_participation()` - Returns: participation_pct, participating_count, total_count
- `get_db_comparison_school_size()` - Returns: student_count, class_count
- `get_db_comparison_student_top_fundraiser()` - Returns: student_name, fundraising, grade_level, teacher_name, team_name
- `get_db_comparison_student_top_reader()` - Returns: student_name, total_minutes, grade_level, teacher_name, team_name
- `get_db_comparison_student_top_sponsors()` - Returns: student_name, sponsor_count, grade_level, teacher_name, team_name
- `get_db_comparison_team_top(metric)` - Supports: fundraising, minutes, size (sponsors/participation return NULL)
- `get_db_comparison_grade_top(metric)` - Supports: fundraising, minutes, size (sponsors/participation return NULL)
- `get_db_comparison_class_top(metric)` - Supports: fundraising, minutes, size (sponsors/participation return NULL)

**Important Notes:**
- All queries use `class_name` (not `teacher_name`) for display
- Team/Grade/Class size queries return `student_count` (not `team_size`/`grade_size`/`class_size`)
- For Class size: returns `total_students` field from Class_Info table
- Winning values styled with `.winning-value-db1` (blue) and `.winning-value-db2` (orange)

---

## Overview

A comprehensive database comparison feature that allows users to compare any two databases from the registry across all key metrics. This enables year-over-year analysis to track growth, identify trends, and understand performance changes across school years.

**Key Capabilities:**
- Compare any 2 databases from registry (e.g., 2025 vs 2024)
- Compare across 5 entity levels: School, Team, Grade, Class, Student
- Compare 11 key metrics (fundraising, minutes, participation, etc.)
- Show top performers at each entity level for each year
- Highlight which year performed better (gold highlighting)
- Filter, search, and sort results
- Export to CSV/Excel

---

## Database Selection (COMPACT ONE-ROW LAYOUT)

**CRITICAL:** All selection controls on ONE ROW to minimize vertical space:

```
Database 1: [Active (Currently: 2025) ▼]  Database 2: [2024 Read-a-Thon ▼]  📅 Filter Period: [Full Contest ▼]  [Compare]
```

### Layout Specifications
- **All on one row:** Database 1, Database 2, Filter Period, Compare button
- **Responsive:** Wraps on narrow screens (<1200px)
- **Labels inline:** Short labels ("Database 1:", "Database 2:", "📅 Filter Period:")
- **Dropdowns:** `form-select form-select-sm`, max-width constraints
  - DB1: max-width: 280px
  - DB2: max-width: 280px
  - Filter: max-width: 220px
- **Button:** "Compare" (not "Compare Databases"), compact sizing

### Dropdown 1: Primary Database
**Options:**
- **"Active (Currently: [Database Name])"** - Dynamically uses current active database
  - Example: "Active (Currently: 2025 Read-a-Thon)"
  - If user changes active database in main app, this comparison updates automatically
- All databases from registry (by display name)

### Dropdown 2: Comparison Database
**Options:**
- All databases from registry (by display name)
- No "Active" option for second database (must pick specific database)

### Behavior
- User can compare "Active vs specific year" (dynamic)
- OR "Specific year vs specific year" (static comparison)
- Database list loaded from `db/readathon_registry.db`
- Clicking "Compare" button triggers comparison query

---

## Filter Period (Independent from Main App)

**CRITICAL:** This filter is INDEPENDENT from the main app's filter period because:
- Main app uses absolute dates OR "Full Contest Period"
- Database comparison uses RELATIVE days (Day 1, Day 2, etc.)
- Contest dates differ by year (2025: Oct 10-19, 2024: Oct 8-17)

### Filter Options
- Day 1 (first day of each contest)
- Day 2 (second day of each contest)
- Day 3
- Day 4
- Day 5
- Day 6
- **Full Contest Period (default)**

### Behind the Scenes
- 2025 Day 1 = Oct 10, 2025
- 2024 Day 1 = Oct 8, 2024
- User sees "Day 1" comparison (apples-to-apples)

---

## Comparison Table Structure

### Entity Hierarchy (Default Sort Order)
1. **School** (sort key: 1)
2. **Team** (sort key: 2)
3. **Grade** (sort key: 3)
4. **Class** (sort key: 4)
5. **Student** (sort key: 5)

### Total Rows
**55 total rows** = 5 entity levels × 11 metrics

### Columns
1. **Entity Level** - School/Team/Grade/Class/Student (sortable, hierarchical default)
2. **Metric** - Fundraising, Minutes, Sponsors, etc. (sortable, alphabetical)
3. **2025 Read-a-Thon (Contest Dates)** - Value + Winner context (sortable)
4. **2024 Read-a-Thon (Contest Dates)** - Value + Winner context (sortable)
5. **Change** - Absolute + Percentage + Arrow (sortable)

---

## 11 Metrics Compared

| # | Metric | Icon | Format | Notes |
|---|--------|------|--------|-------|
| 1 | Fundraising | 💰 | `$45,678` | Total donations raised |
| 2 | Minutes Read | 📚 | `8,234 hours` | Capped at 120/day |
| 3 | Sponsors | 🤝 | `28 sponsors` | Total sponsor count |
| 4 | **Total Participating (≥1 Day)** | 👥 | `79.8% (328/411)` | % who logged ANY reading |
| 5 | Avg Participation % (With Color) | 👥 | `78.5%` | Avg daily participation + color bonus |
| 6 | Goal Met (≥1 Day) | 🎯 | `65.2%` | % who met goal at least once |
| 7 | All N Days Active % | ✅ | `72.8%` | % who logged reading EVERY day |
| 8 | Goal Met All Days % | 🎯 | `61.5%` | % who met goal EVERY day |
| 9 | Color War Points | 🎨 | `12,679 points` | Total color war points |
| 10 | Class/Grade/Team/School Size | 👥 | `411 students` | Entity size |
| 11 | (Metric varies by entity level) | | | See table structure |

### Metric #4 - Total Participating (≥1 Day) - CRITICAL
**Definition:** Students who logged ANY reading (minutes_read > 0) on ANY day

**Display Format:**
```
79.8% (328/411)
```
- Percentage first (most important)
- Count in parentheses (context)

**Calculation:**
```sql
COUNT(DISTINCT CASE WHEN dl.minutes_read > 0 THEN dl.student_name END) / total_roster * 100
```

**Data Source:** Same as "Total Participating" section on School page

---

## Winner Display Format (CRITICAL)

### Student Level
```
Winner: Johnny S.
Grade 3, Ms. Smith, Team 1
```

**Format:**
- Line 1: `Winner: [Student Name]`
- Line 2: `Grade [N], [Class Name], Team [N]`

### Class Level
```
Winner: Ms. Smith
Grade 3, Team 1
```

**Format:**
- Line 1: `Winner: [Class Name]`
- Line 2: `Grade [N], Team [N]`

### Grade Level
```
Winner: Grade 4
Top class: Mr. Chen (Team 1)
```

**Format:**
- Line 1: `Winner: Grade [N]`
- Line 2: `Top class: [Class Name] (Team [N])`

**Note:** Winner is the GRADE, not the class. Mr. Chen is supporting context (top contributor within that grade).

### Team Level
```
Winner: Team 1 (Phoenix)
Top class: Mr. Chen (Grade 4)
```

**Format:**
- Line 1: `Winner: Team [N] ([Team Name])`
- Line 2: `Top class: [Class Name] (Grade [N])`

**Note:** Winner is the TEAM, not the class. Mr. Chen is supporting context (top contributor within that team).

### School Level
```
Top class: Mr. Chen (Grade 4, Team 1)
```

**Format:**
- Line 1: `Top class: [Class Name] (Grade [N], Team [N])`

**Note:** No "Winner: Whole School" - it's always whole school. Show top contributing class instead.

---

## Visual Design

### Winner Highlighting (CRITICAL - Using Team Colors)
**IMPORTANT:** Do NOT use gold/silver. Use team badge colors to distinguish years:
- **Blue highlight (2025):** `background: #1e3a5f; color: white;`
- **Yellow highlight (2024):** `background: #f59e0b; color: #1e3a5f;`
- Applied to winning value using `.winning-value` class with rounded pill style
- Same styling as team badges in teams.html
- Makes it immediately clear which year performed better

### Sortable Columns
- All column headers clickable
- Click to sort ascending, click again for descending
- Visual indicator: ⬍⬍ or arrow icon
- Default sort: Entity Level (hierarchical: School → Team → Grade → Class → Student)

### Search + Filter UI (Same Row)
```
Search: [_____________________________________________] 🔍  Filter: [All Entities ▼]  55 comparisons  [Copy] [Export]
```

**Layout:**
- Search box: flex: 1, max-width: 700px (LARGE for long searches)
- Filter dropdown: min-width: 120px, max-width: 130px (COMPACT)
- Results count: "55 comparisons" text between filter and buttons
- Export buttons: Copy + Export, matching Reports page style (`btn btn-sm btn-primary`)
- All on same row (like Reports & Data screen)

### Search Behavior
- Search across ALL columns
- Searches: Student names, class names, metric names, grade levels, team names, values
- Example: Search "participation" → shows all participation-related rows
- Example: Search "Johnny" → shows all rows mentioning Johnny S.
- Real-time filtering (updates as you type)

### Filter Dropdown Options
- All Types (default)
- School
- Grade
- Class
- Team
- Student

---

## Default Sort Order (Hierarchical)

### Entity Level Column
**Custom sort order (NOT alphabetical):**

| Entity | Display | Sort Key | Order |
|--------|---------|----------|-------|
| School | 🏫 School | 1 | First |
| Team | 🔷 Team | 2 | Second |
| Grade | 🎓 Grade | 3 | Third |
| Class | 🏛️ Class | 4 | Fourth |
| Student | 👤 Student | 5 | Fifth |

**Implementation:**
```html
<tr data-sort-key="1">  <!-- School -->
<tr data-sort-key="2">  <!-- Team -->
<tr data-sort-key="3">  <!-- Grade -->
<tr data-sort-key="4">  <!-- Class -->
<tr data-sort-key="5">  <!-- Student -->
```

**JavaScript:**
```javascript
// Default sort: by entity level (hierarchical)
rows.sort((a, b) => {
    return parseInt(a.dataset.sortKey) - parseInt(b.dataset.sortKey);
});
```

**Click behavior:**
- First click: School → Team → Grade → Class → Student (ascending hierarchical)
- Second click: Student → Class → Grade → Team → School (descending hierarchical)
- NOT alphabetical

---

## Top Performer Comparison Logic

### Key Principle
**Compare 2025's #1 vs 2024's #1 (NOT same individual tracked across years)**

**Example:**
- 2025 top fundraiser: Johnny S. ($850)
- 2024 top fundraiser: Emma K. ($720)
- Comparison: $850 vs $720 → 2025 wins (+$130, +18.1%)

**NOT:**
- Tracking Johnny S. across years (he might not have existed in 2024)

### Winner Determination
At each entity level, for each metric:
1. Find the #1 performer in 2025 database
2. Find the #1 performer in 2024 database
3. Compare their values
4. Highlight the higher value in gold

### Ties
- Show tie count: "(3-way tie)"
- List names: "Johnny S., Sarah M., and 1 more"
- Format: "Name A, Name B, and N more"
- Use same tie display logic as existing cards (Teams/School pages)

---

## Drill-Down (Future Enhancement)

### Placeholder for Future
Each row will have `[Click for details]` indicator (or make entire row clickable).

### Example Drill-Down: School > Fundraising
**User clicks row → Modal opens:**

```
┌─────────────────────────────────────────────────────────────┐
│ 📊 FUNDRAISING BREAKDOWN BY GRADE              [✕ Close]   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  2025 Read-a-Thon vs 2024 Read-a-Thon - Full Contest      │
│                                                             │
│  Grade   │ 2025 Amount  │ 2024 Amount  │ Change            │
│  ────────┼──────────────┼──────────────┼──────────────     │
│  K       │ $5,200       │ $4,100       │ +$1,100 (+26.8%) │
│  1       │ $6,500       │ $5,800       │ +$700 (+12.1%)   │
│  2       │ 🟡 $7,800    │ $7,200       │ +$600 (+8.3%)    │
│  ...     │ ...          │ ...          │ ...              │
│  ────────┼──────────────┼──────────────┼──────────────     │
│  Total   │ $45,678      │ $38,234      │ +$7,444 (+19.5%) │
│                                                             │
│  2025 Winner: Grade 4 ($9,200) - Mr. Chen (Team 1)        │
│  2024 Winner: Grade 3 ($8,500) - Ms. Smith (Team 1)       │
└─────────────────────────────────────────────────────────────┘
```

**Not in initial implementation** - design allows for it later.

---

## Data Sources

### Registry Database
- File: `db/readathon_registry.db`
- Table: `Database_Registry`
- Used for: Loading list of available databases for dropdowns

### Contest Databases
- Files: User-selected (e.g., `db/readathon_2025.db`, `db/readathon_2024.db`)
- Tables: `Roster`, `Daily_Logs`, `Reader_Cumulative`, `Class_Info`, `Grade_Rules`, `Team_Color_Bonus`
- Used for: All metric calculations

### Metric Calculations
**CRITICAL:** Follow `md/RULES.md` for all calculations:
- Fundraising: `Reader_Cumulative` SUM(amount_raised) - NEVER capped
- Minutes: `Daily_Logs` SUM(capped_minutes) - Capped at 120/day
- Sponsors: `Reader_Cumulative` SUM(sponsor_count)
- Participation: See existing School page calculations
- Goals Met: Compare `minutes_read` vs `Grade_Rules.min_daily_minutes`
- Color War Points: `Team_Color_Bonus` + participation calculations
- Team assignments: Alphabetical order (Team 1 = first alphabetically)

---

## Implementation Notes

### Must Follow
1. **md/RULES.md** - Universal rules for data sources, calculations, colors
2. **md/UI_PATTERNS.md** - Established patterns for colors, components, styling
3. **Existing pages** - School/Teams/Grade pages for reference patterns

### Bootstrap Icons to Use
- 💰 → `<i class="bi bi-currency-dollar"></i>`
- 📚 → `<i class="bi bi-book"></i>`
- 🤝 → `<i class="bi bi-people"></i>`
- 👥 → `<i class="bi bi-person-check"></i>`
- 🎯 → `<i class="bi bi-bullseye"></i>`
- ✅ → `<i class="bi bi-check-circle"></i>`
- 🎨 → `<i class="bi bi-palette"></i>`
- 🏫 → `<i class="bi bi-building"></i>`
- 🎓 → `<i class="bi bi-mortarboard"></i>`
- 🏛️ → `<i class="bi bi-house"></i>`
- 🔷 → `<i class="bi bi-diamond-fill"></i>`
- 👤 → `<i class="bi bi-person"></i>`

### Color Palette (from UI_PATTERNS.md)
- Primary Blue: `#1e3a5f`
- Gold/Yellow (winner): `#ffd700` or Bootstrap `bg-warning`
- Green (increase): `#28a745` or Bootstrap `text-success`
- Red (decrease): `#dc3545` or Bootstrap `text-danger`
- Table header: `#1e3a5f` background, white text
- Alternating rows: white and `#f8f9fa`

---

## Testing Requirements

### Automated Tests
**File:** `tests/test_database_comparison.py`

**Required tests:**
1. `test_page_loads_successfully` - HTTP 200, no errors
2. `test_database_dropdowns_populated` - Both dropdowns show registry databases
3. `test_active_database_option` - "Active (Currently: [name])" present in dropdown 1
4. `test_filter_period_options` - Day 1-6, Full Contest Period present
5. `test_comparison_table_structure` - 55 rows (5 entities × 11 metrics)
6. `test_entity_level_sort_order` - Default hierarchical order (School → Student)
7. `test_winner_display_format` - Student/Class/Grade/Team/School formats correct
8. `test_gold_highlighting` - Winning year's cell has gold background
9. `test_total_participating_format` - Percentage format: "79.8% (328/411)"
10. `test_search_functionality` - Search filters rows correctly
11. `test_filter_by_entity_type` - Filter dropdown works correctly
12. `test_export_buttons_present` - CSV and Excel buttons present
13. `test_calculations_match_database` - Verify calculations against raw SQL queries

### Manual Browser Testing
**Checklist (BEFORE claiming complete):**
- [ ] Run tests: `pytest tests/test_database_comparison.py -v` (all passing)
- [ ] Start Flask: `python3 app.py --db sample`
- [ ] Open URL: `http://127.0.0.1:5001/database-comparison` (or appropriate route)
- [ ] Page loads without errors (no exceptions, no blank page)
- [ ] Both database dropdowns populated with registry databases
- [ ] "Active (Currently: [name])" option present in dropdown 1
- [ ] Filter period dropdown shows Day 1-6, Full Contest Period
- [ ] Click "Compare Databases" → Results table appears
- [ ] Table shows 55 rows (5 entities × 11 metrics)
- [ ] Default sort: School → Team → Grade → Class → Student
- [ ] Click column header → Sort changes (ascending/descending)
- [ ] Gold highlighting on winning year's cells
- [ ] Winner display formats match design (Student/Class/Grade/Team/School)
- [ ] "Total Participating" shows percentage: "79.8% (328/411)"
- [ ] Search box filters rows correctly
- [ ] Filter dropdown filters by entity type correctly
- [ ] Export buttons present (CSV/Excel)
- [ ] Run SQL queries to verify calculations match displayed values
- [ ] Side-by-side comparison with ASCII prototype (visual match)

---

## File Locations

### Templates
- **HTML:** `templates/database_comparison.html`
- **Base:** Extends `templates/base.html`

### Backend
- **Route:** `app.py` - Add `/database-comparison` route
- **Database Operations:** `database.py` - Add `get_database_comparison()` method
- **SQL Queries:** `queries.py` - Add comparison queries

### Tests
- **Test File:** `tests/test_database_comparison.py`

### Prototype
- **HTML Prototype:** `prototypes/database_comparison.html` (with fictitious data)

---

## Known Considerations

### Performance
- Querying two databases simultaneously may be slow for large datasets
- Consider caching comparison results
- Limit to most recent 5 years in registry?

### Edge Cases
- What if databases have different contest lengths? (Day 6 filter may not apply to both)
- What if student/class/grade doesn't exist in one year? (Show "N/A" or "—")
- What if both years tie? (Show both as gold? Or no highlighting?)

### Future Enhancements
1. Drill-down modals (click row → see breakdown)
2. Chart visualization (line chart showing year-over-year trends)
3. Multi-year comparison (compare 3+ years at once)
4. Saved comparisons (bookmark favorite comparisons)
5. PDF export with charts
6. Comparison summaries ("2025 improved on 8 out of 11 metrics")

---

## Design Rationale

### Why Option D (Top Performers)?
- **Storytelling:** Shows overall trends (school improved) → identifies contributors (Grade 4 led)
- **Scannable:** Eyes naturally flow from School → Team → Grade → Class → Student
- **Actionable:** Shows what level drove improvement
- **Consistent:** Matches existing app structure (hierarchy-based)

### Why Relative Days (Not Absolute Dates)?
- Contest dates differ by year (2025: Oct 10-19, 2024: Oct 8-17)
- Comparing Oct 10, 2025 vs Oct 10, 2024 is meaningless (different contest days)
- Day 1 vs Day 1 is apples-to-apples (first day momentum)
- Day 6 vs Day 6 is apples-to-apples (final day push)

### Why Independent Filter Period?
- Main app filter uses absolute dates OR "Full Contest Period"
- Database comparison uses relative days (Day 1, Day 2, etc.)
- These are fundamentally different concepts
- Prevents confusion and incorrect comparisons

### Why Show "Top Class" Context?
- Provides actionable insight (which class led improvement?)
- Enables recognition (celebrate top performers)
- Enables investigation (what did Mr. Chen do differently?)
- Balances aggregate metrics with individual context

---

## Success Criteria

**This feature is complete when:**
1. ✅ User can select any 2 databases from registry
2. ✅ User can select relative day filter (Day 1-6, Full Contest)
3. ✅ Table displays 55 rows (5 entities × 11 metrics)
4. ✅ Gold highlighting shows which year performed better
5. ✅ Winner display formats match design specification exactly
6. ✅ Search filters rows across all columns
7. ✅ Filter dropdown filters by entity type
8. ✅ Export to CSV/Excel works
9. ✅ Default sort is hierarchical (School → Student)
10. ✅ All automated tests passing
11. ✅ Manual browser testing checklist complete
12. ✅ Calculations verified against database queries
13. ✅ Visual match with HTML prototype

---

## Next Steps

1. **HTML Prototype** - Create `prototypes/database_comparison.html` with fictitious data
2. **User Approval** - Get approval on HTML prototype before production
3. **Production Implementation** - Implement in Flask app with real data
4. **Testing** - Automated tests + manual browser testing
5. **Documentation** - Update user-facing documentation
6. **Commit** - Follow project commit standards

---

**END OF DESIGN DOCUMENT**


---

## Implementation Notes (2025-11-07)

### Files Modified/Created

1. **tests/test_database_comparison.py** - Comprehensive test suite (25+ tests)
   - Page loading, data integrity, UI elements
   - Follows project testing patterns

2. **queries.py** - Database comparison SQL queries
   - School, Team, Grade, Class, Student level queries
   - Supports metrics: fundraising, minutes, sponsors, participation, size
   - Handles date filtering for time-based metrics

3. **database.py** - `get_database_comparison()` method
   - Compares two databases across multiple metrics and entity levels
   - Returns structured data with winner determination
   - Calculates change (absolute, percentage, direction)

4. **app.py** - `/database-comparison` route
   - Handles database selection from registry
   - Supports filter period parameter
   - Integrates with database comparison logic

5. **templates/database_comparison.html** - Standalone template
   - Based on approved prototype
   - Team color highlighting (blue/yellow)
   - Sortable table, search, entity filter
   - Export to CSV

6. **templates/admin.html** - Integrated as 5th tab
   - "Database Comparison" tab (last tab)
   - iframe embedding /database-comparison
   - Clean integration with existing admin UI

### Current Implementation Status

**Implemented:**
- ✅ School-level comparisons (5 metrics)
- ✅ Student-level comparisons (3 metrics)
- ✅ Database selection UI (compact one-row layout)
- ✅ Filter period support (Day 1-6, Full Contest)
- ✅ Winner highlighting (team colors: blue/yellow)
- ✅ Change calculations (absolute, percentage, direction)
- ✅ Search and filter functionality
- ✅ Export to CSV
- ✅ Sortable table
- ✅ Responsive design

**Pending (for future enhancement):**
- Team-level comparisons
- Grade-level comparisons
- Class-level comparisons
- Additional metrics (average participation, goals met, etc.)

### Usage

**Access:** Admin → Database Comparison tab (5th tab)

**Workflow:**
1. Select Database 1 (can use "Active" for current database)
2. Select Database 2 (comparison database)
3. Select Filter Period (optional - defaults to "Full Contest Period")
4. Click "Compare" button
5. View comparison table with winning year highlighted
6. Use search/filter to find specific comparisons
7. Sort by any column
8. Export results to CSV

### Testing

Run automated tests:
```bash
pytest tests/test_database_comparison.py -v
```

Manual browser testing:
1. Start app: `python3 app.py --db sample`
2. Navigate to: http://127.0.0.1:5001/admin
3. Click "Database Comparison" tab (last tab)
4. Test database selection and comparison


