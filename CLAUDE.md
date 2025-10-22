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
   - School divided into "Kitsko" and "Staub" teams
   - Team assignments stored in Roster table

4. **Enhanced Metadata System** (Features 30 & 31)
   - Reports include column descriptions, term glossaries, automated analysis
   - Implemented for Q21, Q22, Q23; remaining reports (Q1-Q20) still need it
   - Metadata defined in `report_metadata.py`

### Application Flow
1. **Data Entry:** CSV uploads via `/upload` (from PledgeReg online system)
2. **Processing:** Flask routes in `app.py` → DB operations in `database.py`
3. **Reporting:** 11 pre-configured reports (Q1-Q23, non-sequential numbering)
4. **Integrity Checks:** Q21 (uncapped), Q22 (capped), Q23 (reconciliation)
5. **Workflows:** Run multiple reports in sequence

### File Structure
```
app.py                    # Flask routes, API endpoints
database.py               # SQLite operations, report generators
report_metadata.py        # Column metadata, terms, analysis for reports
init_data.py              # DB initialization with student roster
requirements.txt          # Flask==3.0.0
templates/                # Jinja2 HTML (base, index, upload, reports, admin, workflows)
docs/                     # Feature documentation (31 features + architecture)
  ├─ 00-INDEX.md          # Master index of all features
  ├─ QUICK_START_NEXT_SESSION.md  # Current work status
  └─ features/            # Individual feature specs
IMPLEMENTATION_PROMPT.md  # SOURCE OF TRUTH (130KB requirements doc)
```

## Critical Context

### Before Starting Work
1. **Read IMPLEMENTATION_PROMPT.md** - Complete requirements document
2. **Check docs/QUICK_START_NEXT_SESSION.md** - Current development status
3. **Consult docs/00-INDEX.md** - Searchable feature index

### Current Development Status
- **In Progress:** Enhanced Report Metadata (Features 30 & 31)
- **Completed:** Q21, Q22, Q23 have enhanced metadata with analysis
- **Pending:** Floating analysis button modal implementation (current blocker)
- **TODO:** Add metadata to Q1-Q20 reports

### Important Constraints
- **Local-only application:** No server deployment, runs on user's Mac
- **Offline-capable:** Works without internet (after Bootstrap CDN loads once)
- **CSV-based data entry:** All data imported from PledgeReg system
- **Multi-environment support:** `readathon_prod.db` (prod) vs `readathon_sample.db` (test)

### Report Numbering (Non-Sequential)
The system has 11 reports with non-sequential numbers:
- Q1, Q2, Q3, Q5, Q6, Q8, Q13, Q14, Q21, Q22, Q23
- Q21-Q23 are data integrity/reconciliation reports
- Each report has specific business logic (see IMPLEMENTATION_PROMPT.md)

## Development Workflow
- All development must be on feature branches (per global CLAUDE.md rules)
- Never commit directly to master
- Master changes only through approved merges after testing
