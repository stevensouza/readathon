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

## Build notes (next step)

- Follow the prototype → production rules in `CLAUDE.md` and `md/RULES.md`.
- Reuse the day-N mapping from the database comparison page (`get_database_comparison(..., 'dayN')`) for the Showdown.
- Tests modeled on `tests/test_school_page.py`; for the drawing, assert the winner belongs to the eligible pool and is stable for the same (date, drawing #).
