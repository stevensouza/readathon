# Read-a-Thon Application Rules

**Last Updated:** 2026-09-23

This file contains universal rules that apply across all pages and features in the Read-a-Thon application. These rules MUST be followed for every implementation.

---

## Data Source Rules (ALWAYS TRUE)

### Primary Data Sources
- **Classes/Students:** `Roster` table (columns: `student_name`, `teacher_name`, `grade_level`, `team_name`, `class_name`)
- **Reading Minutes:** `Daily_Logs` table (capped at 120 minutes/day, includes color bonus)
- **Participation:** `Daily_Logs` table (students with >0 minutes for a given day)
- **Goals Met:** `Daily_Logs` table (students who met ≥1 day reading goal)
- **Fundraising/Sponsors:** `Reader_Cumulative` table (aggregated totals per student, latest upload)
- **Fundraising as of a past day:** `Reader_Cumulative_History` (one saved copy of the cumulative upload per contest day - see Scoreboards)
- **Team Assignments:** `Roster.team_name` column

### Data Calculation Rules
- **Minutes are ALWAYS capped at 120/day** for contest calculations
- **Color war bonus points MUST always be included** in minute totals
- **Participation % = (students with >0 minutes) / (total students in class/grade/school)**
- **Goals Met = count of students who achieved reading goal ≥1 day**

### Contest Period
- **Defined by the data:** the range is the first..last date uploaded to `Daily_Logs` (2025: 10 days, Oct 10-19)
- **Start date and length may vary** between years - never hard-code dates or timestamps
- **Out-of-range dates:** Cause reconciliation differences (tracked in reports Q21-Q23)

### Roster Name Matching (uploads)
Parents type their child's name on read-a-thon.com, so uploads contain first names only ("Mateo"), nicknames
("Joey Lambert" for Joseph Lambert), typos and case differences. A name that isn't a `Roster.student_name` counts for
**no class, grade or team** (those reports start from `Roster`), but still counts in school-wide totals that read
`Daily_Logs`/`Reader_Cumulative` directly - so every name must be fixed or left out. Code: `name_matching.py`.
- **Stored names are always roster spellings.** Uploads translate each name before saving, so every query keeps
  comparing names exactly (no case-insensitive SQL needed).
- **Order (`NameMatcher.resolve`):** exact roster name → saved correction (`Name_Alias`) → the only roster name that
  differs just in capitals/spaces/punctuation (automatic, reported as info) → unmatched (imported under the typed name
  with a "Student not found in roster" warning; cumulative rows get team `ERROR: NO ROSTER MATCH`).
- **An unmatched name is saved with its teacher: "Ellie (Hart)"** (`unmatched_label` / `split_unmatched_label`), so
  two unmatched "Ellie"s in different classes stay two rows, and matching them later knows the class (Daily_Logs has
  no teacher column). Q23 and the Students page show that label.
- **Corrections (`Name_Alias`) are keyed by uploaded name + teacher**, both compared ignoring case/spacing (teacher
  also without Mr./Mrs./Ms.: "Mrs. Delgado" = "delgado"). Two kids typed "Ellie" in different classes map to different
  students. `student_name` NULL = not a roster student: those rows are left out of uploads.
- **Check before upload:** the Upload page posts the files to `/api/check_upload_names` (saves nothing). Unmatched
  names are shown in a **Match names to the roster** panel with suggestions (`NameMatcher.suggest`).
  Wording on the page (avoid "check"/"pre-check" - it reads like "examine"): **Accept** = the tick box (accepted rows are
  saved as name corrections and used for this upload and every later one); **Strong match** = accepted for you;
  **Possible match** = suggested, not accepted; **Your choice**; **No match found**; **Not a roster student**.
- **Strong match** only when it's the only strong match (first name only, nickname + same last name, near-identical
  spelling, same first + last name) **in the same class** and that student has no data of their own in the upload.
  Same last name with an unrelated first name (preferred name or sibling?), another teacher's student, two possible
  students, or a student who already has their own row are **possible matches**.
