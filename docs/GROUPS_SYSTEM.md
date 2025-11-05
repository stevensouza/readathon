# Group-Based Tagging System

**Last Updated:** 2025-11-05
**Version:** v2026.9.0

## Overview

The Read-a-Thon system uses a **pure group-based tagging system** for classifying and organizing all items (reports, tables, workflows). This replaces the previous `item_type` and `report_type` fields with a single, flexible `groups` array.

### Key Principles

1. **Single Source of Truth:** All classification is in the `groups` array
2. **Multiple Group Membership:** Items can belong to multiple groups simultaneously
3. **Hierarchical Naming:** Use periods for namespaces (e.g., `workflow.qa`, `requires.date`)
4. **Flat Naming:** No prefix for basic categories (e.g., `admin`, `prize`, `report`)
5. **Self-Describing:** Tags declare structure, behavior, membership, and domain

## Group Categories

### 1. Structural Tags (Type)
Define what kind of item this is:
- `report` - A query that generates report data
- `table` - A database table view
- `workflow` - A collection of reports to run in sequence

**Usage:** Every item MUST have exactly one structural tag.

### 2. Semantic Tags (Purpose)
Describe the purpose or category:
- `prize` - Report shows prize winners
- `slides` - Report appears in daily slide deck
- `admin` - Administrative/maintenance report
- `export` - Export/analysis report
- `cumulative` - Shows cumulative totals
- `daily` - Shows daily data
- `integrity` - Data integrity check
- `utility` - General utility report
- `database` - Database management

**Usage:** Reports typically have 1-2 semantic tags.

### 3. Workflow Tags (Membership)
Indicate which workflows include this report:
- `workflow.qa` - QA: All Main Reports (23 reports)
- `workflow.qd` - QD: Daily Slide Update (5 reports)
- `workflow.qc` - QC: Cumulative Workflow (6 reports)
- `workflow.qf` - QF: Final Prize Winners (10 reports)

**Usage:** Reports can belong to multiple workflows.

### 4. Behavior Tags (Requirements)
Specify what parameters the report needs:
- `requires.date` - Report requires a date parameter
- `requires.group_by` - Report requires a group_by parameter
- `requires.sort` - Report requires sort options
- `requires.limit` - Report requires limit options

**Usage:** Add all applicable requirement tags.

### 5. Domain Tags (Subject Area)
Describe what the report is about:
- `fundraising` - Related to donations/money
- `reading` - Related to reading minutes
- `participation` - Related to participation rates
- `sponsors` - Related to sponsor counts

**Usage:** Optional, helps with organization and search.

## Complete Tag Reference

### Structural Tags
| Tag | Description | Count |
|-----|-------------|-------|
| `report` | Query-based report | 22 |
| `table` | Database table | 8 |
| `workflow` | Workflow collection | 4 |

### Semantic Tags
| Tag | Description | Example Reports |
|-----|-------------|-----------------|
| `prize` | Prize winner reports | Q9, Q10, Q11, Q12, Q13, Q15, Q16 |
| `slides` | Daily slide deck | Q2, Q4, Q14, Q18, Q19, Q20 |
| `admin` | Administrative reports | Q1, Q21, Q22, Q23, Q24 |
| `export` | Export/analysis | Q3, Q7, Q8 |
| `cumulative` | Cumulative totals | Q3, Q5, Q6, Q14, Q15 |
| `daily` | Daily data | Q2, Q4, Q7, Q8 |
| `integrity` | Data integrity | Q21, Q22, Q23 |
| `utility` | General utility | Q1 |
| `database` | Database mgmt | Q24 |

### Workflow Tags
| Tag | Description | Report Count |
|-----|-------------|--------------|
| `workflow.qa` | All Main Reports | 23 |
| `workflow.qd` | Daily Slide Update | 5 |
| `workflow.qc` | Cumulative Workflow | 6 |
| `workflow.qf` | Final Prize Winners | 10 |

### Behavior Tags
| Tag | Description | Used By |
|-----|-------------|---------|
| `requires.date` | Needs date parameter | Q2, Q4, Q7, Q8 |
| `requires.group_by` | Needs group_by param | Q2 |
| `requires.sort` | Needs sort options | Q5 |
| `requires.limit` | Needs limit options | Q5 |

## Example Report Definitions

### Simple Report (Q1)
```python
{
    'id': 'q1',
    'name': 'Q1: Table Row Counts',
    'description': 'Shows row counts for all database tables',
    'groups': ['report', 'utility', 'admin', 'workflow.qa']
}
```
- **Structural:** `report`
- **Semantic:** `utility`, `admin`
- **Workflow:** `workflow.qa`

