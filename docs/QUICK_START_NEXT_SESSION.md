# Quick Start Guide - Next Session

**Last Updated:** 2025-11-10
**Status:** ✅ Development Complete - Maintenance Mode
**Current Version:** v2026.14.2

---

## 📋 RESTART PROMPT (Copy/Paste This)

```
Continue work on Read-a-Thon application.

**Current Status:**
- ✅ All planned features implemented for 2026 school year
- ✅ 460 tests passing (includes comprehensive content regression tests)
- ✅ Pre-commit hook active with all content tests
- ✅ All 9 dashboard tabs fully functional: School, Teams, Grade Level, Students, Upload, Reports, Workflows, Admin, Help
- ✅ Filter persistence working across all pages (date, grade, team)
- ✅ Gold/silver highlighting working correctly across all pages
- ✅ Database registry system operational
- ✅ Export functionality working

**Development Status:**
- 🟢 Maintenance mode: No active development planned
- 🟢 Application ready for 2026 read-a-thon event
- 🟢 Bug fixes only (increment patch version for fixes)

**If bugs are discovered:**
1. Report issue and reproduction steps
2. Create/update tests to reproduce bug
3. Fix bug
4. Verify all 460 tests pass
5. Increment patch version (v2026.14.3)

Refer to:
- Universal rules: md/RULES.md
- UI patterns: md/UI_PATTERNS.md
- Regression tests: docs/REGRESSION_TEST_IMPROVEMENTS.md
- Session state: docs/QUICK_START_NEXT_SESSION.md (this file)
```

---

## ✅ RECENT COMPLETIONS (v2026.14.0 - v2026.14.2)

### v2026.14.2 (2025-11-10) - Pre-commit Hook Enhancement
**Changes:**
- Added content regression tests to pre-commit hook
- All 460 tests now run on every commit
- Documented regression test improvements

**Commits:**
- `889aaf3` - Bump version to v2026.14.2
- `0baca7e` - Document content regression tests added to pre-commit hook

### v2026.14.1 (2025-11-10) - Bug Fix
**Changes:**
- Fixed color bonus calculation in TOP CLASS Reading cards
- Color bonus now properly included in top class calculations

**Commits:**
- `f8fcd89` - Fix: Include color bonus in TOP CLASS Reading calculations

### v2026.14.0 (2025-11-10) - Final Release for 2025-2026 School Year
**Changes:**
- Completed all content regression tests (Phases 1-3)
- Added 54 comprehensive content tests across 3 major pages
- Documentation improvements (help pages, workflows, interface)
- Test refactoring (removed sys.exit() patterns)

**Commits:**
- `0c2c70a` - Bump version to v2026.14.0
- `8f5c64a` - Add School page content regression tests (Phase 3)
- `1d27ec4` - Add Grade Level content regression tests (Phase 2)
- `d6e8897` - Add content regression tests for Teams page

---

## 📊 PROJECT STATUS OVERVIEW

### Test Coverage
- **Total tests:** 460 passing
- **Content regression tests:** 54 tests (Teams, Grade Level, School pages)
- **Structural tests:** 406 tests (page loads, UI elements, calculations)
- **Pre-commit hook:** All 460 tests run automatically

### Documentation Status
- ✅ RULES.md - Universal rules across all pages
- ✅ UI_PATTERNS.md - Established UI component patterns
- ✅ REGRESSION_TEST_IMPROVEMENTS.md - Content regression test documentation
- ✅ All help pages complete with sticky TOCs
- ✅ All feature documentation in docs/features/

### Application Features
- **9 Dashboard Tabs:** School, Teams, Grade Level, Students, Upload, Reports, Workflows, Admin, Help
- **22 Pre-configured Reports:** Q1-Q23 (non-sequential numbering)
- **Workflow Automation:** Run multiple reports in sequence
- **Database Registry:** Multi-database support with UI switcher
- **Enhanced Metadata:** Column descriptions, terms, automated analysis for all reports
- **Export Capabilities:** Copy to clipboard or download as CSV
- **Upload Audit Trail:** Track every file upload with detailed history
- **Filter Persistence:** Grade, team, and date filters persist across pages

---

## 🎯 NO ACTIVE DEVELOPMENT PLANNED

**Application Status:**
- ✅ All features complete for 2026 school year
- ✅ Comprehensive test coverage (460 tests)
- ✅ Pre-commit hooks prevent regressions
- ✅ Documentation complete
- ✅ Ready for production use

**Maintenance Mode:**
- Bug fixes only (if discovered)
- Patch version increments (v2026.14.x)
- No new features planned until next school year (v2027.x.x)

---

## 📁 KEY FILE LOCATIONS

### Core Application
- `app.py` - Flask routes and API endpoints
- `database.py` - Database operations and report generators
- `queries.py` - SQL queries extracted for maintainability
- `report_metadata.py` - Column metadata and analysis

