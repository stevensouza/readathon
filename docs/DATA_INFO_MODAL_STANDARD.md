# Data Info Modal Standard

**Last Updated:** 2025-11-02
**Status:** ✅ Complete (implemented across all 4 tabs)
**Purpose:** Standardize Data Info modals across all dashboard tabs for consistency

## Executive Summary

After analyzing all 4 dashboard tabs, two different modal implementations were found:

1. **School & Teams:** Use `dataSourceModal` with focus on data sources and timestamps
2. **Grade Level & Students:** Use `dataInfoModal` with focus on filtering behavior

This document standardizes them to use **`dataInfoModal`** with a unified structure.

---

## Current State Analysis

### School Tab Modal (`dataSourceModal`)
**Location:** `templates/school.html` line 727
**Focus:** Data sources and last updated timestamps
**Sections:**
- Reading Minutes & Participation (Daily_Logs table)
- Fundraising & Sponsors (Reader_Cumulative table)
- Student Counts (Roster table)
- Team Color Bonus (Team_Color_Bonus table)
- Date Filter Behavior (filtered vs. non-filtered metrics)

**Modal Size:** `modal-dialog-centered` (default size)
**Header Style:** Custom header (`modal-header-custom`)

### Teams Tab Modal (`dataSourceModal`)
**Location:** `templates/teams.html` line 795
**Focus:** Data sources and last updated timestamps
**Sections:**
- **IDENTICAL to School tab** - copy/paste implementation

**Modal Size:** `modal-dialog-centered` (default size)
**Header Style:** Custom header (`modal-header-custom`)

### Grade Level Tab Modal (`dataInfoModal`)
**Location:** `templates/grade_level.html` line 955
**Focus:** Filtering behavior and highlighting logic
**Sections:**
- Table Filtering Behavior (grade filter explanation)
  - All Grades behavior (gold highlights)
  - Specific grade behavior (silver + gold highlights)
- Metrics That Honor Date Filter
- Metrics That Don't Filter
- Note about capping

**Modal Size:** `modal-lg` (large)
**Header Style:** Default header (no custom class)

### Students Tab Modal (`dataInfoModal`)
**Location:** `templates/students.html` line 826
**Focus:** Filtering behavior and highlighting logic
**Sections:**
- Banner and Table Filtering (grade + team filters)
- Silver Highlighting (filter active explanation)
- Metrics That Honor Date Filter
- Metrics That Don't Filter by Date

**Modal Size:** `modal-lg` (large)
**Header Style:** Default header (no custom class)

---

## Key Differences Found

| Aspect | School/Teams | Grade Level/Students |
|--------|--------------|---------------------|
| **Modal ID** | `dataSourceModal` | `dataInfoModal` |
| **Modal Size** | Default (centered) | Large (`modal-lg`) |
| **Header Style** | Custom (`modal-header-custom`) | Default |
| **Primary Focus** | Data sources & timestamps | Filter behavior & highlighting |
| **Data Tables Listed** | ✅ Yes (4 tables) | ❌ No |
| **Last Updated Dates** | ✅ Yes (4 timestamps) | ❌ No |
| **Grade Filter Logic** | ❌ No | ✅ Yes (Grade Level only) |
| **Team Filter Logic** | ❌ No | ✅ Yes (Students only) |
| **Highlighting Explanation** | ❌ No | ✅ Yes |
| **Date Filter Behavior** | ✅ Yes (detailed) | ✅ Yes (slightly different wording) |

---

## Standardized Modal Structure

### 1. Standard Modal ID
**Use:** `dataInfoModal` (more descriptive than "dataSource")

### 2. Standard Modal Size
**Use:** `modal-lg` (large modal for better readability)

### 3. Standard Header
**Use:** Default Bootstrap header (no custom class)
```html
<div class="modal-header">
    <h5 class="modal-title"><i class="bi bi-info-circle"></i> Data Information</h5>
    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
</div>
```

### 4. Standard Sections (In Order)

All modals should have these sections in this order:

#### Section 1: Filtering Behavior (Tab-Specific)
**Required for:** All tabs with filters
**Customization:** Adapt to tab's specific filters

