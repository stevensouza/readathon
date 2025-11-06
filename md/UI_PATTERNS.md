# Read-a-Thon UI Patterns Reference

**Last Updated:** 2025-10-29

This document captures established UI patterns from existing pages (School, Teams, Grade Level). Use these patterns for consistency when implementing new features.

---

## Color Palette

### Primary Colors
```css
Dark Blue (Headers, Active Nav):     #1e3a5f
Medium Blue (Hovers):                 #2c3e50
Light Blue (Backgrounds):             #dbeafe
```

### Team Colors
```css
Team 1 (Blue):                        #1e3a5f
Team 1 Border:                        rgba(255,255,255,0.4)

Team 2 (Yellow/Amber):                #f59e0b
Team 2 Text:                          #1e3a5f
Team 2 Border:                        rgba(30,58,95,0.3)
```

### Winning Value Highlights
```css
Gold (School Winners):                #ffd700
Gold Background:                      rgba(255, 215, 0, 0.15)
Gold Border:                          2px solid #ffd700

Silver (Grade/Team Winners):          #c0c0c0
Silver Background:                    rgba(192, 192, 192, 0.15)
Silver Border:                        2px solid #c0c0c0
```

### Table Colors
```css
Header Background:                    #1e3a5f
Header Text:                          #ffffff
Odd Rows:                             #ffffff
Even Rows:                            #f8f9fa
Hover:                                rgba(0,0,0,0.03)
```

---

## Component Patterns

### 1. Filter Period Selector

**Location:** Top of page, centered, below navigation

**HTML Structure:**
```html
<div class="text-center mb-4">
    <div class="filter-inline">
        <label for="dateFilter">📅 Filter Period:</label>
        <select id="dateFilter" class="form-select form-select-sm" onchange="applyDateFilter()">
            <option value="all">Full Contest (Oct 10 - Oct 19)</option>
            <option value="2025-10-10">Friday, October 10</option>
            <!-- More dates... -->
        </select>
    </div>
</div>
```

**CSS:**
```css
.filter-inline {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
}

.filter-inline label {
    font-weight: 600;
    margin: 0;
}

.filter-inline .form-select {
    width: auto;
}
```

**JavaScript (Sticky Filter):**
```javascript
// On page load - restore saved filter
const savedFilter = sessionStorage.getItem('readathonDateFilter');
if (savedFilter) {
    document.getElementById('dateFilter').value = savedFilter;
}

// On change - save and reload
function applyDateFilter() {
    const dateFilter = document.getElementById('dateFilter').value;
    sessionStorage.setItem('readathonDateFilter', dateFilter);

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

### 2. Headline Banner (5 Metrics)

**Location:** Below filter, above cards

**HTML Structure:**
```html
<div class="headline-banner">
    <div class="row gx-2">
        <!-- Metric 1: Fundraising -->
        <div class="col headline-metric">
            <div class="headline-label">💰 Fundraising</div>
            <div class="headline-winner">
                <span class="team-badge team-badge-kitsko">KITSKO</span>
            </div>
            <div class="headline-extra">
                🏆 Winner: 5th Grade • ogg
            </div>
        </div>

        <!-- Metric 2: Minutes Read -->
        <div class="col headline-metric">...</div>

        <!-- Metric 3: Sponsors -->
        <div class="col headline-metric">...</div>

        <!-- Metric 4: Participation % -->
        <div class="col headline-metric">...</div>

        <!-- Metric 5: Goals Met -->
        <div class="col headline-metric">...</div>
    </div>
