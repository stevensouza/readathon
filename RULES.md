# Read-a-Thon Application Rules

**Last Updated:** 2025-10-30

This file contains universal rules that apply across all pages and features in the Read-a-Thon application. These rules MUST be followed for every implementation.

---

## Data Source Rules (ALWAYS TRUE)

### Primary Data Sources
- **Classes/Students:** `Roster` table (columns: `student_name`, `teacher_name`, `grade_level`, `team_name`, `class_name`)
- **Reading Minutes:** `Daily_Logs` table (capped at 120 minutes/day, includes color bonus)
- **Participation:** `Daily_Logs` table (students with >0 minutes for a given day)
- **Goals Met:** `Daily_Logs` table (students who met ≥1 day reading goal)
- **Fundraising/Sponsors:** `Reader_Cumulative` table (aggregated totals per student)
- **Team Assignments:** `Roster.team_name` column

### Data Calculation Rules
- **Minutes are ALWAYS capped at 120/day** for contest calculations
- **Color war bonus points MUST always be included** in minute totals
- **Participation % = (students with >0 minutes) / (total students in class/grade/school)**
- **Goals Met = count of students who achieved reading goal ≥1 day**

### Contest Period
- **Duration:** 10 consecutive days (e.g., Oct 10-19)
- **Start date may vary** between years, but always 10 days
- **Out-of-range dates:** Cause reconciliation differences (tracked in reports Q21-Q23)

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

4. **🎁 Sponsors** - Students with sponsors
   - Format: X,XXX count
   - Subtitle: "X of Y Students (Z%)"
   - Filter: Does NOT respect date filter (cumulative from Reader_Cumulative)
   - Icon: 🎁 (NOT 🤝)

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

## State Management & Persistence

### Sticky Filters (Cross-Page)
- **Filter Period:** Persists via `sessionStorage.setItem('readathonDateFilter', value)`
- **Restored on page load:** All pages check sessionStorage and apply saved filter
- **Grade Level Filter:** Persists within grade level page only (stored in sessionStorage)

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

#### Pre-Commit Test Command
```bash
# Run all page tests
pytest test_school_page.py test_teams_page.py test_grade_level_page.py -v

# Or run all tests
pytest -v
```

#### Git Commit Pre-Commit Hook (Recommended)
Add to `.git/hooks/pre-commit`:
```bash
#!/bin/bash
echo "Running tests before commit..."
pytest test_school_page.py test_teams_page.py test_grade_level_page.py -v
if [ $? -ne 0 ]; then
    echo "❌ Tests failed! Commit aborted."
    exit 1
fi
echo "✅ All tests passed!"
```

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
