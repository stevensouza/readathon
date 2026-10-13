# Bug Backlog (from the v2026.23.0 code review)

Found in a full code review on 2026-10-12, checked against the code but **not fixed yet**. They're older than the
roster name-matching change. Fixed items are in `md/CHANGELOG.md` (v2026.23.0).

## Medium
- **Q21 and Q24 exports fail.** Q21 rows have an extra `daily_minutes_capped` key that isn't in `columns`
  (`csv.DictWriter` raises). Q24 rows are lists, not dicts, so its export fails and its on-screen table is blank.
  Fix: `extrasaction='ignore'` in `export_report`, and build Q24 rows as dicts.
- **School page with a date filter:**
  - Color-bonus minutes and points ignore the date (`app.py` school route; Teams page; Grade Level `ColorBonus`
    CTE in `queries.py`).
  - `WHERE dl.log_date <= ...` on a `LEFT JOIN Daily_Logs` drops students with no minutes yet. That shrinks team
    size and inflates the % metrics.
  - Fix: filter `event_date <= date`, and move the date condition into the `ON` clause.
- **Team colors on the School and Grade Level pages** come from the team-name CSS class (`team-badge-kitsko` etc.),
  not from alphabetical order. Other team names get no color. Fix: pass a team → index map, as `students.html` does.
- **School "Top class"** groups by teacher, so AM and PM kindergarten are merged. Fix: group by `class_name`.
- **Team color bonus upload:**
  - It commits the valid rows even when it reports an error.
  - `event_date` isn't validated.
  - There's no per-date delete.

## Low
- Batch daily upload always sends `confirmed=true`, which skips the "sample file into a real DB" check.
- `/tables` redirects to `group=tables`, but the tag is `table`, so the list comes up empty.
- Upload_History table info: `MAX(upload_date)` should be `MAX(upload_timestamp)` (500, so the panel is hidden). Some
  column descriptions in `get_table_metadata` name columns that don't exist.
- Silent failures:
  - `switchDatabase` ignores a failed response.
  - `makeDatabaseEditable`'s first fetch is outside its `try`.
  - The Reports page never checks the metadata response.
- `tests/test_scoreboards_page.py` settings test writes the default download URLs into the real registry's
  `App_Settings`.
- `float('$1,234')` in a cumulative file silently becomes 0.
- Upload page:
  - Changing the file selection while the Match names panel is open uploads the files that were checked (daily) or
    the newly picked file (cumulative).
  - A daily file with several rows for one name shows "N rows" in the panel, which also means "N days" when several
    files are checked together.