**Examples:**
- **School:** Date filter only (no grade/team filters)
- **Teams:** Date filter only (no grade/team filters)
- **Grade Level:** Grade + Date filters
- **Students:** Grade + Team + Date filters

#### Section 2: Highlighting Explanation (If Applicable)
**Required for:** Tabs with gold/silver oval highlighting
**Customization:** Explain when gold vs. silver appears

**Standard Content:**
- Gold ovals (⭕) = School-wide winners
- Silver ovals (🥈) = Grade/team winners (when filtered)

#### Section 3: Date Filter Behavior (Standard)
**Required for:** All tabs
**Customization:** None (consistent across all tabs)

**Standard Content:**
```
Metrics That Honor Date Filter ◐
• Minutes Read: Cumulative through selected date
• Participation: Average daily participation through selected date
• Goals Met: Students meeting goal through selected date

Metrics That Don't Filter by Date
• Fundraising: Total donations for entire contest
• Sponsors: Total sponsors for entire contest
• Student Counts: Fixed roster counts
```

#### Section 4: Data Sources & Timestamps (Standard)
**Required for:** All tabs
**Customization:** None (identical across all tabs)

**Standard Content:**
```
Data Sources
• Reading Minutes & Participation: Daily_Logs table (Last Updated: {{ metadata.daily_logs_updated }})
• Fundraising & Sponsors: Reader_Cumulative table (Last Updated: {{ metadata.reader_cumulative_updated }})
• Student Counts: Roster table (Last Updated: {{ metadata.roster_updated }})
• Team Color Bonus: Team_Color_Bonus table (Event Date: {{ metadata.team_color_bonus_updated }})
```

#### Section 5: Important Notes (Standard)
**Required for:** All tabs
**Customization:** None (identical across all tabs)

**Standard Content:**
```html
<p class="mb-0 mt-3"><em>Note: All minutes include team color bonus points and are capped at 120 minutes per student per day for official contest totals.</em></p>
```

---

## Complete HTML Template

