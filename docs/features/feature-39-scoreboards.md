# Feature 39: Scoreboards (Daily Scoreboard + Prize Scoreboard)

**[← Back to Index](../00-INDEX.md)**

---

**Status:** PROTOTYPE APPROVED — not yet built into the app
**Priority:** High (the daily scoreboard is the key daily deliverable during the contest)
**Type:** New pages
**Supersedes:** [Feature 21: Slides Tab](feature-21-slides-tab-new.md) (clipboard cards for Google Slides) — the format no longer has to be a slide deck.

---

## Prototypes

- `prototypes/scoreboards_prototype.html` — both pages as tabs (`#daily`, `#prize`)
- `prototypes/daily_report_prototype_v2_scoreboard.html` — Daily Scoreboard
- `prototypes/prize_scoreboard_prototype.html` — Prize Scoreboard (pick Day 10 in the prototype to see the final-results wording)

`prototypes/daily_report_prototype_tabs.html` is the older A/B/C option comparison; its Option B predates these changes.

## Why

The 2025 daily update was a PowerPoint deck rebuilt by hand every contest day, and the closing ceremony had a prize deck. Both are replaced by pages generated from the data, meant to be emailed as an image.

## Placement and naming

- New top-level nav menu **🏆 Scoreboards** with **Daily Scoreboard** and **Prize Scoreboard**.
- Not under Reports & Data: these are fixed-format deliverables, not sortable/exportable tables. They still get their numbers from the existing `ReportGenerator` methods.
- The word "update" is avoided because it's confused with the daily data upload.

## Shared design rules

- Output is **consumable as a static image**: the report area has no pickers or buttons. Controls live in a toolbar above it — **As of Day** picker (defaults to latest day with data), **Copy as image**, **Download PNG**. The image is captured from the report area only (prototype uses `html-to-image`; CDN stylesheets need `crossorigin="anonymous"` so fonts/icons embed, and the capture must zero the page margin).
- No yearly theme. Team names come from the data, first letter capitalized. Team colors follow the alphabetical rule (first = navy, second = gold).
- VS cards: extra inner padding on both panels so the VS badge never crowds labels.
- 2026 vs 2025 Showdown uses school colors: this year navy, last year muted slate gray; gold is reserved for trophies and the gold team.
- School name ("Lincoln Elementary") is not stored anywhere yet — add a one-line setting (Admin) when building.

## Daily Scoreboard