</div>
```

**CSS:**
```css
.headline-banner {
    background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
    border-radius: 1rem;
    padding: 1.5rem;
    margin-bottom: 2rem;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

.headline-metric {
    text-align: center;
    padding: 0.75rem;
}

.headline-metric:not(:last-child) {
    border-right: 1px solid #dee2e6;
}

.headline-label {
    font-size: 0.85rem;
    font-weight: 600;
    color: #6c757d;
    margin-bottom: 0.5rem;
}

.headline-winner {
    font-size: 1.1rem;
    font-weight: 700;
    color: #1e3a5f;
    margin-bottom: 0.25rem;
}

.headline-extra {
    font-size: 0.75rem;
    color: #6c757d;
}

/* Responsive: Stack on mobile */
@media (max-width: 768px) {
    .headline-metric {
        border-right: none !important;
        border-bottom: 1px solid #dee2e6;
        margin-bottom: 1rem;
    }
}
```

**Metric Order (MUST match across all pages):**
1. Fundraising (💰)
2. Minutes Read (📖)
3. Sponsors (👥)
4. Participation % (📊)
5. Goals Met ≥1 Day (🎯)

---

### 3. Team Badges

**HTML:**
```html
<!-- Blue Team (Alphabetically First) -->
<span class="team-badge team-badge-kitsko">KITSKO</span>
<span class="team-badge team-badge-team1">TEAM1</span>

<!-- Yellow Team (Alphabetically Second) -->
<span class="team-badge team-badge-staub">STAUB</span>
<span class="team-badge team-badge-team2">TEAM2</span>
```

**CSS:**
```css
.team-badge {
    display: inline-block;
    padding: 0.25rem 0.75rem;
    border-radius: 1rem;
    font-weight: 700;
    font-size: 0.75rem;
    letter-spacing: 0.5px;
}

/* Team 1 - Blue */
.team-badge-kitsko,
.team-badge-team1 {
    background: #1e3a5f;
    color: white;
    border: 1px solid rgba(255,255,255,0.4);
}

/* Team 2 - Yellow */
.team-badge-staub,
.team-badge-team2 {
    background: #f59e0b;
    color: #1e3a5f;
    border: 1px solid rgba(30,58,95,0.3);
}
```

**Usage Notes:**
- Always uppercase team name in HTML
- Use specific team classes (e.g., `-kitsko`, `-staub`) if known
- Use generic classes (e.g., `-team1`, `-team2`) for sample data
- Apply same colors to leader badges, buttons, ovals

---

### 4. Sortable Tables

**HTML:**
```html
<table class="table table-striped" id="dataTable">
    <thead>
        <tr>
            <th onclick="sortTable(0)" style="cursor:pointer;">Class Name ▲</th>
            <th onclick="sortTable(1)" style="cursor:pointer;">Grade ▲</th>
            <th onclick="sortTable(2)" style="cursor:pointer;">Team ▲</th>
            <th onclick="sortTable(3)" style="cursor:pointer;">Fundraising ▲</th>
            <!-- More columns... -->
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>neurohr am</td>
            <td>K</td>
            <td><span class="team-badge team-badge-kitsko">KITSKO</span></td>
            <td class="text-end" data-value="2624">$2,624</td>
        </tr>
        <!-- More rows... -->
    </tbody>
</table>
```

**CSS:**
```css
/* Table headers */
.table thead th {
    background-color: #1e3a5f !important;
    color: white !important;
    cursor: pointer;
    user-select: none;
    position: relative;
    padding-right: 1.5rem;
}

.table thead th::after {
    content: ' ▲';
    position: absolute;
    right: 0.5rem;
    opacity: 0.3;
}

.table thead th.sorted-asc::after {
    content: ' ▲';
    opacity: 1;
}

.table thead th.sorted-desc::after {
    content: ' ▼';
    opacity: 1;
}

/* Striped rows */
.table-striped tbody tr:nth-of-type(odd) {
    background-color: #ffffff;
}

.table-striped tbody tr:nth-of-type(even) {
    background-color: #f8f9fa;
}

.table-striped tbody tr:hover {
    background-color: rgba(0,0,0,0.03);
}
```

**JavaScript Sorting:**
```javascript
let currentSortColumn = -1;
let currentSortDirection = 'asc';

function sortTable(columnIndex) {
    const table = document.getElementById('dataTable');
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));

    // Toggle direction if same column
    if (currentSortColumn === columnIndex) {
        currentSortDirection = currentSortDirection === 'asc' ? 'desc' : 'asc';
    } else {
        currentSortDirection = 'asc';
        currentSortColumn = columnIndex;
    }

    // Sort rows
    rows.sort((a, b) => {
        const aValue = a.cells[columnIndex].getAttribute('data-value') ||
                      a.cells[columnIndex].textContent.trim();
        const bValue = b.cells[columnIndex].getAttribute('data-value') ||
                      b.cells[columnIndex].textContent.trim();

        // Compare logic...
        const comparison = aValue.localeCompare(bValue, undefined, {numeric: true});
        return currentSortDirection === 'asc' ? comparison : -comparison;
    });

    // Re-append rows
    rows.forEach(row => tbody.appendChild(row));

    // Update visual indicators
    updateSortIndicators(table, columnIndex, currentSortDirection);
}
```

---

### 5. Winning Value Ovals

**HTML (in table cell):**
```html
<!-- Gold Oval (School Winner) -->
<td class="text-end" data-value="2624">
    <span class="winning-value winning-value-school">$2,624</span>
</td>

<!-- Silver Oval (Grade Winner) -->
<td class="text-end" data-value="1777">
    <span class="winning-value winning-value-grade">$1,777</span>