```html
<!-- Data Info Modal -->
<div class="modal fade" id="dataInfoModal" tabindex="-1">
    <div class="modal-dialog modal-lg">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title"><i class="bi bi-info-circle"></i> Data Information</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body">
                <!-- SECTION 1: Filtering Behavior (Tab-Specific) -->
                <!-- Customize this section based on tab's filters -->

                <!-- Example for School/Teams (Date filter only): -->
                <h6>Date Filter</h6>
                <p>The date filter controls which reading data is displayed. Select a specific day to see cumulative progress through that date, or "All Days" for the complete contest.</p>

                <!-- Example for Grade Level (Grade + Date filters): -->
                <h6>Table Filtering Behavior</h6>
                <p><strong>When "All Grades" is selected:</strong></p>
                <ul>
                    <li>Shows all classes from all grades</li>
                    <li>🥇 <span class="winning-value winning-value-school" style="font-size: 0.85rem;">Gold highlights</span> = School-wide winners (best across ALL grades)</li>
                </ul>
                <p><strong>When a specific grade is selected (e.g., "2nd Grade"):</strong></p>
                <ul>
                    <li>Table filters to show ONLY classes from that grade</li>
                    <li>🥈 <span class="winning-value winning-value-grade" style="font-size: 0.85rem;">Silver highlights</span> = Grade-level winners (best within THIS grade)</li>
                    <li>🥇 <span class="winning-value winning-value-school" style="font-size: 0.85rem;">Gold highlights</span> = Classes that are ALSO school-wide winners</li>
                </ul>

                <!-- Example for Students (Grade + Team + Date filters): -->
                <h6>Banner and Table Filtering</h6>
                <p>The banner metrics and table data update based on your filter selections:</p>
                <ul>
                    <li><strong>Grade Filter:</strong> Shows only students from selected grade(s)</li>
                    <li><strong>Team Filter:</strong> Shows only students from selected team(s)</li>
                    <li><strong>Date Filter:</strong> Shows cumulative data through selected date</li>
                    <li><strong>Combined Filters:</strong> All filters work together (e.g., "Grade 5 + Team 1 + Day 3")</li>
                </ul>

                <!-- SECTION 2: Highlighting Explanation (If Applicable) -->
                <!-- Include this for tabs with gold/silver highlighting -->
                <h6 class="mt-4">Highlighting Explanation</h6>
                <ul>
                    <li><strong>Gold ovals (⭕):</strong> School-wide winners (across all students/classes)</li>
                    <li><strong>Silver ovals (🥈):</strong> Grade/team winners (within filtered group only)</li>
                </ul>

                <hr class="my-3">

                <!-- SECTION 3: Date Filter Behavior (Standard - All Tabs) -->
                <h6>Metrics That Honor Date Filter ◐</h6>
                <p>These metrics change based on the selected date filter (cumulative through selected date):</p>
                <ul>
                    <li><strong>Minutes Read:</strong> Total capped reading minutes through selected date</li>
                    <li><strong>Participation:</strong> Average daily participation through selected date</li>
                    <li><strong>Goals Met:</strong> Students who met their goal on at least one day through selected date</li>
                </ul>

                <h6 class="mt-4">Metrics That Don't Filter by Date</h6>
                <p>These metrics always show full contest totals:</p>
                <ul>
                    <li><strong>Fundraising:</strong> Total donations for entire contest</li>
                    <li><strong>Sponsors:</strong> Total unique sponsors for entire contest</li>
                    <li><strong>Student Counts:</strong> Fixed roster counts</li>
                </ul>

                <hr class="my-3">

                <!-- SECTION 4: Data Sources & Timestamps (Standard - All Tabs) -->
                <h6>Data Sources</h6>
                <div class="data-source-item mb-2">
                    <div class="data-source-label mb-1">Reading Minutes & Participation:</div>
                    <div class="data-source-value ms-3">
                        Source: <strong>Daily_Logs</strong> table<br>
                        Last Updated: <strong>{{ metadata.daily_logs_updated }}</strong>
                    </div>
                </div>
                <div class="data-source-item mb-2">
                    <div class="data-source-label mb-1">Fundraising & Sponsors:</div>
                    <div class="data-source-value ms-3">
                        Source: <strong>Reader_Cumulative</strong> table<br>
                        Last Updated: <strong>{{ metadata.reader_cumulative_updated }}</strong>
                    </div>
                </div>
                <div class="data-source-item mb-2">
                    <div class="data-source-label mb-1">Student Counts:</div>
                    <div class="data-source-value ms-3">
                        Source: <strong>Roster</strong> table<br>
                        Last Updated: <strong>{{ metadata.roster_updated }}</strong>
                    </div>
                </div>
                <div class="data-source-item mb-2">
                    <div class="data-source-label mb-1">Team Color Bonus:</div>
                    <div class="data-source-value ms-3">
                        Source: <strong>Team_Color_Bonus</strong> table<br>
                        Event Date: <strong>{{ metadata.team_color_bonus_updated }}</strong>
                    </div>
                </div>

                <!-- SECTION 5: Important Notes (Standard - All Tabs) -->
                <p class="mb-0 mt-3"><em>Note: All minutes include team color bonus points and are capped at 120 minutes per student per day for official contest totals.</em></p>
            </div>
        </div>
    </div>
</div>
```

---

## Tab-Specific Variations

### School Tab
**Sections to Include:**
1. ✅ Filtering Behavior (Date filter only - simple explanation)
2. ❌ Highlighting Explanation (not needed - no grade/team filtering)
3. ✅ Date Filter Behavior (standard)
4. ✅ Data Sources & Timestamps (standard)
5. ✅ Important Notes (standard)

### Teams Tab
**Sections to Include:**
1. ✅ Filtering Behavior (Date filter only - simple explanation)
2. ✅ Highlighting Explanation (explain gold for school-wide winners within team context)
3. ✅ Date Filter Behavior (standard)
4. ✅ Data Sources & Timestamps (standard)
5. ✅ Important Notes (standard)

### Grade Level Tab
**Sections to Include:**
1. ✅ Filtering Behavior (Grade + Date filters - detailed grade filter explanation)
2. ✅ Highlighting Explanation (gold vs. silver when grade filtered)
3. ✅ Date Filter Behavior (standard)
4. ✅ Data Sources & Timestamps (standard)
5. ✅ Important Notes (standard)

### Students Tab
**Sections to Include:**
1. ✅ Filtering Behavior (Grade + Team + Date filters - most complex)
2. ✅ Highlighting Explanation (gold vs. silver when filters active)
3. ✅ Date Filter Behavior (standard)
4. ✅ Data Sources & Timestamps (standard)
5. ✅ Important Notes (standard)

