# Changelog

All notable changes to the Read-a-Thon Management System will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project uses **School Year Calendar Versioning** (vYYYY.MINOR.PATCH).

## [v2026.1.3] - 2025-10-22

### Critical Bug Fixes

**Bug 1: Team Fundraising Amounts Doubled**
- **Problem:** Team fundraising totals were showing 2x the correct amount
  - Sample DB: Showing $110/$440 instead of $60/$220
  - Root cause: `Daily_Logs` join caused row multiplication in SUM aggregation
- **Fix:** Separated fundraising query from minutes query to avoid join conflicts
- **Impact:** All team fundraising amounts now calculate correctly

**Bug 2: Database Preference Not Persisting from CLI**
- **Problem:** Config file only saved when using UI dropdown, not CLI flags
- **Fix:** Added `write_config()` call at startup to persist any database selection
- **Impact:** Database preference now remembered from all sources:
  - ✅ CLI flags (`--db sample` or `--db prod`)
  - ✅ Launcher scripts (`run_sample.sh`, `run_prod.sh`)
  - ✅ Default startup (`python3 app.py`)
  - ✅ UI dropdown (already worked)

**Technical:**
- Refactored team fundraising to use dedicated query without Daily_Logs join
- Moved config persistence to startup (app.py:51) for universal coverage
- Verified fix with both sample and production databases

---

## [v2026.1.2] - 2025-10-22

### Dynamic Team Names (Generic Team Support)

**Problem Resolved:**
- Team names "STAUB" and "KITSKO" were hardcoded throughout the application
- Sample database couldn't display its generic team names ("team1", "team2")
- Made the app specific to one school instead of being reusable

**Changes:**
- **Dynamic Team Name Loading**: App now queries actual team names from database at runtime
- **Template Updates**: School tab displays team names from database instead of hardcoded values
- **Backend Refactoring**: All team queries and comparisons use dynamic team names
- **Universal Compatibility**: Works with any team names in the database

**Impact:**
- Sample database now correctly shows "TEAM1" and "TEAM2"
- Production database still shows "STAUB" and "KITSKO"
- Application is now truly generic and reusable for any school

**Technical:**
- Query team names from Roster table on each page load (~0.1ms performance impact)
- Updated 6 SQL queries in `/school` endpoint to use dynamic names
- Updated team competition template to use `teams[team_name].display_name`
- Maintains backward compatibility with existing databases

**Files Modified:**
- `app.py`: Added dynamic team name query and refactored all team logic
- `templates/school.html`: Updated team competition display to use dynamic names

---

## [v2026.1.1] - 2025-10-22

### Database Selection with Persistent Preference

**New Features:**
- **Persistent Database Preference**: App remembers your last database choice (sample/prod)
- **Command-Line Selection**: Launch with `python3 app.py --db sample` or `--db prod`
- **Launcher Scripts**: `run_sample.sh` and `run_prod.sh` for explicit database selection
- **Safer Default**: Now defaults to sample database (was production)
- **Priority System**: CLI argument > Config file > Default (sample)

**Improvements:**
- Sample database now includes Team_Color_Bonus sample data (5pts team1, 10pts team2)
- UI database switcher now saves preference to `.readathon_config`
- Startup message shows which database is active and why
- Verified production and sample databases have identical schemas

**Technical:**
- Added argparse for command-line argument parsing
- Config file: `.readathon_config` (gitignored, JSON format)
- Updated all routes to use configurable default database

**Benefits:**
- Safer for development (sample by default)
- Convenient for production use (remembers your choice)
- Explicit control when needed (CLI flags override config)

---

## [v2026.1.0] - 2025-10-22

### First Stable Release for 2025-2026 School Year

This is the baseline release with core functionality complete for managing the 2025-2026 school year read-a-thon event.

### Features
- Complete read-a-thon tracking system for 411 students
- 22 comprehensive reports (Q1-Q23) covering all metrics
- Enhanced metadata for all reports (column descriptions, data sources, key terms, automated analysis)
- Team competition tracking (2 teams with color bonus support)
- Daily and cumulative metrics tracking
- Prize drawing support with random selection
- Multi-file CSV upload with automatic date extraction
- Upload audit trail for data integrity
- Workflow automation for running multiple reports in sequence
- Data integrity reconciliation reports (Q21, Q22, Q23)
- Modern responsive UI with Bootstrap 5
- Local SQLite database (no server required)

### Technical
- Flask 3.0.0 web framework
- SQLite 3 database with 7 core tables
- Bootstrap 5.3.0 frontend
- SQL queries extracted to `queries.py` module
- Analysis modal for enhanced report insights
- Privacy-focused: Sanitized sample data and screenshots

### Privacy & Security
- Git history cleaned of sensitive school data
- Team names anonymized in public files (Phoenix/Dragons)
- Sample database with fictitious data included
- Real student data excluded from version control

---

## Versioning Scheme

This project uses **School Year Calendar Versioning**: `vYYYY.MINOR.PATCH`

- **YYYY**: School year (e.g., 2026 = 2025-2026 school year)
- **MINOR**: Feature additions and improvements (increments for each significant update)
- **PATCH**: Bug fixes and small updates (increments for each release)

### Examples
- `v2026.1.0` → `v2026.1.1`: Bug fix
- `v2026.1.0` → `v2026.2.0`: New feature or major update
- `v2026.1.0` → `v2027.1.0`: Next school year version

### When to Increment
- **Year**: New school year or major redesign
- **Minor**: When adding features, reports, or significant improvements
- **Patch**: For bug fixes, documentation updates, or minor tweaks