- Masthead: school name, "2026 Daily Scoreboard", "% of students read at least 1 day" medallion, Day N of TOTAL + date.
- Students: daily prize drawing winner per grade.
- Classes: highest participation % per grade (cumulative), school-wide top class tagged.
- Teams: participation, minutes, money (cumulative) with trophies on the leader, plus "today" figures (today's participation %, +minutes today, +$ today).
- 2026 vs 2025 Showdown: whole school, **Day N this year vs Day N last year**; participation uses the same definition as the team card (average daily participation including color bonus).

### Daily drawing: sticky, with redraw

- Winners are picked with a seed of (date, drawing #): reloading shows the same winners, nothing is saved.
- **Redraw** bumps the drawing # (kept in the URL); "Drawing #N" is printed in the section header so the image shows which draw it is. Covers the case where repeat winners are excluded outside the app.
- Later options: store the chosen drawing # per day, or exclude past winners automatically.

## Prize Scoreboard

Eight prizes (the daily drawing is excluded), runnable for any day ("Prize Leaders — as of Day N") or at the end ("Final Prize Winners"). Ties: every tied winner is listed.

1. **Teams** — Team Participation (trophy per team) and Top Student Earner (1 per team) in one VS card; prize tags under it.
2. **Classes** — Highest Class Participation (spotlight card, $100 for the teacher) and Grade Level Participation (table, grade party/activity).
3. **Students** — one table, grade rows × Top Minutes / Top Donations / Top Sponsors, prize in each column header, ties tagged "N-way tie".
4. **2026 vs 2025 Showdown** — same day mid-contest, final vs final at the end.
5. **Goal Getters** (last, longest) — every name, grade label in a left column, names in 6 columns reading down, long names wrap (never truncate).

## Data availability ("as of" a past day)

| Data | Past days? | Why |
|---|---|---|
| Minutes, participation, goal met, color bonus | Yes | `Daily_Logs` and `Team_Color_Bonus` are stored by date |
| Donations, sponsors (money raised, Top Earner/Donations/Sponsors, "+$ today") | **No, until snapshots exist** | `Reader_Cumulative` is replaced by each cumulative upload |
| 2025 money raised | Final total only | 2025 has no snapshots |

**Planned fix:** a history table that keeps a copy of every cumulative upload, tagged with the contest day it covers (a same-day re-upload replaces that day's copy). `Reader_Cumulative` stays the "latest" copy driving the rest of the app; past-day scoreboards read the history. Store raw rows, not pre-computed metrics, so any day can be recomputed with future report logic.

**Year-to-year tolerance:** each metric is either available for the requested day or not. Missing values show **"Not available\*"** with a footnote (e.g. "2025 only kept final fundraising totals, not day-by-day amounts. 2025 finished with $X raised.") and no trophy is awarded for that row. This covers older databases without special per-year code.

## Data sources (existing `ReportGenerator` methods in `database.py`)

| Section | Source | Notes |
|---|---|---|
| Daily prize winners | `q4_prize_drawing(log_date)` | Currently `random.choice()` per grade — change to the seeded (date, drawing #) pick |
| Classes by grade / Grade Level Participation | `q18_lead_class_by_grade`, `q12_best_class_by_grade_simplified` | Use the `avg_participation_rate_with_color` figure (matches the 2025 closing deck) |
| Highest Class Participation | `q13_overall_best_class_simplified` | Deck says ties go to a raffle (never implemented); new rule: all tied classes win |
| Team participation / minutes / money | `q14_team_participation`, `q19_team_minutes`, `q20_team_donations` | Minutes are capped at 120/day; color-bonus minutes included |
| Top Student Earner (per team) | `q16_top_earner_per_team` | |
| Top Minutes / Donations / Sponsors (per grade) | `q10_most_minutes_by_grade`, `q9_most_donations_by_grade`, `q11_most_sponsors_by_grade` | All tied students listed |
| Goal Getters | `q15_goal_getters` | Mid-contest meaning: met the grade goal every day so far |
| Medallion "% read at least 1 day" | `get_db_comparison_school_participation(date_filter)` in `queries.py` | Minutes > 0 on at least one day — **not** the stricter "goal met ≥1 day" |
| Prize text | the `note` field in each method's metadata (e.g. "Prize: Grandpa Joe's $25 Gift Card per grade level") | Team Participation's prize: losing team's captain does something silly; Goal Getters: a book |

Gaps to close:
- The cumulative methods above take **no date parameter** — add an "as of date" filter (Daily_Logs `log_date <= ?`; money/sponsors from the snapshot for that day). Several have inline SQL in `database.py`; per project convention new SQL goes in `queries.py`.
- Keep the existing Reports page results unchanged (as-of defaults to "all data").

### Definitions

- **Today (daily page):** today's participation % = students with minutes > 0 that day (plus that day's color-bonus points) ÷ roster size; +minutes today = capped minutes that day, including that day's bonus minutes; +$ today = snapshot(day N) − snapshot(day N−1), shown only when both snapshots exist.
- **Prize medallion "Students Winning a Prize":** distinct students winning any student prize (Top Earner, Top Minutes/Donations/Sponsors, Goal Getters).
- **Showdown prior year:** the registry database whose year = this year − 1; day N maps to that database's Nth contest date (same as the database comparison page, `get_database_comparison(..., 'dayN')`). If no prior-year database exists, hide the section.
- **URLs:** `?day=N` (default latest) and `?draw=N` (daily page, default 1).

### Upload history table (decisions)

- New table (e.g. `Reader_Cumulative_History`): same columns as `Reader_Cumulative` + `snapshot_date`, primary key (`snapshot_date`, `student_name`).
- Every cumulative upload also writes a snapshot. `snapshot_date` defaults to the latest `Daily_Logs` date at upload time, shown (and changeable) on the upload page. A re-upload for the same date replaces that date's snapshot.
- Backfill: when the table is first created in an existing database, copy the current `Reader_Cumulative` in as the snapshot for its last contest date (gives 2025 its final totals through the same code path). **Creating/backfilling this in a real year database is a write — ask the user first** (develop against the sample DB).
- Include the table in the places that list/clear tables: `/tables`, table counts (Q1), `clear_all_data.py`, selective clearing, and deleting cumulative data.

### Settings

- School name: new one-line setting in Admin (not in tracked files). Masthead shows "{school} Read-a-Thon" and "{year} Daily Scoreboard"; fall back to "Read-a-Thon" when unset.

## Build notes (next step)

- Follow the prototype → production rules in `CLAUDE.md` and `md/RULES.md`; read the whole prototypes first.
- Suggested order: upload history table → as-of-date filters on the source methods → Daily Scoreboard → Prize Scoreboard → school-name setting → nav menu.
- Tests modeled on `tests/test_school_page.py` (mandatory list in `md/RULES.md`), run against the sample DB; for the drawing, assert the winner belongs to the eligible pool and is stable for the same (date, drawing #). Include a test that a missing prior-year value renders "Not available".
- Docs: `md/RULES.md` (data rules above), `md/UI_PATTERNS.md` (scoreboard components), `templates/help.html`, `md/CHANGELOG.md` + `VERSION` minor bump; mark Feature 21 superseded.
