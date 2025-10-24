# Dashboard Tab Implementation Checklist

**Purpose:** Use this checklist when implementing new dashboard tabs (Classes, Students, etc.) to ensure consistency and avoid common issues discovered during Teams tab implementation.

**Reference Implementation:** Teams tab (commit 916a583)

---

## Phase 1: Planning & Design

### 1.1 Create HTML Prototype First
- [ ] Design HTML prototype in `prototypes/` directory
- [ ] Include sample data (fictitious names/numbers)
- [ ] Get user approval on layout before coding
- [ ] Add prototype to `prototypes/INDEX.html`
- [ ] Add prototype to `prototypes/dashboard_tabs_master_index.html`

### 1.2 Define Data Requirements
- [ ] List all metrics to display
- [ ] Identify which metrics honor date filter vs. show full contest
- [ ] Determine database tables/queries needed
- [ ] Plan aggregations and calculations

---

## Phase 2: Backend Implementation (Flask Route)

### 2.1 Create Flask Route
**File:** `app.py`

```python
@app.route('/tab_name')
def tab_name():
    """Tab description"""
    env = session.get('environment', DEFAULT_DATABASE)
    db = get_current_db()

    # Get filter parameter
    date_filter = request.args.get('date', 'all')
    dates = db.get_all_dates()

    # Build WHERE clauses
    date_where = ""
    date_where_no_alias = ""
    if date_filter != 'all' and date_filter in dates:
        date_where = f"AND dl.log_date <= '{date_filter}'"
        date_where_no_alias = f"AND log_date <= '{date_filter}'"

    # ... calculations ...
```

**Checklist:**
- [ ] Add route decorator with URL path
- [ ] Get environment and database connection
- [ ] Get date filter parameter
- [ ] Build date WHERE clauses (both aliased and non-aliased versions)
- [ ] Query all necessary data
- [ ] Perform calculations and aggregations
- [ ] Calculate `full_contest_range` for date dropdown
- [ ] Calculate `metadata` dict with timestamp info

### 2.2 Calculate full_contest_range
```python
# Calculate full contest date range
sorted_dates = sorted(dates)
if sorted_dates:
    start_date = datetime.strptime(sorted_dates[0], '%Y-%m-%d').strftime('%b %d')
    end_date = datetime.strptime(sorted_dates[-1], '%Y-%m-%d').strftime('%b %d, %Y')
    full_contest_range = f"{start_date}-{end_date}"
else:
    full_contest_range = "Oct 10-15, 2025"  # Fallback
```

**Checklist:**
- [ ] Sort dates chronologically
- [ ] Format start date as "Oct 10"
- [ ] Format end date as "Oct 15, 2025"
- [ ] Provide fallback value if no dates exist

### 2.3 Calculate Metadata (Timestamps)
```python
# === METADATA (Last Updated) ===
metadata = {}

# Daily_Logs timestamp
daily_logs_ts_query = """
    SELECT MAX(upload_timestamp) as last_updated
    FROM Upload_History
    WHERE file_type = 'daily'
"""
daily_logs_ts = db.execute_query(daily_logs_ts_query)
if daily_logs_ts and daily_logs_ts[0] and daily_logs_ts[0]['last_updated']:
    metadata['daily_logs_updated'] = daily_logs_ts[0]['last_updated']
else:
    metadata['daily_logs_updated'] = 'Never'

# Reader_Cumulative timestamp
reader_cumulative_ts_query = """
    SELECT MAX(upload_timestamp) as last_updated
    FROM Upload_History
    WHERE file_type = 'cumulative'
"""
reader_cumulative_ts = db.execute_query(reader_cumulative_ts_query)
if reader_cumulative_ts and reader_cumulative_ts[0] and reader_cumulative_ts[0]['last_updated']:
    metadata['reader_cumulative_updated'] = reader_cumulative_ts[0]['last_updated']
else:
    metadata['reader_cumulative_updated'] = 'Never'

# Roster timestamp (static)
metadata['roster_updated'] = '09/15/2025 8:00 AM'

# Team_Color_Bonus timestamp (if applicable)
team_color_bonus_query = """
    SELECT event_date, COUNT(*) as class_count
    FROM Team_Color_Bonus
    GROUP BY event_date
    ORDER BY event_date DESC
    LIMIT 1
"""
team_color_bonus_ts = db.execute_query(team_color_bonus_query)
if team_color_bonus_ts and team_color_bonus_ts[0] and team_color_bonus_ts[0]['event_date']:
    event_date = team_color_bonus_ts[0]['event_date']
    class_count = team_color_bonus_ts[0]['class_count']
    metadata['team_color_bonus_updated'] = f"{event_date} ({class_count} classes)"
else:
    metadata['team_color_bonus_updated'] = 'No data'
```

