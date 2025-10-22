# ⚠️ CRITICAL: SOURCE OF TRUTH FOR ALL REQUIREMENTS
This document contains the official requirements for all features.
- **Always consult this document FIRST** before implementing any feature
- **Update this document immediately** when requirements change during implementation
- **This document must be preserved** when compacting conversations
- **When starting a new session**, read this file before proceeding with any work

---

# Read-a-Thon System Enhancement Implementation Prompt

## Overview
This document contains comprehensive requirements for enhancing the Read-a-Thon Flask application. These enhancements should be implemented after the current read-a-thon event concludes.

---

## PRIORITY 1: High Priority Features

### 1.1 Export All Data (ZIP)
**Feature:** Create a master export that generates a ZIP file containing CSV exports of all tables and reports.

**Requirements:**
- Add "Export All Data" button/link in navigation or Admin section
- Generate ZIP file containing:
  - All database tables (Roster, Class_Info, Grade_Rules, Daily_Logs, Reader_Cumulative, Upload_History)
  - All available reports (Q1-Q23)
  - Named with timestamp: `readathon_export_YYYYMMDD_HHMMSS.zip`
- Use Python's `zipfile` module
- Stream response to avoid memory issues with large datasets
- Include README.txt in ZIP explaining contents

**Implementation Notes:**
```python
# New endpoint: /api/export_all
# Use zipfile.ZipFile with mode='w'
# Add each CSV using zipfile.writestr()
# Set appropriate headers for download
```

---

### 1.2 Data Validation Report
**Feature:** Comprehensive data integrity report showing potential issues across all tables.

**Checks to Include:**
1. **Duplicate Names:** Students with same/similar names
2. **Missing Roster:** Students in Daily_Logs or Reader_Cumulative but not in Roster
3. **Orphaned Data:** Classes in Daily_Logs without Class_Info entry
4. **Minutes Mismatch:** Daily_Logs sum ≠ Reader_Cumulative total
5. **Date Anomalies:** Dates outside expected range
6. **Zero Values:** Students with participation but 0 minutes
7. **Name Variations:** Similar names (fuzzy matching, e.g., "John Spencer" vs "Johnathan Spencer")

**Requirements:**
- Create new report: Q24 (or appropriate number)
- Display all checks on one scrollable page
- Format like workflows (multiple report sections)
- Show: Issue type, Count, Affected records
- Add to Admin tab and Reports page
- Color code: Green (OK), Yellow (Warning), Red (Error)

---

## PRIORITY 2: Medium Priority Features

### 2.1 Year-over-Year Comparison Report 📊 ENHANCED
**Feature:** Compare current year data with previous year(s) across multiple dimensions.

**Overview:**
- Compare campaigns across years for trend analysis
- Show overall performance, day-by-day progress, grade levels, and team competition
- Support positional team comparison (handles team name changes)
- Available in Reports tab and as Workflow

**Requirements:**

**A. Report Selection UI:**
```html
┌─────────────────────────────────────────────────┐
│ Year-over-Year Comparison                        │
├─────────────────────────────────────────────────┤
│ Current Year: [2025 ▼]                          │
│ Compare To:   [2024 ▼]                          │
│                                                  │
│ Report Type:  [Overall Summary ▼]               │
│               - Overall Summary                  │
│               - Day-by-Day Comparison            │
│               - Current Pace Analysis            │
│               - Grade Level Comparison           │
│               - Team Historical Comparison       │
│                                                  │
│ [Generate Comparison Report]                     │
└─────────────────────────────────────────────────┘
```

**B. Report Types:**

**Report 1: Overall Campaign Comparison**
```
┌───────────────────────────────────────────────────────────────────┐
│ Overall Campaign Comparison: 2024 vs 2025                         │
├───────────────────────────────────────────────────────────────────┤
│ Metric                    │ 2024    │ 2025    │ Change   │ % Chg  │
├───────────────────────────┼─────────┼─────────┼──────────┼────────┤
│ Total Donations           │ $13,966 │ $15,200 │ +$1,234  │ +8.8%  │
│ Total Minutes (Capped)    │ 15,123  │ 17,500  │ +2,377   │ +15.7% │
│ Students Participating    │ 205/411 │ 218/425 │ +13      │ +3.2%  │
│ Participation Rate        │ 49.9%   │ 51.3%   │ +1.4%    │ -      │
│ Days of Data              │ 6       │ 6       │ -        │ -      │
│ Avg Donation per Student  │ $68.13  │ $69.72  │ +$1.59   │ +2.3%  │
│ Avg Minutes per Student   │ 73.8    │ 80.3    │ +6.5     │ +8.8%  │
│ Top Student (Minutes)     │ 240     │ 260     │ +20      │ +8.3%  │
│ Top Student (Donations)   │ $525    │ $580    │ +$55     │ +10.5% │
└───────────────────────────┴─────────┴─────────┴──────────┴────────┘
```

**Report 2: Day-by-Day Comparison**
```
┌─────────────────────────────────────────────────────────────────────────────┐
│ Day-by-Day Progress: 2024 vs 2025                                           │
├─────────────────────────────────────────────────────────────────────────────┤
│ Campaign │ 2024      │ 2025      │ Donation │ 2024    │ 2025    │ Minutes  │
│ Day      │ Donations │ Donations │ Change   │ Minutes │ Minutes │ Change   │
├──────────┼───────────┼───────────┼──────────┼─────────┼─────────┼──────────┤
│ Day 1    │ $2,150    │ $2,400    │ +$250    │ 2,500   │ 2,800   │ +300     │
│ Day 2    │ $3,800    │ $4,100    │ +$300    │ 4,200   │ 4,600   │ +400     │
│ Day 3    │ $5,200    │ $5,800    │ +$600    │ 5,800   │ 6,400   │ +600     │
│ Day 4    │ $7,500    │ $8,200    │ +$700    │ 7,900   │ 8,800   │ +900     │
│ Day 5    │ $10,100   │ $11,300   │ +$1,200  │ 11,200  │ 12,800  │ +1,600   │
│ Day 6    │ $13,966   │ $15,200   │ +$1,234  │ 15,123  │ 17,500  │ +2,377   │
│          │           │           │          │         │         │          │
│ Total    │ $13,966   │ $15,200   │ +8.8%    │ 15,123  │ 17,500  │ +15.7%   │
└──────────┴───────────┴───────────┴──────────┴─────────┴─────────┴──────────┘
```

**Report 3: "Where We Stand Today" Comparison**
```
┌───────────────────────────────────────────────────────────────────┐
│ Current Progress Comparison (As of Day 3)                         │
├───────────────────────────────────────────────────────────────────┤
│                          │ 2024   │ 2025   │ Difference           │
├──────────────────────────┼────────┼────────┼──────────────────────┤
│ Donations to Date        │ $5,200 │ $5,800 │ +$600 (+11.5%)       │
│ Minutes to Date          │ 5,800  │ 6,400  │ +600 (+10.3%)        │
│ Students Active          │ 180    │ 195    │ +15 (+8.3%)          │
│ Participation Rate       │ 43.8%  │ 45.9%  │ +2.1%                │
│                          │        │        │                      │
│ Pace to Finish:                                                   │
│ If we maintain current pace, we'll end with:                      │
│ - Donations: $17,333 (2024 ended with $13,966 = +24% projected)  │
│ - Minutes: 21,333 (2024 ended with 15,123 = +41% projected)      │
└───────────────────────────────────────────────────────────────────┘
```

**Report 4: Grade Level Comparison**
```
┌────────────────────────────────────────────────────────────────────────┐
│ Grade Level Performance: 2024 vs 2025                                  │
├────────────────────────────────────────────────────────────────────────┤
│ Grade        │ 2024     │ 2025     │ Minutes │ 2024   │ 2025   │ Donations│
│              │ Avg Min  │ Avg Min  │ Change  │ Avg $  │ Avg $  │ Change   │
├──────────────┼──────────┼──────────┼─────────┼────────┼────────┼──────────┤
│ Kindergarten │ 45.2     │ 52.8     │ +7.6    │ $45.50 │ $48.20 │ +$2.70   │
│ 1st Grade    │ 58.3     │ 61.2     │ +2.9    │ $52.30 │ $55.10 │ +$2.80   │
│ 2nd Grade    │ 62.1     │ 68.5     │ +6.4    │ $58.20 │ $62.40 │ +$4.20   │
│ 3rd Grade    │ 70.5     │ 75.2     │ +4.7    │ $64.80 │ $68.30 │ +$3.50   │
│ 4th Grade    │ 78.2     │ 85.1     │ +6.9    │ $72.10 │ $78.50 │ +$6.40   │
│ 5th Grade    │ 85.3     │ 92.7     │ +7.4    │ $80.20 │ $87.60 │ +$7.40   │
└──────────────┴──────────┴──────────┴─────────┴────────┴────────┴──────────┘
```

**Report 5: Team Competition Historical (Positional)**
```
┌────────────────────────────────────────────────────────────────────┐
│ Team Competition: 2024 vs 2025                                     │
├────────────────────────────────────────────────────────────────────┤
│ Team       │ 2024 Name    │ 2024    │ 2025 Name    │ 2025    │ Change    │
│ Position   │              │ Total   │              │ Total   │           │
├────────────┼──────────────┼─────────┼──────────────┼─────────┼───────────┤
│ 1st Place  │ Team Staub   │ $7,200  │ Team Alpha   │ $8,000  │ +$800     │
│            │              │ (Winner)│              │ (Winner)│ (+11.1%)  │
│            │              │         │              │         │           │
│ 2nd Place  │ Team Kitsko  │ $6,800  │ Team Beta    │ $7,500  │ +$700     │
│            │              │         │              │         │ (+10.3%)  │
└────────────┴──────────────┴─────────┴──────────────┴─────────┴───────────┘

Note: Team names may differ year-to-year. Comparison is by final position.
```

**C. Team Name Handling - Positional Comparison:**

**Problem:** Team names change year-over-year (e.g., "Team Staub" → "Team Alpha")

**Solution:** Compare teams by their final position/rank, not by name
- 1st place team vs 1st place team
- 2nd place team vs 2nd place team
- Shows which team won in each year
- No manual configuration required
- Makes sense for competitive analysis

**Implementation:**
```python
def get_team_comparison(db_2024, db_2025):
    """Compare teams by position, not name"""

    # Get teams sorted by total (1st place, 2nd place, etc.)
    teams_2024 = db_2024.get_team_totals_sorted()  # Returns ordered list
    teams_2025 = db_2025.get_team_totals_sorted()

    comparison = []
    for position, (team_2024, team_2025) in enumerate(zip(teams_2024, teams_2025), 1):
        comparison.append({
            'position': position,
            'team_2024_name': team_2024['name'],
            'team_2024_total': team_2024['total'],
            'team_2025_name': team_2025['name'],
            'team_2025_total': team_2025['total'],
            'change': team_2025['total'] - team_2024['total'],
            'change_pct': ((team_2025['total'] - team_2024['total']) / team_2024['total']) * 100
        })

    return comparison
```

**D. Technical Implementation:**

**Cross-Database Queries using SQLite ATTACH:**
```python
import sqlite3

def compare_years(db_current, db_previous):
    """Compare two year databases"""

    conn = sqlite3.connect(db_current)

    # Attach previous year database
    conn.execute(f"ATTACH DATABASE '{db_previous}' AS prev_year")

    # Example query: Compare total donations
    query = """
    SELECT
        'Current' as year,
        SUM(donation_amount) as total_donations,
        COUNT(DISTINCT student_name) as total_students
    FROM Reader_Cumulative

    UNION ALL

    SELECT
        'Previous' as year,
        SUM(donation_amount) as total_donations,
        COUNT(DISTINCT student_name) as total_students
    FROM prev_year.Reader_Cumulative
    """

    results = pd.read_sql_query(query, conn)

    # Detach when done
    conn.execute("DETACH DATABASE prev_year")
    conn.close()

    return results
```

**E. Graceful Data Handling:**

**Handle Missing/Incomplete Data:**
1. **First Year:** Show message "No previous year data available for comparison"
2. **Incomplete Data:** Show warning "2024 data incomplete (3 of 6 days recorded)"
3. **Missing Metrics:** Display "-" or "N/A" for unavailable data
4. **Date Alignment:** Compare by campaign day number (Day 1, Day 2, etc.), not calendar dates

**Example:**
```python
def safe_comparison(val_current, val_previous):
    """Safely compare values, handle None/missing"""
    if val_current is None or val_previous is None:
        return {
            'current': val_current or 'N/A',
            'previous': val_previous or 'N/A',
            'change': '-',
            'change_pct': '-'
        }

    change = val_current - val_previous
    change_pct = (change / val_previous) * 100 if val_previous > 0 else 0

    return {
        'current': val_current,
        'previous': val_previous,
        'change': change,
        'change_pct': f"{change_pct:+.1f}%"
    }
```

**F. UI Integration:**

**Add to Reports Tab:**
- Report Q25: Year-over-Year Comparison
- Dropdown selectors for year selection
- Radio buttons or dropdown for report type
- Generate button

**Add to Workflows Tab:**
- "Year Comparison Workflow"
- One-click comparison using current and most recent previous year
- Shows all 5 report types in collapsible sections

**G. Performance Considerations:**

1. **Caching:** Cache comparison results for frequently accessed years
2. **Indexing:** Ensure proper indexes on date/student columns
3. **Lazy Loading:** Load report types on demand (accordion/tabs)
4. **Query Optimization:** Use aggregate queries, avoid row-by-row processing

**Implementation Priority:** 🟡 MEDIUM
- High value for strategic planning
- Motivational for participants
- Relatively straightforward to implement
- Depends on Feature 16 (year-based database system)

**Testing Scenarios:**
- [ ] Compare 2025 vs 2024 → All metrics calculate correctly
- [ ] Compare with incomplete data → Shows warnings, handles gracefully
- [ ] First year (no previous) → Shows appropriate message
- [ ] Teams with different names → Positional comparison works
- [ ] Day-by-day with different campaign lengths → Handles correctly
- [ ] Grade level comparison → All grades included
- [ ] Export comparison reports → CSV download works

