# Feature 4: Combined Reader Report

**[← Back to Index](../00-INDEX.md)**

---

### Feature 4: Combined Reader Report
**New Report:** Q27 Complete Student Report

**Requirements:**
- Combines data from multiple sources:
  - All columns from Reader_Cumulative: student_name, teacher_name, team_name, donation_amount, sponsors, cumulative_minutes
  - From Daily_Logs aggregation:
    - days_participated (count of days with minutes > 0)
    - days_met_goal (count of days where minutes ≥ min_daily_minutes)
    - total_minutes_capped (SUM with 120-min daily cap)
- SQL query:
```sql
SELECT
    r.student_name,
    r.class_name,
    r.teacher_name,
    r.grade_level,
    r.team_name,
    COALESCE(rc.donation_amount, 0) as donation_amount,
    COALESCE(rc.sponsors, 0) as sponsors,
    COALESCE(rc.cumulative_minutes, 0) as cumulative_minutes,
    COUNT(CASE WHEN dl.minutes_read > 0 THEN 1 END) as days_participated,
    SUM(CASE WHEN dl.minutes_read >= gr.min_daily_minutes THEN 1 ELSE 0 END) as days_met_goal,
    SUM(MIN(dl.minutes_read, 120)) as total_minutes_capped
FROM Roster r
LEFT JOIN Reader_Cumulative rc ON r.student_name = rc.student_name
LEFT JOIN Daily_Logs dl ON r.student_name = dl.student_name
LEFT JOIN Grade_Rules gr ON r.grade_level = gr.grade_level
GROUP BY r.student_name, r.class_name, r.teacher_name, r.grade_level, r.team_name,
         rc.donation_amount, rc.sponsors, rc.cumulative_minutes
ORDER BY total_minutes_capped DESC, r.student_name ASC
```

- Add to Reports page in "Export Reports" section
- Include export/copy buttons
- Sortable columns

---



---

**[← Back to Index](../00-INDEX.md)**
