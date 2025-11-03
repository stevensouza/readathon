# Changelog

All notable changes to the Read-a-Thon Management System will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project uses **School Year Calendar Versioning** (vYYYY.MINOR.PATCH).

## [v2026.5.0] - 2025-11-03

### Students Page - Final Fixes and Completion

**Major Feature: Students Page Complete**
- All 17 critical bugs fixed from initial production deployment
- 50 automated tests passing (100% pass rate)
- 235 total tests across entire application
- 2 comprehensive regression tests added to lock in expected behavior
- Production-ready with full filter persistence and gold/silver highlighting

**Critical Bug Fixes:**

1. **Half-circle indicators (◐)** - Conditional rendering based on date filter
   - Now only appear when single day selected, NOT full contest
   - Added to 3 banner metrics and 6 table headers
   - Implemented Bootstrap tooltips with cumulative date context
   - Fixed template logic in `templates/students.html` lines 560-698

2. **Banner title correction** - Removed "(With Color)" from Avg. Participation
   - Color war bonuses don't apply at individual student level
   - Matches actual calculation (no color bonus in student-level participation)
   - Fixed in `templates/students.html` line 576

3. **Participation calculation** - Simplified from broken nested aggregates
   - Before: `AVG(COUNT(...))` (SQL error: misuse of aggregate function)
   - After: `COUNT(*) / (students × days) × 100` (direct calculation)
   - User confirmed both methods mathematically equivalent
   - Fixed in `queries.py` lines 1796-1804

4. **Grade-level silver highlighting** - Fixed for all-grades view
   - Created `get_students_grade_winners()` method in `database.py`
   - Calculates max values per grade for all 8 metrics
   - Each grade's top performers now get silver highlights when viewing all grades
   - Gold (school-wide) always takes precedence over silver (grade-level)
   - Fixed highlighting logic for all 8 table columns
   - Added in `database.py` lines 1200-1327, `app.py` lines 1688-1696, 1783

5. **Grade filter persistence bug** - Critical fix for filter restoration
   - **Problem:** Grade filter was lost when navigating between pages
   - **Root cause:** Code read date/team from DOM *before* sessionStorage populated them
   - **Solution:** Read ALL filters from sessionStorage simultaneously
   - Check if ANY filter needs restoration, then redirect with complete URL
   - Prevents grade filter from being lost during School ↔ Students ↔ Grade Level navigation
   - Fixed in `templates/students.html` lines 1324-1369

**Regression Tests Added:**

1. **student21 Detail Modal Test** (`test_student21_detail_regression`)
   - Locks in 20+ exact values from user-verified screenshot
   - Student info, fundraising, reading, participation, goal metrics
   - Daily breakdown with exact dates and minutes
   - Catches any unintended changes to student detail calculation logic

2. **Complete Table Regression Test** (`test_complete_table_all_grades_all_teams_full_contest`)
   - Verifies all 7 students with exact values from user-verified screenshot
   - All fundraising values, sponsor counts, minutes, participation metrics
   - Gold highlights (10+ instances) for school-wide winners
   - Silver highlights (4+ instances) for grade-level winners
   - Team badges and proper color assignments
   - Catches any calculation or display changes

**Files Modified:**
- `templates/students.html` - Conditional rendering, filter restoration logic, grade-level highlighting
- `queries.py` - Simplified participation calculation
- `database.py` - Added `get_students_grade_winners()` method
- `app.py` - Call grade_winners when viewing all grades
- `test_students_page.py` - Added 2 comprehensive regression tests (50 tests total)
- `VERSION` - v2026.4.0 → v2026.5.0
- `docs/QUICK_START_NEXT_SESSION.md` - Updated with completion status
- `docs/STUDENTS_PAGE_STATUS.md` - Marked as COMPLETE

**Test Results:**
- Students page: 50/50 tests passing ✅
- Full suite: 235 tests passing ✅

---

## [v2026.4.0] - 2025-11-01

### Development Process Improvements

**Major Enhancement: Testing Discipline Framework**
- Established mandatory testing requirements for all feature implementations
- Never claim "complete" without automated tests + manual browser verification
- 11-point completion checklist before declaring features "working"
- Proper completion statement format with database verification examples
- Create tests DURING implementation (not after)

**Major Enhancement: Immediate Documentation Standards**
- Document important decisions immediately when made (reflex action, not "later")
- Survive conversation compaction by capturing context in files
- Table showing which files to update for different decision types
- Update "Last Updated" dates when files change
- Honest acknowledgment: No pre-compaction notifications, occasional reminders may be needed

**Students Page Implementation Roadmap**
- Phase 1-2: Design (ASCII → HTML for master + detail views)
- Phase 3-4: Production (with full testing checklists)
- Phase 5: Documentation & commit
- Each phase has explicit testing requirements
- New master-detail pattern (first for this application)

