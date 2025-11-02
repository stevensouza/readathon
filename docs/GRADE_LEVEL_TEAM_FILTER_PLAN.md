# Grade Level Team Filter Implementation Plan

**Created:** 2025-11-02
**Status:** In Progress
**Purpose:** Add team filter dropdown to Grade Level page (matching Students page pattern)

---

## Overview

The Grade Level page currently has:
- Date filter (dropdown)
- Grade filter (button toggles)

We need to add:
- Team filter (dropdown, like Students page)

---

## Files to Modify

### 1. Backend: app.py (Grade Level route)
**Location:** Lines 1388-1635

**Changes needed:**
- [ ] Add `team_filter = request.args.get('team', 'all')` after grade_filter (line ~1647)
- [ ] Build `team_where` clause similar to grade_where (line ~1407)
- [ ] Pass `team_where` to all queries that currently only use `grade_where`
- [ ] Update debug logging to include team_filter

**Queries affected:**
- `get_grade_level_classes_query(date_where, grade_where)` → add `team_where`
- `get_grade_aggregations_query(date_where)` → add `grade_where, team_where`
- `get_grade_level_leaders_query(date_where, grade_where)` → add `team_where`

### 2. Backend: queries.py
**Functions to update:**

- [ ] `get_grade_level_classes_query(date_where, grade_where)` → add `team_where` parameter
- [ ] `get_grade_aggregations_query(date_where)` → add `grade_where, team_where` parameters
- [ ] `get_grade_level_leaders_query(date_where, grade_where)` → add `team_where` parameter

**Pattern:** Add `team_where` to WHERE clause (similar to how grade_where is used)
```python
WHERE 1=1
    {date_where}
    {grade_where}
    {team_where}  # NEW
```

### 3. Frontend: templates/grade_level.html
**Location:** Lines 1-1031

**Changes needed:**

#### A. Add Team Filter Dropdown (after Grade Filter buttons)
Pattern from Students page:
```html
<div class="filter-row">
    <div class="team-filter-buttons">
        <label for="teamFilter" class="filter-label">🏆 Team Filter:</label>
        <select id="teamFilter" class="form-select form-select-sm" onchange="applyTeamFilter()">
            <option value="all" {% if team_filter == 'all' %}selected{% endif %}>All Teams</option>
            {% for team in team_names %}
            <option value="{{ team }}" {% if team_filter == team %}selected{% endif %}>{{ team }}</option>
            {% endfor %}
        </select>
    </div>
</div>
```

#### B. Add JavaScript for Team Filter
```javascript
function applyTeamFilter() {
    const teamFilter = document.getElementById('teamFilter').value;
    sessionStorage.setItem('readathonTeamFilter', teamFilter);

    const currentUrl = new URL(window.location.href);
    currentUrl.searchParams.set('team', teamFilter);

    // Preserve other filters
    const dateFilter = document.getElementById('dateFilter').value;
    const gradeFilter = currentGradeFilter;
    currentUrl.searchParams.set('date', dateFilter);
    currentUrl.searchParams.set('grade', gradeFilter);

    window.location.href = currentUrl.toString();
}

// On page load, restore team filter from sessionStorage
window.addEventListener('DOMContentLoaded', function() {
    const savedTeamFilter = sessionStorage.getItem('readathonTeamFilter');
    if (savedTeamFilter && document.getElementById('teamFilter')) {
        document.getElementById('teamFilter').value = savedTeamFilter;
    }
});
```

#### C. Update Data Info Modal
Add explanation about team filter behavior (similar to grade filter explanation)

### 4. Testing
**Test cases:**
- [ ] All Teams + All Grades (baseline)
- [ ] Team 1 only
- [ ] Team 2 only
- [ ] Team 1 + Grade K
- [ ] Team 2 + Grade 5
- [ ] Date filter + Team filter combinations
- [ ] SessionStorage persistence (navigate away and back)
- [ ] Banner updates correctly
- [ ] Table filters correctly
- [ ] Gold/silver highlighting works correctly

---

## Implementation Order

1. **Step 1: Backend - queries.py**
   - Update query functions to accept team_where parameter
   - Add team_where to WHERE clauses

2. **Step 2: Backend - app.py**
   - Get team_filter from request
   - Build team_where clause
   - Pass to all query functions

3. **Step 3: Frontend - grade_level.html**
   - Add team filter dropdown UI
   - Add JavaScript for filter logic
   - Update Data Info modal

4. **Step 4: Testing**
   - Test all combinations
   - Verify sessionStorage
   - Verify highlighting

---

## Notes

- Students page is the reference implementation (has both grade and team filters)
- Team filter should work independently or combined with grade filter
- Team names are dynamically loaded from database (alphabetical order)
- SessionStorage key: `readathonTeamFilter` (matches Students page pattern)
- Silver highlighting should appear when team filter is active
- Gold highlighting always shows school-wide winners (across all teams)

---

## Expected Behavior

**When "All Teams" selected:**
- Shows all classes (no team filtering)
- Gold highlights = school-wide winners
- No silver highlights

**When specific team selected (e.g., "Team 1"):**
- Table shows only classes from Team 1
- Banner metrics calculate only for Team 1 students
- Gold highlights = school-wide winners (if they happen to be in Team 1)
- Silver highlights = best within Team 1 (if grade filter also applied)

**When Team + Grade filters combined:**
- Both filters apply (e.g., "Grade 3 + Team 1" = only Grade 3 classes from Team 1)
- Silver highlights show best within that filtered subset
