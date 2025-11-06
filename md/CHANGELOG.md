# Changelog

All notable changes to the Read-a-Thon Management System will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project uses **School Year Calendar Versioning** (vYYYY.MINOR.PATCH).

## [v2026.9.0] - 2025-11-05

### Pure Group-Based Tagging System

**Core System Refactor:**
- Replaced `item_type` and `report_type` fields with single `groups` array
- Implemented hierarchical naming convention using periods (workflow.qa, requires.date)
- Five group categories: structural, semantic, workflow, behavior, domain
- All 35 items tagged (23 reports + 8 tables + 4 workflows)
- Dynamic workflow execution based on group tags (no hardcoded lists)

**Helper Functions:**
- `get_items_by_group()` - Query items by single group with wildcard support
- `get_items_by_groups()` - Query items by multiple groups (AND/OR logic)
- `is_report()`, `is_table()`, `is_workflow()` - Type checking functions
- `requires_date()`, `requires_group_by()` - Behavior checking functions
- `get_workflow_reports()` - Get all reports in a workflow

**UI Improvements:**
- Custom CSS badge colors for group tags (high-contrast, accessible)
- Added "GROUPS:" label above group badges for clarity
- Changed "All Groups" to "All Items" label
- Fixed group filter dropdown counts (workflow.qa, workflow.qd, etc.)
- Fixed regression: Added missing items array for JavaScript report options

**Testing & Documentation:**
- Added `test_group_system.py` with 28 comprehensive regression tests
- Added `test_export_all.py` for export functionality tests
- Added `docs/GROUPS_SYSTEM.md` with complete system documentation
- Updated `test_reports_page.py` to use new group system
- All 305 tests passing (5 skipped)

**Benefits:**
- Flexible multi-group membership for items
- No hardcoded workflow lists (easier to maintain)
- Searchable across all group tags
- Easy to add new groups or workflows
- Self-documenting tags describe purpose and behavior

**Files Modified:**
- `app.py` - Added helper functions, updated routes for group system
- `database.py` - Updated item definitions with groups array
- `templates/reports.html` - Badge CSS, GROUPS label, JavaScript fix
- `templates/workflows.html` - Dynamic counts for Run Group dropdown
- `templates/admin.html` - Minor group system integration
- `test_group_system.py` - NEW: Comprehensive regression tests
- `test_export_all.py` - NEW: Export functionality tests
- `test_reports_page.py` - Updated for group system
- `docs/GROUPS_SYSTEM.md` - NEW: Complete system documentation
- `VERSION` - v2026.8.0 → v2026.9.0
- `CHANGELOG.md` - This file

## [v2026.8.0] - 2025-11-05

### Admin Page Data Management Enhancements

**Transactional vs System Tables Grouping:**
- Renamed "Clear Data Tables" → "Data Management"
- Added explanatory info panel distinguishing transactional from system tables
- Transactional Tables section: 4 clearable tables (Upload_History, Reader_Cumulative, Daily_Logs, Team_Color_Bonus)
- System Tables section: 3 reference-only tables (Roster, Class_Info, Grade_Rules)
- Added Team_Color_Bonus to clear data functionality (previously missing)

**Collapsible Sections:**
- Database Tables Overview: Collapsible, collapsed by default
- Transactional Tables: Collapsible, expanded by default
- System Tables: Collapsible, expanded by default
- Chevron icons automatically toggle on expand/collapse

**Table Count Display:**
- All 7 tables now show record counts
- System tables use contextual labels: "students", "classes", "grade levels"
- Transactional tables use generic "records" label

**Backend Updates:**
- `/api/table_counts` now returns all 7 tables (4 transactional + 3 system)
- `/api/clear_tables` validates only transactional tables (security)
- `clear_all_data.py` script updated to include Team_Color_Bonus

**Files Modified:**
- `app.py` - Updated `/api/table_counts` route to include system tables
- `templates/admin.html` - Added collapsible sections, system tables section, chevron toggle JavaScript
- `clear_all_data.py` - Added Team_Color_Bonus to clear operations
- `VERSION` - v2026.7.0 → v2026.8.0
- `CHANGELOG.md` - This file

## [v2026.7.0] - 2025-11-05

### Reports & Data Page Enhancements

**UI Improvements:**
- Redesigned filter layout: compact horizontal design saves vertical space
- Search and Group filters now side-by-side below header
- Report items display title and description on single line (bold + dash separator)
- Removed collapsible Filters card for always-visible access
- More reports visible on screen without scrolling

**Enhanced Search Functionality:**
- Search now includes item type (report, table, workflow)
- Search now includes group tags (prize, slides, export, admin, tables)
- Searching "table" shows all database tables
- Searching "workflow" shows all workflows
- Searching "prize", "export", "slides" shows respective group items
- Added data-groups attribute to HTML for client-side filtering

**Comprehensive Test Suite:**
- Created test_reports_page.py with 31 tests (all passing)
- Group filter tests (7): all, prize, slides, export, admin, tables, workflows
- Search functionality tests (7): name, description, type, groups, attributes
- Structure & regression tests (13): counts, multi-group, UI elements, data integrity
- Mandatory tests (4): page loads, no errors, sample data verification
- **Total test suite: 246 tests (up from 215)**

