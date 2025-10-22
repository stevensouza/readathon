# Feature 8: Enhanced Participation Metrics

**[← Back to Index](../00-INDEX.md)**

---

### Feature 8: Enhanced Participation Metrics
**Current:** Shows "Students Participating: X of Y (Z%)"

**Enhancements:** Add to the blue participation box:
```
Students Participating: 205 of 411 (49.9%)
├─ Participated ALL days: 180 (43.8%)
├─ Met goal ≥1 day: 195 (47.4%)
└─ Met goal ALL days: 150 (36.5%)
Days of Data: 3
```

**SQL Queries Needed:**
```sql
-- Participated ALL days
SELECT COUNT(DISTINCT student_name)
FROM (
    SELECT student_name, COUNT(DISTINCT log_date) as days
    FROM Daily_Logs WHERE minutes_read > 0
    GROUP BY student_name
    HAVING days = (SELECT COUNT(DISTINCT log_date) FROM Daily_Logs)
)

-- Met goal at least 1 day
SELECT COUNT(DISTINCT student_name)
FROM Daily_Logs dl
JOIN Grade_Rules gr ON dl.grade_level = gr.grade_level
WHERE dl.minutes_read >= gr.min_daily_minutes

-- Met goal ALL days
SELECT COUNT(DISTINCT student_name)
FROM (
    SELECT dl.student_name,
           COUNT(CASE WHEN dl.minutes_read >= gr.min_daily_minutes THEN 1 END) as goal_days,
           COUNT(DISTINCT dl.log_date) as total_days
    FROM Daily_Logs dl
    JOIN Roster r ON dl.student_name = r.student_name
    JOIN Grade_Rules gr ON r.grade_level = gr.grade_level
    GROUP BY dl.student_name
    HAVING goal_days = (SELECT COUNT(DISTINCT log_date) FROM Daily_Logs)
       AND total_days = goal_days
)
```

**Note:** Will iterate with UI prototype for display format.

---



---

**[← Back to Index](../00-INDEX.md)**