**Design Decisions Documented:**
- Students page reading column will use capped minutes (max 120/day)
- Matches School/Teams/Grade Level pages for consistency
- Detail view will show daily breakdown when clicking student row

**Files Modified:**
- `CLAUDE.md`: Added 202 lines covering Testing Discipline, Immediate Documentation, Students Page phases
- `docs/STUDENTS_PAGE_DESIGN.md`: Updated status, documented capped minutes decision
- `VERSION`: v2026.3.0 → v2026.4.0

**Commits:**
- This release establishes development standards before Students page implementation begins

---

## [v2026.3.0] - 2025-10-25

### Teams Competition Page Redesign

**Major Feature: 4-Column Layout**
- Redesigned Teams page from 2-column to 4-column layout (2 rows x 4 cards)
- Reduced vertical space usage for better screen real estate
- Row 1: All Team Kitsko metrics (Fundraising Leader, Top Class Fundraising, Reading Leader, Top Class Reading)
- Row 2: All Team Staub metrics (same structure)
- Team-specific card styling with colored borders and backgrounds
- Blue (#1e3a5f) for Team Kitsko, Yellow (#f59e0b) for Team Staub

**Visual Enhancements:**
- Colored oval highlights around winning values in comparison table
- Team-specific winning value colors (blue ovals for Kitsko, yellow ovals for Staub)
- Section row headers with team-specific colors
- Removed redundant team color indicator dots
- Improved card spacing and padding consistency

**Filter Indicators (◐) - Bug Fixes:**
- Added ◐ symbol to Teams page "READING LEADER" cards (both teams)
- Added ◐ symbol to Teams page "TOP CLASS (READING)" cards (both teams)
- Added ◐ symbol to School page team cards for "Reading (With Color)" metric
- Added ◐ symbol to School page team cards for "Avg. Participation (With Color)" metric
- Symbol appears with tooltip: "Cumulative through [date]"

**Global Filter Persistence:**
- Implemented sessionStorage-based filter persistence across pages
- Date filter selection now persists when navigating School ↔ Teams
- Automatic filter application on page load if previously selected
- Maintains backward compatibility with direct URL access

**Testing:**
- Created comprehensive test suite: `test_teams_page.py` with 13 tests
- Tests cover layout structure, team presence, metrics, highlights, and data integrity
- All 22 tests passing (9 School + 13 Teams)

**Files Modified:**
- `templates/teams.html`: 4-column layout, colored highlights, filter persistence
- `templates/school.html`: Filter indicators added to team cards, filter persistence
- `test_teams_page.py`: New comprehensive test suite (13 tests)
- `prototypes/dashboard_teams_tab_v3.html`: HTML prototype for 4-column design

**Commits:**
- `93f3127`: Add comprehensive dashboard tab implementation checklist
- `916a583`: Implement Teams Competition tab with head-to-head team metrics
- `fde0efc`: Add Teams Tab V2 prototype with unified table structure
- `8d50386`: Update Teams page with 4-column layout and team color consistency
- `3f9bd5d`: Add colored oval highlights to winning values in comparison table
- `260b2cf`: Add comprehensive test suite for Teams Competition page
- `101b8ed`: Fix filter indicators and implement global filter persistence

---

## [v2026.2.0] - 2025-10-23

### Subdued Color Scheme (Option H)

**New Design:**
- Professional subdued blue color palette replacing bright Bootstrap colors
- Cohesive visual identity across entire application
- Improved readability and reduced visual fatigue

**Color Scheme:**
- **Card/Accordion Headers**: Soft blue gradient (#dbeafe → #f0f9ff) with blue left border (#3b82f6)
- **Action Buttons**: Medium blue gradient (#3b82f6 → #2563eb) replacing bright green/cyan/yellow
- **Table Headers**: Dark navy blue (#1e3a5f) matching school banner
- **Status Badges**: Soft pastels - yellow (warning), green (success), red (danger), blue (info)
- **Team 2 Preserved**: Light yellow (#fffbeb) with amber border (#f59e0b) on School page

**Implementation:**
- Added global CSS in `base.html` for consistent styling
- Updated 10 template files to use new color classes
- Created prototype with 8 design options for user selection
- All bright colors (bg-primary, bg-success, bg-warning, bg-info, bg-danger) replaced

**Pages Updated:**
- Upload, Reports, Admin, Workflows, Tables, Help, Home/Dashboard
- Claude Development, Application Requirements
- All pages now have consistent subdued blue aesthetic

**Technical:**
- New CSS classes: `.card-header-blue`, soft button styles
- Global !important overrides for Bootstrap default colors
- Maintains accessibility with proper contrast ratios
- Team-specific colors preserved where meaningful (School page)

**Files Modified:**
- `templates/base.html`: +119 lines of new CSS
- `templates/*.html`: 10 templates updated
- `prototypes/ui_prototype_color_scheme_options.html`: New prototype file (1,783 lines)

---

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