### Templates (Jinja2 + Bootstrap 5)
- `templates/base.html` - Base template with navigation
- `templates/school.html` - School dashboard tab
- `templates/teams.html` - Teams tab (4-column layout)
- `templates/grade_level.html` - Grade Level tab
- `templates/students.html` - Students tab with detail modal
- `templates/upload.html` - CSV upload interface
- `templates/reports.html` - Report selection and display
- `templates/workflows.html` - Workflow automation
- `templates/admin.html` - Admin controls and database registry

### Documentation (Critical Reading)
- `CLAUDE.md` - Project guidance for Claude Code
- `md/RULES.md` - **MUST READ** - Universal rules across all pages
- `md/UI_PATTERNS.md` - **MUST READ** - UI component patterns
- `docs/REGRESSION_TEST_IMPROVEMENTS.md` - Content regression test documentation
- `docs/QUICK_START_NEXT_SESSION.md` - This file

### Tests (460 tests total)
- `tests/test_teams_content_regression.py` - 12 content tests
- `tests/test_grade_level_content_regression.py` - 21 content tests
- `tests/test_school_content_regression.py` - 21 content tests
- `tests/test_students_page.py` - 50+ tests for Students page
- Plus 15+ other test files for all features

---

## 🚨 CRITICAL PATTERNS TO REMEMBER

### Filter Persistence (SessionStorage)
```javascript
// Save filters when user changes them
sessionStorage.setItem('readathonDateFilter', date);
sessionStorage.setItem('readathonGradeFilter', grade);
sessionStorage.setItem('readathonTeamFilter', team);

// Restore on page load (read ALL at once!)
const savedDate = sessionStorage.getItem('readathonDateFilter');
const savedGrade = sessionStorage.getItem('readathonGradeFilter');
const savedTeam = sessionStorage.getItem('readathonTeamFilter');
```

### Winner Highlighting Logic
```python
# Backend calculates:
school_winners = db.get_students_school_winners(date_filter)  # Gold
filtered_winners = db.get_students_filtered_winners(...)  # Silver
grade_winners = db.get_students_grade_winners(date_filter)  # Silver for all-grades

# Frontend applies (gold takes precedence):
if value == school_winners.get('metric'):
    GOLD (school-wide winner)
elif value == filtered_winners.get('metric') or value == grade_winners.get(grade, {}).get('metric'):
    SILVER (filtered or grade-level winner)
else:
    PLAIN
```

### Half-Circle Indicators
```jinja2
{# Only show when single day selected, not full contest #}
{% if date_filter != 'all' %}
    <span class="filter-indicator" data-bs-toggle="tooltip" title="Cumulative through {{ date_filter }}">◐</span>
{% endif %}
```

### Team Colors (Alphabetical Order)
```python
# Team 1 (alphabetically first) = blue (#1e3a5f)
# Team 2 (alphabetically second) = yellow (#f59e0b)
team_index_map = {}
for idx, team_name in enumerate(sorted(team_names)):
    team_index_map[team_name] = idx
```

---

## 📊 DATABASE ARCHITECTURE

### Databases
- `db/readathon_registry.db` - Registry database (tracks all contest databases)
- `db/readathon_2025.db` - 2025 contest database (production, 411 students)
- `db/readathon_sample.db` - Sample database (fictitious data, 7 students for testing)

### Key Tables (Contest Databases)
- `Roster` - Student roster (411 students in prod, 7 in sample)
- `Daily_Logs` - Day-by-day reading minutes (capped and uncapped)
- `Reader_Cumulative` - Aggregated stats (fundraising, sponsors)
- `Class_Info` - Teacher assignments, grade levels
- `Grade_Rules` - Grade-specific reading goals
- `Team_Color_Bonus` - Bonus minutes for team spirit events
- `Upload_History` - Audit trail for CSV imports

### Important Business Rules (see md/RULES.md)
- Reading minutes **capped at 120 per day** for contest calculations
- Database stores both `capped_minutes` and `uncapped_minutes`
- Sanctioned dates: **Oct 10-15, 2025** (6-day window)
- Two-team competition: **Team colors assigned alphabetically** (team1=blue, team2=yellow)
- **Fundraising is NEVER capped** (always from Reader_Cumulative)
- Participation can **exceed 100%** with color bonus

---

## 🧪 TESTING (Before Any Commits)

**Stop Flask before running tests:**
```bash
lsof -ti:5001 | xargs kill
```

**Run full test suite:**
```bash
pytest                          # All 460 tests
pytest --tb=short -q            # Concise output
pytest tests/test_specific.py   # Specific test file
```

**Manual browser testing:**
```bash
python3 app.py --db sample
open http://127.0.0.1:5001
```

**Pre-commit hook:**
- Automatically runs all 460 tests on every commit
- Includes content regression tests (catches display/calculation bugs)
- Must pass before commit succeeds

---

## 💡 MAINTENANCE MODE REMINDERS

1. **No new features:** Development complete for 2026 school year
2. **Bug fixes only:** If bugs discovered, create test → fix → verify → commit
3. **Always read RULES.md and UI_PATTERNS.md** before any changes
4. **Test thoroughly:** All 460 tests must pass before committing
5. **Version increments:** Patch only (v2026.14.x) for bug fixes
