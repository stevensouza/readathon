# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Flask web app for running an elementary-school read-a-thon: tracks ~411 students' reading minutes and fundraising, all stored locally in SQLite. Local-only (runs on the user's Mac, port 5001), CSV-driven (uploads from the PledgeReg system), Jinja2 + Bootstrap 5 via CDN, no build step.

Version: see `VERSION` (`vYYYY.MINOR.PATCH`, YYYY = **event** year). v2026.1.0–v2026.14.3 were the code for the *2025* event (tag `readathon-2025-final`); 2026-event work continues from v2026.15.0. Release history: `md/CHANGELOG.md`.

## Commands

```bash
./install.sh                       # create venv/ (gitignored) + install requirements.txt (Homebrew Python blocks system pip - PEP 668)
./run.sh [--db sample]             # start app (uses venv/, opens browser). Same options as `python3 app.py`
python3 init_data.py 2026          # create + register db/readathon_2026.db from roster.csv, class_info.csv, grade_rules.csv
                                   # (or in-app: Admin -> Database Registry -> Create New Database)
python3 clear_all_data.py          # reset tables (keeps schema)
./package_data.sh                  # zip db/ to move data between computers (stop the app first; code moves via git)

venv/bin/pytest                    # all tests (system python3 lacks the deps and fails at collection)
venv/bin/pytest tests/test_school_page.py -k test_page_loads_successfully   # single test
```

`--db` accepts display name, filename, or alias (`sample`), case-insensitive. Startup DB priority: CLI arg > `.readathon_config` (gitignored, written when you switch DB in the UI) > registry's active DB.

### Testing gotchas (verified)

- **Stop Flask first** (`lsof -ti:5001 | xargs kill`) — a running app causes SQLite locking failures.
- **Tests are meant to use the sample DB, but currently don't enforce it.** The `client` fixtures set `session['environment']='sample'`, a legacy no-op: `app.py` picks the DB at import time from `.readathon_config` / the registry's active DB. If that is a real year DB (e.g. `readathon_2025.db`), ~76 page/regression tests fail on sample-specific assertions (team names "Phoenix"/"Dragons", etc.). Until the fixtures are fixed, make the sample DB active before running the suite: `echo '{"active_database_id": 1, "active_database_filename": "readathon_sample.db"}' > .readathon_config` (sample is `db_id` 1 in the registry). Clean run: ~492 passed, 5 skipped (~2s).
- Tests that use `db/readathon_2025.db` skip when it's absent.
- `pre-commit.sh` (install manually: `cp pre-commit.sh .git/hooks/pre-commit`) runs only the school, grade-level and teams page tests — not the full suite. Run `venv/bin/pytest` before committing.
- New pages need the standard mandatory tests listed in `md/RULES.md` (page loads, no error text, % / currency formats, DB-verified values, team badges, winner highlights, 6-metric headline banner). Use `tests/test_school_page.py` as the template.

## Architecture

Three big modules, tightly coupled — a change to one report usually touches all three:

- **`app.py`** (~4000 lines): all routes, and *startup side effects at import time* (argparse of `--db`, `DatabaseRegistry()` init, auto-registering `db/readathon_<YEAR>.db` files, picking `DEFAULT_DATABASE_ID`). Per-request DB is `get_current_db()` (session `active_database_id`, else default), with loaded `ReadathonDB` objects cached in `database_cache`. Dashboard tabs (`/school`, `/teams`, `/grade-level`, `/students`, `/students/<name>`) compute their data inline in the route; `/reports`, `/workflows`, `/tables`, `/admin`, `/upload`, `/database-comparison` are the other pages.
- **`database.py`**: `DatabaseRegistry` (catalog DB at `db/readathon_registry.db`: display name, year, filename, active flag, summary stats), `ReadathonDB` (one connection per contest DB file; creates schema, CSV ingestion), and `ReportGenerator` (one `qN_*` method per report, returns `{title, columns, data, metadata, ...}`).
- **`queries.py`**: every SQL string (CREATE TABLEs, report queries, `get_db_comparison_*` helpers). No SQL in `database.py`/`app.py` if avoidable.
- **`report_metadata.py`**: `COLUMN_METADATA[qN]`, `GLOBAL_TERMS` glossary, `REPORT_TERM_SETS`, and `generate_q21/22/23_analysis` for the analysis modal.