- **After the fact:** `/api/unmatched_names` lists names already saved that aren't roster names (with their minutes and
  money). The Upload page shows them in an alert at the top ("N uploaded names are not on the roster") with **Match names
  to the roster** (same panel; saving moves their data) and a link to the Q23 report.
- **Changing or deleting a correction** affects uploads from then on. Data already moved stays with the earlier student
  until those days are uploaded again (daily files for those days + the latest cumulative file).
- **Saving a correction moves data already saved** under that name (Daily_Logs, Reader_Cumulative,
  Reader_Cumulative_History), adding to the student's row if there is one. Only that class's rows move ("Ellie (Hart)",
  not "Ellie (Kim)").
- **Duplicates are summed** (as before). read-a-thon.com's readers report lists an empty placeholder row
  (PageCreated = No, all zeros) beside a student's real page, so a duplicate warning only appears when 2+ rows have data.
- **A daily upload replaces everything saved for its date** (the file is the whole day from read-a-thon.com), so a
  changed or deleted correction leaves nothing stale behind once the day is uploaded again.
- `Name_Alias` belongs to the roster: `clear_all_data.py` keeps it (Admin → Clear Tables can clear it).

---

## Team Rules

### Team Color Assignment
**CRITICAL:** Team colors are determined by **alphabetical order (ascending)**, NOT by database order or team ID.

- **Team 1 (alphabetically first)** = **Blue** (`#1e3a5f`)
- **Team 2 (alphabetically second)** = **Yellow/Amber** (`#f59e0b`)

**Examples:**
- If teams are "Kitsko" and "Staub": Kitsko = Blue, Staub = Yellow
- If teams are "Phoenix" and "Dragons": Dragons = Blue, Phoenix = Yellow
- If sample DB uses "team1" and "team2": team1 = Blue, team2 = Yellow

### Team Color Consistency
- **Apply to ALL team representations:** ovals, rectangles, badges, buttons, highlights
- **Must be consistent across ALL pages:** school, teams, grade level, students, reports
- **CSS classes must follow this pattern:**
  - `.team-badge-kitsko`, `.team-badge-team1`, `.leader-badge-kitsko` → Blue
  - `.team-badge-staub`, `.team-badge-team2`, `.leader-badge-staub` → Yellow

---

## Visual Design Rules

### Winner Highlights
- **Gold ovals** = School-wide winners (best across ALL grades)
- **Silver ovals** = Grade-level/Team-level winners (best within filtered group)
- **Gold overrides silver:** If a class is both school and grade winner, show GOLD only

### Table Styling
- **Headers:** Dark blue background (`#1e3a5f`), white text, sortable with cursor:pointer
- **Rows:** Alternating white and light gray (`table-striped` in Bootstrap)
- **Hover:** Light highlight on row hover for better UX

### Page Layout Order (Card-Based Pages)
All card-based pages (School, Teams, Grade Level, Students) MUST follow this order:
1. **Filter Period dropdown** (centered, with label "📅 Filter Period:")
2. **Data Info & Sources button** (collapsible footer at bottom of page)
3. **Banner** (6 headline metrics in consistent order across all pages)
4. **Middle Section Cards** (grade/team cards with top performers)
5. **Detail Table** (sortable, filterable data table)

### Banner Metrics - Standard 6-Metric Structure
**CRITICAL:** All three pages (School, Teams, Grade Level) use the EXACT SAME 6 metrics in the SAME ORDER:

1. **📅 Campaign Day** - Status metric (no team competition)
   - Format: "X of Y" (e.g., "Day 3 of 10")
   - Subtitle: Current date or date range
   - Filter: Does NOT respect date filter (always shows full campaign status)

2. **💰 Fundraising** - Total donations raised
   - Format: $X,XXX (no decimals)
   - Subtitle: Varies by page (e.g., "Top Class: TeacherName - $1,234")
   - Filter: Does NOT respect date filter (cumulative from Reader_Cumulative)