### Complex Report (Q2)
```python
{
    'id': 'q2',
    'name': 'Q2: Daily Summary Report',
    'description': 'Daily summary by class or team with participation rates',
    'groups': ['report', 'daily', 'slides', 'workflow.qa',
               'requires.date', 'requires.group_by']
}
```
- **Structural:** `report`
- **Semantic:** `daily`, `slides`
- **Workflow:** `workflow.qa`
- **Behavior:** `requires.date`, `requires.group_by`

### Multi-Workflow Report (Q14)
```python
{
    'id': 'q14',
    'name': 'Q14/Slide 3: Team Participation',
    'description': 'Team participation rates with color bonus',
    'groups': ['report', 'cumulative', 'prize', 'slides',
               'workflow.qa', 'workflow.qd', 'workflow.qc', 'workflow.qf']
}
```
Appears in **4 workflows!**

## Querying by Groups

### Helper Functions (app.py)

#### Get items by single group
```python
from app import get_items_by_group

# Get all reports
reports = get_items_by_group('report')

# Get all prize reports
prize_reports = get_items_by_group('prize')

# Get all items in QA workflow (supports wildcards)
qa_items = get_items_by_group('workflow.qa')

# Get ALL workflow items (using wildcard)
all_workflow_items = get_items_by_group('workflow.*')
```

#### Get items by multiple groups (AND/OR logic)
```python
from app import get_items_by_groups

# AND logic: Reports that are BOTH prize AND slides
prize_slides = get_items_by_groups(['prize', 'slides'], match_all=True)

# OR logic: Reports that are EITHER prize OR slides
either = get_items_by_groups(['prize', 'slides'], match_all=False)
```

#### Type checking helpers
```python
from app import is_report, is_workflow, is_table

item = {'groups': ['report', 'prize']}
if is_report(item):
    print("This is a report")
```

#### Check requirements
```python
from app import requires_date, requires_group_by

item = {'groups': ['report', 'requires.date']}
if requires_date(item):
    print("This report needs a date parameter")
```

#### Get workflow reports
```python
from app import get_workflow_reports

# Get all reports in QA workflow
qa_reports = get_workflow_reports('qa')  # Returns items with 'workflow.qa'
```

### Dynamic Workflow Execution

**Before (hardcoded):**
```python
@app.route('/api/workflow/qa')
def run_qa_workflow():
    report_ids = ['q1', 'q2', 'q3', ...]  # Hardcoded list
```

**After (dynamic):**
```python
@app.route('/api/workflow/<workflow_id>')
def run_workflow(workflow_id):
    workflow_items = get_workflow_reports(workflow_id)
    report_ids = [item['id'] for item in workflow_items]
```

## Frontend Integration

### Data Attributes

Items in the Reports page include:
```html
<a href="#" class="list-group-item"
   data-item-id="q2"
   data-name="Q2: Daily Summary Report"
   data-description="Daily summary..."
   data-groups="report daily slides workflow.qa requires.date requires.group_by">
```

### JavaScript Group Detection

**Determine item type:**
```javascript
const groups = element.dataset.groups.split(' ');
if (groups.includes('report')) {
    // This is a report
} else if (groups.includes('table')) {
    // This is a table
} else if (groups.includes('workflow')) {
    // This is a workflow
}
```

### Search Functionality

**Search across group arrays:**
```javascript
const groupsMatch = item.groups.split(' ').some(g => g.includes(search));
if (groupsMatch) {
    // Item matches search
}
```

### Dynamic Report Options

**Show/hide options based on tags:**
```javascript
function showReportOptions(reportId) {
    const item = items.find(i => i.id === reportId);

    if (item.groups.includes('requires.date')) {
        document.getElementById('dateOption').style.display = 'block';
    }
    if (item.groups.includes('requires.group_by')) {
        document.getElementById('groupByOption').style.display = 'block';
    }
}
```

## Adding New Items

### Adding a New Report

1. **Add to `get_unified_items()` in app.py:**
```python
{
    'id': 'q25',
    'name': 'Q25: New Report',
    'description': 'Description of what it does',
    'groups': [
        'report',              # Structural (required)
        'prize',               # Semantic (purpose)
        'workflow.qa',         # Workflow membership
        'requires.date'        # Behavior (if needed)
    ]
}
```