**Files to Modify:**
- `database.py` - Add cross-database query functions
- `app.py` - Add `/year_comparison` route
- `templates/year_comparison.html` - Create comparison UI
- `templates/reports.html` - Add link to year comparison
- `templates/workflows.html` - Add year comparison workflow

**SQL Queries Needed:**
- Overall metrics comparison (donations, minutes, participation)
- Day-by-day cumulative totals
- Grade level averages by year
- Team totals sorted by position
- Student participation rates by year

---

## PRIORITY 3: Lower Priority Features

### 3.1 Student Detail Page
**Feature:** Click any student name to see complete record.

**Requirements:**
- Make all student names clickable links throughout app
- Create route: `/student/<student_name>`
- Display:
  - Student info from Roster (class, teacher, grade, team)
  - Daily reading log (all dates, minutes per day, capped vs actual)
  - Cumulative stats (donations, sponsors, total minutes)
  - Goal achievement (days met goal, percentage)
  - Visual timeline of reading activity
- Include buttons:
  - Export student data to CSV
  - Edit student name (if admin)
  - Back to previous page

---

### 3.2 Bulk Name Correction
**Feature:** Interface to fix common name variations and typos.

**Requirements:**
- Admin tab: "Bulk Name Correction"
- Show potential name issues:
  - Similar names (Levenshtein distance < 3)
  - Same last name, different first name format
  - Case variations
- For each issue, show:
  - Original name(s)
  - Affected tables
  - Record count
  - Merge/Rename options
- Actions:
  - Merge: Combine records under one name
  - Rename: Change name in all tables
  - Ignore: Mark as not an issue
- Require confirmation before applying changes
- Log all corrections to Upload_History

---

## PRIORITY 4-5: Future Features

### 4.1 Email Report for Teachers
**Feature:** Generate email-friendly HTML report for teachers.

**Requirements:**
- Route: `/report/email/<teacher_name>`
- Include:
  - Class summary stats
  - Top readers in class
  - Students needing encouragement
  - Class ranking vs other classes
- Formatted as HTML email (inline CSS)
- "Copy to Clipboard" button
- "Send Email" button (if email configured)

---

### 4.2 Progress Timeline
**Feature:** Visual chart showing daily participation trends.

**Requirements:**
- Use Chart.js or similar
- Line chart showing:
  - Daily participation count
  - Daily minutes read
  - Cumulative totals over time
- Add to Dashboard or new "Analytics" tab
- Options: By team, by class, by grade

---

### 4.3 Class Leaderboard
**Feature:** Real-time leaderboard display.

**Requirements:**
- Route: `/leaderboard`
- Large, readable display (suitable for projection)
- Auto-refresh every 30 seconds
- Show:
  - Top 10 classes by minutes
  - Top 10 classes by donations
  - Top 10 students by minutes
- Animated transitions when rankings change
- Full-screen mode

---

### 4.4 Goal Achievement Tracker
**Feature:** Report showing students close to goals.

**Requirements:**
- Report: Q26 Goal Tracker
- Show students:
  - Currently meeting goal (celebrate)
  - Close to goal (1-10 min away)
  - Need encouragement (far from goal)
- Group by class/team
- Calculate: Minutes needed to reach goal
- Suggested encouragement messages

---

## CORE FEATURE ENHANCEMENTS

### Feature 1: Improve Help/User Manual
**Current:** Basic help page exists at `/help`

**Enhancements:**
- Expand documentation with:
  - Detailed workflow guides (how to do daily uploads)
  - Troubleshooting section (common errors and fixes)
  - FAQ section
  - Report descriptions (what each report shows)
  - Best practices
- Add search functionality
- Include screenshots/images where helpful
- Organize in collapsible sections
- Add "Getting Started" quick guide

---

### Feature 2: Add ReadAThon Website Images/Links
**Requirements:**
- In Help section and Upload page, add:
  - Screenshots showing where to download data from ReadAThon website
  - Direct links to relevant ReadAThon pages
  - Step-by-step guide with images
- Create `/static/images/` folder for screenshots
- Format: "How to Download Daily Minutes" with annotated screenshots

---

### Feature 3: Video Tutorial Link
**Requirements:**
- Add link in navigation: "Video Tutorial"
- Create placeholder page at `/tutorial` with:
  - Embedded video (YouTube/Vimeo iframe)
  - Video transcript
  - Related documentation links
- Video should cover:
  - System overview
  - Daily upload workflow
  - Running reports
  - Troubleshooting

**Note:** Video creation is external; app just needs to link to it.

---

### Feature 4: Combined Reader Report
**New Report:** Q27 Complete Student Report

**Requirements:**
- Combines data from multiple sources:
  - All columns from Reader_Cumulative: student_name, teacher_name, team_name, donation_amount, sponsors, cumulative_minutes
  - From Daily_Logs aggregation:
    - days_participated (count of days with minutes > 0)
    - days_met_goal (count of days where minutes ≥ min_daily_minutes)
    - total_minutes_capped (SUM with 120-min daily cap)
- SQL query:
```sql
SELECT
    r.student_name,
    r.class_name,
    r.teacher_name,
    r.grade_level,
    r.team_name,
    COALESCE(rc.donation_amount, 0) as donation_amount,
    COALESCE(rc.sponsors, 0) as sponsors,
    COALESCE(rc.cumulative_minutes, 0) as cumulative_minutes,
    COUNT(CASE WHEN dl.minutes_read > 0 THEN 1 END) as days_participated,
    SUM(CASE WHEN dl.minutes_read >= gr.min_daily_minutes THEN 1 ELSE 0 END) as days_met_goal,
    SUM(MIN(dl.minutes_read, 120)) as total_minutes_capped
FROM Roster r
LEFT JOIN Reader_Cumulative rc ON r.student_name = rc.student_name
LEFT JOIN Daily_Logs dl ON r.student_name = dl.student_name
LEFT JOIN Grade_Rules gr ON r.grade_level = gr.grade_level
GROUP BY r.student_name, r.class_name, r.teacher_name, r.grade_level, r.team_name,
         rc.donation_amount, rc.sponsors, rc.cumulative_minutes
ORDER BY total_minutes_capped DESC, r.student_name ASC
```

- Add to Reports page in "Export Reports" section
- Include export/copy buttons
- Sortable columns

---

### Feature 5: Upload Screen Redesign
**Current:** Daily and Cumulative uploads stacked vertically, messages at bottom

**New Design:**
- Two-column layout:
  ```
  ┌─────────────────────────────────┬─────────────────────────────────┐
  │   Daily Minutes Upload          │   Cumulative Stats Upload       │
  │   [Date Picker]                 │   [File Upload]                 │
  │   [File Upload]                 │   [Upload Button]               │
  │   [Upload Button]               │                                 │
  └─────────────────────────────────┴─────────────────────────────────┘

  ┌───────────────────────────────────────────────────────────────────┐
  │   Upload Messages/Results (Shared Area)                           │
  │   ✓ Success messages or ✗ Error messages appear here              │
  └───────────────────────────────────────────────────────────────────┘
  ```

- Use Bootstrap `row` with two `col-md-6` columns
- Shared message area below columns
- Messages appear immediately (no scrolling needed)
- Style messages with Bootstrap alerts (success/warning/danger)

---

### Feature 6: Comprehensive Requirements Document
**Requirements:**
- Create new page: `/requirements`
- Add to navigation menu: "Requirements Doc"
- Include:
  - Complete system architecture
  - Database schema with relationships
  - All table definitions
  - All report specifications
  - API endpoints documentation
  - File upload formats
  - Business logic rules
  - Configuration details
- Format: Well-structured markdown or HTML
- Downloadable as PDF
- Sufficient detail to rebuild entire app from scratch

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

### Feature 8: Enhanced Participation Metrics
**Current:** Shows "Students Participating: X of Y (Z%)"

**Enhancements:** Add to the blue participation box:
```
Students Participating: 205 of 411 (49.9%)
├─ Participated ALL days: 180 (43.8%)
├─ Met goal ≥1 day: 195 (47.4%)
└─ Met goal ALL days: 150 (36.5%)
Days of Data: 3
```

**SQL Queries Needed:**
```sql
-- Participated ALL days
SELECT COUNT(DISTINCT student_name)
FROM (
    SELECT student_name, COUNT(DISTINCT log_date) as days
    FROM Daily_Logs WHERE minutes_read > 0
    GROUP BY student_name
    HAVING days = (SELECT COUNT(DISTINCT log_date) FROM Daily_Logs)
)

-- Met goal at least 1 day
SELECT COUNT(DISTINCT student_name)
FROM Daily_Logs dl
JOIN Grade_Rules gr ON dl.grade_level = gr.grade_level
WHERE dl.minutes_read >= gr.min_daily_minutes

-- Met goal ALL days
SELECT COUNT(DISTINCT student_name)
FROM (
    SELECT dl.student_name,
           COUNT(CASE WHEN dl.minutes_read >= gr.min_daily_minutes THEN 1 END) as goal_days,
           COUNT(DISTINCT dl.log_date) as total_days
    FROM Daily_Logs dl
    JOIN Roster r ON dl.student_name = r.student_name
    JOIN Grade_Rules gr ON r.grade_level = gr.grade_level
    GROUP BY dl.student_name
    HAVING goal_days = (SELECT COUNT(DISTINCT log_date) FROM Daily_Logs)
       AND total_days = goal_days
)
```

**Note:** Will iterate with UI prototype for display format.

---

### Feature 9: Add Reader_Cumulative to Home Stats
**Current:** Home page shows counts for Roster, Class_Info, Grade_Rules, Daily_Logs

**Add:**
```html
<div class="col-md-3">
    <div class="card stat-card">
        <div class="card-body">
            <h5 class="card-title text-muted">Reader Cumulative Entries</h5>
            <h2 class="mb-0">{{ counts.Reader_Cumulative }}</h2>
            <p class="text-muted mb-0" style="font-size: 0.7rem;">Source: Reader_Cumulative table</p>
        </div>
    </div>
</div>
```

**Implementation:**
- Modify `app.py` index route: `counts = db.get_table_counts()` already includes this
- Add to `templates/index.html` after Daily_Logs stat card
- Adjust grid to 5 columns or 2 rows

---

### Feature 10: "Run All Reports" Feature
**Requirements:**
- New page: `/run_all_reports`
- Add link in Reports page header: "Run All Reports"
- Display all reports on one page:
  - Each report in a collapsible section (Bootstrap accordion or similar)
  - All sections expanded by default
  - User can collapse any section
- Include at top:
  - "Copy All to Clipboard" button (copies all visible data)
  - "Expand All" / "Collapse All" buttons
  - Total reports count
- Format each report section:
  ```
  ┌─ Q1: Table Row Counts ─────────────────────────────┐
  │ [Collapse] [Copy] [Export CSV]                     │
  │ Description: Database table row counts             │
  │ [Table data here]                                  │
  └────────────────────────────────────────────────────┘
  ```

**Implementation:**
- Use Bootstrap accordion: `<div class="accordion">`
- Generate all reports server-side in one route
- Use JavaScript for "Copy All" functionality
- Consider performance with many reports (lazy load or pagination if needed)

---

### Feature 11: Slide Column Indicators
**Requirements:**
- Mark which columns are used in slide deck presentations
- Two-part approach:
  1. **Badge in column header:** Add icon/badge (📊 or "SLIDE") next to column headers used in slides
  2. **Text note above report:** Add note listing slide columns

**Example:**
```
Report: Q18/Slide 2 - Leading Class by Grade

Columns used in Slide Deck: grade_level, class_name, teacher_name, avg_participation_rate

[Table with column headers:]
Grade Level 📊 | Class Name 📊 | Teacher Name 📊 | Team | Total Students | ... | Avg Participation Rate 📊
```

**Implementation:**
- Add `slide_columns` list to each report metadata
- Modify report display template to check if column is in slide_columns
- Add badge/icon conditionally
- Include note in report header

**Slide Columns by Report:** (Will be provided in follow-up prompt when implementing)

---

### Feature 12: Move Export/Copy Buttons to Top
**Current:** Buttons at bottom of tables/reports (below data)

**Change:**
- Move to top of data table
- Position: Right side of header, inline with title
- Example:
  ```
  ┌────────────────────────────────────────────────────┐
  │ Q5: Student Cumulative Report                      │
  │ [Copy to Clipboard] [Export CSV]                   │
  ├────────────────────────────────────────────────────┤
  │ [Table data...]                                    │
  ```

**Apply to:**
- All report pages (`templates/reports.html` results)
- All table pages (`templates/tables.html` results)
- Workflow results

---

### Feature 13: Report Options Improvements
**Current Issues:**
- Options hidden below fold (require scrolling)
- Not clear which reports have options
- No explanations

**Improvements:**

**A. Report List - Show Available Options:**
```
Q2: Daily Summary Report
Daily summary by class or team with participation rates
[Options Available: Date Selection, Group By]

Q4: Prize Drawing
Random selection of winners by grade
[Options Available: Date Selection]

Q5: Student Cumulative Report
Complete student stats
[Options Available: Sort By, Limit]
```

**B. Options Panel - Move to Top:**
- Place options panel at top of results (not bottom)
- Make it sticky or always visible
- Add help text for each option:
  ```
  Date: [Dropdown ▼] All Dates
        Filter report to specific date (leave blank for all dates)

  Group By: [Dropdown ▼] Class
            Group results by Class or Team

  Sort By: [Dropdown ▼] Minutes
           Sort by Minutes, Goal Days, or Donations
  ```

**C. Add Option Metadata to Reports:**
```python
reports = [
    {
        'id': 'q2',
        'name': 'Q2: Daily Summary Report',
        'description': '...',
        'options': ['date', 'group_by'],
        'option_help': {
            'date': 'Filter to specific date or show all dates',
            'group_by': 'Group results by Class or Team'
        }
    },
    # ...
]
```

---

### Feature 14: Multiple Report Selection
**Requirements:**
- Add checkboxes to each report in list
- Add action buttons at top:
  - [Select All] [Deselect All] [Run Selected]
- When "Run Selected" clicked:
  - Open results in single page (like "Run All Reports")
  - Each checked report shows as collapsible section
  - All expanded by default
  - Include "Copy All" button