3. **📚/📖 Minutes Read** - Total reading minutes
   - Format: X,XXX hours (converted from minutes)
   - Subtitle: Varies by page (e.g., "Avg per Student: 45 hours")
   - Filter: Respects date filter ◐
   - Icon: 📚 on School/Teams pages, 📖 on Grade Level page

4. **🎁 Sponsors** - Total sponsor commitments
   - Format: X,XXX count (SUM of all sponsor_count values from Reader_Cumulative)
   - Subtitle: "X of Y Students have sponsors (Z%)" where X = students with at least 1 sponsor
   - Filter: Does NOT respect date filter (cumulative from Reader_Cumulative)
   - Icon: 🎁 (NOT 🤝)
   - **Calculation:** Main value is TOTAL sponsors (SUM), subtitle shows student count
   - Example: "28 sponsors" main value, "7 of 411 students (1.7%)" subtitle

5. **👥 Avg. Participation (With Color)** - Average daily participation + color bonus
   - Format: X.X% (1 decimal place)
   - Subtitle: Varies by page (e.g., "Top Class: TeacherName - 85.3%")
   - Filter: Respects date filter ◐
   - Formula: (days_read / (students * days)) * 100 + (color_points / (students * days)) * 100
   - **Special Rule: CAN EXCEED 100%** if all students read all days AND team has color war points
   - Example: 10 students read 10/10 days = 100%, + 5 color points = 105%

6. **🎯 Goal Met (≥1 Day)** - Students who met daily goal at least once
   - Format: X.X% (1 decimal place)
   - Subtitle: "X of Y students"
   - Filter: Respects date filter ◐

### Participation Metrics - Two Different Calculations

The application uses **TWO distinct participation metrics**. DO NOT confuse them:

#### 1. Participation % (Simple Cumulative)
- **Formula:** `(students_who_participated / total_students) * 100`
- **Definition:** Percentage of students who read >0 minutes at least once in the date range
- **Used in:**
  - Grade Level classes table "PARTICIPATION %" column
  - Teams comparison table "Participation %" row
- **Example:** 80 out of 100 students participated = 80%
- **Does NOT include:** Color war bonus points
- **Does NOT reflect:** Daily participation patterns or consistency

#### 2. Avg. Participation (With Color)
- **Formula:**
  ```
  base_avg = (total_days_read / (team_size * days_in_range)) * 100
  color_adj = (color_war_points / (team_size * days_in_range)) * 100
  result = base_avg + color_adj
  ```
- **Definition:** Average daily participation rate + color bonus points
- **Used in:**
  - All 3 page banners (School, Teams, Grade Level)
  - Teams comparison table "Avg. Participation (With Color)" row
  - Grade Level classes table "AVG. PARTICIPATION (WITH COLOR)" column
- **Example:** 10 students read 5 days each out of 10 days = 50%, plus 2 color points = 52%
- **Includes:** Color war bonus points
- **Reflects:** Daily participation patterns (average across all days in range)
- **Special Rule:** Can exceed 100% if all students read all days AND team has color points

#### Why Two Metrics?

**Simple Participation %:**
- Shows breadth: "What percentage of students participated at all?"
- Binary: Either a student participated (1) or didn't (0)
- Useful for: Comparing class engagement levels

**Avg. Participation (With Color):**
- Shows depth + consistency: "How consistently did students participate day-to-day?"
- Continuous: Reflects daily participation patterns
- Includes color bonus as incentive
- Useful for: Measuring sustained engagement + team spirit

**Key Difference:**
- A class with 100% Simple Participation (all students read once) might have 50% Avg. Participation (if they only read half the days)
- Avg. Participation rewards consistent daily reading + team color spirit

### Team Badges
- **Shape:** Rounded rectangles with padding
- **Colors:** Follow team color rules (blue for team 1, yellow for team 2)
- **Border:** Subtle border matching team color (semi-transparent)
- **Text:** Uppercase team name, contrasting color for readability

---

## Editable Database (read-only protection)

- Exactly **one** database is editable; it is stored in the registry's `App_Settings` (`editable_database_id`,
  `DatabaseRegistry.get_editable_database_id()` / `set_editable_database()`), not in `.readathon_config`.
