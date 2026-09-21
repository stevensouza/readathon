# Read-a-Thon Reporting System: Requirements Document (v26)

**Last Updated:** 2026-09-21 (prepared for the Oct 2026 read-a-thon)

**History:** v1–v25 (Sep–Oct 2025) lived in the Google Doc "2025 Read-a-thon Requirements". Back then an AI chat session (Gemini) acted as the database and reporting engine. v26 is the first version kept in git. It describes the Flask application that replaced that approach and ran the 2025 event.

**Related documents:**
- `md/IMPLEMENTATION_PROMPT.md`: full feature-by-feature implementation spec (also shown in the app under Help → Application Requirements)
- `md/RULES.md`: calculation and UI rules every page must follow
- `md/UI_PATTERNS.md`: styling and component patterns
- `md/CHANGELOG.md`: release history

**Privacy:** real student, teacher, team and school names never go in git. Public files use fictitious data. The sample data uses "team1"/"team2", and docs use "Phoenix"/"Dragons".

---

## I. System Overview

The system is a data analysis and reporting tool for a multi-day elementary school read-a-thon. It tracks, per student:
- reading minutes
- participation
- fundraising (donations and sponsors)

It reports these by student, class, grade, team and school.

- **Form:** a local Flask web application, run on the organizer's Mac, with data in SQLite files. No server deployment, no accounts.
- **Design principle:** simplicity and transparency for a non-technical user.
  - Normalized tables on the backend.
  - A fully denormalized "flat" export (Q7 Complete Log) for Excel/Google Sheets review.
  - Every report explains its columns, data sources and terms.
- **Scale:** about 400 students, about 20 classes, grades K–5, two teams.

## II. Data Model & Environment

### A. Databases (one per year)

| File | Purpose | In git? |
|---|---|---|
| `db/readathon_registry.db` | Registry of all year databases, plus which one is active | No (created automatically on first start) |
| `db/readathon_<YEAR>.db` | One contest database per event year, e.g. `readathon_2025.db`, `readathon_2026.db` | **No**: contains student PII. Back it up yourself. |
| `db/readathon_sample.db` | Fictitious sample data for testing and demos | Yes |

- **Naming convention:** the database file and display name carry the **event year** ("2026 Read-a-Thon" → `readathon_2026.db`).
- **Sharing:** code comes from `git clone`/`git pull`; databases are copied into `db/` privately. Any `db/readathon_<YEAR>.db` is registered automatically when the app starts. `./package_data.sh` zips `db/` for moving the current state to another computer (only one computer should be "live" at a time).
- **Sample protection:** the sample database shows a yellow/amber banner. Uploading a file with "sample" in its name into a non-sample database asks for confirmation.
- **Picking the active database:** the header dropdown or `--db` on the command line. The choice is remembered in `.readathon_config`.

### B. Setup Tables (loaded once per year, when the database is created)

- **Roster**: `student_name, class_name, home_room, teacher_name, grade_level, team_name`
- **Class_Info**: `class_name, home_room, teacher_name, grade_level, team_name, total_students`
- **Grade_Rules**: `grade_level, min_daily_minutes, max_daily_minutes_credit`

### C. Event Tables (loaded by uploads during the event)

- **Daily_Logs**: `log_date, student_name, minutes_read` (one row per student per day; stores the raw, uncapped minutes)
- **Reader_Cumulative**: `student_name, teacher_name, team_name, donation_amount, sponsors, cumulative_minutes, upload_timestamp`. Totals from the fundraising site; each upload replaces the previous one.
- **Team_Color_Bonus**: `event_date, class_name, students_wearing_colors, bonus_minutes, bonus_participation_points`
- **Upload_History**: audit trail of every upload (file, date, rows, action taken, records replaced, warnings/errors, `file_type`)

### D. Generated Output

- **Q7 Complete Log**: denormalized join of Daily_Logs with Roster/Class_Info, for export.
- **Export All**: a ZIP containing every table as CSV plus a README with summary statistics.

## III. Key Definitions & Business Logic

- **Contest period:** defined by the dates actually uploaded to Daily_Logs. The first and last uploaded dates set the range shown on every page ("Oct 12-Oct 16, 2026"). Nothing is hard-coded per year.
- **Daily cap:** at most **120 minutes per student per day** count toward any total (`MIN(minutes_read, 120)`). Uncapped minutes are kept for reconciliation (Q21–Q23).
- **Participation:** a student participated on a day if `minutes_read > 0`.
- **Goal met:** the student read at least their grade's `min_daily_minutes` that day.
- **Avg. Participation (With Color):** average daily participation rate plus team-color bonus points. It **can exceed 100%**.
- **Team Color Bonus:** on a spirit day, each student wearing team colors adds **+10 minutes** and **+1 participation point** to their class.
- **Ties:** when entities tie for first place, **all tied entities are winners**.
- **Team colors:** assigned by alphabetical team name. The first team is blue (`#1e3a5f`), the second is amber (`#f59e0b`).
- **Winner highlights:** gold = school-wide best; silver = best within the current grade/team filter.
- **Synonyms (case-insensitive):** Kindergarten = K = 0; class = home room; Reader Name = student_name.

## IV. Core Functionality

### A. Dashboard Pages

| Page | Contents |
|---|---|
| School | 6-metric banner, team head-to-head, top performers |
| Teams | Team-by-team leaders and a comparison table |
| Classes (Grade Level) | Grade cards, sortable class table, grade/team filters |
| Students | All students with filters and highlighting; click a row for the daily detail |
| Upload | Daily minutes, cumulative fundraising and team color bonus uploads, with history |
| Reports & Data | Reports Q1–Q24, raw tables, workflows, Admin |
| Database Comparison | Year-over-year comparison of two registered databases (both need reading data) |