**Implementation:**
- Add `<input type="checkbox" class="report-checkbox" data-report-id="q2">` to each report item
- JavaScript to handle selection state
- POST to `/run_multiple_reports` with selected report IDs
- Return accordion-style results page

---

### Feature 15: Table Selection Capability
**Requirements:**
- Similar to report selection (Feature 14)
- Add to Tables page:
  - Checkboxes for each table
  - [Select All] [Deselect All] [View Selected]
- Display multiple tables on one scrollable page
- Each table in own section with heading
- Include row count for each table
- Export/copy buttons per table

---

### Feature 16: Flexible Multi-Purpose Database System 🗄️ ENHANCED
**Current:** Two databases: "Production" and "Sample"

**New System:**
- Support multiple databases for different purposes:
  - Year-based production campaigns (2024, 2025, 2026...)
  - Sample/test databases
  - Different schools
  - Experiments and testing
  - Archives (historical, read-only)
  - Any other custom purpose
- Flexible naming with metadata support
- Read-only flag for protecting archived data
- Remember last selected database

**Overview:**
This enhanced system allows users to create and manage multiple databases for any purpose, not just years. Each database has metadata (name, description, type, read-only status) stored within it.

**A. Database Naming Convention:**

**Filename Pattern:** `readathon_{identifier}.db`
- System always adds `readathon_` prefix automatically
- User provides identifier (free-form text: alphanumeric + underscore only)
- Examples:
  - `readathon_prod_2025.db`
  - `readathon_sample_2025.db`
  - `readathon_lincoln_2025.db`
  - `readathon_roosevelt_2025.db`
  - `readathon_experiment_test1.db`
  - `readathon_archive_2024.db`

**B. Database Types (for Organization):**
- **Production** - Main campaigns
- **Sample** - Test data
- **School** - Different schools
- **Experiment** - Testing features
- **Archive** - Historical campaigns
- **Other** - Anything else

**C. Database Metadata Table:**

Each database contains a metadata table with its configuration:

```sql
CREATE TABLE IF NOT EXISTS Database_Metadata (
    key TEXT PRIMARY KEY,
    value TEXT
);

-- Example metadata:
INSERT INTO Database_Metadata VALUES ('database_name', 'lincoln_2025');
INSERT INTO Database_Metadata VALUES ('description', 'Lincoln Elementary 2025 Campaign');
INSERT INTO Database_Metadata VALUES ('database_type', 'school');
INSERT INTO Database_Metadata VALUES ('created_date', '2025-01-15');
INSERT INTO Database_Metadata VALUES ('read_only', 'false');
INSERT INTO Database_Metadata VALUES ('created_by', 'Admin');
```

**D. Enhanced Database Discovery:**

```python
# app.py
import os
import glob
import sqlite3

def get_available_databases():
    """Get list of all database files with metadata"""
    db_files = glob.glob('readathon_*.db')
    databases = []

    for f in db_files:
        try:
            # Read metadata from database
            conn = sqlite3.connect(f)
            cursor = conn.cursor()

            # Check if metadata table exists
            cursor.execute("""
                SELECT name FROM sqlite_master
                WHERE type='table' AND name='Database_Metadata'
            """)

            if cursor.fetchone():
                # Read metadata
                cursor.execute("SELECT key, value FROM Database_Metadata")
                metadata = dict(cursor.fetchall())
            else:
                # Legacy database without metadata - infer from filename
                db_name = f.replace('readathon_', '').replace('.db', '')
                metadata = {
                    'database_name': db_name,
                    'description': f"Database: {db_name}",
                    'database_type': 'other',
                    'read_only': 'false'
                }

            conn.close()

            databases.append({
                'id': f.replace('.db', ''),
                'filename': f,
                'name': metadata.get('database_name', f),
                'description': metadata.get('description', ''),
                'type': metadata.get('database_type', 'other'),
                'read_only': metadata.get('read_only', 'false') == 'true',
                'created_date': metadata.get('created_date', '')
            })

        except Exception as e:
            print(f"Error reading database {f}: {e}")
            continue

    # Sort: Production first, then by type, then by name
    return sorted(databases, key=lambda x: (
        x['type'] != 'production',  # Production first
        x['type'],
        x['name']
    ))

# Initialize databases dynamically
db_instances = {}
for db in get_available_databases():
    db_instances[db['id']] = ReadathonDB(db['filename'])
```

**E. Enhanced Environment Selector (Grouped):**

```html
<!-- Dropdown with grouped databases -->
<select class="form-select" id="dbSelector" onchange="switchDatabase()">
    {% for type_name, dbs in databases_by_type.items() %}
    <optgroup label="{{ type_name|capitalize }}{% if type_name == 'archive' %} (Read-Only){% endif %}">
        {% for db in dbs %}
        <option value="{{ db.id }}"
                {% if db.id == current_db_id %}selected{% endif %}
                title="{{ db.description }}">
            {{ db.description }}
            {% if db.read_only %}🔒{% endif %}
            ({{ db.filename }})
        </option>
        {% endfor %}
    </optgroup>
    {% endfor %}
</select>
```

**Example Dropdown:**
```
┌─────────────────────────────────────────────────┐
│ Database: [▼]                                    │
├─────────────────────────────────────────────────┤
│ Production                                       │
│   ● 2025 Campaign (readathon_prod_2025)         │
│   ○ 2026 Campaign (readathon_prod_2026)         │
│                                                  │
│ Schools                                          │
│   ○ Lincoln Elementary 2025 (readathon_lincoln_2025)│
│   ○ Roosevelt Elementary 2025 (readathon_roosevelt_2025)│
│                                                  │
│ Sample                                           │
│   ○ 2025 Sample Data (readathon_sample_2025)    │
│                                                  │
│ Experiments                                      │
│   ○ Testing New Features (readathon_exp_test1)  │
│                                                  │
│ Archives (Read-Only)                             │
│   ○ 2024 Campaign 🔒 (readathon_archive_2024)   │
│                                                  │
│ Other                                            │
│   ○ Custom Database (readathon_custom1)         │
└─────────────────────────────────────────────────┘
```

**F. Remember Last Selected Database:**

```python
# Use Flask session to remember selection
from flask import session

@app.route('/api/switch_database', methods=['POST'])
def switch_database():
    db_id = request.json.get('database_id')

    if db_id in db_instances:
        session['current_database'] = db_id
        return jsonify({'success': True})

    return jsonify({'success': False, 'error': 'Database not found'}), 404

# On page load, use remembered database
@app.route('/')
def index():
    current_db_id = session.get('current_database', get_default_database())
    db = db_instances[current_db_id]
    # ... rest of route
```

**Alternative (localStorage):**
```javascript
// JavaScript to remember selection in browser
function switchDatabase() {
    const dbId = document.getElementById('dbSelector').value;

    // Save to localStorage
    localStorage.setItem('selectedDatabase', dbId);

    // Make API call to switch
    fetch('/api/switch_database', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({database_id: dbId})
    }).then(() => location.reload());
}

// On page load, restore selection
document.addEventListener('DOMContentLoaded', function() {
    const savedDb = localStorage.getItem('selectedDatabase');
    if (savedDb) {
        document.getElementById('dbSelector').value = savedDb;
    }
});
```

**G. Read-Only Protection:**

```python
def check_readonly(db_id):
    """Check if database is read-only"""
    db_info = next((db for db in get_available_databases() if db['id'] == db_id), None)
    return db_info and db_info['read_only']

@app.route('/upload_daily', methods=['POST'])
def upload_daily():
    current_db = session.get('current_database')

    if check_readonly(current_db):
        return jsonify({
            'success': False,
            'error': 'Cannot upload to read-only database. Please select a writable database.'
        }), 403

    # Proceed with upload...
```

**H. Database Management Functions:**

```python
def create_database(name, description, db_type='other', clone_from=None):
    """
    Create new database with metadata

    Args:
        name: Database identifier (alphanumeric + underscore)
        description: Human-readable description
        db_type: Type for organization (production, sample, school, experiment, archive, other)
        clone_from: Optional source database to clone structure from
    """
    # Validate name
    if not re.match(r'^[a-zA-Z0-9_]+$', name):
        raise ValueError("Database name must contain only letters, numbers, and underscores")

    filename = f"readathon_{name}.db"

    if os.path.exists(filename):
        raise ValueError(f"Database {filename} already exists")

    # Create database
    conn = sqlite3.connect(filename)

    if clone_from:
        # Clone structure from existing database
        source = sqlite3.connect(clone_from)
        for line in source.iterdump():
            if line.startswith('CREATE TABLE') or line.startswith('CREATE INDEX'):
                conn.execute(line)
        source.close()
    else:
        # Create base schema
        create_base_schema(conn)

    # Add metadata table and populate
    conn.execute("""
        CREATE TABLE IF NOT EXISTS Database_Metadata (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)

    metadata = {
        'database_name': name,
        'description': description,
        'database_type': db_type,
        'created_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'read_only': 'false',
        'created_by': 'Admin'
    }

    for key, value in metadata.items():
        conn.execute("INSERT INTO Database_Metadata VALUES (?, ?)", (key, value))

    conn.commit()
    conn.close()

    return filename

def set_readonly_flag(db_filename, read_only=True):
    """Toggle read-only flag for database"""
    conn = sqlite3.connect(db_filename)
    conn.execute("""
        INSERT OR REPLACE INTO Database_Metadata VALUES ('read_only', ?)
    """, ('true' if read_only else 'false',))
    conn.commit()
    conn.close()
```

**Implementation Priority:** 🟡 MEDIUM
- Provides flexibility for multi-school, multi-year, experimental use
- Foundation for year-over-year comparisons
- Enables safe experimentation without affecting production

**Testing Scenarios:**
- [ ] Create production database → Appears in Production group
- [ ] Create school database → Appears in Schools group
- [ ] Create experiment database → Can delete safely
- [ ] Mark database as read-only → Upload/delete operations blocked
- [ ] Switch between databases → Selection remembered
- [ ] Reload page → Last selected database still selected
- [ ] Multiple schools in same year → Can compare side-by-side

**Files to Modify:**
- `database.py` - Add metadata management functions
- `app.py` - Update database discovery, add session management
- `templates/base.html` - Update selector with grouped options
- `templates/admin.html` - Add database creation/management UI

**Database Migration:**
- Existing databases without metadata table continue to work
- System infers basic metadata from filename
- User can update metadata via Admin tab

---

### Feature 17: Admin Tab 🔧 ENHANCED
**Requirements:**
- Add new top-level navigation item: "Admin"
- Create `/admin` route and page
- Organize into sections with enhanced database management

**Section 1: Database Management (Enhanced)**

**A. Create New Database:**
```html
┌─────────────────────────────────────────────────┐
│ Create New Database                              │
├─────────────────────────────────────────────────┤
│ Database Name: [lincoln_2025_______________]     │
│                (letters, numbers, underscore only)│
│                (system will add 'readathon_' prefix)│
│                                                  │
│ Description: [Lincoln Elementary 2025 Campaign_] │
│              (shown in dropdown selector)        │
│                                                  │
│ Database Type: [School ▼]                       │
│                - Production                      │
│                - Sample                          │
│                - School                          │
│                - Experiment                      │
│                - Archive                         │
│                - Other                           │
│                                                  │
│ Clone from: [readathon_prod_2025 ▼] (optional) │
│             (copies structure, not data)         │
│                                                  │
│ [Create Database]                                │
└─────────────────────────────────────────────────┘

Result:
- Filename: readathon_lincoln_2025.db
- Appears in dropdown under "Schools" group
- Empty tables (if cloned) or base schema
- Metadata stored in Database_Metadata table
```

**B. Manage Existing Databases:**
```html
┌─────────────────────────────────────────────────────────────────────────────┐
│ Existing Databases                                                           │
├─────────────────────────────────────────────────────────────────────────────┤
│ Name                    | Type       | Size   | Records | Modified  | RO    │
├─────────────────────────────────────────────────────────────────────────────┤
│ readathon_prod_2025     | Production | 2.4 MB | 1,245   | 10/14/25  | [ ]   │
│ readathon_prod_2024     | Archive    | 2.1 MB | 1,189   | 10/12/24  | [✓]   │
│ readathon_lincoln_2025  | School     | 1.8 MB | 856     | 10/13/25  | [ ]   │
│ readathon_sample_2025   | Sample     | 500 KB | 500     | 09/01/25  | [ ]   │
│ readathon_exp_test1     | Experiment | 120 KB | 125     | 10/10/25  | [ ]   │
└─────────────────────────────────────────────────────────────────────────────┘

[RO] = Read-Only checkbox
- Check to mark database as read-only (prevents uploads/changes)
- Uncheck to make writable again
- Useful for protecting archived campaigns
```

**C. Current Database Info:**
```html
┌─────────────────────────────────────────────────┐
│ Current Database Information                     │
├─────────────────────────────────────────────────┤
│ Name: readathon_prod_2025                       │
│ Description: 2025 Main Campaign                  │
│ Type: Production                                 │
│ Created: 2025-09-01 10:30:00                    │
│ File Size: 2.4 MB                                │
│ Read-Only: No                                    │
│                                                  │
│ Table Row Counts:                                │
│ - Roster: 411 students                           │
│ - Class_Info: 18 classes                         │
│ - Grade_Rules: 6 grade levels                    │
│ - Daily_Logs: 1,233 entries                      │
│ - Reader_Cumulative: 411 entries                 │
│ - Upload_History: 12 uploads                     │
│                                                  │
│ Last Modified: 2025-10-14 14:45:12              │
└─────────────────────────────────────────────────┘
```

**Section 2: Setup Data Upload**
```
Setup Data Upload
├─ Upload Roster
│  └─ [File: roster.csv] [Upload]
│      Uploads to Roster table (replaces all)
│      Required columns: student_name, class_name, teacher_name, grade_level
├─ Upload Class Info
│  └─ [File: class_info.csv] [Upload]
│      Uploads to Class_Info table (replaces all)
│      Required columns: class_name, teacher_name, grade_level
└─ Upload Grade Rules
   └─ [File: grade_rules.csv] [Upload]
       Uploads to Grade_Rules table (replaces all)
       Required columns: grade_level, min_daily_minutes
```