- It is **independent of the database being viewed**: switching (selector, Activate, `--db`) never changes it.
  Change it only in Admin → Database Registry → Make Editable, or by creating a new database (`make_editable`, on by default).
- Until one is chosen, the newest registered `readathon_YYYY.db` is picked and saved. Sample follows the same rules
  (read-only unless made editable). If the chosen database is unregistered, nothing is editable; the editable
  database can't be unregistered.
- **Every route that writes to a contest database must use `@require_editable_db`** (`app.py`): it returns 403
  `{read_only: true, error}` when the viewed database isn't the editable one. Currently: `upload_daily`,
  `upload_cumulative`, `upload_team_color_bonus`, `delete_day`, `delete_cumulative`, `delete_upload_history_batch`,
  `clear_tables`, `save_name_aliases`, `delete_name_alias`. CLI scripts (`clear_all_data.py`, `init_data.py`) are not guarded.
- Tests that write through these routes use the `make_editable(db_id)` fixture (`tests/conftest.py`) so the real
  registry's setting is never changed.

---

## State Management & Persistence

### Sticky Filters (Cross-Page)
All filters persist across page navigation until explicitly changed by the user.

1. **Database Selector** (Application-Wide)
   - Persistence: `.readathon_config` file (server-side)
   - Scope: All pages (navigation bar in base.html)
   - Restored: Automatically on server startup

2. **Filter Period / Date Filter** (Browser Session)
   - Persistence: `sessionStorage.setItem('readathonDateFilter', value)`
   - Scope: School, Teams, Grade Level, Students pages
   - Restored: On page load via sessionStorage

3. **Grade Level Filter** (Browser Session)
   - Persistence: `sessionStorage.setItem('readathonGradeFilter', value)`
   - Scope: Grade Level and Students pages
   - Restored: On page load via sessionStorage

4. **Team Filter** (Browser Session)
   - Persistence: `sessionStorage.setItem('readathonTeamFilter', value)`
   - Scope: Grade Level and Students pages
   - Restored: On page load via sessionStorage

### Filter Restoration Pattern
```javascript
// On page load:
const savedFilter = sessionStorage.getItem('readathonDateFilter');
if (savedFilter) {
    document.getElementById('dateFilter').value = savedFilter;
    // Apply filter to data
}

// On filter change:
sessionStorage.setItem('readathonDateFilter', newValue);
```

---

## Banner Calculation Rules

### School-Wide Leaders
- **Must calculate from ALL classes** (not filtered subset)
- **Use `class_name`, NOT `teacher_name`** (handles teachers with multiple classes)
- **Must include color bonus in minutes** calculations

### Example: Handling Multi-Class Teachers
```python
# CORRECT - Group by class_name
GROUP BY ci.class_name, ci.teacher_name, ci.grade_level

# WRONG - Group by teacher_name (aggregates multiple classes)
GROUP BY ci.teacher_name, ci.grade_level
```

---

## Bulletins: Scoreboards (Feature 39) and Meet the Teams (Feature 41)

The **📰 Bulletins** menu (named "Scoreboards" until v2026.17.0; URLs, `scoreboards.py` and the `_scoreboard_*`
templates keep the old name): Meet the Teams (`/scoreboards/teams`), Daily Scoreboard (`/scoreboards/daily`) and
Prize Scoreboard (`/scoreboards/prize`). Data code: `scoreboards.py`.

### Contest days and "as of"
- **Day N = the Nth date uploaded to `Daily_Logs`.** Skipped weekends never appear, so no start/end dates are stored.
- **"Day N of T":** T = the `contest_days` setting (Admin → Actions → Bulletin Settings, default 10), never less
  than the days uploaded. The Prize Scoreboard shows "Final Prize Winners" once the as-of day reaches T.
- **Reading data** (minutes, participation, goals, color bonus) counts through day N (`log_date <= day N`,
  `event_date <= day N`). **The latest day counts the whole contest**, so it matches the Reports page exactly.