---

## Styling Guidelines

### Modal Classes
```html
<div class="modal fade" id="dataInfoModal" tabindex="-1">
    <div class="modal-dialog modal-lg">
```

### Header
```html
<div class="modal-header">
    <h5 class="modal-title"><i class="bi bi-info-circle"></i> Data Information</h5>
    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
</div>
```

### Section Headers
```html
<h6>Section Title</h6>
<h6 class="mt-4">Subsequent Section</h6>
```

### Horizontal Dividers
```html
<hr class="my-3">
```

### Data Source Items
```html
<div class="data-source-item mb-2">
    <div class="data-source-label mb-1">Label:</div>
    <div class="data-source-value ms-3">
        Source: <strong>TableName</strong> table<br>
        Last Updated: <strong>{{ variable }}</strong>
    </div>
</div>
```

### Inline Code/Highlights
```html
<span class="winning-value winning-value-school" style="font-size: 0.85rem;">Gold highlights</span>
<span class="winning-value winning-value-grade" style="font-size: 0.85rem;">Silver highlights</span>
```

---

## Update Checklist

### School Tab (`templates/school.html`)
- [ ] Change modal ID: `dataSourceModal` → `dataInfoModal`
- [ ] Change modal size: `modal-dialog-centered` → `modal-dialog modal-lg`
- [ ] Remove custom header class: `modal-header-custom` → `modal-header`
- [ ] Keep existing Section 1: Date filter explanation (simplify wording)
- [ ] Add Section 2: Highlighting explanation (not currently present)
- [ ] Keep existing Section 3: Date filter behavior (standardize wording)
- [ ] Keep existing Section 4: Data sources (already present, standardize formatting)
- [ ] Add Section 5: Important notes (not currently present)
- [ ] Update button trigger: Change all `data-bs-target="#dataSourceModal"` to `data-bs-target="#dataInfoModal"`

### Teams Tab (`templates/teams.html`)
- [ ] Change modal ID: `dataSourceModal` → `dataInfoModal`
- [ ] Change modal size: `modal-dialog-centered` → `modal-dialog modal-lg`
- [ ] Remove custom header class: `modal-header-custom` → `modal-header`
- [ ] Keep existing Section 1: Date filter explanation (simplify wording)
- [ ] Add Section 2: Highlighting explanation (explain gold in team context)
- [ ] Keep existing Section 3: Date filter behavior (standardize wording)
- [ ] Keep existing Section 4: Data sources (already present, standardize formatting)
- [ ] Add Section 5: Important notes (not currently present)
- [ ] Update button trigger: Change all `data-bs-target="#dataSourceModal"` to `data-bs-target="#dataInfoModal"`

### Grade Level Tab (`templates/grade_level.html`)
- [ ] Keep modal ID: `dataInfoModal` ✅
- [ ] Keep modal size: `modal-lg` ✅
- [ ] Keep header style: default ✅
- [ ] Keep existing Section 1: Table filtering behavior ✅ (already good)
- [ ] Add Section 2: Highlighting explanation (expand existing content)
- [ ] Keep existing Section 3: Date filter behavior ✅ (standardize wording slightly)
- [ ] Add Section 4: Data sources & timestamps (not currently present)
- [ ] Keep existing Section 5: Important notes ✅ (already present)

### Students Tab (`templates/students.html`)
- [ ] Keep modal ID: `dataInfoModal` ✅
- [ ] Keep modal size: `modal-lg` ✅
- [ ] Keep header style: default ✅
- [ ] Keep existing Section 1: Banner and table filtering ✅ (already good)
- [ ] Keep existing Section 2: Silver highlighting ✅ (already good)
- [ ] Keep existing Section 3: Date filter behavior ✅ (standardize wording slightly)
- [ ] Add Section 4: Data sources & timestamps (not currently present)
- [ ] Add Section 5: Important notes (not currently present)

---

## Implementation Examples

### Example 1: School Tab (Simplified)

