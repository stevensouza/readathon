# Feature 11: Slide Column Indicators

**[← Back to Index](../00-INDEX.md)**

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



---

**[← Back to Index](../00-INDEX.md)**