- The source methods take `as_of_date=None` (default = whole contest, unchanged Reports results).

### Money as of a day (snapshots)
- Every cumulative upload is also saved in `Reader_Cumulative_History` under a **snapshot date** (Upload page;
  defaults to the latest `Daily_Logs` date because the Day N file is often uploaded the morning of Day N+1).
- **The latest upload for a day wins:** re-uploading for the same date replaces that day's whole copy (not a merge).
- Money for day N comes **only from day N's snapshot**. No snapshot → "Not available\*" with a footnote, and no
  trophy for that row. Never carry an older day's money forward.
- When the table is first added to an existing database, the current `Reader_Cumulative` becomes the snapshot for
  its last contest date (how 2025 got its final totals).
- "+$ today" = snapshot(day N) − snapshot(day N−1), shown only when both exist.

### Definitions
- **Team participation / Showdown participation:** Avg. Participation (With Color) (Q14 formula) through day N.
- **Minutes:** capped at 120/day plus color-bonus minutes through day N (Q19).
- **Today's participation %:** students with minutes > 0 that day + that day's color-bonus points, ÷ team size
  (can exceed 100% on a color day). **+minutes today:** capped minutes that day + that day's bonus minutes.
- **Medallion (daily):** % of students with minutes > 0 on at least one day (not "goal met ≥1 day").
- **Medallion (prize):** distinct students winning any student prize (Top Earner, Top Minutes/Donations/Sponsors, Goal Getters).
- **Class prizes are per class (`class_name`), not per teacher.** A half-day kindergarten teacher's AM and PM classes
  compete separately. Any class named "<teacher> am/pm" is shown as "Teacher AM" / "Teacher PM" (even a teacher with
  a single half-day class). Ties: every tied class/student wins.