**Checklist:**
- [ ] Query Daily_Logs last update from Upload_History
- [ ] Query Reader_Cumulative last update from Upload_History
- [ ] Set Roster static timestamp
- [ ] Query Team_Color_Bonus event date (if used on this tab)
- [ ] Provide fallback values for missing data

### 2.4 Pass All Variables to Template
```python
return render_template('tab_name.html',
                     environment=env,
                     dates=dates,
                     date_filter=date_filter,
                     full_contest_range=full_contest_range,
                     metadata=metadata,
                     # ... other data ...
                     )
```

**Checklist:**
- [ ] Pass `environment`
- [ ] Pass `dates` (list of all dates)
- [ ] Pass `date_filter` (current selected date or 'all')
- [ ] Pass `full_contest_range` (formatted date range string)
- [ ] Pass `metadata` (dict with timestamps)
- [ ] Pass all calculated metrics/data

---

## Phase 3: Template Implementation

### 3.1 Template Structure
**File:** `templates/tab_name.html`

```jinja
{% extends "base.html" %}

{% block title %}Tab Name - Read-a-Thon System{% endblock %}

{% block extra_css %}
<style>
    /* Tab-specific styles matching Option H colors */

    /* Filter Indicator Icon - REQUIRED */
    .filter-indicator {
        font-size: 0.85rem;
        color: #17a2b8;
        cursor: help;
        margin-left: 0.3rem;
        transition: color 0.2s;
        display: inline-block;
    }

    .filter-indicator:hover {
        color: #138496;
    }

    /* In headline banner, use white for contrast */
    .headline-banner .filter-indicator {
        color: rgba(255,255,255,0.6);
    }

    .headline-banner .filter-indicator:hover {
        color: rgba(255,255,255,0.95);
    }

    /* ... other styles ... */
</style>
{% endblock %}

{% block content %}
<!-- Page content -->
{% endblock %}
```