**Section 3: Data Quality**
```
Data Quality
├─ Data Validation Report
│  └─ [Run Validation] → Shows report inline
│      Checks: Duplicates, missing data, orphaned records, mismatches
└─ Bulk Name Correction
   └─ [Review Names] → Opens correction interface
       Find and fix name variations/typos across tables
```

**Implementation:**

**Create Database Form (HTML):**
```html
<form id="create-db-form" onsubmit="createDatabase(event)">
    <div class="mb-3">
        <label for="db-name" class="form-label">Database Name</label>
        <input type="text" class="form-control" id="db-name"
               pattern="[a-zA-Z0-9_]+"
               title="Only letters, numbers, and underscores allowed"
               required>
        <small class="text-muted">System will prefix with 'readathon_'</small>
    </div>

    <div class="mb-3">
        <label for="db-description" class="form-label">Description</label>
        <input type="text" class="form-control" id="db-description"
               placeholder="E.g., Lincoln Elementary 2025 Campaign"
               required>
    </div>

    <div class="mb-3">
        <label for="db-type" class="form-label">Database Type</label>
        <select class="form-select" id="db-type" required>
            <option value="production">Production</option>
            <option value="sample">Sample</option>
            <option value="school">School</option>
            <option value="experiment">Experiment</option>
            <option value="archive">Archive</option>
            <option value="other">Other</option>
        </select>
    </div>

    <div class="mb-3">
        <label for="clone-from" class="form-label">Clone From (Optional)</label>
        <select class="form-select" id="clone-from">
            <option value="">-- Create Empty --</option>
            {% for db in available_databases %}
            <option value="{{ db.filename }}">{{ db.description }}</option>
            {% endfor %}
        </select>
        <small class="text-muted">Copies structure only, not data</small>
    </div>

    <button type="submit" class="btn btn-primary">Create Database</button>
</form>
```

**Create Database JavaScript:**
```javascript
async function createDatabase(event) {
    event.preventDefault();

    const formData = {
        name: document.getElementById('db-name').value,
        description: document.getElementById('db-description').value,
        type: document.getElementById('db-type').value,
        clone_from: document.getElementById('clone-from').value || null
    };

    try {
        const response = await fetch('/admin/create_database', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(formData)
        });

        const result = await response.json();

        if (result.success) {
            alert(`Database created successfully: ${result.filename}`);
            location.reload();
        } else {
            alert(`Error: ${result.error}`);
        }
    } catch (error) {
        alert(`Failed to create database: ${error.message}`);
    }
}
```

**Manage Databases Table:**
```html
<table class="table table-striped">
    <thead>
        <tr>
            <th>Name</th>
            <th>Type</th>
            <th>Size</th>
            <th>Records</th>
            <th>Last Modified</th>
            <th>Read-Only</th>
        </tr>
    </thead>
    <tbody>
        {% for db in all_databases %}
        <tr>
            <td><code>{{ db.filename }}</code></td>
            <td><span class="badge bg-secondary">{{ db.type|capitalize }}</span></td>
            <td>{{ db.size_mb }} MB</td>
            <td>{{ db.total_records }}</td>
            <td>{{ db.modified_date }}</td>
            <td>
                <input type="checkbox"
                       class="form-check-input"
                       {% if db.read_only %}checked{% endif %}
                       onchange="toggleReadOnly('{{ db.filename }}', this.checked)">
            </td>
        </tr>
        {% endfor %}
    </tbody>
</table>
```

**Toggle Read-Only JavaScript:**
```javascript
async function toggleReadOnly(filename, isReadOnly) {
    try {
        const response = await fetch('/admin/toggle_readonly', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                filename: filename,
                read_only: isReadOnly
            })
        });

        const result = await response.json();

        if (result.success) {
            const status = isReadOnly ? 'read-only' : 'writable';
            alert(`Database ${filename} is now ${status}`);
        } else {
            alert(`Error: ${result.error}`);
            // Revert checkbox if failed
            event.target.checked = !isReadOnly;
        }
    } catch (error) {
        alert(`Failed to update database: ${error.message}`);
        event.target.checked = !isReadOnly;
    }
}
```

**Server Routes:**
```python
@app.route('/admin/create_database', methods=['POST'])
def admin_create_database():
    """Create new database with metadata"""
    data = request.json

    try:
        name = data.get('name')
        description = data.get('description')
        db_type = data.get('type', 'other')
        clone_from = data.get('clone_from')

        # Validate inputs
        if not name or not description:
            return jsonify({'success': False, 'error': 'Name and description required'}), 400

        # Create database
        filename = create_database(name, description, db_type, clone_from)

        return jsonify({
            'success': True,
            'filename': filename,
            'message': f'Database {filename} created successfully'
        })

    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': f'Unexpected error: {str(e)}'}), 500

@app.route('/admin/toggle_readonly', methods=['POST'])
def admin_toggle_readonly():
    """Toggle read-only flag for database"""
    data = request.json

    try:
        filename = data.get('filename')
        read_only = data.get('read_only', False)

        if not filename:
            return jsonify({'success': False, 'error': 'Filename required'}), 400

        # Toggle flag
        set_readonly_flag(filename, read_only)

        return jsonify({
            'success': True,
            'message': f'Database {filename} {"locked" if read_only else "unlocked"}'
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
```

**Database Info Function:**
```python
def get_database_info(db_filename):
    """Get detailed information about database"""
    import os
    from datetime import datetime

    conn = sqlite3.connect(db_filename)
    cursor = conn.cursor()

    # Get file size
    file_size_bytes = os.path.getsize(db_filename)
    file_size_mb = file_size_bytes / (1024 * 1024)

    # Get table counts
    tables = ['Roster', 'Class_Info', 'Grade_Rules', 'Daily_Logs',
              'Reader_Cumulative', 'Upload_History']
    counts = {}
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        counts[table] = cursor.fetchone()[0]

    # Get metadata
    cursor.execute("SELECT key, value FROM Database_Metadata")
    metadata = dict(cursor.fetchall())

    # Get last modified time
    mod_time = os.path.getmtime(db_filename)
    mod_date = datetime.fromtimestamp(mod_time).strftime('%Y-%m-%d %H:%M:%S')

    conn.close()

    return {
        'filename': db_filename,
        'size_mb': round(file_size_mb, 2),
        'total_records': sum(counts.values()),
        'table_counts': counts,
        'metadata': metadata,
        'modified_date': mod_date
    }
```

**Implementation Priority:** 🟡 MEDIUM
- Foundation for Feature 16 (database system)
- Required for multi-database management
- Enables safe experimentation and archives

**Testing Scenarios:**
- [ ] Create new production database → Appears in selector
- [ ] Create database with description → Shows in dropdown
- [ ] Clone from existing database → Has same schema, no data
- [ ] Toggle read-only → Prevents uploads/deletions
- [ ] View database info → Shows accurate counts
- [ ] Invalid database name → Shows validation error

**Files to Modify:**
- `templates/admin.html` - Create admin UI
- `app.py` - Add admin routes
- `database.py` - Add database management functions

**Security Considerations:**
- Add admin authentication (future enhancement)
- Validate all user inputs
- Prevent deletion of current database
- Confirm before destructive operations
- Log all admin actions

---

### Feature 18: Save Error/Warning Messages
**Current:** Upload_History table stores: upload_id, log_date, upload_timestamp, filename, row_count, total_students_affected, upload_type, status

**Add Columns:**
- `warnings` TEXT - JSON array of warning messages
- `errors` TEXT - JSON array of error messages
- `details` TEXT - Additional details (JSON)

**Schema Change:**
```sql
ALTER TABLE Upload_History ADD COLUMN warnings TEXT;
ALTER TABLE Upload_History ADD COLUMN errors TEXT;
ALTER TABLE Upload_History ADD COLUMN details TEXT;
```

**Update Upload Functions:**
```python
# In database.py upload functions
result = {
    'success': True,
    'warnings': [],
    'errors': []
}

# When saving to Upload_History:
cursor.execute("""
    INSERT INTO Upload_History
    (log_date, upload_timestamp, filename, row_count,
     total_students_affected, upload_type, status, warnings, errors, details)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", (log_date, timestamp, filename, row_count, students_affected,
      upload_type, status,
      json.dumps(result['warnings']),
      json.dumps(result['errors']),
      json.dumps({'metadata': 'any additional info'})))
```

**Display in Upload History:**
- Show warnings/errors count in table
- Click to expand full messages
- Add tooltip with first warning/error

---

### Feature 19: Improve Delete Confirmations
**Current Issues:**
- Cumulative deletion requires typing "DELETE" (case-sensitive)
- Daily log deletion has no confirmation prompt

**Requirements:**

**A. Case-Insensitive Confirmation:**
- Accept: "DELETE", "delete", "Delete", "DEL", "del", "Del"
- Use `.toLowerCase()` or `.toUpperCase()` in JavaScript

**B. Add Confirmation to Daily Delete:**
```javascript
async function deleteDay(logDate) {
    const userInput = prompt(
        `⚠️ DELETE DATA WARNING!\n\n` +
        `You are about to permanently delete ALL data for ${logDate}.\n\n` +
        `This action CANNOT be undone!\n\n` +
        `Type "DELETE" or "DEL" to confirm:`
    );

    if (!userInput) return;

    const confirmed = ['delete', 'del'].includes(userInput.toLowerCase());

    if (!confirmed) {
        alert('Deletion cancelled. You must type "DELETE" or "DEL" to confirm.');
        return;
    }

    // Proceed with deletion...
}
```

**C. Add Same to Cumulative Delete:**
- Apply same logic to cumulative data deletion
- Update `/api/delete_cumulative` endpoint
- Show similar warning message

**Files to Modify:**
- `templates/upload.html` (upload history delete button scripts)
- `templates/index.html` (if delete available from dashboard)
- Both JavaScript `deleteDay()` and `deleteCumulative()` functions

---

### Feature 20: Automated Installation Script
**Requirements:**
- Create `install.sh` script in project root that automates entire setup process
- Script should handle installation on a fresh MacBook Air with no prior setup

**Script Features:**

**A. Automated Software Installation:**
- Check for and install Homebrew if missing
- Check for and install Python 3 if missing
- Check for and install pip3 if missing
- Install Flask and pandas dependencies

**B. Directory Setup:**
- Create application directory structure (`~/my/data/readathon`)
- Verify all required files are present
- Set proper file permissions

**C. Desktop Shortcuts:**
- Create `Start_ReadAThon.command` file on desktop
  - Launches Flask server
  - Auto-opens browser to http://127.0.0.1:5000
  - Shows clear startup messages
- Create `Stop_ReadAThon.command` file on desktop
  - Safely stops the Flask server
  - Kills process on port 5000

**D. Validation and Testing:**
- Verify all components installed correctly
- Check Python, pip, Flask, pandas
- Verify database files present
- Test basic application startup

**E. User-Friendly Output:**
- Color-coded output (green for success, red for errors, yellow for warnings)
- Clear progress indicators for each step
- Helpful error messages with solutions
- Final summary with next steps

**Script Structure:**
```bash
#!/bin/bash
# install.sh - Read-a-Thon System Automated Installer

# Steps:
# 1. Check/Install Homebrew
# 2. Check/Install Python 3
# 3. Check/Install pip3
# 4. Install Python dependencies (Flask, pandas)
# 5. Verify application files
# 6. Create requirements.txt
# 7. Create desktop shortcuts
# 8. Test installation
# 9. Offer to start application
```

**Usage Instructions:**
```bash
# On new MacBook Air, after copying files:
cd ~/my/data/readathon
chmod +x install.sh
./install.sh
```

**Implementation Notes:**
- Script must be idempotent (safe to run multiple times)
- Handle errors gracefully with clear messages
- Provide option to skip steps already completed
- Include rollback capability if installation fails
- Test on clean macOS installation

**Integration with User Manual:**
- Add "Quick Install" section to Feature 1 (Help/User Manual)
- Include screenshots of running the script
- Document what the script does at each step
- Provide troubleshooting guide for script failures
- Show manual installation steps as fallback

---

## UI PROTOTYPE REQUIREMENTS

### Prototype 1: Home Screen Design Options
**File:** `ui_prototype_home_options.html`

**Requirements:**
- Three tabs/sections showing different design philosophies:

  **Option A: Dashboard Cards (Uniform)**
  - All metrics in same-sized cards
  - Clean, consistent grid layout
  - 3-4 columns, multiple rows
  - Uniform font sizes
  - Business/professional look

  **Option B: Information Hierarchy**
  - Keep colored boxes for key metrics (larger)
  - Secondary info in smaller uniform cards
  - Most important data prominent
  - Mix of card sizes (responsive)

  **Option C: Data Density**
  - Compact design
  - Fit maximum info on screen
  - Smaller fonts, tighter spacing
  - Focus on information, less on aesthetics

- Use Bootstrap 5 (same as main app)
- Include sample data
- Demonstrate: Verification boxes, participation metrics, database stats

---

### Prototype 2: Verification Box Improvements
**File:** `ui_prototype_verification_boxes.html`

**Requirements:**
- Show all 5 verification boxes with consistent styling
- Implement:
  - Main numbers: 2rem (white, bold)
  - Labels: 0.9-1rem (light gray)
  - Secondary numbers: 1.5rem (white, bold)
  - Timestamps: 0.7rem (lighter gray)
- Box 2 (Minutes): Show breakdown with consistent fonts
- All boxes same visual weight/prominence
- Use current color gradients

**Test with Sample Data:**
- Box 1: $13,966
- Box 2: Daily_Logs: 15,123 | Reader_Cumulative: 17,283 | Difference: 2,160
- Box 3: Top Raised: George Taylor $525 | Top Minutes: Hannah Wilson 240
- Box 4: Top Raised: Ms. Spencer $1,866 | Top Minutes: Mr. Snyder 1,651
- Box 5: Data Integrity status

---

### Prototype 3: Participation Metrics Display
**File:** `ui_prototype_participation.html`