**Critical Documentation:**
- Added prominent section in RULES.md about updating pre-commit hook when creating new test files
- Documents requirement to add new test files to `.git/hooks/pre-commit`
- Prevents future context loss by making this requirement explicit and searchable

**Files Modified:**
- `templates/reports.html` - Compact filters, enhanced search
- `test_reports_page.py` - New comprehensive test suite
- `.git/hooks/pre-commit` - Updated to include test_reports_page.py (246 tests)
- `RULES.md` - Added critical pre-commit hook documentation
- `VERSION` - v2026.6.1 → v2026.7.0
- `CHANGELOG.md` - This file

## [v2026.6.1] - 2025-11-03

### Documentation Enhancements

**Major Update: Comprehensive Documentation of Implemented Features**
- Updated all three documentation pages to reflect current v2026.6.0 feature set
- Added detailed "Development Patterns That Worked Well" section with 8 comprehensive patterns
- Clarified distinction between implemented features and future enhancements

**User Manual (help.html):**
- Added navigation overview with 5 main tabs
- New "Dashboard Tabs" section covering School, Teams, Grade Level, and Students pages
- Updated "Reports & Data" section describing consolidated three-in-one page structure
- Documented enhanced metadata with automated analysis modal
- Added filter persistence information
- Removed duplicate Tables section (now integrated into Reports & Data)

**Claude Development Guide (claude_development.html):**
- Added comprehensive "Development Patterns That Worked Well" section (8 patterns)
  1. Development Guardrails (RULES.md & UI_PATTERNS.md)
  2. Multi-Phase Complex Features (Banner Standardization)
  3. Regression Tests (Lock in Verified Behavior)
  4. Filter Persistence (sessionStorage Pattern)
  5. Gold/Silver Highlighting System
  6. Testing During Implementation (Not After)
  7. Conditional Indicators (Half-Circle ◐ Pattern)
  8. Master-Detail Pattern (Students Page)
- Each pattern includes problem statement, actual prompts used, code examples, and benefits
- Updated navigation consolidation workflow (7→5 tabs)
- Added Students page example workflow (v2026.5.0)
- Added Reports & Data consolidation workflow (v2026.6.0)
- Updated version summary with 215 passing tests

**Requirements Document (IMPLEMENTATION_PROMPT.md):**
- Added comprehensive "Current Implementation Status" section (150+ lines)
- Documented all 5 dashboard tabs with detailed features
- Listed complete technical stack and database schema (8 tables)
- Explained key business logic (120-min cap, sanctioned dates, team competition)
- Added gold/silver highlighting rules and filter behavior
- Documented testing approach (215 tests) and versioning scheme
- Clarified distinction: implemented features (top section) vs future enhancements (bottom section)

**Files Modified:**
- `templates/help.html` - Updated with latest features and consolidated structure
- `templates/claude_development.html` - Added 8 development patterns with examples
- `IMPLEMENTATION_PROMPT.md` - Added current implementation status section
- `VERSION` - v2026.6.0 → v2026.6.1
- `CHANGELOG.md` - Added v2026.6.1 release notes

**Commits:**
- `f30c7ab`: Update documentation to reflect latest features (v2026.6.0)
- `5876080`: Add comprehensive "Development Patterns That Worked Well" section

**Benefits:**
- Complete reference for users learning the application
- Valuable guide for developers wanting to understand successful Claude Code patterns
- Requirements document can now be used to recreate the application from scratch
- All documentation accurate through v2026.6.0

---

## [v2026.6.0] - 2025-11-03

### Reports & Data Page Consolidation

**Major Feature: Unified Reports & Data Interface**
- Consolidated three separate pages (Reports, Tables, Admin) into single "Reports & Data" page
- Improved navigation with clearer organizational structure
- Reduced menu clutter from 7 tabs to 5 tabs
- Better user experience with all data access functions in one location

**Page Reorganization:**
- **Reports Tab** → **Reports & Data Tab**
  - Reports section (22 pre-configured reports with metadata and analysis)
  - Tables section (direct table viewing)
  - Admin section (database management tools)
- Maintained all existing functionality while improving discoverability
- Accordion-based interface for clean organization

**Visual Consistency Improvements:**
- Standardized all Reports page buttons to blue theme (#3b82f6 gradient)
- Removed inconsistent green/teal/yellow action buttons
- Matches application-wide subdued blue color scheme from v2026.2.0
- Professional, cohesive look across entire interface

**Upload Page Enhancements:**
- Improved consistency with application color scheme
- Enhanced documentation for upload process
- Better visual hierarchy and organization

**Files Modified:**
- `templates/base.html` - Updated navigation menu (7 tabs → 5 tabs)
- `templates/reports.html` - Consolidated three pages into accordion sections
- `templates/upload.html` - Improved consistency and documentation
- `app.py` - Updated routes and removed obsolete /tables and /admin endpoints
- `VERSION` - v2026.5.0 → v2026.6.0

**Commits:**
- `72b420d`: Consolidate Reports, Tables, and Admin into unified Reports & Data page
- `3cf1710`: Standardize Reports page button colors to blue theme
- `503885c`: Improve Upload page consistency and documentation

---

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