**Checklist:**
- [ ] Extend base.html
- [ ] Set page title
- [ ] Include `.filter-indicator` CSS (REQUIRED)
- [ ] Match Option H color scheme (#1e3a5f, #2c3e50, etc.)
- [ ] Use consistent spacing and shadows

### 3.2 Page Header with Filter
```jinja
<div class="page-header-[tab-name]">
    <h2 class="page-title-[tab-name]">[Icon] Tab Title</h2>

    <div class="filter-inline">
        <label for="dateFilter">📅 Filter Period:</label>
        <select id="dateFilter" class="form-select form-select-sm" onchange="applyDateFilter()">
            <option value="all" {% if date_filter == 'all' %}selected{% endif %}>Full Contest ({{ full_contest_range }})</option>
            {% for date in dates|reverse %}
            <option value="{{ date }}" {% if date_filter == date %}selected{% endif %}>{{ date }} (Day {{ loop.index }})</option>
            {% endfor %}
        </select>
        <span class="filter-note">(ⓘ = honors filter)</span>
    </div>

    <button class="data-info-btn" data-bs-toggle="modal" data-bs-target="#dataSourceModal">
        <i class="bi bi-info-circle"></i> Data Info
    </button>
</div>
```

**Checklist:**
- [ ] Use flexbox layout for header (space-between)
- [ ] Include page title with emoji icon
- [ ] Add date filter dropdown
  - [ ] "Full Contest (Oct 10-Oct 15, 2025)" format for 'all'
  - [ ] "YYYY-MM-DD (Day X)" format for specific dates
  - [ ] Use `form-select-sm` Bootstrap class
- [ ] Include filter note "(ⓘ = honors filter)"
- [ ] Add Data Info button with modal trigger
- [ ] Add `applyDateFilter()` JavaScript function

### 3.3 Filter Indicators (CRITICAL)
**Rule:** Only show indicators when `date_filter != 'all'`

**Banner/Headers:**
```jinja
<div class="headline-label">
    {{ metric.icon }} {{ metric.name }}
    {% if metric.honors_filter and date_filter != 'all' %}
    <span class="filter-indicator" data-bs-toggle="tooltip" data-bs-placement="top" title="Cumulative through {{ date_filter }}">◐</span>
    {% endif %}
</div>
```

**Sections:**
```jinja
<div class="section-label">
    📚 Section Name
    {% if date_filter != 'all' %}
    <span class="filter-indicator" data-bs-toggle="tooltip" data-bs-placement="top" title="Cumulative through {{ date_filter }}">◐</span>
    {% endif %}
</div>
```

**Table Rows:**
```jinja
<td>
    <strong>{{ row.metric }}</strong>
    {% if row.metric in ['Metric 1', 'Metric 2'] and date_filter != 'all' %}
    <span class="filter-indicator" data-bs-toggle="tooltip" data-bs-placement="top" title="Cumulative through {{ date_filter }}">◐</span>
    {% endif %}
</td>
```

**Checklist:**
- [ ] Use ◐ character (half-filled circle, NOT ⓘ)
- [ ] Wrap in `<span class="filter-indicator">`
- [ ] Add Bootstrap tooltip attributes
- [ ] Tooltip text: "Cumulative through {{ date_filter }}"
- [ ] Conditional: `{% if ... and date_filter != 'all' %}`
- [ ] Apply to ALL metrics that honor the date filter

**Metrics That Honor Filter:**
- Reading minutes
- Participation percentages
- Goal met counts/percentages
- Daily activity metrics
- Top performers (reading-related)

**Metrics That DON'T Honor Filter:**
- Fundraising totals
- Sponsor counts
- Student counts (team sizes)
- Cumulative-only metrics

### 3.4 Data Sources Footer
```jinja
<!-- Collapsible Footer: Data Sources -->
<div class="collapsible-footer">
    <div class="collapsible-header" onclick="toggleFooter()">
        <span><i class="bi bi-chevron-right" id="footerIcon"></i> Data Sources & Last Updated</span>
        <span style="font-size: 0.75rem; color: #6c757d;">Click to expand</span>
    </div>
    <div class="collapsible-content" id="footerContent">
        <div class="data-source-item">
            <span class="data-source-label">• Reading minutes, Participation:</span>
            <span class="data-source-value">Daily_Logs table (Updated: {{ metadata.daily_logs_updated }})</span>
        </div>
        <div class="data-source-item">
            <span class="data-source-label">• Fundraising, Sponsors:</span>
            <span class="data-source-value">Reader_Cumulative table (Updated: {{ metadata.reader_cumulative_updated }})</span>
        </div>
        <div class="data-source-item">
            <span class="data-source-label">• Student counts:</span>
            <span class="data-source-value">Roster table (Updated: {{ metadata.roster_updated }})</span>
        </div>
        <!-- Add Team_Color_Bonus if applicable -->
    </div>
</div>
```

**Checklist:**
- [ ] Add collapsible footer at bottom of page
- [ ] Include chevron icon that toggles
- [ ] List all data sources with metadata timestamps
- [ ] Add `toggleFooter()` JavaScript function

### 3.5 Data Sources Modal
```jinja
<!-- Data Source Modal -->
<div class="modal fade" id="dataSourceModal" tabindex="-1" aria-labelledby="dataSourceModalLabel" aria-hidden="true">
    <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
            <div class="modal-header modal-header-custom">
                <h5 class="modal-title" id="dataSourceModalLabel">
                    <i class="bi bi-database"></i> Data Sources & Last Updated
                </h5>
                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body">
                <div class="data-source-item mb-3">
                    <div class="data-source-label mb-1">Reading Minutes & Participation:</div>
                    <div class="data-source-value ms-3">
                        Source: <strong>Daily_Logs</strong> table<br>
                        Last Updated: <strong>{{ metadata.daily_logs_updated }}</strong>
                    </div>
                </div>
                <!-- ... more sources ... -->

                <hr class="my-3">

                <div class="data-source-item">
                    <div class="data-source-label mb-2"><i class="bi bi-funnel"></i> Date Filter Behavior:</div>
                    <div class="data-source-value ms-3" style="font-size: 0.8rem; line-height: 1.6;">
                        <strong>Reading Metrics (Filtered by date):</strong><br>
                        <span style="color: #6c757d;">• Minutes Read, Participation, Goals Met</span><br>
                        <span style="color: #6c757d;">• Shows data <em>cumulative through</em> selected date</span><br>
                        <span style="color: #6c757d;">• Example: Day 3 = Days 1+2+3 combined</span><br><br>

                        <strong>Fundraising Metrics (Not filtered):</strong><br>
                        <span style="color: #6c757d;">• Total Fundraising, Sponsors</span><br>
                        <span style="color: #6c757d;">• Always shows <em>full contest</em> totals</span><br>
                        <span style="color: #6c757d;">• Fundraising is cumulative by design</span>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
```

**Checklist:**
- [ ] Create Bootstrap modal with ID `dataSourceModal`
- [ ] Add custom header styling (`.modal-header-custom`)
- [ ] List all data sources with timestamps
- [ ] Explain filter behavior (filtered vs. non-filtered metrics)
- [ ] Use white close button (`.btn-close-white`)

### 3.6 JavaScript Functions
```javascript
<script>
function applyDateFilter() {
    const dateFilter = document.getElementById('dateFilter').value;
    const currentUrl = new URL(window.location.href);

    if (dateFilter === 'all') {
        currentUrl.searchParams.delete('date');
    } else {
        currentUrl.searchParams.set('date', dateFilter);
    }

    window.location.href = currentUrl.toString();
}

function toggleFooter() {
    const content = document.getElementById('footerContent');
    const icon = document.getElementById('footerIcon');
    content.classList.toggle('show');
    icon.classList.toggle('bi-chevron-right');
    icon.classList.toggle('bi-chevron-down');
}

// Add any other necessary functions (sorting, etc.)
</script>
```

**Checklist:**
- [ ] Add `applyDateFilter()` for date dropdown
- [ ] Add `toggleFooter()` for collapsible footer
- [ ] Add any tab-specific functions (sorting, filtering, etc.)

---

## Phase 4: Testing & Verification

### 4.1 Visual Verification
- [ ] Page loads without errors
- [ ] All sections render correctly
- [ ] Colors match School/Teams tabs (Option H)
- [ ] Layout matches approved HTML prototype
- [ ] Date filter dropdown works
- [ ] Data Info button opens modal
- [ ] Collapsible footer toggles correctly

### 4.2 Filter Indicator Verification
**CRITICAL: Test with both "Full Contest" and specific dates**

When **Full Contest** selected:
- [ ] NO indicators (◐) appear anywhere
- [ ] All metrics show full contest data

When **specific date** selected (e.g., "2025-10-10 (Day 1)"):
- [ ] Indicators (◐) appear next to filtered metrics
- [ ] Indicators have cyan color (#17a2b8)
- [ ] Tooltip shows "Cumulative through [date]" on hover
- [ ] Data updates to show cumulative through selected date

### 4.3 Data Accuracy
- [ ] Metrics calculate correctly
- [ ] Totals match database queries
- [ ] Percentages format properly (1 decimal place)
- [ ] Currency formats with commas and 2 decimals
- [ ] Numbers format with commas
- [ ] Filter changes data appropriately

### 4.4 Timestamp Verification
- [ ] Collapsible footer shows correct timestamps
- [ ] Modal shows correct timestamps
- [ ] Timestamps match actual data upload times

---

## Phase 5: Documentation

### 5.1 Update Prototype Index
- [ ] Add new tab to `prototypes/INDEX.html`
- [ ] Add new tab to `prototypes/dashboard_tabs_master_index.html`
- [ ] Include description and screenshots

### 5.2 Update Base Template Navigation
**File:** `templates/base.html`

Add navigation link in dashboard tabs section:
```html
<a href="{{ url_for('tab_name') }}" class="nav-link">
    [Icon] Tab Name
</a>
```

**Checklist:**
- [ ] Add navigation link to base.html
- [ ] Use appropriate icon
- [ ] Test navigation between all tabs

---

## Common Issues to Avoid

### Issue 1: Filter Indicators Always Showing
**Problem:** Indicators appear even when "Full Contest" is selected
**Solution:** Always include `and date_filter != 'all'` in conditional

**Correct:**
```jinja
{% if metric.honors_filter and date_filter != 'all' %}
```

**Incorrect:**
```jinja
{% if metric.honors_filter %}
```

### Issue 2: Wrong Indicator Character
**Problem:** Using ⓘ (info circle) instead of ◐ (half-circle)
**Solution:** Always use ◐ character for filter indicators

### Issue 3: Missing Metadata Variable
**Problem:** Template error when trying to display timestamps
**Solution:** Always pass `metadata` dict in render_template()

### Issue 4: Incorrect Date Filter Format
**Problem:** Dropdown shows "YYYY-MM-DD" instead of "Oct 10-Oct 15, 2025"
**Solution:** Format dates properly in backend:
- Full Contest: "Full Contest (Oct 10-Oct 15, 2025)"
- Specific dates: "2025-10-10 (Day 1)"

### Issue 5: Missing full_contest_range
**Problem:** Date dropdown shows "()" for full contest option
**Solution:** Calculate and pass `full_contest_range` in Flask route

### Issue 6: Metrics Not Updating with Filter
**Problem:** Data doesn't change when selecting different dates
**Solution:** Ensure date WHERE clause is applied correctly:
```python
date_where = f"AND dl.log_date <= '{date_filter}'"
```

### Issue 7: Team Colors Inconsistent
**Problem:** Colors don't match School/Teams tabs
**Solution:** Use Option H colors:
- Primary dark: #1e3a5f
- Secondary dark: #2c3e50
- Staub blue: #1e3a5f
- Kitsko yellow: #f59e0b

---

## Quick Reference

### Option H Color Palette
```css
Primary Dark:      #1e3a5f
Secondary Dark:    #2c3e50
Accent Blue:       #3b82f6
Cyan (indicators): #17a2b8
Success Green:     #28a745
Text Gray:         #6c757d
Background:        #f8f9fa

Staub Blue:        #1e3a5f
Kitsko Yellow:     #f59e0b
```

### Filter Indicator Pattern
```jinja
{% if [condition] and date_filter != 'all' %}
<span class="filter-indicator" data-bs-toggle="tooltip" data-bs-placement="top" title="Cumulative through {{ date_filter }}">◐</span>
{% endif %}
```

### Date Filter JavaScript
```javascript
function applyDateFilter() {
    const dateFilter = document.getElementById('dateFilter').value;
    const currentUrl = new URL(window.location.href);
    if (dateFilter === 'all') {
        currentUrl.searchParams.delete('date');
    } else {
        currentUrl.searchParams.set('date', dateFilter);
    }
    window.location.href = currentUrl.toString();
}
```

---

## Final Checklist Before Commit

- [ ] All visual elements match approved prototype
- [ ] Filter indicators work correctly (only show when date selected)
- [ ] Date filter updates data appropriately
- [ ] Metadata timestamps display correctly
- [ ] Data Info button and modal work
- [ ] Collapsible footer works
- [ ] Navigation to/from other tabs works
- [ ] No console errors
- [ ] Code follows existing patterns
- [ ] Commit message is descriptive
- [ ] Tests pass (if applicable)

---

**Next Tabs to Implement:**
1. Classes Tab (leaderboard of all classes)
2. Students Tab (individual student performance)