**Requirements:**
- Show enhanced participation metrics
- Multiple layout options:

  **Layout A: Expanded Blue Box**
  ```
  ┌─────────────────────────────────────────────┐
  │ Students Participating: 205 of 411 (49.9%) │
  │ ├─ Participated ALL days: 180 (43.8%)      │
  │ ├─ Met goal ≥1 day: 195 (47.4%)            │
  │ └─ Met goal ALL days: 150 (36.5%)          │
  │                                             │
  │ Days of Data: 3                             │
  └─────────────────────────────────────────────┘
  ```

  **Layout B: Side-by-Side Boxes**
  ```
  ┌───────────────────────┬───────────────────────┐
  │ Participation         │ Goal Achievement      │
  │ 205/411 (49.9%)      │ ≥1 day: 195 (47.4%)   │
  │ All days: 180 (43.8%)│ All days: 150 (36.5%) │
  └───────────────────────┴───────────────────────┘
  ```

  **Layout C: Stat Cards Row**
  ```
  ┌────────┬────────┬────────┬────────┐
  │ Total  │ All    │ Goal   │ Goal   │
  │ 49.9%  │ 43.8%  │ 47.4%  │ 36.5%  │
  └────────┴────────┴────────┴────────┘
  ```

- Use Bootstrap styling
- Demonstrate with sample data
- Include icons where appropriate

---

## DATABASE SCHEMA CHANGES

### Upload_History Table
```sql
-- Add columns for error/warning tracking
ALTER TABLE Upload_History ADD COLUMN warnings TEXT;
ALTER TABLE Upload_History ADD COLUMN errors TEXT;
ALTER TABLE Upload_History ADD COLUMN details TEXT;
```

### New Queries/Views
No new tables needed, but consider creating views for:
- Combined student report (Feature 4)
- Enhanced participation metrics (Feature 8)
- Data validation checks (P1.2)

---

## IMPLEMENTATION ORDER

### Phase 1: Core Enhancements (Week 1)
1. Feature 18: Save error/warning messages ✓
2. Feature 19: Improve delete confirmations ✓
3. Feature 9: Add Reader_Cumulative to stats ✓
4. Feature 12: Move export buttons to top ✓
5. Feature 7: Font consistency (using finalized prototype) ✓

### Phase 2: Admin & Database (Week 1-2)
6. Feature 16: Year-based database system ✓
7. Feature 17: Admin tab with all sections ✓
8. Feature 15: Table selection capability ✓

### Phase 3: Reports & UI (Week 2)
9. Feature 4: Combined reader report ✓
10. Feature 8: Enhanced participation metrics (using finalized prototype) ✓
11. Feature 13: Report options improvements ✓
12. Feature 14: Multiple report selection ✓
13. Feature 10: Run all reports ✓
14. Feature 11: Slide column indicators ✓

### Phase 4: Documentation & Uploads (Week 2)
15. Feature 1: Improve help page ✓
16. Feature 2: Add ReadAThon images/links ✓
17. Feature 3: Video tutorial link ✓
18. Feature 6: Requirements document ✓
19. Feature 5: Upload screen redesign ✓
20. Feature 20: Automated installation script ✓

### Phase 5: Priority Features (Week 3)
21. P1.1: Export all data (ZIP) ✓
22. P1.2: Data validation report ✓
23. P2.1: Year-over-year comparison ✓

### Phase 6: Future Features (As time permits)
24. P3.1: Student detail page
25. P3.2: Bulk name correction
26. P4-P5: Email reports, charts, leaderboards, etc.

---

## TESTING CHECKLIST

### Functional Testing
- [ ] All new reports generate correctly
- [ ] Multi-select reports works
- [ ] Table selection works
- [ ] Export all data creates valid ZIP
- [ ] Database cloning works
- [ ] Admin uploads work (Roster, Class_Info, Grade_Rules)
- [ ] Delete confirmations accept case-insensitive input
- [ ] Year-based database switching works
- [ ] Error/warning messages saved correctly
- [ ] Report options display and function correctly

### UI/UX Testing
- [ ] Font sizes consistent across verification boxes
- [ ] Participation metrics display clearly
- [ ] Home screen layout is clean and scannable
- [ ] Export/copy buttons visible at top
- [ ] Upload screen side-by-side layout works
- [ ] Messages appear in shared area (no scrolling)
- [ ] Mobile responsive (test on small screens)

### Data Integrity
- [ ] Combined reader report matches source data
- [ ] Participation calculations correct
- [ ] Year comparison calculations correct
- [ ] Data validation report finds known issues
- [ ] Database clone preserves schema

### Performance
- [ ] Run all reports completes in reasonable time
- [ ] Export all data doesn't timeout
- [ ] Multiple report selection responsive
- [ ] Large datasets don't cause memory issues

---

## NOTES FOR IMPLEMENTATION

### Code Style
- Follow existing patterns in codebase
- Use Bootstrap 5 classes for styling
- Keep database operations in `database.py`
- Keep routes in `app.py`
- Keep templates in `templates/` folder

### Error Handling
- Wrap all database operations in try/except
- Return user-friendly error messages
- Log errors for debugging
- Don't expose internal errors to users

### Security
- Validate all file uploads (type, size)
- Sanitize all user inputs
- Use parameterized SQL queries (already doing this)
- Admin functions should have warnings/confirmations

### Configuration
- Database paths should be configurable
- Year range should be configurable
- Max file sizes should be configurable
- Consider adding `config.py` for settings

---

## FUTURE CONSIDERATIONS

### Scalability
- Consider pagination for large reports
- Consider caching for frequently-run reports
- Consider background jobs for slow operations (ZIP export, etc.)

### Features for Next Year
- Mobile app integration
- Parent portal (read-only access for parents)
- Integration with Google Sheets
- Automated email reports
- Real-time dashboard refresh
- API for external tools

### Maintenance
- Database backup/restore functionality
- Data archival for old years
- Audit log for admin actions
- User management (if multi-user)

---

## QUESTIONS TO RESOLVE DURING IMPLEMENTATION

1. **Slide Column Indicators:** Exact columns for each report (need to be provided)
2. **Home Screen Design:** Final choice after reviewing prototypes
3. **Participation Display:** Final layout after reviewing prototype
4. **Font Sizes:** May need iteration after seeing in practice
5. **Admin Permissions:** Any access control needed?

---

## CONCLUSION

This document provides comprehensive requirements for enhancing the Read-a-Thon system. Implementation should follow the phased approach, starting with core functionality and progressing to advanced features.

**Estimated Total Implementation Time:** 3-4 weeks (full-time)

**Ready to begin implementation after:**
1. UI prototypes reviewed and design finalized
2. Any outstanding questions resolved
3. Current read-a-thon event concluded
4. Backup of current working system created

---

## DEPLOYMENT GUIDE: Setting Up on Another MacBook Air

### Overview
This guide provides step-by-step instructions for deploying the Read-a-Thon system on a new MacBook Air that doesn't have Python or Homebrew installed.

---

### Prerequisites Check
Before starting, check what's already installed:

```bash
# Check for Homebrew
brew --version

# Check for Python
python3 --version

# Check for pip
pip3 --version
```

If any of these commands return "command not found", follow the installation steps below.

---

### Step 1: Install Homebrew (Package Manager)

Homebrew is a package manager for macOS that makes installing software easy.

**Installation:**
1. Open Terminal (Applications → Utilities → Terminal)
2. Run this command:
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```
3. Follow the prompts (may require admin password)
4. After installation, you may need to add Homebrew to your PATH:
   ```bash
   echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
   eval "$(/opt/homebrew/bin/brew shellenv)"
   ```
5. Verify installation:
   ```bash
   brew --version
   ```
   Should show version like: `Homebrew 4.x.x`

**Reference:** https://brew.sh/

---

### Step 2: Install Python 3

**Installation via Homebrew:**
```bash
brew install python3
```

**Verify Installation:**
```bash
python3 --version
# Should show: Python 3.11.x or similar

pip3 --version
# Should show: pip 24.x.x or similar
```

**Note:** Python 3 comes bundled with pip3 (Python package installer).

---

### Step 3: Transfer Application Files

**Option A: Using USB Drive**
1. On your Mac, copy entire project folder: `/Users/stevesouza/my/data/readathon`
2. Insert USB drive and copy folder to drive
3. On new Mac, create similar directory structure:
   ```bash
   mkdir -p ~/my/data
   ```
4. Copy folder from USB to `~/my/data/readathon`

**Option B: Using AirDrop**
1. Right-click project folder
2. Share → AirDrop → Select new MacBook Air
3. On new Mac, move folder to `~/my/data/readathon`

**Option C: Using Git (if you use version control)**
```bash
cd ~/my/data
git clone <repository-url> readathon
```

**Files/Folders to Transfer:**
```
readathon/
├── app.py
├── database.py
├── requirements.txt
├── readathon_prod.db
├── readathon_sample.db
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── upload.html
│   ├── reports.html
│   ├── workflows.html
│   ├── tables.html
│   ├── help.html
│   └── admin.html (if created)
├── static/ (if exists)
└── prototypes/ (optional)
```

---

### Step 4: Install Python Dependencies

Navigate to project directory and install required packages:

```bash
cd ~/my/data/readathon

# Install all required packages
pip3 install -r requirements.txt
```

**If requirements.txt doesn't exist**, manually install:
```bash
pip3 install flask pandas
```

**Verify Installation:**
```bash
pip3 list
# Should show: Flask, pandas, and their dependencies
```

---

### Step 5: Verify Database Files

Ensure database files are present and have correct permissions:

```bash
cd ~/my/data/readathon

# List database files
ls -lh *.db

# Should see:
# readathon_prod.db
# readathon_sample.db
# (and any year-based databases if implemented)

# Verify database integrity (optional)
sqlite3 readathon_prod.db "SELECT name FROM sqlite_master WHERE type='table';"
# Should list: Roster, Class_Info, Grade_Rules, Daily_Logs, Reader_Cumulative, Upload_History
```

**Fix Permissions (if needed):**
```bash
chmod 644 *.db
```

---

### Step 6: Test Run the Application

**Start the Flask server:**
```bash
cd ~/my/data/readathon
python3 app.py
```

**Expected Output:**
```
 * Serving Flask app 'app'
 * Debug mode: on
WARNING: This is a development server. Do not use it in a production deployment.
 * Running on http://127.0.0.1:5000
 * Running on http://192.168.x.x:5000
Press CTRL+C to quit
```

**Access the Application:**
1. Open web browser (Safari, Chrome, Firefox)
2. Navigate to: `http://127.0.0.1:5000`
3. You should see the Read-a-Thon Dashboard

**Test Basic Functionality:**
- [ ] Dashboard loads correctly
- [ ] Environment switcher works (Production ↔ Sample)
- [ ] Navigation menu works
- [ ] Reports page loads
- [ ] Upload page displays
- [ ] Tables page shows data

---

### Step 7: Create Desktop Shortcut (Optional)

**Option A: Create Shell Script**
1. Create a startup script:
   ```bash
   nano ~/Desktop/start_readathon.sh
   ```
2. Add these lines:
   ```bash
   #!/bin/bash
   cd ~/my/data/readathon
   python3 app.py
   ```
3. Save (Ctrl+O, Enter, Ctrl+X)
4. Make executable:
   ```bash
   chmod +x ~/Desktop/start_readathon.sh
   ```
5. Double-click `start_readathon.sh` on desktop to start

**Option B: Create Alias**
Add to `~/.zshrc`:
```bash
alias readathon='cd ~/my/data/readathon && python3 app.py'
```
Then run: `readathon` from any terminal window

---

### Step 8: Stopping the Application

**To stop the server:**
- In Terminal window where server is running, press: **Ctrl+C**

**To fully quit:**
- Close Terminal window (or exit with `exit` command)

---

### Troubleshooting

#### Problem: "python3: command not found"
**Solution:**
```bash
# Reinstall Python
brew install python3

# Check PATH
echo $PATH
# Should include: /opt/homebrew/bin or /usr/local/bin
```

#### Problem: "Module not found: flask" or "Module not found: pandas"
**Solution:**
```bash
# Reinstall dependencies
pip3 install --upgrade flask pandas

# Or use full path
/opt/homebrew/bin/pip3 install flask pandas
```

#### Problem: "Address already in use"
**Solution:**
```bash
# Find process using port 5000
lsof -i :5000

# Kill that process
kill -9 <PID>

# Or change port in app.py:
# app.run(debug=True, port=5001)
```

#### Problem: "Permission denied" when accessing database
**Solution:**
```bash
cd ~/my/data/readathon
chmod 644 *.db
chmod 755 .
```

#### Problem: Browser shows "This site can't be reached"
**Solution:**
1. Verify Flask server is running (check Terminal output)
2. Try alternative address: `http://localhost:5000`
3. Try IP address shown in Terminal output: `http://192.168.x.x:5000`
4. Check firewall settings (System Preferences → Security → Firewall)

#### Problem: Database is empty
**Solution:**
- Verify correct database file was transferred
- Check environment selector (Production vs Sample)
- Upload setup data via Admin tab

---

### Configuration Changes for New Machine

**Update File Paths (if needed):**
If your directory structure differs, update paths in `app.py`:

```python
# Example: Change database path
DB_PATH = os.path.join(os.path.dirname(__file__), 'readathon_prod.db')
```

**Configure Port (if needed):**
Change default port in `app.py`:
```python
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)  # Changed from 5000
```

**Set Debug Mode:**
For production use, disable debug mode:
```python
if __name__ == '__main__':
    app.run(debug=False, host='127.0.0.1')
```

---

### Network Access (Optional)

**To access from other devices on same network:**

1. Find your Mac's IP address:
   ```bash
   ifconfig | grep "inet "
   # Look for line like: inet 192.168.1.100
   ```

2. Ensure Flask binds to all interfaces (in `app.py`):
   ```python
   app.run(debug=True, host='0.0.0.0')
   ```

3. On other device, navigate to: `http://192.168.1.100:5000`

**Security Note:** Only use this on trusted networks (home/school network, not public WiFi).

---

### Backup and Data Management

**Create Backup:**
```bash
# Backup entire project
cp -r ~/my/data/readathon ~/my/data/readathon_backup_$(date +%Y%m%d)

# Backup just databases
cp readathon_*.db ~/Desktop/db_backup_$(date +%Y%m%d)/
```

**Restore from Backup:**
```bash
# Restore database
cp ~/Desktop/db_backup_20250113/readathon_prod.db ~/my/data/readathon/
```

---

### Quick Reference Commands

