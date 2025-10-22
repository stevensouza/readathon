# Feature 13: Report Options Improvements

**[← Back to Index](../00-INDEX.md)**

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



---

**[← Back to Index](../00-INDEX.md)**