- **Daily drawing:** N winners per grade (Admin → Bulletin Settings → "Drawing winners per grade", 1-5, default **2**
  since the 2026 event; 1 before) from students who met their grade goal that day, picked with a seed of
  (date, grade, drawing #). Same drawing # → same winners; "Redraw" bumps the # (in the URL, printed in the header).
  A grade with fewer goal-meeters than N gets them all. The bulletin shows one row per grade, names stacked.
  - **Saved winners (`Drawing_Winners`, key date + grade + student):** "Save winners" (editable database only) stores
    that day's winners; a saved day always shows them, whatever `?draw=` says or the setting is now, and hides Redraw.
    Unsaved days are a *preview* (recomputed each load, with the current setting). The server draws again when
    saving - winner names never come from the browser.
  - **Read-only databases never draw:** a random preview of a past year isn't who really won, so they show the saved
    winners, or "Prize winners were not saved for Day N." in place of the table.
  - **Win once per contest:** the preview leaves out every student saved as a winner on *any other* day (only saved
    winners count - an unsaved preview never excludes anyone).
  - **Fallback:** students who haven't won are drawn first; if fewer than N are left in a grade, the remaining spots
    are drawn from that day's goal-meeters who already won. Those rows store `fallback = 1` and a note shows in the
    toolbar (not in the copied image).
  - **Clear is per day:** "Clear saved winners (Day N)" deletes only that day; its winners become eligible again in
    other days' previews, and other days' saved winners never change.
  - Q4 on the Reports page is unchanged (unseeded, ignores saved winners).
- **Showdown:** the registry database whose `year` = this year − 1, using its own Nth contest date (final vs final
  on the Prize Scoreboard's final view). Hidden when there is no prior-year database. Always the **last section** of
  both bulletins (on the Prize Scoreboard, below Goal Getters).
- **School name:** `school_name` setting (registry, not tracked files); masthead "{school} Read-a-Thon", or
  "Read-a-Thon" when unset.

### Meet the Teams (Feature 41)
`/scoreboards/teams` (📰 Bulletins → Meet the Teams). **Roster only** - no reading data, so it works before day 1.
- Student counts are `COUNT(*)` from `Roster` per class (`SELECT_TEAM_CLASS_COUNTS`), not `Class_Info.total_students`.
- One row per class (`class_name`), labeled like the scoreboards (`class_label`: "Teacher AM" / "Teacher PM"), sorted
  by grade (K first) then label. Teams use the same alphabetical navy/gold sides (`team_sides`); with other than two
  teams the matchup and rosters are replaced by a note.
- Year in the masthead ("Meet the {year} Teams") = the event year (registry year, else first contest date).
- Copy/Download capture at `pixel_ratio=3` (sharp when printed or zoomed); the scoreboards stay at 2.

### Scoreboard page tests
The 8 mandatory page tests apply with the scoreboard components standing in for the dashboard ones: team panels
(`score-panel team-blue/team-gold`) for team badges, `win-trophy-badge` for winning-value ovals, and the masthead +
medallion for the headline banner. See `tests/test_scoreboards_page.py`. Meet the Teams has no percentages, money or
winners, so those checks are replaced by roster counts verified against SQL (`TestMeetTheTeamsPage`).

---

## UI Consistency Principles

### Before Implementing ANY New Feature:
1. **Check existing pages** (school.html, teams.html, grade_level.html) for similar elements
2. **Match established patterns** for tables, cards, banners, filters
3. **Use the same CSS classes** and styling for similar data representations
4. **Maintain consistent spacing, colors, fonts** with existing pages

### When Displaying Similar Data:
- If data has been displayed elsewhere (even for different entity), use the SAME visual treatment
- Example: If fundraising is shown in a green card on School page, use green card for fundraising on Students page

### General Design Principle:
**"Be consistent. Always."** - Check existing implementations before creating new ones.

---

## Testing Requirements

### All Pages Must Have Tests
**CRITICAL:** Every user-facing page (School, Teams, Grade Level, Students, etc.) MUST have a corresponding pytest test suite before being deployed or committed.

### Test File Naming Convention
- File: `test_<page_name>_page.py`
- Class: `Test<PageName>Page`
- Example: `test_school_page.py` contains `class TestSchoolPage`

### Mandatory Tests for ALL Pages
Every page test suite MUST include these tests:

1. **test_page_loads_successfully** - Verify HTTP 200 response
   ```python
   def test_page_loads_successfully(self, client):
       response = client.get('/page_route')
       assert response.status_code == 200
       assert b'Read-a-Thon System' in response.data
   ```

2. **test_no_error_messages** - Scan for error patterns
   ```python
   def test_no_error_messages(self, client):
       response = client.get('/page_route')
       html = response.data.decode('utf-8')
       error_patterns = ['Error:', 'Exception:', 'Traceback', 'error occurred']
       html_lower = html.lower()
       for pattern in error_patterns:
           assert pattern.lower() not in html_lower
   ```

3. **test_percentage_formats** - Validate all percentages
   ```python
   def test_percentage_formats(self, client):
       response = client.get('/page_route')
       html = response.data.decode('utf-8')
       percentages = re.findall(r'(\d+\.?\d*)%', html)
       assert len(percentages) > 0
       for pct in percentages:
           float(pct)  # Should not raise ValueError
   ```

4. **test_currency_formats** - Validate all dollar amounts
   ```python
   def test_currency_formats(self, client):
       response = client.get('/page_route')
       html = response.data.decode('utf-8')
       currencies = re.findall(r'\$[\d,]+\.?\d*', html)
       assert len(currencies) > 0
       for curr in currencies:
           value = curr.replace('$', '').replace(',', '')
           float(value)  # Should not raise ValueError
   ```

5. **test_sample_data_integrity** - Verify DB calculations
   ```python
   def test_sample_data_integrity(self, client, sample_db):
       response = client.get('/page_route')
       html = response.data.decode('utf-8')
       # Query expected values from database
       # Verify they appear in HTML
   ```

6. **test_team_badges_present** - Verify team color consistency
   ```python
   def test_team_badges_present(self, client):
       response = client.get('/page_route')
       html = response.data.decode('utf-8')
       assert 'team-badge' in html
   ```

7. **test_winning_value_highlights** - Check gold/silver ovals
   ```python
   def test_winning_value_highlights(self, client):
       response = client.get('/page_route')
       html = response.data.decode('utf-8')
       assert 'winning-value' in html
   ```

8. **test_headline_banner** - Validate banner structure
   ```python
   def test_headline_banner(self, client):
       response = client.get('/page_route')
       html = response.data.decode('utf-8')
       assert 'headline-banner' in html or 'headline-metric' in html
   ```

### Page-Specific Tests
In addition to mandatory tests, each page should have tests for:
- Page-specific UI elements (cards, tables, filters)
- Page-specific functionality (grade filter, date filter)
- Page-specific data calculations

### Running Tests Before Commit
**MANDATORY:** All tests MUST pass before creating a commit.

### ⚠️ CRITICAL: When Creating New Test Files

**YOU MUST UPDATE THE PRE-COMMIT HOOK FILE IMMEDIATELY!**

When you create a new test file (e.g., `test_reports_page.py`), you MUST:

1. **Add the test file to `.git/hooks/pre-commit`**
2. **Update the test count comment in the pre-commit hook**
3. **Run the pre-commit hook manually to verify it works**

**Location:** `.git/hooks/pre-commit` (lines 11-22)

**Example of what to update:**
```bash
# Old (before adding test_reports_page.py):
# Updated: 2025-11-03 - All tests including Students page (240 tests total)
python3 -m pytest \
  test_school_page.py \
  test_teams_page.py \
  test_grade_level_page.py \
  test_students_page.py \
  test_data_accuracy.py \
  ...

# New (after adding test_reports_page.py):
# Updated: 2025-11-05 - All tests including Reports & Data page (246 tests total)
python3 -m pytest \
  test_school_page.py \
  test_teams_page.py \
  test_grade_level_page.py \
  test_students_page.py \
  test_reports_page.py \    # ← ADD NEW TEST FILE HERE
  test_data_accuracy.py \
  ...
```

**Why this is critical:**
- Pre-commit hook has **hardcoded list** of test files
- New test files won't run automatically unless explicitly added
- Forgetting this step means tests pass locally but may fail in CI/CD

**Verification steps:**
```bash
# After updating .git/hooks/pre-commit:
1. Run: python3 -m pytest test_reports_page.py -v
2. Count tests: Should see NEW test count in output
3. Test hook: git commit (will run all tests including new file)
```

#### Pre-Commit Test Command
```bash
# Run all page tests
pytest test_school_page.py test_teams_page.py test_grade_level_page.py test_reports_page.py -v

# Or run all tests
pytest -v
```

#### Git Commit Pre-Commit Hook Location
**File:** `.git/hooks/pre-commit` (this file is NOT tracked in git - must be updated manually)

### Test Fixtures
All page tests should use these standard fixtures:

```python
@pytest.fixture
def client():
    """Create a test client for the Flask application."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        with app.app_context():
            with client.session_transaction() as sess:
                sess['environment'] = 'sample'
        yield client

@pytest.fixture
def sample_db():
    """Get sample database instance for verification queries."""
    return ReadathonDB('readathon_sample.db')
```

### Test Coverage Goals
- **Minimum:** 80% code coverage for all Flask routes
- **Target:** 90% code coverage
- **Check coverage:** `pytest --cov=app --cov-report=html`

### Adding Tests for New Pages
When creating a new page:
1. Create `test_<page_name>_page.py` before implementing the page
2. Include all 8 mandatory tests
3. Add page-specific tests for unique functionality
4. Verify all tests pass before committing

### Updating Tests After Bug Fixes
When fixing a bug:
1. Add a test that reproduces the bug (should fail)
2. Fix the bug
3. Verify test now passes
4. Add similar tests to catch related issues

---

## Adding New Rules

When you or the user identifies a new universal rule:
1. Add it to the appropriate section in this file
2. Include specific examples if applicable
3. Note which pages/features the rule applies to
4. Update the "Last Updated" date at the top

**If uncertain whether something is a rule, ASK THE USER.**