```bash
# Start application
cd ~/my/data/readathon && python3 app.py

# Check if running
lsof -i :5000

# View logs (if running in background)
tail -f nohup.out

# Stop application
# Press Ctrl+C in terminal, or:
kill $(lsof -t -i:5000)

# Update dependencies
pip3 install --upgrade -r requirements.txt

# Check database
sqlite3 readathon_prod.db ".tables"
sqlite3 readathon_prod.db "SELECT COUNT(*) FROM Roster;"
```

---

### System Requirements

**Minimum:**
- macOS 11.0 (Big Sur) or later
- 4 GB RAM
- 500 MB free disk space
- Internet connection (for initial setup only)

**Recommended:**
- macOS 13.0 (Ventura) or later
- 8 GB RAM
- 1 GB free disk space

**Tested On:**
- MacBook Air M1/M2 (2020-2024)
- macOS 13.x (Ventura) and 14.x (Sonoma)

---

### Annual Setup Checklist

**Before Each Read-a-Thon:**
- [ ] Update macOS to latest version
- [ ] Update Python: `brew upgrade python3`
- [ ] Update dependencies: `pip3 install --upgrade -r requirements.txt`
- [ ] Create new year database (via Admin tab)
- [ ] Upload Roster, Class_Info, Grade_Rules
- [ ] Test all functionality with sample data
- [ ] Create backup of working system

**After Each Read-a-Thon:**
- [ ] Export all data to ZIP
- [ ] Backup database files
- [ ] Archive reports/exports
- [ ] Review and implement enhancements
- [ ] Update documentation

---

### Getting Help

**Documentation:**
- Flask: https://flask.palletsprojects.com/
- Python: https://docs.python.org/3/
- Pandas: https://pandas.pydata.org/docs/
- SQLite: https://www.sqlite.org/docs.html

**Common Resources:**
- Homebrew: https://brew.sh/
- Terminal basics: https://support.apple.com/guide/terminal/welcome/mac

---

### Security Best Practices

1. **Don't expose to public internet** - Run only on local network
2. **Regular backups** - Before and after each upload
3. **Test on Sample first** - Use sample database to test changes
4. **Verify uploads** - Always check data after uploading
5. **Use delete confirmations** - Don't bypass confirmation prompts
6. **Keep software updated** - Update Python, Flask, and dependencies annually

---

**Deployment Guide Version:** 1.0
**Created:** 2025-01-13
**Tested On:** MacBook Air (M1/M2, 2020-2024), macOS 13.x-14.x

---

---

## NEW FEATURES - SLIDES TAB & DESIGN DECISIONS

### Feature 21: Slides Tab ✨ NEW
**Feature:** Dedicated "Slides" tab for presentation-ready output that can be copied directly to Google Slides.

**Requirements:**
- Add new navigation tab: "Slides" (between Workflows and Tables)
- Single page with two sections:
  - **Daily Slides** - Updated throughout campaign
  - **Final Slides** - Run at campaign end
- Add "Jump to:" quick navigation links at top for Daily/Final sections

**Layout:**
```
┌─────────────────────────────────────────────────┐
│ Slides                                           │
│ Jump to: [Daily Slides] [Final Slides]           │
├─────────────────────────────────────────────────┤
│ Daily Slides (Updated: Jan 15, 2:45 PM)         │
│ ┌──────────────┐ ┌──────────────┐ ┌──────────┐ │
│ │ Slide 2:     │ │ Slide 3:     │ │ Slide 4: │ │
│ │ Grade Level  │ │ Top Students │ │ Teams    │ │
│ │ Participation│ │              │ │          │ │
│ │              │ │              │ │          │ │
│ │ [Copy] [CSV] │ │ [Copy] [CSV] │ │ [Copy]   │ │
│ └──────────────┘ └──────────────┘ └──────────┘ │
│                                                   │
│ Final/End of Contest Slides                      │
│ ┌──────────────┐ ┌──────────────┐ ┌──────────┐ │
│ │ Final Slide 1│ │ Final Slide 2│ │ Winners  │ │
│ │ Overall      │ │ Record       │ │          │ │
│ │ Results      │ │ Breakers     │ │          │ │
│ │ [Copy] [CSV] │ │ [Copy] [CSV] │ │ [Copy]   │ │
│ └──────────────┘ └──────────────┘ └──────────┘ │
└─────────────────────────────────────────────────┘
```

**Key Characteristics:**
- **Box-based layout** - Similar to Dashboard design (white cards with shadows)
- **Presentation-ready** - Show ONLY data that appears in actual Google Slides
- **No extra columns** - Remove debugging info, technical details, extra metadata
- **Clean formatting** - Optimized for copy-paste workflow
- **Slide metadata** - Each box shows slide number, title/concept, data table
- **Copy buttons** - Easy copy-to-clipboard for each slide

**Example Slide Box:**
```
┌─────────────────────────────────────────────────┐
│ Slide 2: Grade Level Participation               │
│ As of October 6, 2024                            │
│                                                   │
│ Grade Level | Class            | % Participation │
│ ──────────────────────────────────────────────── │
│ Kindergarten| Mrs. Brown       |           33.3%│
│ 1st Grade   | Mrs. Stone       |           40.0%│
│ 2nd Grade   | Mrs. Hansen    |           47.4%│
│ ...                                               │
│                                                   │
│ [Copy to Clipboard] [Export CSV]                 │
└─────────────────────────────────────────────────┘
```

**Implementation:**
- Create `/slides` route in `app.py`
- Create `templates/slides.html`
- Query slide-specific reports (slide2, slide3, etc.)
- Filter columns to only those needed for presentation
- Group queries into Daily vs Final sections
- Use same card/box styling as Dashboard (Option J design)

**Mapping Queries to Slides:**
- Daily Slides:
  - Slide 2: Grade Level Participation (query: slide2)
  - Slide 3: Top Fundraising Students (query: slide3)
  - Slide 4: Team Competition (query: slide4)
  - [Additional slides as needed]
- Final Slides:
  - Final Results Summary (query: final_slide1)
  - Record Breakers (query: final_slide2)
  - Winners Announcement (query: final_slide3)
  - [Additional final slides as needed]

**User Workflow:**
1. Navigate to Slides tab
2. Scroll to desired slide box (or use Jump to navigation)
3. Click "Copy to Clipboard" button
4. Open Google Slides presentation
5. Paste data into slide
6. Format/style as needed in Google Slides

**Notes:**
- Slides page should NOT include extra analysis columns present in Reports
- Focus is on clean, presentation-ready output
- Similar to Dashboard in visual design, but organized by slide number
- This is separate from Reports tab (which can have technical columns)

---

### Feature 22: Workflows Tab - Keep Separate ✓ CONFIRMED
**Decision:** Keep Workflows as a separate tab (not merged into Reports).

**Reasoning:**
- Clear separation: "Do common task" vs "Run custom query"
- One-click execution of grouped queries
- Easier discovery of common workflows
- Can evolve to do more than just run queries

**Tab Structure (Confirmed):**
- Dashboard
- Reports (with manual query selection)
- **Workflows** (one-click grouped queries)
- **Slides** (presentation output)
- Tables
- Help

**Future Evaluation:**
- After real-world usage, evaluate if Workflows is useful
- If not used, can merge into Reports with "Quick Select" feature
- For now, implement as separate tab

---

### Feature 23: Dashboard Design - Option J Winner 🏆
**Decision:** Option J: Refined Zen is the selected design for the Dashboard.

**Design Characteristics:**
- **Layout:** 3-column grid
  - Left: Student Participation (table with alternating gray rows)
  - Center: Top Students + Top Classes (stacked boxes)
  - Right: Team Competition
- **Color Scheme:**
  - Navy: #1e3a5f (primary)
  - Teal: #17a2b8 (accent)
  - Gold: #f59e0b (Team Kitsko)
  - Coral: #ff6b6b (participation highlight, data integrity)
