# Feature 41: Meet the Teams (and the 📰 Bulletins menu)

**[← Back to Index](../00-INDEX.md)**

---

**Status:** ✅ BUILT in v2026.17.0 — `/scoreboards/teams` (menu 📰 Bulletins → Meet the Teams)
**Priority:** Medium
**Type:** New page + menu rename

---

## Why

Before each contest the teams are announced to families. The first version was a one-off image made from the 2026
roster. It is now generated from the roster every year, in the same branded style as the scoreboards, so it can be
copied into an email or printed.

## Menu rename: Scoreboards → Bulletins

A roster announcement is not a scoreboard, so the menu that holds the image-style pages is now **📰 Bulletins**
(Meet the Teams, Daily Scoreboard, Prize Scoreboard). Help and docs call them "branded bulletins" (school masthead, team
colors, copy as image). **Labels only:** the `/scoreboards/...` URLs, `scoreboards.py`, the `_scoreboard_*` templates
and the tests keep their names so bookmarks keep working. Admin's settings card is now **Bulletin Settings**.

## What the page shows

- **Masthead:** "{school} Read-a-Thon", gold "Meet the {year} Teams", "{N} classes · Grades K–5"; medallion = total
  students ("Readers Ready to Read"); right side "2 Teams" and the date.
- **Tagline:** "Every minute counts for your team. Grab a book and read!"
- **VS panels** (navy vs gold, alphabetical): each team's students (big), classes, and grade range.
- **Team Rosters:** one table per team under a team-colored band - Grade | Teacher | Readers, sorted by grade, with a
  total row. Half-day kindergarten classes are separate rows ("Teacher AM" / "Teacher PM").
- **Footer:** "Read-a-Thon {year} · Go Team Phoenix! Go Team Dragons!" and the generated date.

A "head to head by grade" section was tried in the prototype image and dropped.

## Rules

- **Roster only:** counts are `COUNT(*)` from `Roster` per class (`SELECT_TEAM_CLASS_COUNTS` in `queries.py`), so the
  page works as soon as the year's database is created, before any reading data. Empty roster → "No roster yet".
- Not exactly two teams → the masthead still shows, and the matchup/rosters are replaced by a note.
- No day picker. Copy as image / Download PNG capture at `pixel_ratio=3` (the scoreboards use 2) so names stay sharp
  when printed or zoomed; the file is `meet_the_teams_{year}.png`.

## As built

- `scoreboards.build_meet_the_teams()` and `grade_range()`; route `meet_the_teams()` in `app.py` (shares
  `bulletin_context()` with the scoreboards); template `templates/meet_the_teams.html`.
- Macros gained options used by this page: `toolbar(..., can_copy=)`, `no_data(..., subtitle, message)`,
  `capture_script(filename, pixel_ratio=2)`.
- Tests: `TestMeetTheTeamsPage` and the Meet the Teams cases in `TestEmptyDatabase` (`tests/test_scoreboards_page.py`),
  plus the nav/simple-view/stale-session lists.