### Adding or changing a report (Q-numbers are non-sequential; Q1–Q24 minus gaps)

Reports are wired in several places that must stay in sync: SQL in `queries.py` → `ReportGenerator.qN_*` in `database.py` (uses `COLUMN_METADATA['qN']`) → the `if/elif report_id` chains in **both** `run_report` and `export_report` in `app.py` → the entry (with `groups` tags such as `workflow.qa`, `requires.date`) in `get_unified_items()` in `app.py` → metadata in `report_metadata.py`. Workflows (QA/QC/QD/QF) are *dynamic*: they run every report tagged `workflow.<id>` in `get_unified_items()`.

### Data model (per contest DB, `db/readathon_<YEAR>.db`)

`Roster` (student_name PK, class, teacher, grade, team) → `Daily_Logs` (minutes per student per date) and `Reader_Cumulative` (total minutes, donations, sponsors); supporting: `Class_Info`, `Grade_Rules`, `Upload_History` (audit trail), `Team_Color_Bonus`. One DB per event year; only the registry knows which is active. Real DBs, registry, rosters and real CSVs are gitignored (PII); only `db/readathon_sample.db` (fictitious) is tracked. `readathon.db`, `readathon_sample.db` in the repo root and `init_sample*.py` are legacy leftovers.

### Domain rules that are easy to get wrong

Full list in **`md/RULES.md`** (mandatory reading before implementing any feature) and palette/components in **`md/UI_PATTERNS.md`**. Highlights:

- Contest minutes are **capped at 120/day** (`capped_minutes` vs `uncapped_minutes` are both stored); reports/banners use capped, and team-color bonus minutes are always included.
- **Contest dates come from the data** (first..last date in `Daily_Logs`); never hard-code a year's dates.
- Team colors are assigned by **alphabetical order of team name** (first = blue `#1e3a5f`, second = yellow `#f59e0b`), never by DB order/ID.
- Public files anonymize teams as "Phoenix" and "Dragons"; keep real names/PII out of tracked files, tests and docs.
- `md/IMPLEMENTATION_PROMPT.md` is the source-of-truth requirements doc (very large — grep it, don't read it whole).

## Workflow Rules

- **Prototype → production:** for anything derived from `prototypes/*.html`, read `md/RULES.md` + `md/UI_PATTERNS.md` and the whole prototype first, inventory its elements, and compare against `school.html` / `teams.html` / `grade_level.html`. Load the real URL against a running app and check numbers with SQL before saying it works. When you mention a prototype give both `open prototypes/<name>.html` and the absolute `file://` URL for this checkout.
- **Document decisions immediately** (data-source/calculation rules → `md/RULES.md`; UI/styling → `md/UI_PATTERNS.md`; feature design → `docs/`). Session-state files `docs/SESSION_MEMORY.md` and `docs/QUICK_START_NEXT_SESSION.md` are maintained by the project skills in `.claude/skills/` (pre-commit check, database safety, document reflex, workflow detector, context saver) — they trigger automatically.
- **Database safety:** develop and test against the sample DB; ask before any write/DELETE/`clear_all_data.py` against a real year DB.
- **Commits:** work on `main` (user preference); never commit or push without asking. Summarize `git status`/`git diff`, propose a message in the style of `md/CHANGELOG.md`, and wait for approval. Bump `VERSION` and `md/CHANGELOG.md` for releases (patch = fix/docs, minor = feature; annotated tag + push tag). Commit trailer: `Co-Authored-By: Claude <noreply@anthropic.com>`.
- Update README/help templates (`templates/help.html`, `installation.html`) when user-facing behavior changes.