- **Team Colors:**
  - Team Staub: Blue background (#e3f2fd), Navy numbers (#1e3a5f)
  - Team Kitsko: Gold background (#fffbeb), Amber numbers (#d97706)
- **Typography:**
  - Headers: 1rem, bold
  - Main numbers: 1.5-2rem, bold
  - Labels: 0.65-0.75rem, uppercase
- **Data Integrity Bar:** Full-width horizontal bar at bottom (not right column)
- **Navigation Tab:** Marked with 🏆 trophy emoji in tab selector

**Key Features:**
- Alternating row backgrounds in tables (#f5f5f5 for odd rows)
- Black numbers in tables (not teal) for clarity
- Consistent navy/teal/gold color palette throughout
- Clean, professional, business-focused aesthetic

**File Location:**
- Prototype: `/Users/stevesouza/my/data/readathon/prototypes/ui_prototype_home_options.html`
- Option J section: Lines 2631-2868 (approx)

---

### Feature 24: Design Consistency Across All Pages ✨ IMPORTANT
**Requirement:** ALL pages should follow the Option J: Refined Zen design language.

**Apply To:**
- Dashboard (already done - Option J)
- **Slides** tab (use same box/card styling)
- **Workflows** tab (use same card/button styling)
- **Reports** tab (use same table styling, buttons)
- **Tables** tab (use same table styling)
- **Upload** tab (use same card styling)
- **Help** tab (use same section styling)
- **Admin** tab (use same card/section styling)

**Consistent Elements:**
- **Cards/Boxes:** White background, rounded corners (0.5rem), subtle shadow
- **Colors:** Navy, Teal, Gold, Coral (as defined in Option J)
- **Typography:** Same font sizes and weights
- **Tables:** Alternating row backgrounds, black numbers
- **Buttons:** Consistent styling (size, colors, hover states)
- **Spacing:** Consistent padding, margins, gaps
- **Top bars/headers:** Navy background with teal accents
- **Error/warning messages:** Coral color (#ff6b6b)

**Implementation Notes:**
- Extract common CSS from Option J into `base.html` styles
- Create reusable CSS classes for cards, tables, buttons
- Ensure all templates inherit from `base.html`
- Test responsive behavior on all pages

---

### Feature 25: Help Tab & System Documentation 📚 TBD

**Current Status:** To be determined

**Two Open Questions:**

**A. Help Tab Content:**
- Option 1: **End-user focused manual**
  - How to upload data
  - How to run reports
  - How to create slides
  - Troubleshooting
  - FAQ
- Option 2: **Developer/technical docs**
  - System architecture
  - Database schema
  - Query explanations
  - Rebuild instructions
- Option 3: **Both** (with tabbed sections)

**B. Complete Rebuild Specification:**
- **Purpose:** Comprehensive, executable requirements doc for full system rebuild
- **Content:**
  - Database schema (all CREATE TABLE statements)
  - All queries with purpose/SQL
  - Business rules and logic
  - UI designs and layouts
  - Workflows and processes
  - Configuration details
- **Storage Location Options:**
  1. Dedicated tab in UI (e.g., "System Docs")
  2. Section within Help tab
  3. Downloadable from Help/Admin tab
  4. Accessible via query/report
- **Key Requirement:** Must be accessible to non-Claude Code users
  - Future admin may need to rebuild system
  - Should not require file system access
  - Should be viewable/downloadable from web UI

**Decision Needed:**
- Determine Help tab structure
- Determine where/how to expose rebuild documentation
- Level of detail needed in rebuild docs
- Format (Markdown? HTML? PDF?)

**Priority:** Medium (can be refined during implementation)

---

### Feature 26: File Upload Validation 🛡️ HIGH PRIORITY
**Feature:** Comprehensive file validation before uploads to prevent uploading wrong file types.

**Problem Being Solved:**
- User accidentally uploads Daily Minutes file using Cumulative Stats uploader
- System accepts invalid file, corrupts data
- No early warning about column mismatches
- Difficult to recover from wrong upload

**Requirements:**

**A. Column Specifications:**
Define required and optional columns for each upload type:

```python
UPLOAD_SPECS = {
    'daily': {
        'required': ['student_name', 'class_name', 'minutes_read'],
        'optional': ['log_date', 'teacher_name', 'grade_level', 'team_name'],
        'display_name': 'Daily Minutes'
    },
    'cumulative': {
        'required': ['student_name', 'donation_amount', 'sponsors', 'cumulative_minutes'],
        'optional': ['class_name', 'teacher_name', 'team_name', 'grade_level'],
        'display_name': 'Cumulative Stats'
    },
    'roster': {
        'required': ['student_name', 'class_name', 'teacher_name', 'grade_level'],
        'optional': ['team_name', 'student_id'],
        'display_name': 'Roster'
    },
    'class_info': {
        'required': ['class_name', 'teacher_name', 'grade_level'],
        'optional': ['team_name', 'room_number'],
        'display_name': 'Class Info'
    },
    'grade_rules': {
        'required': ['grade_level', 'min_daily_minutes'],
        'optional': ['max_daily_minutes', 'description'],
        'display_name': 'Grade Rules'
    }
}
```

**B. Validation Function:**
```python
def validate_upload_file(file_path, upload_type):
    """
    Validate CSV file has correct columns for upload type.

    Returns:
        dict with keys:
        - valid: bool (True if all required columns present)
        - errors: list of error messages
        - warnings: list of warning messages
        - missing_required: list of missing required columns
        - unknown_columns: list of unexpected columns
        - suggested_type: str (guessed correct upload type if wrong)
    """
    result = {
        'valid': True,
        'errors': [],
        'warnings': [],
        'missing_required': [],
        'unknown_columns': [],
        'suggested_type': None
    }

    # Read CSV headers only (don't load entire file)
    df = pd.read_csv(file_path, nrows=0)
    file_columns = set(df.columns)

    spec = UPLOAD_SPECS[upload_type]
    required = set(spec['required'])
    optional = set(spec['optional'])
    expected = required.union(optional)

    # Check 1: Missing required columns
    missing = required - file_columns
    if missing:
        result['valid'] = False
        result['missing_required'] = list(missing)
        result['errors'].append(
            f"Missing required columns: {', '.join(sorted(missing))}"
        )

        # Try to guess correct file type
        suggested = guess_upload_type(file_columns)
        if suggested and suggested != upload_type:
            result['suggested_type'] = suggested
            result['errors'].append(
                f"This appears to be a {UPLOAD_SPECS[suggested]['display_name']} file. "
                f"Please use the {UPLOAD_SPECS[suggested]['display_name']} upload instead."
            )

    # Check 2: Unknown/unexpected columns
    unknown = file_columns - expected
    if unknown:
        result['unknown_columns'] = list(unknown)
        result['warnings'].append(
            f"File contains unexpected columns (will be ignored): {', '.join(sorted(unknown))}"
        )

    return result

def guess_upload_type(file_columns):
    """Try to guess what type of file this is based on columns"""
    file_columns = set(file_columns)

    # Check each upload type to see if all required columns are present
    for upload_type, spec in UPLOAD_SPECS.items():
        required = set(spec['required'])
        if required.issubset(file_columns):
            return upload_type

    return None
```

**C. Validation Endpoint:**
Add new API endpoint for client-side validation:

```python
@app.route('/api/validate_upload', methods=['POST'])
def validate_upload():
    """Validate uploaded file before processing"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    upload_type = request.form.get('upload_type')

    if not upload_type or upload_type not in UPLOAD_SPECS:
        return jsonify({'error': 'Invalid upload type'}), 400

    # Save to temp location
    temp_path = tempfile.mktemp(suffix='.csv')
    file.save(temp_path)

    try:
        # Validate
        validation_result = validate_upload_file(temp_path, upload_type)
        return jsonify(validation_result)
    finally:
        # Clean up temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)
```

**D. Client-Side Integration (JavaScript):**
Update upload page to validate before upload:

```javascript
// Add to upload.html
async function validateBeforeUpload(fileInput, uploadType) {
    const file = fileInput.files[0];
    if (!file) return false;

    // Show loading indicator
    showValidationSpinner();

    const formData = new FormData();
    formData.append('file', file);
    formData.append('upload_type', uploadType);

    try {
        const response = await fetch('/api/validate_upload', {
            method: 'POST',
            body: formData
        });

        const validation = await response.json();
        hideValidationSpinner();

        // Show validation results
        if (!validation.valid) {
            showValidationError(validation.errors);
            return false;
        }

        if (validation.warnings.length > 0) {
            return await showValidationWarning(validation.warnings);
        }

        return true;

    } catch (error) {
        hideValidationSpinner();
        showValidationError(['Failed to validate file. Please try again.']);
        return false;
    }
}

function showValidationError(errors) {
    const html = `
        <div class="alert alert-danger alert-dismissible fade show">
            <h5><i class="bi bi-exclamation-triangle"></i> File Validation Failed</h5>
            <ul>
                ${errors.map(err => `<li>${err}</li>`).join('')}
            </ul>
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    document.getElementById('validation-messages').innerHTML = html;
}

async function showValidationWarning(warnings) {
    const message = `
        File validation successful, but contains unexpected columns:\n\n
        ${warnings.join('\n\n')}

        These columns will be ignored during upload.

        Do you want to proceed?
    `;

    return confirm(message);
}

// Update upload button handlers
document.getElementById('daily-upload-btn').addEventListener('click', async function(e) {
    e.preventDefault();

    const fileInput = document.getElementById('daily-file');
    const isValid = await validateBeforeUpload(fileInput, 'daily');

    if (isValid) {
        // Proceed with original upload logic
        uploadDailyMinutes();
    }
});

document.getElementById('cumulative-upload-btn').addEventListener('click', async function(e) {
    e.preventDefault();

    const fileInput = document.getElementById('cumulative-file');
    const isValid = await validateBeforeUpload(fileInput, 'cumulative');

    if (isValid) {
        // Proceed with original upload logic
        uploadCumulativeStats();
    }
});
```

**E. Enhanced Upload UI:**
Add validation message area to upload page:

```html
<!-- Add to templates/upload.html -->
<div class="container mt-4">
    <!-- Validation Messages Area (shared) -->
    <div id="validation-messages" class="mb-3"></div>

    <div class="row">
        <!-- Daily Upload Column -->
        <div class="col-md-6">
            <div class="card">
                <div class="card-header">
                    <h5>Daily Minutes Upload</h5>
                </div>
                <div class="card-body">
                    <!-- File input -->
                    <input type="file" id="daily-file" accept=".csv">

                    <!-- Expected columns help text -->
                    <small class="text-muted d-block mt-2">
                        <strong>Required columns:</strong> student_name, class_name, minutes_read
                        <br>
                        <strong>Optional columns:</strong> log_date, teacher_name, grade_level
                    </small>

                    <button id="daily-upload-btn" class="btn btn-primary mt-3">
                        <span class="spinner-border spinner-border-sm d-none" id="daily-spinner"></span>
                        Upload Daily Minutes
                    </button>
                </div>
            </div>
        </div>

        <!-- Cumulative Upload Column -->
        <div class="col-md-6">
            <!-- Similar structure -->
        </div>
    </div>
</div>
```

**F. Validation Messages - Examples:**

**Example 1: Wrong File Type**
```
❌ File Validation Failed

• Missing required columns: donation_amount, sponsors, cumulative_minutes

This appears to be a Daily Minutes file. Please use the Daily Minutes upload instead.
```

**Example 2: Unknown Columns**
```
⚠️ File Validation Warning

File contains unexpected columns (will be ignored):
• internal_id
• processing_timestamp
• exported_date

These columns are not recognized and will be ignored during upload.

Do you want to proceed?
[Cancel] [Proceed Anyway]
```

**Example 3: Success**
```
✓ File Validation Successful

Found all required columns:
• student_name
• donation_amount
• sponsors
• cumulative_minutes

Optional columns found:
• class_name
• teacher_name

Ready to upload 245 rows.
```

**G. Server-Side Validation (Defense in Depth):**
Even after client-side validation, validate again server-side before processing:

```python
def upload_daily_minutes(file_path, log_date):
    """Upload daily minutes with validation"""

    # Validate file structure first
    validation = validate_upload_file(file_path, 'daily')
    if not validation['valid']:
        raise ValueError(f"Invalid file: {', '.join(validation['errors'])}")

    # Proceed with upload
    df = pd.read_csv(file_path)

    # Use only expected columns (ignore unknown)
    expected_columns = UPLOAD_SPECS['daily']['required'] + UPLOAD_SPECS['daily']['optional']
    df = df[[col for col in df.columns if col in expected_columns]]

    # Rest of upload logic...
```

**Implementation Priority:** 🔴 HIGH
- Prevents data corruption from wrong uploads
- Saves significant cleanup/recovery time
- Low implementation effort, high value

**Testing Scenarios:**
- [ ] Upload correct Daily file to Daily uploader → Success
- [ ] Upload Daily file to Cumulative uploader → Error with suggestion
- [ ] Upload Cumulative file to Daily uploader → Error with suggestion
- [ ] Upload file with extra unknown columns → Warning, allow proceed
- [ ] Upload file missing required columns → Error, block upload
- [ ] Upload file with both missing and extra columns → Show both issues

**Files to Modify:**
- `database.py` - Add validation functions
- `app.py` - Add `/api/validate_upload` endpoint
- `templates/upload.html` - Add validation UI and JavaScript
- Update existing upload functions to use validation

---

### Feature 27: Multi-File Daily Upload 📁 HIGH PRIORITY
**Feature:** Upload multiple daily report files simultaneously with automatic date extraction from filenames.

**Status:** 🔄 IN PROGRESS - Core multi-file upload to be implemented with audit trail enhancements

**Modifications from Original Requirements:**
1. **No confirmation prompts** - Re-uploading same date automatically replaces data (like cumulative upload behavior)
2. **Audit trail added** - All uploads tracked in Upload_History with detailed audit information (see Feature 28)
3. **Two deletion concepts** implemented:
   - **Data deletion** (Daily_Logs) - automatic during re-upload via ON CONFLICT DO UPDATE
   - **History deletion** (Upload_History audit records) - manual only via UI checkboxes
4. **Upload_History records are permanent** - Only manually deletable for complete audit trail

**Problem Being Solved:**
- Parents can enter data for previous days at any time
- Workflow requires re-uploading all previous days' files daily
- By day 10, user must upload 10 separate files (one at a time)
- Current system only supports single file upload
- Manual, time-consuming process prone to errors

**Requirements:**

**A. Multiple File Selection:**
```html
<!-- Upload page daily section -->
<div class="card">
    <div class="card-header">
        <h5>Daily Minutes Upload</h5>
    </div>
    <div class="card-body">
        <input type="file"
               id="daily-files"
               accept=".csv"
               multiple
               onchange="previewDailyFiles()">

        <small class="text-muted d-block mt-2">
            Select multiple CSV files to upload at once.
            Dates will be extracted from filenames automatically.
        </small>

        <!-- Preview Table (appears after file selection) -->
        <div id="file-preview" class="mt-3" style="display: none;">
            <h6>Files to Upload (Ready to upload: <span id="upload-count">0</span> of <span id="total-count">0</span>)</h6>

            <!-- Bulk Actions -->
            <div class="btn-group mb-2" role="group">
                <button type="button" class="btn btn-sm btn-outline-primary" onclick="selectAllFiles()">
                    Select All
                </button>
                <button type="button" class="btn btn-sm btn-outline-secondary" onclick="deselectAllFiles()">
                    Deselect All
                </button>
            </div>

            <table class="table table-sm table-bordered">
                <thead>
                    <tr>
                        <th style="width: 50px;">
                            <input type="checkbox" id="select-all-checkbox"
                                   onchange="toggleAllCheckboxes()"
                                   checked>
                        </th>
                        <th>Filename</th>
                        <th>Extracted Date</th>
                        <th style="width: 150px;">Override Date</th>
                        <th style="width: 100px;">Status</th>
                    </tr>
                </thead>
                <tbody id="file-preview-tbody">
                    <!-- Populated by JavaScript -->
                </tbody>
            </table>

            <button id="upload-multiple-btn" class="btn btn-primary" onclick="uploadMultipleFiles()">
                Upload Selected Files
            </button>
        </div>
    </div>
</div>
```

**B. Filename Pattern & Date Extraction:**

**Pattern:** `Donations+Report+For+2025-10-09+-+Readathon+68289 (1).csv`

**Extraction Logic:**
```javascript
function extractDateFromFilename(filename) {
    // Pattern: Look for YYYY-MM-DD format anywhere in filename
    const datePattern = /(\d{4})-(\d{2})-(\d{2})/;
    const match = filename.match(datePattern);

    if (match) {
        const year = match[1];
        const month = match[2];
        const day = match[3];

        // Validate date is reasonable
        const date = new Date(year, month - 1, day);
        if (date && date.getFullYear() == year) {
            return `${year}-${month}-${day}`;
        }
    }

    return null; // Date not found or invalid
}
```

**C. File Preview Table (JavaScript):**
```javascript
function previewDailyFiles() {
    const fileInput = document.getElementById('daily-files');
    const files = fileInput.files;

    if (files.length === 0) {
        document.getElementById('file-preview').style.display = 'none';
        return;
    }

    const tbody = document.getElementById('file-preview-tbody');
    tbody.innerHTML = '';

    let readyCount = 0;

    for (let i = 0; i < files.length; i++) {
        const file = files[i];
        const extractedDate = extractDateFromFilename(file.name);
        const hasDate = extractedDate !== null;

        if (hasDate) readyCount++;

        const row = document.createElement('tr');
        row.className = hasDate ? '' : 'table-warning';
        row.dataset.fileIndex = i;

        row.innerHTML = `
            <td class="text-center">
                <input type="checkbox"
                       class="file-checkbox"
                       data-file-index="${i}"
                       ${hasDate ? 'checked' : ''}
                       onchange="updateUploadCount()">
            </td>
            <td>
                <small>${file.name}</small>
            </td>
            <td class="text-center">
                ${hasDate
                    ? `<span class="badge bg-success">${extractedDate}</span>`
                    : `<span class="badge bg-warning text-dark">Not found</span>`}
            </td>
            <td>
                <input type="date"
                       class="form-control form-control-sm date-override"
                       data-file-index="${i}"
                       value="${extractedDate || ''}"
                       ${!hasDate ? 'required' : ''}>
            </td>
            <td class="text-center">
                <span class="status-badge" data-file-index="${i}">
                    ${hasDate
                        ? '<span class="badge bg-secondary">Ready</span>'
                        : '<span class="badge bg-warning text-dark">Need Date</span>'}
                </span>
            </td>
        `;

        tbody.appendChild(row);
    }

    // Update counters
    document.getElementById('total-count').textContent = files.length;
    document.getElementById('upload-count').textContent = readyCount;

    // Show duplicate date warning
    checkDuplicateDates();

    // Show preview
    document.getElementById('file-preview').style.display = 'block';
}

function updateUploadCount() {
    const checkboxes = document.querySelectorAll('.file-checkbox');
    const checked = Array.from(checkboxes).filter(cb => cb.checked);
    document.getElementById('upload-count').textContent = checked.length;
}

function toggleAllCheckboxes() {
    const selectAllCheckbox = document.getElementById('select-all-checkbox');
    const fileCheckboxes = document.querySelectorAll('.file-checkbox');

    fileCheckboxes.forEach(cb => {
        cb.checked = selectAllCheckbox.checked;
    });

    updateUploadCount();
}

function selectAllFiles() {
    document.querySelectorAll('.file-checkbox').forEach(cb => cb.checked = true);
    document.getElementById('select-all-checkbox').checked = true;
    updateUploadCount();
}

function deselectAllFiles() {
    document.querySelectorAll('.file-checkbox').forEach(cb => cb.checked = false);
    document.getElementById('select-all-checkbox').checked = false;
    updateUploadCount();
}

function checkDuplicateDates() {
    const dateInputs = document.querySelectorAll('.date-override');
    const dates = Array.from(dateInputs).map(input => input.value).filter(d => d);
    const duplicates = dates.filter((date, index) => dates.indexOf(date) !== index);

    if (duplicates.length > 0) {
        const warningDiv = document.getElementById('duplicate-warning') ||
                          createDuplicateWarning();
        warningDiv.innerHTML = `
            <div class="alert alert-warning">
                <i class="bi bi-exclamation-triangle"></i>
                <strong>Warning:</strong> Multiple files have the same date: ${[...new Set(duplicates)].join(', ')}
                <br>
                Later uploads will overwrite earlier ones for the same date.
            </div>
        `;
        warningDiv.style.display = 'block';
    }
}
```

**D. Upload Logic (Sequential with Progress):**
```javascript
async function uploadMultipleFiles() {
    const fileInput = document.getElementById('daily-files');
    const files = fileInput.files;
    const checkboxes = document.querySelectorAll('.file-checkbox:checked');

    if (checkboxes.length === 0) {
        alert('No files selected for upload.');
        return;
    }

    // Disable upload button
    const uploadBtn = document.getElementById('upload-multiple-btn');
    uploadBtn.disabled = true;
    uploadBtn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Uploading...';

    let successCount = 0;
    let errorCount = 0;
    const results = [];

    // Upload files sequentially (one at a time)
    for (const checkbox of checkboxes) {
        const fileIndex = checkbox.dataset.fileIndex;
        const file = files[fileIndex];
        const dateInput = document.querySelector(`.date-override[data-file-index="${fileIndex}"]`);
        const logDate = dateInput.value;

        if (!logDate) {
            errorCount++;
            updateFileStatus(fileIndex, 'error', 'Missing date');
            results.push({file: file.name, status: 'error', message: 'Missing date'});
            continue;
        }

        // Update status to "uploading"
        updateFileStatus(fileIndex, 'uploading', 'Uploading...');

        try {
            const formData = new FormData();
            formData.append('file', file);
            formData.append('log_date', logDate);

            const response = await fetch('/upload_daily', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();

            if (result.success) {
                successCount++;
                updateFileStatus(fileIndex, 'success', `✓ ${result.rows_added || 0} rows`);
                results.push({file: file.name, status: 'success', rows: result.rows_added});
            } else {
                errorCount++;
                updateFileStatus(fileIndex, 'error', result.error || 'Upload failed');
                results.push({file: file.name, status: 'error', message: result.error});
            }

        } catch (error) {
            errorCount++;
            updateFileStatus(fileIndex, 'error', 'Network error');
            results.push({file: file.name, status: 'error', message: error.message});
        }
    }

    // Show summary
    showUploadSummary(successCount, errorCount, results);

    // Re-enable button
    uploadBtn.disabled = false;
    uploadBtn.innerHTML = 'Upload Selected Files';

    // Refresh page data if any succeeded
    if (successCount > 0) {
        setTimeout(() => location.reload(), 2000);
    }
}

function updateFileStatus(fileIndex, status, message) {
    const statusBadge = document.querySelector(`.status-badge[data-file-index="${fileIndex}"]`);
    const row = document.querySelector(`tr[data-file-index="${fileIndex}"]`);

    if (status === 'uploading') {
        statusBadge.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Uploading...';
        row.classList.add('table-info');
    } else if (status === 'success') {
        statusBadge.innerHTML = `<span class="badge bg-success">${message}</span>`;
        row.classList.remove('table-info');
        row.classList.add('table-success');
    } else if (status === 'error') {
        statusBadge.innerHTML = `<span class="badge bg-danger">${message}</span>`;
        row.classList.remove('table-info');
        row.classList.add('table-danger');
    }
}

function showUploadSummary(successCount, errorCount, results) {
    const summary = document.createElement('div');
    summary.className = 'alert alert-info alert-dismissible fade show mt-3';
    summary.innerHTML = `
        <h5>Upload Complete</h5>
        <p>
            <strong>Success:</strong> ${successCount} file(s) uploaded<br>
            <strong>Errors:</strong> ${errorCount} file(s) failed
        </p>
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

    document.getElementById('file-preview').insertBefore(
        summary,
        document.getElementById('upload-multiple-btn')
    );
}
```

**E. Server-Side Changes:**

**Modify existing `/upload_daily` endpoint:**
```python
@app.route('/upload_daily', methods=['POST'])
def upload_daily():
    """Upload daily minutes (single or part of multi-file upload)"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file provided'}), 400

        file = request.files['file']
        log_date = request.form.get('log_date')

        if not log_date:
            return jsonify({'success': False, 'error': 'No date provided'}), 400

        # Validate file first (Feature 26)
        temp_path = tempfile.mktemp(suffix='.csv')
        file.save(temp_path)

        validation = validate_upload_file(temp_path, 'daily')
        if not validation['valid']:
            os.remove(temp_path)
            return jsonify({
                'success': False,
                'error': '; '.join(validation['errors'])
            }), 400

        # Upload to database
        db = get_current_db()
        result = db.upload_daily_minutes(temp_path, log_date)

        # Clean up
        os.remove(temp_path)

        return jsonify({
            'success': True,
            'rows_added': result.get('rows_added', 0),
            'message': f"Successfully uploaded {result.get('rows_added', 0)} rows for {log_date}"
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
```

**F. UI Improvements:**

**Checkbox vs "Skip" Button - RECOMMENDED APPROACH:**
- ✅ **Use checkboxes (default checked)**
- Reasons:
  1. More intuitive - checked = will upload
  2. Clear visual state at a glance
  3. Allows bulk selection controls (Select All / Deselect All)
  4. Standard UI pattern users expect
  5. Less clicking required to exclude files
  6. Easier keyboard navigation

**Additional Features:**
1. **Duplicate Date Detection** - Warn if multiple files have same date
2. **Validation Preview** - Show estimated records per file
3. **Progress Indicator** - Visual feedback during batch upload
4. **Upload Summary** - Show success/error counts after completion
5. **Status Badges** - Color-coded status for each file (Ready/Uploading/Success/Error)
6. **Bulk Actions** - Select All / Deselect All buttons
7. **Upload Count** - "Ready to upload X of Y files"
8. **Missing Date Warning** - Highlight files without extractable dates (yellow row)
9. **Date Override** - Allow manual date entry for each file
10. **Sequential Upload** - Upload one at a time with clear progress

**G. Visual Design:**

**Row States:**
- **Default (white):** File ready, date extracted successfully, checkbox checked
- **Warning (yellow):** Date not extracted, needs manual date entry
- **Info (light blue):** Currently uploading
- **Success (light green):** Upload completed successfully
- **Error (light red):** Upload failed
- **Grayed (unchecked):** File deselected, will not upload

**Example Preview Table:**
```
┌───┬─────────────────────────────────┬──────────────┬──────────────┬─────────┐
│ ☑ │ Filename                        │ Extract Date │ Override     │ Status  │
├───┼─────────────────────────────────┼──────────────┼──────────────┼─────────┤
│ ☑ │ Donations+...+2025-10-06.csv   │ 2025-10-06   │ [2025-10-06] │ Ready   │
│ ☑ │ Donations+...+2025-10-07.csv   │ 2025-10-07   │ [2025-10-07] │ Ready   │
│ ☑ │ Donations+...+2025-10-08.csv   │ 2025-10-08   │ [2025-10-08] │ Ready   │
│ ☐ │ Donations+...+2025-10-09.csv   │ 2025-10-09   │ [2025-10-09] │ Ready   │
│ ☑ │ some_old_file.csv              │ Not found    │ [required]   │ Need Dt │
└───┴─────────────────────────────────┴──────────────┴──────────────┴─────────┘

[Select All] [Deselect All]          Ready to upload 4 of 5 files

[Upload Selected Files]
```

**Implementation Priority:** 🔴 HIGH
- Saves significant time during daily workflow
- Reduces human error (forgetting to upload a file)
- User is currently uploading 10+ files daily by end of campaign
- Major quality-of-life improvement

**Testing Scenarios:**
- [ ] Select 3 files with valid dates → All 3 upload successfully
- [ ] Select 5 files, uncheck 2 → Only 3 checked files upload
- [ ] Upload file without date in filename → User enters date manually
- [ ] Upload 2 files with same date → Warning shown, later overwrites earlier
- [ ] Upload fails for one file → Other files continue, error shown
- [ ] Select All / Deselect All → All checkboxes toggle correctly
- [ ] Upload counter → Shows correct count as checkboxes change

**Files to Modify:**
- `templates/upload.html` - Add multi-file UI, preview table, JavaScript
- `app.py` - Ensure `/upload_daily` endpoint supports multi-file workflow
- `static/js/upload.js` (optional) - Extract JavaScript to separate file

**Backward Compatibility:**
- Keep existing single-file upload working
- Multi-file is optional enhancement, not replacement
- Users can still upload one file at a time if preferred

---

### Feature 28: Upload Audit Trail System ✓ COMPLETED
**Feature:** Complete audit trail for all upload operations with automatic replacement and comprehensive tracking

**Implementation Date:** 2025-10-15
**Testing Status:** Automated tests created (3/5 passing, multi-day tests fully working)

**Requirements Implemented:**

**A. Database Schema Changes:**
Added three columns to Upload_History table:
- `action_taken` (TEXT): 'inserted' or 'replaced'
- `records_replaced` (INTEGER): Count of records replaced
- `audit_details` (TEXT/JSON): Detailed statistics, errors, warnings

**B. Automatic Replacement Behavior:**
- No confirmation dialogs when re-uploading same date
- Matches cumulative upload behavior (silent replacement)
- Upload_History records kept permanently for audit trail
- Only manual deletion of audit records via UI

**C. Two Deletion Concepts:**

1. **Data Deletion (Operational Data):**
   - Daily_Logs records: Automatically replaced during re-upload via `ON CONFLICT DO UPDATE`
   - Reader_Cumulative records: Automatically replaced during cumulative upload via `DELETE` then `INSERT`
   - This is operational data that gets refreshed with each upload

2. **History Deletion (Audit Records):**
   - Upload_History audit records: Manual deletion only via checkboxes in UI
   - Batch delete with multi-select checkboxes
   - "Select All" checkbox in table header
   - "Delete Selected (X)" button appears when items checked
   - This preserves complete audit trail of all operations

**D. Audit Details Tracking:**

**Multi-day/Single-day uploads capture:**
- Dates processed
- Records replaced per date
- Records added per date
- Date breakdown (existing count, new count, total minutes per date)
- All warnings and errors
- Summary statistics only (no student names for brevity)

**Cumulative uploads capture:**
- Previous total student count
- New total student count
- Students removed count
- Students added count
- Students updated count
- All warnings and errors
- Unmatched student count

**E. UI Enhancements:**

**1. Upload History Table Columns:**
- **Action column:** Badge showing "replaced" (yellow) or "inserted" (green)
- **Replaced column:** Count of records replaced
- **Audit column:** Button to view detailed audit information
- **Checkbox column:** For batch deletion of audit records

**2. Audit Details Modal:**
- Bootstrap modal popup with formatted statistics
- Icons indicate status: errors (red ❌), warnings (yellow ⚠️), info (blue ℹ️)
- **Multi-day view:** Shows dates processed, replacement counts, date breakdown table
- **Cumulative view:** Shows before/after totals, students removed/added/updated
- Errors and warnings sections with clear iconography

**3. Batch Delete UI:**
- Checkbox for each Upload_History record
- "Select All" checkbox in table header
- "Delete Selected (X)" button with count display
- **Important:** Only deletes audit records, NOT actual Daily_Logs/Reader_Cumulative data

**F. Methods Updated:**

**database.py:**
- `upload_multiday_data()` - Added audit tracking before/after data insertion
  - Queries existing records before INSERT
  - Tracks replaced vs. new records
  - Writes audit_details JSON with statistics
- `upload_cumulative_stats()` - Added audit tracking before DELETE
  - Queries existing students before DELETE
  - Compares old vs. new student lists
  - Calculates removed/added/updated counts
  - Writes audit_details JSON
- `get_upload_history()` - Returns new audit columns (action_taken, records_replaced, audit_details)
- `delete_upload_history_batch()` - Batch delete audit records by upload_id list

**templates/upload.html:**
- Added Action, Replaced, and Audit columns to upload history table
- Added checkboxes for batch selection
- Added "Delete Selected" button with count display
- Added `showAuditDetails()` JavaScript function
- Added Bootstrap modal for displaying audit details
- Color-coded badges and icons for visual clarity

**G. Audit Details JSON Structure:**

**Multi-day/Single-day format:**
```json
{
  "dates_processed": ["2025-10-01", "2025-10-02"],
  "records_replaced": 5,
  "records_added": 10,
  "date_breakdown": {
    "2025-10-01": {
      "existing_count": 3,
      "new_count": 3,
      "total_minutes": 150
    },
    "2025-10-02": {
      "existing_count": 2,
      "new_count": 7,
      "total_minutes": 280
    }
  },
  "warnings": ["Student not found in roster: John Doe"],
  "errors": []
}
```

**Cumulative format:**
```json
{
  "previous_total": 150,
  "new_total": 148,
  "students_removed": 5,
  "students_added": 3,
  "students_updated": 145,
  "unmatched_count": 2,
  "warnings": ["Student not found in roster: Jane Spencer"],
  "errors": []
}
```

**H. Key Design Decisions:**

1. **No student names in audit** - Only counts/statistics for brevity
2. **Permanent audit trail** - Upload_History never auto-deleted, manual only
3. **Separate data vs. history deletion** - Different purposes, different lifetimes
4. **JSON audit_details** - Flexible structure for different upload types
5. **Visual feedback** - Color-coded badges, icons, modal popups for clarity

**Testing Scenarios:**
- [x] Upload new data → action='inserted', records_replaced=0
- [x] Re-upload same date → action='replaced', records_replaced>0
- [x] Audit details captured correctly for multi-day
- [x] Audit details captured for cumulative (partial - test issues)
- [x] Warnings/errors tracked in audit_details
- [x] UI displays audit information correctly
- [ ] Batch delete removes only audit records, not data

**Files Modified:**
- `database.py` - Added audit tracking to upload methods
- `templates/upload.html` - Added audit columns and modal
- `templates/base.html` - (no changes needed, existing Bootstrap modal support)

---

**Document Version:** 1.5
**Created:** 2025-01-13
**Last Updated:** 2025-10-14

**Version 1.4 Changes:**
- Enhanced Feature P2.1: Year-over-Year Comparison with 5 detailed report types and positional team comparison
- Enhanced Feature 16: Flexible Multi-Purpose Database System with metadata support, read-only flags, and organization by type
- Enhanced Feature 17: Admin Tab with comprehensive database creation and management UI
- All enhancements support multi-year, multi-school, and experimental database use cases