```html
<!-- Data Info Modal -->
<div class="modal fade" id="dataInfoModal" tabindex="-1">
    <div class="modal-dialog modal-lg">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title"><i class="bi bi-info-circle"></i> Data Information</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body">
                <!-- Section 1: Filtering Behavior -->
                <h6>Date Filter</h6>
                <p>The date filter controls which reading data is displayed:</p>
                <ul>
                    <li><strong>Specific Day:</strong> Shows cumulative progress through that date (e.g., Day 3 = Days 1+2+3 combined)</li>
                    <li><strong>All Days:</strong> Shows complete contest totals</li>
                </ul>

                <hr class="my-3">

                <!-- Section 3: Date Filter Behavior -->
                <h6>Metrics That Honor Date Filter ◐</h6>
                <p>These metrics change based on the selected date filter:</p>
                <ul>
                    <li><strong>Minutes Read:</strong> Cumulative through selected date</li>
                    <li><strong>Participation:</strong> Average daily participation through selected date</li>
                    <li><strong>Goals Met:</strong> Students who met goal through selected date</li>
                </ul>

                <h6 class="mt-4">Metrics That Don't Filter by Date</h6>
                <p>These metrics always show full contest totals:</p>
                <ul>
                    <li><strong>Fundraising:</strong> Total donations for entire contest</li>
                    <li><strong>Sponsors:</strong> Total sponsors for entire contest</li>
                </ul>

                <hr class="my-3">

                <!-- Section 4: Data Sources -->
                <h6>Data Sources</h6>
                <div class="data-source-item mb-2">
                    <div class="data-source-label mb-1">Reading Minutes & Participation:</div>
                    <div class="data-source-value ms-3">
                        Source: <strong>Daily_Logs</strong> table<br>
                        Last Updated: <strong>{{ metadata.daily_logs_updated }}</strong>
                    </div>
                </div>
                <div class="data-source-item mb-2">
                    <div class="data-source-label mb-1">Fundraising & Sponsors:</div>
                    <div class="data-source-value ms-3">
                        Source: <strong>Reader_Cumulative</strong> table<br>
                        Last Updated: <strong>{{ metadata.reader_cumulative_updated }}</strong>
                    </div>
                </div>
                <div class="data-source-item mb-2">
                    <div class="data-source-label mb-1">Student Counts:</div>
                    <div class="data-source-value ms-3">
                        Source: <strong>Roster</strong> table<br>
                        Last Updated: <strong>{{ metadata.roster_updated }}</strong>
                    </div>
                </div>
                <div class="data-source-item mb-2">
                    <div class="data-source-label mb-1">Team Color Bonus:</div>
                    <div class="data-source-value ms-3">
                        Source: <strong>Team_Color_Bonus</strong> table<br>
                        Event Date: <strong>{{ metadata.team_color_bonus_updated }}</strong>
                    </div>
                </div>

                <!-- Section 5: Notes -->
                <p class="mb-0 mt-3"><em>Note: All minutes include team color bonus points and are capped at 120 minutes per student per day for official contest totals.</em></p>
            </div>
        </div>
    </div>
</div>
```

### Example 2: Students Tab (Most Complex)

