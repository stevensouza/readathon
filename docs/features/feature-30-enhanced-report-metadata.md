# Feature 30: Enhanced Report Metadata (Column Descriptions, Source Tables, Collapsible Sections)

**Status:** In Progress
**Priority:** High
**Category:** Reports & Analytics
**Related Features:** Feature-31 (Dynamic Report Analysis)

---

## 📋 Overview

Add comprehensive metadata to all reports and table views, including column descriptions, source table information, and collapsible UI sections to keep the interface clean while providing detailed reference information.

---

## 🎯 Problem Statement

Current reports lack context:
- Column names aren't always self-explanatory (e.g., "difference", "issue_type")
- Users don't know which database tables are the source of the data
- All metadata is displayed at once, pushing results down the page
- No easy way to understand what each column means without asking

---

## ✅ Solution

### 1. **Column Descriptions**
Every report will include a `column_descriptions` dictionary that explains each column:

```python
'column_descriptions': {
    'student_name': 'Student\'s full name from Roster table',
    'daily_minutes_sum': 'Total minutes from Daily_Logs (uncapped actual values)',
    'cumulative_minutes': 'Total minutes from Reader_Cumulative download',
    'difference': 'Cumulative minus Daily (positive = Cumulative is higher)',
    'cap_exceeded': 'Minutes lost due to 120-minute daily cap',
    'issue_type': 'CAP_ONLY: Exceeded cap | DATA_MISMATCH: Different values | BOTH: Both issues'
}
```

### 2. **Source Tables**
Every report will include a `source` section identifying:
- **Primary tables:** Main data sources (e.g., Daily_Logs, Reader_Cumulative)
- **Reference tables:** Supporting tables (e.g., Roster, Grade_Rules)
- **Note:** Brief explanation of how tables are joined or combined

```python
'source': {
    'primary_tables': ['Daily_Logs', 'Reader_Cumulative'],
    'reference_tables': ['Roster'],
    'note': 'Compares sum of Daily_Logs.minutes_read vs Reader_Cumulative.cumulative_minutes'
}
```

### 3. **Collapsible UI Sections**
To prevent information overload and keep results visible:

**Default View:**
```
┌─────────────────────────────────────────────────┐
│ Q21: Minutes Integrity Check         [Export]  │
├─────────────────────────────────────────────────┤
│ ▶ Report Information (Click to expand)         │
│   [Collapsed - Description, Source, Columns]   │
│                                                 │
│ ▼ Analysis (Click to collapse)                 │
│   [Expanded - Key insights and metrics]        │
├─────────────────────────────────────────────────┤
│ Results Table (immediately visible)            │
└─────────────────────────────────────────────────┘
```

**Expanded Report Information Section:**
```
▼ Report Information (Click to collapse)
  ┌─────────────────────────────────────────────┐
  │ Description:                                 │
  │   Verify daily minutes sum matches           │
  │   cumulative minutes from Reader_Cumulative  │
  │                                              │
  │ Source Tables:                               │
  │   Primary: Daily_Logs, Reader_Cumulative     │
  │   Reference: Roster                          │
  │   Note: Compares sum of Daily_Logs...        │
  │                                              │
  │ Column Descriptions:                         │
  │   • student_name: Student's full name...     │
  │   • daily_minutes_sum: Total minutes...      │
  │   • cumulative_minutes: Total from...        │
  │   • difference: Cumulative minus Daily...    │
  │   • cap_exceeded: Minutes lost to cap...     │
  │   • issue_type: CAP_ONLY | MISMATCH | BOTH   │
  │                                              │
  │ Sort Order: difference (desc)                │
  └─────────────────────────────────────────────┘
```

---

## 🔧 Implementation Details

### Backend (database.py)

Update all report functions to return enhanced metadata:

```python
def q21_minutes_integrity_check(self) -> Dict[str, Any]:
    # ... existing query code ...

    return {
        'title': 'Q21: Minutes Integrity Check',
        'description': 'Verify daily minutes sum matches cumulative minutes',

        # NEW: Column descriptions
        'column_descriptions': {
            'student_name': 'Student\'s full name from Roster',
            'daily_minutes_sum': 'Total minutes from Daily_Logs (uncapped)',
            # ... more columns ...
        },

        # NEW: Source tables
        'source': {
            'primary_tables': ['Daily_Logs', 'Reader_Cumulative'],
            'reference_tables': ['Roster'],
            'note': 'Compares Daily_Logs sum vs Reader_Cumulative'
        },

        'columns': [...],
        'data': results,
        'sort': 'difference (desc)'
    }
```

### Frontend (templates/report_display.html)

Create reusable template component for report metadata:

```html
<!-- Collapsible Report Information Section (Collapsed by Default) -->
<details class="report-metadata mb-3">
    <summary class="report-metadata-header">
        <i class="fas fa-info-circle"></i> Report Information
    </summary>
    <div class="report-metadata-body">
        <!-- Description -->
        <div class="metadata-section">
            <h6>Description</h6>
            <p>{{ report.description }}</p>
        </div>

        <!-- Source Tables -->
        <div class="metadata-section">
            <h6>Source Tables</h6>
            <p>
                <strong>Primary:</strong> {{ report.source.primary_tables|join(', ') }}<br>
                {% if report.source.reference_tables %}
                <strong>Reference:</strong> {{ report.source.reference_tables|join(', ') }}<br>
                {% endif %}
                {% if report.source.note %}
                <em>{{ report.source.note }}</em>
                {% endif %}
            </p>
        </div>

        <!-- Column Descriptions -->
        <div class="metadata-section">
            <h6>Column Descriptions</h6>
            <dl class="column-descriptions">
                {% for col, desc in report.column_descriptions.items() %}
                <dt>{{ col }}</dt>
                <dd>{{ desc }}</dd>
                {% endfor %}
            </dl>
        </div>

        <!-- Sort Order -->
        {% if report.sort %}
        <div class="metadata-section">
            <h6>Sort Order</h6>
            <p>{{ report.sort }}</p>
        </div>
        {% endif %}
    </div>
</details>
```

### CSS Styling

```css
/* Report Metadata Section */
.report-metadata {
    background-color: #f8f9fa;
    border: 1px solid #dee2e6;
    border-radius: 0.25rem;
    padding: 0;
}

.report-metadata-header {
    padding: 0.75rem 1rem;
    cursor: pointer;
    user-select: none;
    font-weight: 600;
    background-color: #e9ecef;
}

.report-metadata-header:hover {
    background-color: #dee2e6;
}

.report-metadata-body {
    padding: 1rem;
}

.metadata-section {
    margin-bottom: 1rem;
}

.metadata-section:last-child {
    margin-bottom: 0;
}

.metadata-section h6 {
    font-weight: 600;
    color: #495057;
    margin-bottom: 0.5rem;
}

.column-descriptions {
    margin-left: 1rem;
}

.column-descriptions dt {
    font-family: 'Courier New', monospace;
    font-weight: 600;
    color: #007bff;
    margin-top: 0.5rem;
}

.column-descriptions dd {
    margin-left: 1.5rem;
    color: #6c757d;
}
```

---

## 📊 Affected Reports

All reports will be updated with enhanced metadata:

### Phase 1: High-Priority Reports (with Analysis)
- ✅ Q21: Minutes Integrity Check
- Q22: Student Name Sync Check
- Q23: Roster Integrity Check

### Phase 2: Core Reports
- Q2: Daily Summary Report
- Q5: Student Cumulative Report
- Q6: Class Participation Winner
- Q14: Team Participation
- Q18: Lead Class by Grade
- Q19: Team Minutes
- Q20: Team Donations

### Phase 3: Remaining Reports
- Q1: Table Row Counts
- Q4: Prize Drawing
- Q7: Complete Log
- Q8: Student Reading Details

---

## 🧪 Testing Checklist

- [ ] All reports return `column_descriptions` and `source` metadata
- [ ] Collapsible sections work on all browsers
- [ ] Report Information section is collapsed by default
- [ ] Analysis section (when present) is expanded by default
- [ ] Mobile-friendly: sections expand/collapse smoothly on mobile
- [ ] Column descriptions are clear and helpful
- [ ] Source tables are accurately documented
- [ ] No JavaScript required (uses HTML5 `<details>` tag)
- [ ] Keyboard accessible (can expand/collapse with Enter/Space)

---

## 📱 User Experience

**Before:**
- User sees report title, then immediately the data table
- No context about what columns mean
- No information about data sources
- Questions like "What does 'difference' mean?" require asking someone

**After:**
- User sees report title and Analysis (if applicable)
- Data table is immediately visible
- "Report Information" section is available but collapsed
- One click reveals all metadata: descriptions, sources, column meanings
- Self-service: users can understand reports without asking

---

## 🔄 Migration Path

1. **Create template component** for report metadata display
2. **Update Q21** as pilot (most complex metadata)
3. **Test and refine** UI/UX based on feedback
4. **Gradually update** remaining reports in priority order
5. **Add to table views** (Roster, Daily_Logs, etc.)

---

## 📝 Related Documentation

- Feature-31: Dynamic Report Analysis
- Database Schema: `docs/architecture/database-schema.md`
- Report API: `docs/architecture/api-endpoints.md`

---

## 💡 Future Enhancements

1. **User Preferences:** Remember if user prefers sections expanded/collapsed
2. **Tooltips:** Hover over column headers to see descriptions inline
3. **Search:** Search within column descriptions
4. **Export Metadata:** Include column descriptions in CSV exports
5. **Visual Schema:** Show table relationships visually for complex reports

---

**Last Updated:** 2025-10-16
**Author:** System Design Team
**Approved By:** Pending