2. **Report will automatically appear in:**
   - Reports & Data page (filtered by all groups)
   - QA workflow (because of `workflow.qa` tag)
   - Search results when searching "prize", "report", "workflow", etc.

3. **No hardcoded lists to update!**

### Adding a New Workflow

1. **Add workflow item:**
```python
{
    'id': 'qx',
    'name': 'QX: New Workflow',
    'description': 'Description',
    'groups': ['workflow']
}
```

2. **Tag relevant reports with `workflow.qx`:**
```python
{
    'id': 'q2',
    'groups': ['report', 'daily', 'workflow.qa', 'workflow.qx']  # Added
}
```

3. **Create template section in workflows.html:**
```html
<div class="card">
    <div class="card-header">QX: New Workflow</div>
    <div class="card-body">
        <p>Runs {{ qx_count }} reports:</p>
        <ul>
            {% for report in qx_reports %}
            <li>{{ report.name }}</li>
            {% endfor %}
        </ul>
        <button onclick="runWorkflow('qx')">Run Workflow</button>
    </div>
</div>
```

4. **Update workflows route:**
```python
@app.route('/workflows')
def workflows_page():
    qx_reports = get_workflow_reports('qx')
    return render_template('workflows.html', qx_reports=qx_reports,
                         qx_count=len(qx_reports))
```

## Migration Notes

### What Changed

**Removed fields:**
- `item_type` (replaced by structural tags: `report`, `table`, `workflow`)
- `report_type` (replaced by semantic tags: `daily`, `cumulative`, etc.)

**Added:**
- Single `groups` array contains all classification
- Helper functions for querying and type checking
- Dynamic workflow execution

### Code Updates

1. **Data Model (app.py lines 75-134):**
   - All 24 reports updated with new group tags
   - Removed `item_type` and `report_type` fields

2. **Helper Functions (app.py lines 137-202):**
   - Added `get_items_by_group()`
   - Added `get_items_by_groups()`
   - Added `is_report()`, `is_workflow()`, `is_table()`
   - Added `requires_date()`, `requires_group_by()`
   - Added `get_workflow_reports()`

3. **Routes (app.py):**
   - `/workflows` - passes dynamic report lists
   - `/api/workflow/<id>` - uses `get_workflow_reports()`
   - `/api/group/<id>/items` - new endpoint for group queries

4. **Frontend (templates/):**
   - `reports.html` - displays multiple group badges, searches groups array
   - `workflows.html` - dynamic report lists using Jinja2 loops
   - Run Group feature fetches from `/api/group/<id>/items`

5. **Tests (test_reports_page.py):**
   - Updated to check for groups instead of item_type
   - Removed item_type from required fields
   - Updated search tests to check data-groups

### Benefits

✅ **Flexibility:** Items can belong to multiple groups
✅ **No Hardcoding:** Workflows automatically include tagged reports
✅ **Searchable:** Search across all group tags
✅ **Extensible:** Easy to add new groups or workflows
✅ **Self-Documenting:** Tags describe purpose and behavior
✅ **Maintainable:** Single source of truth

## Testing

All tests pass (277 passing, 5 skipped):
```bash
pytest -v
```

Key test files:
- `test_reports_page.py` - Reports page group functionality
- `test_export_all.py` - Export feature tests
- All other tests verify no regression from refactor

## Examples

### Find all prize reports that require a date
```python
from app import get_items_by_groups, requires_date

prize_reports = get_items_by_group('prize')
prize_with_date = [item for item in prize_reports if requires_date(item)]
print(f"Found {len(prize_with_date)} prize reports requiring date")
```

### Get all reports in multiple workflows
```python
from app import get_unified_items

all_items = get_unified_items()
multi_workflow = [
    item for item in all_items
    if is_report(item) and
    sum(1 for g in item['groups'] if g.startswith('workflow.')) > 1
]
print(f"Found {len(multi_workflow)} reports in multiple workflows")
# Result: Q14 appears in 4 workflows!
```

### Find reports that haven't been assigned to any workflow
```python
from app import get_unified_items, is_report

all_reports = [item for item in get_unified_items() if is_report(item)]
no_workflow = [
    item for item in all_reports
    if not any(g.startswith('workflow.') for g in item['groups'])
]
print(f"Found {len(no_workflow)} reports not in any workflow")
```

## Future Enhancements

Potential additional groups:
- `requires.sort` - Report supports sorting
- `requires.limit` - Report supports row limiting
- `interactive` - Report has interactive features
- `realtime` - Report updates in real-time
- `scheduled` - Report can be scheduled

---

**For questions or suggestions, update this document and commit.**
