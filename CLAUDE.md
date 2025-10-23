# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **Flask web application** for managing an elementary school read-a-thon event. It's a browser-based GUI for tracking 411 students' reading minutes and fundraising, with all data stored locally in SQLite (no server deployment required).

## Development Commands

### Setup & Installation
```bash
pip3 install -r requirements.txt  # Only dependency: Flask==3.0.0
python3 init_data.py              # Initialize DB with 411 student roster + class data
```

### Running the Application
```bash
python3 app.py                    # Start server on http://127.0.0.1:5001
# OR
python3 start_server_5001.py      # Alternative start script
```

### Testing
```bash
python3 test_audit_trail.py       # Test audit trail functionality
```

### Database Operations
```bash
python3 clear_all_data.py         # Reset database tables (keeps schema)
```

## Architecture Overview

### Technology Stack
- **Backend:** Flask 3.0.0 (pure Python, no build tools)
- **Database:** SQLite 3 (local file: `readathon_prod.db`)
- **Frontend:** Bootstrap 5.3.0 + Bootstrap Icons (CDN-loaded)
- **No npm/webpack:** Static HTML templates with Jinja2

### Core Data Model
```
Roster (411 students)
  ├─> Daily_Logs (day-by-day reading minutes per student)
  └─> Reader_Cumulative (aggregated stats: total minutes, donations, sponsors)

Supporting Tables:
  - Class_Info (teacher assignments, grade levels)
  - Grade_Rules (grade-specific reading goals)
  - Upload_History (audit trail for CSV imports)
```

### Key Design Decisions

1. **120-Minute Daily Cap**
   - Students can read more than 120 min/day, but official totals cap at 120
   - Database stores both `capped_minutes` and `uncapped_minutes`
   - Reports use capped values for contest calculations

2. **Sanctioned Dates: Oct 10-15, 2025**
   - Only this 6-day window counts toward official contest
   - Out-of-range dates cause reconciliation differences (tracked in Q21-Q23)

3. **Two-Team Competition**
   - School divided into two teams (anonymized as "Phoenix" and "Dragons" in public files)
   - Team assignments stored in Roster table

4. **Enhanced Metadata System** (Features 30 & 31)
   - All reports include column descriptions, term glossaries, automated analysis
   - Implemented for all 22 reports (Q1-Q23)
   - Metadata defined in `report_metadata.py`
   - Analysis modal displays insights for data integrity reports

5. **SQL Query Organization**
   - All SQL queries extracted to `queries.py` module (Feature 29)
   - Cleaner separation between database operations and query definitions
   - Easier to maintain and review SQL logic

### Application Flow
1. **Data Entry:** CSV uploads via `/upload` (from PledgeReg online system)
2. **Processing:** Flask routes in `app.py` → DB operations in `database.py`
3. **Reporting:** 22 pre-configured reports (Q1-Q23, non-sequential numbering)
4. **Integrity Checks:** Q21 (uncapped), Q22 (capped), Q23 (reconciliation)
5. **Workflows:** Run multiple reports in sequence
6. **Analysis:** Enhanced metadata with automated insights modal

### File Structure
```
app.py                    # Flask routes, API endpoints
database.py               # SQLite operations, report generators
queries.py                # SQL queries extracted from database.py
report_metadata.py        # Column metadata, terms, analysis for reports
init_data.py              # DB initialization with student roster
requirements.txt          # Flask==3.0.0
VERSION                   # Current version number (vYYYY.MINOR.PATCH)
CHANGELOG.md              # Version history and release notes
CLAUDE.md                 # This file - project guidance for Claude Code
templates/                # Jinja2 HTML (base, index, upload, reports, admin, workflows)
prototypes/               # HTML prototypes (sanitized with fictitious data)
docs/                     # Feature documentation (31 features + architecture)
  ├─ 00-INDEX.md          # Master index of all features
  ├─ QUICK_START_NEXT_SESSION.md  # Current work status
  └─ features/            # Individual feature specs
  └─ screenshots/         # Screenshots (sanitized for privacy)
IMPLEMENTATION_PROMPT.md  # SOURCE OF TRUTH (130KB requirements doc)
```

## Critical Context

### Before Starting Work
1. **Read IMPLEMENTATION_PROMPT.md** - Complete requirements document
2. **Check docs/QUICK_START_NEXT_SESSION.md** - Current development status
3. **Consult docs/00-INDEX.md** - Searchable feature index

### Current Version
**v2026.1.0** - First stable release for 2025-2026 school year

See `VERSION` file for current version and `CHANGELOG.md` for release history.

### Recent Completions
- ✅ Enhanced metadata implemented for all 22 reports (Q1-Q23)
- ✅ Analysis modal working with automated insights
- ✅ SQL queries extracted to queries.py module
- ✅ Git history cleaned of sensitive school data
- ✅ Sample data and screenshots sanitized for privacy
- ✅ Versioning scheme established (School Year CalVer)

### Important Constraints
- **Local-only application:** No server deployment, runs on user's Mac
- **Offline-capable:** Works without internet (after Bootstrap CDN loads once)
- **CSV-based data entry:** All data imported from PledgeReg system
- **Multi-environment support:** `readathon_prod.db` (prod) vs `readathon_sample.db` (test)

### Report Numbering (Non-Sequential)
The system has 22 reports with non-sequential numbers:
- Q1, Q2, Q3, Q5, Q6, Q8, Q13, Q14, Q21, Q22, Q23, and others
- Q21-Q23 are data integrity/reconciliation reports
- Each report has specific business logic (see IMPLEMENTATION_PROMPT.md)
- All reports include enhanced metadata (column descriptions, terms, automated analysis)

## Development Workflow
- Continue development on main branch (user preference)
- Can use feature branches for larger experimental work
- Tag releases when ready with appropriate version number

## Versioning Scheme

**School Year Calendar Versioning**: `vYYYY.MINOR.PATCH`

### Format
- **YYYY**: School year (e.g., 2026 = 2025-2026 school year ending in Spring 2026)
- **MINOR**: Feature additions and improvements (1, 2, 3, ...)
- **PATCH**: Bug fixes and small updates (0, 1, 2, ...)

### When to Increment
- **Year (2026 → 2027)**: New school year or major redesign
- **Minor (1 → 2)**: New features, reports, UI changes, significant improvements
- **Patch (0 → 1)**: Bug fixes, documentation updates, minor tweaks

### Examples
```
v2026.1.0 → v2026.1.1  (bug fix or small update)
v2026.1.0 → v2026.2.0  (new feature added)
v2026.1.0 → v2027.1.0  (next school year)
```

### Version Management
1. **Current version** stored in `VERSION` file
2. **Release history** tracked in `CHANGELOG.md`
3. **Git tags** created for each release (annotated tags with release notes)
4. **Automatic incrementing**: Claude Code will read VERSION, increment appropriately, and update all files

### Creating a New Release
When ready to tag a new release, tell Claude Code:
- "Increment patch version and tag" → v2026.1.0 → v2026.1.1
- "Increment minor version and tag" → v2026.1.0 → v2026.2.0
- "Create new school year version" → v2026.1.0 → v2027.1.0

Claude will:
1. Update VERSION file
2. Update CHANGELOG.md with changes
3. Create git tag with release notes
4. Push tag to GitHub