```html
<!-- Data Info Modal -->
<div class="modal fade" id="dataInfoModal" tabindex="-1">
    <div class="modal-dialog modal-lg">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title"><i class="bi bi-info-circle"></i> Data Information</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body">
                <!-- Section 1: Filtering Behavior -->
                <h6>Banner and Table Filtering</h6>
                <p>The banner metrics and table data update based on your filter selections:</p>
                <ul>
                    <li><strong>Grade Filter:</strong> Shows only students from selected grade(s)</li>
                    <li><strong>Team Filter:</strong> Shows only students from selected team(s)</li>
                    <li><strong>Date Filter:</strong> Shows cumulative data through selected date</li>
                    <li><strong>Combined Filters:</strong> All filters work together (e.g., "Grade 5 + Team 1 + Day 3")</li>
                </ul>

                <!-- Section 2: Highlighting -->
                <h6 class="mt-4">Silver Highlighting (Filter Active)</h6>
                <p>When you filter by grade or team, silver ovals (🥈) appear on the highest values within that filtered group.</p>
                <ul>
                    <li><strong>Gold ovals (⭕):</strong> School-wide winners (across all 411 students)</li>
                    <li><strong>Silver ovals (🥈):</strong> Grade/team winners (within filtered group only)</li>
                </ul>

                <hr class="my-3">

                <!-- Section 3: Date Filter Behavior -->
                <h6>Metrics That Honor Date Filter ◐</h6>
                <p>These metrics change based on the selected date filter:</p>
                <ul>
                    <li><strong>Minutes Read:</strong> Cumulative through selected date</li>
                    <li><strong>Participation:</strong> Average daily participation through selected date</li>
                    <li><strong>Goal Met:</strong> Students who met goal through selected date</li>
                    <li><strong>Days Participated:</strong> Count of days with >0 minutes through selected date</li>
                </ul>

                <h6 class="mt-4">Metrics That Don't Filter by Date</h6>
                <p>These metrics always show full contest totals:</p>
                <ul>
                    <li><strong>Fundraising:</strong> Total donations for entire contest</li>
                    <li><strong>Sponsors:</strong> Total sponsors for entire contest</li>
                </ul>

                <hr class="my-3">

                <!-- Section 4: Data Sources -->
                <h6>Data Sources</h6>
                <div class="data-source-item mb-2">
                    <div class="data-source-label mb-1">Reading Minutes & Participation:</div>
                    <div class="data-source-value ms-3">
                        Source: <strong>Daily_Logs</strong> table<br>
                        Last Updated: <strong>{{ metadata.daily_logs_updated }}</strong>
                    </div>
                </div>
                <div class="data-source-item mb-2">
                    <div class="data-source-label mb-1">Fundraising & Sponsors:</div>
                    <div class="data-source-value ms-3">
                        Source: <strong>Reader_Cumulative</strong> table<br>
                        Last Updated: <strong>{{ metadata.reader_cumulative_updated }}</strong>
                    </div>
                </div>
                <div class="data-source-item mb-2">
                    <div class="data-source-label mb-1">Student Counts:</div>
                    <div class="data-source-value ms-3">
                        Source: <strong>Roster</strong> table<br>
                        Last Updated: <strong>{{ metadata.roster_updated }}</strong>
                    </div>
                </div>
                <div class="data-source-item mb-2">
                    <div class="data-source-label mb-1">Team Color Bonus:</div>
                    <div class="data-source-value ms-3">
                        Source: <strong>Team_Color_Bonus</strong> table<br>
                        Event Date: <strong>{{ metadata.team_color_bonus_updated }}</strong>
                    </div>
                </div>

                <!-- Section 5: Notes -->
                <p class="mb-0 mt-3"><em>Note: All minutes include team color bonus points and are capped at 120 minutes per student per day for official contest totals.</em></p>
            </div>
        </div>
    </div>
</div>
```

---

## Benefits of Standardization

1. **Consistency:** Users see the same modal structure across all tabs
2. **Completeness:** All tabs now have data sources AND filter behavior
3. **Maintainability:** One template to update instead of 4 different implementations
4. **User Education:** Data sources are visible on every tab
5. **Clarity:** Filtering logic is explained where applicable
6. **Predictability:** Users know what to expect when clicking "Data Info"

---

## Migration Priority

**High Priority (Most Different from Standard):**
1. School tab - needs most changes (add data sources section, restructure)
2. Teams tab - needs most changes (add data sources section, restructure)

**Low Priority (Close to Standard):**
3. Grade Level tab - mostly compliant, add data sources section
4. Students tab - mostly compliant, add data sources section

---

## Testing Checklist

After updating each modal, verify:
- [ ] Modal opens correctly when button clicked
- [ ] Modal ID matches button's `data-bs-target`
- [ ] All 5 sections present (or appropriate subset)
- [ ] Content matches tab's filtering capabilities
- [ ] Timestamps populate from `{{ metadata }}` variables
- [ ] Visual formatting is consistent with standard
- [ ] Modal closes properly
- [ ] No console errors

---

## Future Enhancements

1. **Dynamic Content:** Consider generating some sections from backend metadata
2. **Collapsible Sections:** For modals with lots of content, consider accordions
3. **Visual Examples:** Add screenshots or diagrams showing filter behavior
4. **Interactive Help:** Link to video tutorials or guided tours
5. **Customization:** Allow users to toggle which sections they want to see

---

**END OF DOCUMENT**