- **Banner:** every dashboard page shows the same 6 metrics in the same order: Campaign Day, Fundraising, Minutes Read, Sponsors, Avg. Participation (With Color), Goal Met (≥1 Day).
- **Date filter:** "through date X". It applies to minutes, participation and goals. Fundraising and sponsors are always cumulative.
- **Filter persistence:** date, grade and team filters carry across pages.

### B. Reports

Reports are numbered, grouped, and include column descriptions, data sources, a glossary and (for the integrity reports) an automated analysis.

| # | Name | Timeframe |
|---|---|---|
| Q1 | Table Row Counts | Utility |
| Q2 | Daily Summary (by class or team) | Daily |
| Q3 | Reader Cumulative Enhanced | Cumulative |
| Q4 / Slide 4 | Prize Drawing: one random goal-meeting student per grade | Daily |
| Q5 | Student Cumulative (Top Readers, Goal Getters, Top Fundraisers) | Cumulative |
| Q6 | Class Participation Winner | Cumulative |
| Q7 | Complete Log (flat export) | Any |
| Q8 | Student Reading Details | Cumulative |
| Q9 / Q10 / Q11 | Most Donations / Minutes / Sponsors per Grade | Cumulative |
| Q12 / Q13 | Best Class per Grade / in School | Cumulative |
| Q14 / Slide 3 | Team Participation | Cumulative |
| Q15 | Goal Getters (met goal every day) | Cumulative |
| Q16 | Top Earner per Team | Cumulative |
| Q18 / Slide 2 | Lead Class by Grade | Cumulative |
| Q19 / Slide 5 | Team Minutes | Cumulative |
| Q20 / Slide 6 | Team Donations | Cumulative |
| Q21 / Q22 / Q23 | Data integrity: minutes sync, name sync, roster check | Admin |
| Q24 | Database Registry | Admin |

**Workflows:** each workflow runs every report tagged for it.

| Workflow | Purpose |
|---|---|
| QD | Daily slide update |
| QC | Cumulative |
| QF | Final prize winners |
| QA | All main reports |

Reports and workflows are chosen from lists in the app. The v25 chat commands (such as "show me all reports" or typing "q5") are no longer used.

### C. Help

The in-app Help menu provides:
- a User Manual
- Application Requirements
- an Installation guide
- a page on how the app was built with Claude Code

## V. Data Ingestion

### A. Yearly Setup (before the event)

Create a new database from three CSVs (Section II.B). There are two ways:
- **In the app:** Admin → Database Registry → Create New Database
- **From the command line:** `python3 init_data.py <year>` (it reads `roster.csv`, `class_info.csv` and `grade_rules.csv` from the project folder)

The filename must be a plain name ending in `.db`. An existing database is never overwritten.

### B. Daily Workflow (during the event)

| Upload | Format | Behavior |
|---|---|---|
| Daily minutes | PledgeReg export: `ClassID, Teacher, ReaderID, ReaderName, Minutes`. The date comes from the filename (e.g. `daily_2026-10-12.csv`) or is chosen in the form. | Uploading a date again replaces that date's data. |
| Cumulative fundraising | PledgeReg export: `Reader Name, Teacher, Email, Raised, Sponsors, Sessions, PageCreated, Minutes` | Replaces the previous cumulative data. |
| Team color bonus (spirit day) | `timestamp, class_name, team_name, grade_level, students_count` | Team must match the class. |

Extra columns are ignored. Column matching is case-insensitive.

### C. Error Handling

- Unknown student names, duplicate rows and format problems are reported back after each upload and saved in Upload_History.
- Q21–Q23 reconcile the tables after uploads.
- Unknown filter values in page URLs are ignored (treated as "all").

## VI. Typical User Workflow

1. **Once per year:** create `readathon_<YEAR>.db` from the roster, class info and grade rules, then switch to it.
2. **Each event day:** upload the day's minutes. Upload cumulative fundraising as often as wanted. Run **QD** for the daily slides.
3. **Spirit day:** upload the team color bonus file.
4. **End of event:** run **QF** (prize winners) and **QC**. Use Export All to archive the year. Optionally compare with last year.
5. **Afterwards:** back up `db/readathon_<YEAR>.db` and `db/readathon_registry.db` outside git.

## VII. Versioning

- **Format:** `vYYYY.MINOR.PATCH`, where **YYYY is the read-a-thon event year**:
  - Oct 2026 event → `v2026.*`
  - Oct 2027 event → `v2027.1.0`
- **Historical exception:** tags `v2026.1.0`–`v2026.14.3` were created under the earlier school-year scheme and are the code used for the **2025** event. Tag `readathon-2025-final` marks the end of that code. Work for the 2026 event continues from `v2026.15.0`.

## VIII. 2026 Changes (v26)

- A fresh checkout starts on the sample database. The registry is created automatically, so no migration script is needed.
- New year databases get the full Upload_History schema. Before this, pages and uploads failed on a freshly created database.
- No 2025 dates or timestamps remain in page code. The contest range, roster load time and spirit-day date all come from the data.
- The "sample file uploaded into a real database" confirmation works again. Upload messages name the actual database.
- `init_data.py <year>` creates **and registers** `readathon_<year>.db`. `clear_all_data.py <file>` requires an explicit database.
- Year-over-year comparison explains when a database has no reading data yet, instead of erroring. "Through Day N" compares each year through its own Nth contest day.
- Year database files copied into `db/` are registered automatically; "Register Existing Database" writes to the real registry; `package_data.sh` packages the data for another computer.