</td>
```

**CSS:**
```css
.winning-value {
    display: inline-block;
    padding: 0.35rem 0.9rem;
    border-radius: 2rem;
    font-weight: 700;
}

/* Gold (School Winners) */
.winning-value-school {
    background: rgba(255, 215, 0, 0.15);
    border: 2px solid #ffd700;
    color: #1e3a5f;
}

/* Silver (Grade/Team Winners) */
.winning-value-grade {
    background: rgba(192, 192, 192, 0.15);
    border: 2px solid #c0c0c0;
    color: #1e3a5f;
}
```

**Application Logic:**
- Gold overrides silver (check school winner first)
- Only apply to positive values (> 0)
- Preserve existing cell content formatting

---

### 6. Data Sources Footer

**Location:** Bottom of page, collapsible

**HTML:**
```html
<div class="collapsible-footer">
    <div class="collapsible-header" onclick="toggleFooter()">
        <span><i class="bi bi-chevron-right" id="footerIcon"></i> Data Sources & Last Updated</span>
        <span style="font-size: 0.75rem; color: #6c757d;">Click to expand</span>
    </div>
    <div class="collapsible-content" id="footerContent">
        <div class="data-source-item">
            <span class="data-source-label">• Reading minutes, Participation:</span>
            <span class="data-source-value">Daily_Logs table (Updated: 2025-10-19 14:30)</span>
        </div>
        <div class="data-source-item">
            <span class="data-source-label">• Fundraising, Sponsors:</span>
            <span class="data-source-value">Reader_Cumulative table (Updated: 2025-10-19 14:30)</span>
        </div>
        <div class="data-source-item">
            <span class="data-source-label">• Student counts, Team assignments:</span>
            <span class="data-source-value">Roster table (Updated: 2025-10-19 14:30)</span>
        </div>
    </div>
</div>
```

**CSS:**
```css
.collapsible-footer {
    margin-top: 3rem;
    border-top: 2px solid #e9ecef;
    padding-top: 1.5rem;
}

.collapsible-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    cursor: pointer;
    padding: 1rem;
    background: #f8f9fa;
    border-radius: 0.5rem;
    transition: background 0.2s;
}

.collapsible-header:hover {
    background: #e9ecef;
}

.collapsible-content {
    max-height: 0;
    overflow: hidden;
    transition: max-height 0.3s ease;
}

.collapsible-content.show {
    max-height: 500px;
    padding-top: 1rem;
}

.data-source-item {
    display: flex;
    justify-content: space-between;
    padding: 0.5rem 1rem;
    margin-bottom: 0.5rem;
    background: white;
    border-radius: 0.375rem;
}
```

---

## Layout Templates

### Card-Based Page Template
```
┌─────────────────────────────────────────┐
│ Navigation Bar                          │
├─────────────────────────────────────────┤
│         📅 Filter Period: [Dropdown]    │  ← Centered
├─────────────────────────────────────────┤
│ Headline Banner (5 Metrics)             │  ← School-wide leaders
├─────────────────────────────────────────┤
│ ┌──────────┐ ┌──────────┐ ┌──────────┐│
│ │ Card 1   │ │ Card 2   │ │ Card 3   ││  ← Grade/Team cards
│ └──────────┘ └──────────┘ └──────────┘│
├─────────────────────────────────────────┤
│ Detail Table (Sortable, Striped)        │  ← All data
├─────────────────────────────────────────┤
│ [Click to expand] Data Sources          │  ← Footer
└─────────────────────────────────────────┘
```

---

## Implementation Checklist

Before implementing a new page, verify:
- [ ] Filter period selector is centered with label
- [ ] Banner metrics in correct order (Fundraising → Minutes → Sponsors → Participation → Goals)
- [ ] Team colors follow alphabetical rule (team 1 = blue, team 2 = yellow)
- [ ] Tables use dark blue headers (#1e3a5f) with white text
- [ ] Tables have alternating row colors (white/gray)
- [ ] Winning values use gold/silver ovals correctly
- [ ] Data sources footer is present and collapsible
- [ ] Sticky filter saves to sessionStorage
- [ ] All interactive elements have hover states

---

## Quick Reference

**Files to Check for Patterns:**
- `/templates/school.html` - Simplest layout, good baseline
- `/templates/teams.html` - Team comparison patterns
- `/templates/grade_level.html` - Grade filtering, gold/silver highlights
- `/templates/base.html` - Global styles (lines 740-800)

**Common CSS Classes:**
- `.headline-banner` - Top metrics section
- `.team-badge` - Team name badges
- `.winning-value` - Gold/silver ovals
- `.table-striped` - Alternating row colors
- `.collapsible-footer` - Data sources section
