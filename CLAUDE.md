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
# Default: Uses last database choice (or sample if first run)
python3 app.py

# Explicitly use sample database
python3 app.py --db sample

# Use specific database by name (case-insensitive)
python3 app.py --db "2025 Read-a-Thon"

# Use specific database by filename
python3 app.py --db readathon_2025.db
```

**Database Selection:**
- App uses **Database Registry** (`db/readathon_registry.db`) to manage multiple year databases
- CLI argument supports: display name, filename, or alias ("sample")
- Case-insensitive matching for all CLI arguments
- App remembers last database choice in `.readathon_config` (gitignored)
- Priority: CLI argument > Config file > Default (sample)
- Can switch databases via UI dropdown in header (persists to config file)
- Startup shows which database is active and why
- Sample database displays with yellow/amber banner for visual distinction

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
- **Database:** SQLite 3 with multi-database architecture:
  - **Registry Database:** `db/readathon_registry.db` - Centralized database catalog
  - **Contest Databases:** `db/readathon_2025.db`, `db/readathon_sample.db`, etc.
- **Frontend:** Bootstrap 5.3.0 + Bootstrap Icons (CDN-loaded)
- **No npm/webpack:** Static HTML templates with Jinja2

### Database Architecture

**Registry Database** (`db/readathon_registry.db`):
```
Database_Registry table:
  - Tracks all available contest databases
  - Stores metadata: display_name, year, description, filename
  - Manages active database selection (only one active at a time)
  - Maintains summary statistics (student_count, total_days, total_donations)
```

**Contest Database** (e.g., `db/readathon_2025.db`):
```
Roster (411 students)
  ├─> Daily_Logs (day-by-day reading minutes per student)
  └─> Reader_Cumulative (aggregated stats: total minutes, donations, sponsors)

Supporting Tables:
  - Class_Info (teacher assignments, grade levels)
  - Grade_Rules (grade-specific reading goals)
  - Upload_History (audit trail for CSV imports)
  - Team_Color_Bonus (bonus minutes for team color day participation)
```

**Key Architecture Principles:**
- **Separation of Concerns:** Registry metadata separate from contest data
- **Multi-Year Support:** Each school year has its own contest database
- **Dynamic Loading:** Databases loaded on-demand based on registry configuration
- **Single Source of Truth:** Registry database defines available databases

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

6. **Database Registry System**
   - External registry database (`readathon_registry.db`) tracks all contest databases
   - Replaces old embedded `Database_Metadata` table approach
   - Enables true multi-year database management
   - Q24 report now queries central registry instead of contest database
   - Admin page includes "Database Registry" tab for managing databases
   - Supports dynamic database registration, activation, and statistics updates

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
README.md                 # Project README
CLAUDE.md                 # This file - project guidance for Claude Code
md/                       # Markdown documentation
  ├─ CHANGELOG.md         # Version history and release notes
  ├─ RULES.md             # Universal rules for all pages
  ├─ UI_PATTERNS.md       # Established UI patterns
  ├─ IMPLEMENTATION_PROMPT.md  # SOURCE OF TRUTH (130KB requirements doc)
  └─ ...                  # Other markdown docs
db/                       # SQLite databases
  ├─ readathon_registry.db  # Registry database (tracks all contest databases)
  ├─ readathon_2025.db    # 2025 contest database (production)
  └─ readathon_sample.db  # Sample database (fictitious data for testing)
csv/                      # Sample CSV files for initialization
tests/                    # All test files (18 files, 411 tests)
  ├─ test_database_registry.py  # Database registry tests (13 tests)
  └─ ...                  # Other test files
templates/                # Jinja2 HTML (base, index, upload, reports, admin, workflows)
prototypes/               # HTML prototypes (sanitized with fictitious data)
docs/                     # Feature documentation (31 features + architecture)
  ├─ 00-INDEX.md          # Master index of all features
  ├─ QUICK_START_NEXT_SESSION.md  # Current work status
  └─ features/            # Individual feature specs
  └─ screenshots/         # Screenshots (sanitized for privacy)
```

## Universal Rules & UI Patterns

**MANDATORY READING before implementing ANY feature:**

1. **[RULES.md](md/RULES.md)** - Universal rules that apply across all pages
   - Data source rules (which tables for what data)
   - Team color assignments (alphabetical order: team 1 = blue, team 2 = yellow)
   - Winner highlighting rules (gold = school-wide, silver = grade/team level)
   - Banner metric order, state management, consistency principles

2. **[UI_PATTERNS.md](md/UI_PATTERNS.md)** - Established UI patterns from existing pages
   - Color palette (hex codes for all colors)
   - Component patterns (filters, banners, badges, tables, footers)
   - Layout templates and implementation checklists
   - Quick reference to files with good examples

**When to consult these files:**
- Before starting any new feature implementation
- When uncertain about data sources, colors, or styling
- If you identify a new pattern or rule (add it and update the date)
- When prototype → production implementation isn't matching expectations

## Prototype-to-Production Workflow

**MANDATORY process when implementing features from prototypes:**

### Step 1: Before Starting Implementation
- [ ] Read md/RULES.md completely
- [ ] Read the prototype HTML file completely
- [ ] Create element inventory: List ALL visual/functional features in prototype
- [ ] Check 2-3 existing pages (school.html, teams.html, grade_level.html) for similar patterns
- [ ] Consult md/UI_PATTERNS.md for styling, colors, component structures
- [ ] Plan implementation: Map each prototype element → production code

### Step 2: During Implementation
- [ ] Reference md/RULES.md for every data calculation
- [ ] Use md/UI_PATTERNS.md for consistent styling
- [ ] Check school/teams/grade pages when uncertain about patterns
- [ ] Add code comments for complex logic or rule applications

### Step 3: Before Saying "It's Working"
- [ ] Actually test with running Flask app (load URL, not just code review)
- [ ] Open page in browser and compare side-by-side with prototype
- [ ] Test ALL interactive elements (buttons, filters, sorting, dropdowns)
- [ ] Verify calculations against database queries
- [ ] Check md/RULES.md checklist (data sources, colors, consistency)

### Step 4: Testing Discipline
Instead of saying *"The banner now shows correct values"*, do this:
1. Read prototype banner section
2. Identify exact elements: 4 metrics? which ones? what order?
3. Implement using correct data sources (per md/RULES.md)
4. Test: Load actual URL in browser
5. Verify: Banner shows same 4 metrics as prototype, same order
6. Verify: Numbers match database (run SQL to confirm)
7. Status: ✅ Matches prototype, ✅ Follows md/RULES.md

---

## Testing Discipline (MANDATORY)

**CRITICAL PROBLEM:** In the past, features were claimed "complete" when simple tests would have caught errors (including page load failures due to exceptions).

**NEW RULE:** NEVER claim a feature is "working" or "complete" without:

### 1. Automated Tests (Create DURING Implementation, NOT After)
```bash
# Create test file while implementing, not after
test_students_page.py

# Mandatory tests for ALL pages (see md/RULES.md lines 228-320):
- test_page_loads_successfully (HTTP 200)
- test_no_error_messages (scan for exceptions)
- test_percentage_formats (validate all %)
- test_currency_formats (validate all $)
- test_sample_data_integrity (verify DB calculations)
- test_team_badges_present (team color consistency)
- test_winning_value_highlights (gold/silver ovals)
- test_headline_banner (6 metrics present)
```

### 2. Manual Browser Testing (BEFORE Claiming Done)
**Checklist - ALL must pass before saying "it's working":**
- [ ] ✅ Run tests: `pytest test_students_page.py -v` (all passing)
- [ ] ✅ Start Flask app: `python3 app.py --db sample`
- [ ] ✅ Open URL in browser: `http://127.0.0.1:5001/students`
- [ ] ✅ Page loads without errors (no exceptions, no blank page)
- [ ] ✅ Compare side-by-side with prototype (visual match)
- [ ] ✅ Banner: 6 metrics present, correct order, correct values
- [ ] ✅ Table: Sortable headers, alternating row colors, correct data
- [ ] ✅ Filters: Work correctly, persist via sessionStorage
- [ ] ✅ Team colors: Follow alphabetical rule (blue/yellow)
- [ ] ✅ Run SQL queries to verify calculations match displayed values

### 3. Completion Statement Format
**BAD:** "The banner now shows correct values ✅"

**GOOD:**
```
✅ Banner implementation complete:
- Tested in browser: http://127.0.0.1:5001/students
- All 6 metrics present in correct order
- Values verified against database queries:
  * Fundraising: $45,678 (matches Reader_Cumulative SUM)
  * Minutes: 8,234 hours (matches Daily_Logs capped SUM)
  * Sponsors: 28 (matches Reader_Cumulative SUM)
- Visual match with prototype ✅
- All tests passing (8/8) ✅
```

**When tests fail or page doesn't load:**
- ❌ Do NOT say "it's working"
- ✅ Fix the issue first
- ✅ Re-test until all checks pass
- ✅ THEN report completion

---

## Immediate Documentation (REFLEX ACTION)

**PROBLEM:** Context is lost during conversation compaction. Important decisions/rules are forgotten.

**SOLUTION:** Document important information **immediately** when discovered, not "later" or "at the end".

### When to Document Immediately (REFLEX)

**User asks important question → Document answer NOW:**
```
User: "Should fundraising be capped or uncapped?"
Claude: [Immediately edits md/RULES.md]
        "✅ Documented in md/RULES.md line 82-85: Fundraising is NEVER capped,
            always from Reader_Cumulative table"
```

**Design decision made → Update design doc NOW:**
```
User: "Students page should use capped minutes"
Claude: [Immediately updates docs/STUDENTS_PAGE_DESIGN.md]
        "✅ Documented in STUDENTS_PAGE_DESIGN.md line 178:
            Reading column uses capped minutes (max 120/day)"
```

**New pattern discovered → Update md/UI_PATTERNS.md NOW:**
```
Claude: "I notice all pages use the same filter dropdown pattern"
        [Immediately updates UI_PATTERNS.md]
        "✅ Added Filter Period Selector pattern to md/UI_PATTERNS.md lines 50-109"
```

### Which Files to Update

| Decision Type | File to Update | Example |
|---------------|----------------|---------|
| Data source rule | `md/RULES.md` | "Fundraising always from Reader_Cumulative" |
| Calculation rule | `md/RULES.md` | "Participation can exceed 100% with color bonus" |
| Visual pattern | `md/UI_PATTERNS.md` | "Team badges use rounded rectangles" |
| Color assignment | `md/UI_PATTERNS.md` or `md/RULES.md` | "Team 1 (alphabetically first) = blue" |
| Feature design | `docs/STUDENTS_PAGE_DESIGN.md` | "Detail view shows daily breakdown" |
| Open questions | `docs/STUDENTS_PAGE_DESIGN.md` | "TBD: Export to CSV or Excel?" |

### Compaction Reality

**Q: Will Claude get notified before compaction happens?**
- **A: No.** Compaction happens transparently. By the time conversation is shorter, it's too late.

**Q: Can Claude save state during compaction?**
- **A: No.** There's no "pre-compaction hook" to trigger documentation.

**Q: Will user need to remind Claude to document?**
- **A: Possibly yes, occasionally.** But by making it a **reflex action** (document immediately when decision is made), we minimize context loss.

**Best Practice:**
- ✅ Document IMMEDIATELY when decision is made (not later)
- ✅ Update "Last Updated" date in file
- ✅ Reference file location so user knows where to find it
- ✅ If uncertain whether to document, ASK USER

---

## Students Page Implementation Phases

**Context:** New Students tab with master-detail pattern (new for this app). Process must follow strict groundrules to avoid past issues.

### Phase 1: Design - Master View (Table)
**ASCII Prototype:**
- [ ] Review md/RULES.md, md/UI_PATTERNS.md, existing pages
- [ ] Create ASCII prototype for Students table view (all 411 students)
- [ ] Define columns: Name, Grade, Team, Class, Fundraising, Reading (capped), Sponsors, Participation
- [ ] Document design decisions in `docs/STUDENTS_PAGE_DESIGN.md`
- [ ] Get user approval before HTML prototype

**HTML Prototype:**
- [ ] Create `/prototypes/students_tab.html` with fictitious data
- [ ] Match color palette, component patterns from md/UI_PATTERNS.md
- [ ] Verify sortable table headers (#1e3a5f background, white text)
- [ ] Verify team colors (alphabetical rule: blue/yellow)
- [ ] Verify 6-metric banner (same order as School/Teams/Grade pages)
- [ ] **Test in browser** (not just code review!)
- [ ] Provide both links (terminal + file://)
- [ ] Get user approval before production

### Phase 2: Design - Detail View (Daily Breakdown)
**ASCII Prototype:**
- [ ] Design detail view shown when clicking student row
- [ ] Define content: Daily reading log, goal achievement, sponsor info, charts?
- [ ] Document in `docs/STUDENTS_PAGE_DESIGN.md`
- [ ] Get user approval before HTML prototype

**HTML Prototype:**
- [ ] Create `/prototypes/student_detail.html` with fictitious data
- [ ] Match existing patterns for modal/detail views
- [ ] **Test in browser** (clicking row → opens detail)
- [ ] Get user approval before production

### Phase 3: Production - Master View
**Implementation:**
- [ ] Create `test_students_page.py` (all 8 mandatory tests)
- [ ] Update `app.py`: Add `/students` route
- [ ] Update `database.py`: Add `get_students_data()` method
- [ ] Update `queries.py`: Add student queries (capped minutes!)
- [ ] Create `templates/students.html` (Jinja2)
- [ ] Update `templates/base.html`: Add "Students" to nav menu
- [ ] Implement filters, sorting, pagination

**Testing (BEFORE claiming done):**
- [ ] Run tests: `pytest test_students_page.py -v` (all passing)
- [ ] Start Flask: `python3 app.py --db sample`
- [ ] Open browser: `http://127.0.0.1:5001/students`
- [ ] Verify: Page loads, no errors
- [ ] Verify: Side-by-side match with prototype
- [ ] Verify: All 6 banner metrics correct
- [ ] Verify: Table sortable, correct colors
- [ ] Verify: Calculations match database (run SQL)
- [ ] **ONLY THEN** report completion

### Phase 4: Production - Detail View
**Implementation:**
- [ ] Update `test_students_page.py`: Add detail view tests
- [ ] Update `app.py`: Add `/students/<student_id>` route
- [ ] Update `database.py`: Add `get_student_detail()` method
- [ ] Update `queries.py`: Add daily breakdown queries
- [ ] Create `templates/student_detail.html` or add modal to students.html
- [ ] Implement click → open detail logic

**Testing (BEFORE claiming done):**
- [ ] Run tests: `pytest test_students_page.py -v` (all passing)
- [ ] Test in browser: Click student row → detail opens
- [ ] Verify: Daily breakdown shows correct data
- [ ] Verify: Calculations match database
- [ ] **ONLY THEN** report completion

### Phase 5: Documentation & Commit
- [ ] Update `docs/STUDENTS_PAGE_DESIGN.md` with final implementation
- [ ] Update `docs/00-INDEX.md` if needed
- [ ] Prepare commit message (project style)
- [ ] **Ask for user approval** before committing

---

## Critical Context

### Before Starting Work
1. **Read [RULES.md](md/RULES.md)** - Universal app rules
2. **Read [UI_PATTERNS.md](md/UI_PATTERNS.md)** - Established patterns from existing pages
3. **Read md/IMPLEMENTATION_PROMPT.md** - Complete requirements document
4. **Check docs/QUICK_START_NEXT_SESSION.md** - Current development status
5. **Consult docs/00-INDEX.md** - Searchable feature index

### Current Version
**v2026.1.1** - Database selection with persistent preference

See `VERSION` file for current version and `CHANGELOG.md` for release history.

### Recent Completions
- ✅ **Database Registry Architecture** (v2026.2.0) - Major redesign:
  - Moved from embedded Database_Metadata table to external registry database
  - Implemented DatabaseRegistry class for centralized database management
  - Updated CLI to support display name, filename, or alias matching
  - Renamed readathon_prod.db → readathon_2025.db
  - Admin page now includes "Database Registry" tab
  - Q24 report queries central registry
  - Export includes database registry info in README
  - Sample database shows yellow/amber banner
  - All 18 test files updated (411 tests passing)
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
- **Multi-database architecture:**
  - Registry database: `db/readathon_registry.db` (tracks all contest databases)
  - Contest databases: `db/readathon_2025.db` (production), `db/readathon_sample.db` (testing)
  - Persistent database preference stored in `.readathon_config`
  - Default: sample database (safer for development)
  - CLI supports: display name, filename, or alias (`--db sample`, `--db "2025 Read-a-Thon"`, `--db readathon_2025.db`)
  - Sample database displays with yellow/amber visual banner

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

## Prototype Development & Links

**IMPORTANT: Whenever creating or referencing HTML prototypes, ALWAYS provide BOTH link formats:**

### 1. Terminal Command Format (for `open` command)
```bash
open prototypes/prototype_name.html
```

### 2. File URL Format (for direct browser paste)
```
file:///Users/stevesouza/my/data/readathon/v2026_development/prototypes/prototype_name.html
```

### Example:
When creating or referencing `prototypes/dashboard_teams_tab.html`, provide:

**Terminal command:**
```bash
open prototypes/dashboard_teams_tab.html
```

**Direct browser URL:**
```
file:///Users/stevesouza/my/data/readathon/v2026_development/prototypes/dashboard_teams_tab.html
```

This applies to:
- Newly created prototypes
- References to existing prototypes
- Documentation mentioning prototype files
- Any HTML file in the prototypes/ directory

## Post-Implementation Checklist

**CRITICAL: Claude must automatically perform these steps after ANY feature implementation without being asked.**

This checklist ensures quality, security, and completeness for every feature. User only needs to approve final commit.

### 1. Testing ✅
**Automatically Create or Update Tests:**
- Create test file (e.g., `test_students_page.py`) using pytest framework
- Include tests for:
  - Page loading successfully (HTTP 200, no errors)
  - Data structure verification (tables, sections, headings present)
  - Sample data integrity (calculations match database)
  - UI elements present (buttons, filters, navigation)
- Run existing test suite to check for regressions
- Report test results: "✅ X tests created, all passing" or "⚠️ Y tests failing"
- Suggest adding to pre-commit hook if critical feature

### 2. Security Review ⚠️ WARN ONLY
**Automatically Check for Security Issues:**

**SQL Injection:**
- ✅ Verify parameterized queries: `cursor.execute(query, params)`
- ❌ Flag string formatting: `f"SELECT * FROM {table}"`

**XSS (Cross-Site Scripting):**
- ✅ Verify Jinja2 auto-escaping: `{{ variable }}`
- ⚠️ Flag unsafe HTML: `{{ variable | safe }}` (warn user)

**Input Validation:**
- ✅ Check length limits (e.g., `if len(input) > 100`)
- ✅ Check format validation (regex patterns)
- ✅ Check sanitization (strip, validate)

**File Operations:**
- ✅ Check path traversal prevention
- ✅ Check file type validation
- ✅ Check size limits

**Error Handling:**
- ❌ Flag exposing system details: `return f"Database error: {str(e)}"`
- ✅ Verify generic user messages: `return "Operation failed. Please try again"`

**If issues found:**
- ⚠️ **WARN user but don't block implementation**
- Explain issue clearly
- Provide recommended fix
- Ask: "I can fix this now. Proceed with fix?"

**If no issues found:**
- ✅ Report: "Security review: No issues found ✅"

### 3. Documentation 📝
**Automatically Update Documentation:**
- Update relevant feature documentation (`docs/features/feature-XX.md`)
- Add code comments for complex logic (algorithms, security-critical sections)
- Update `docs/QUICK_START_NEXT_SESSION.md` if major change
- Update `docs/00-INDEX.md` if new feature
- Document any new dependencies in `requirements.txt` and CLAUDE.md
- Add prototype to `prototypes/INDEX.html` if applicable

### 4. Version Control 🤚 ASK FIRST
**Automatically Prepare Commit (But Ask for Approval):**

**Step 1: Review Changes**
- Run `git status` to see modified/new files
- Run `git diff` to see actual changes
- Summarize what changed

**Step 2: Generate Commit Message**
Follow project style (from CHANGELOG.md):
```
<Short descriptive title>

- Bullet point of change 1
- Bullet point of change 2
- Bullet point of change 3

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>
```

**Step 3: Present to User and ASK**
```
"✅ [Feature name] implementation complete!

What I did:
- [Summary of implementation]
- Added X automated tests (Y passing ✅ / Z failing ⚠️)
- Security review: [No issues found ✅ / Found N issues ⚠️]
- Updated X documentation files

Proposed commit message:

'[Generated commit message]'

Approve this commit? (yes/no)"
```

**Step 4: After Approval**
- Commit with generated message
- Show `git log -1` to verify
- Suggest version increment if significant: "This is a [minor/patch] feature, increment to vYYYY.X.0?"

**NEVER auto-commit without asking first!**

### 5. User Communication 📢
**Automatically Provide:**

**For Prototypes:**
- Terminal command: `open prototypes/file.html`
- Browser URL: `file:///Users/stevesouza/my/data/readathon/v2026_development/prototypes/file.html`

**Summary:**
- What was implemented
- Test results
- Security review results
- Documentation updated
- Commit ready for approval

**Next Steps:**
- Suggest version increment
- Note any breaking changes or migrations needed
- Recommend follow-up work if applicable

---

## When Claude Should Ask vs. Act

**Act Automatically (No User Permission Needed):**
- ✅ Creating or updating automated tests
- ✅ Running existing test suite
- ✅ Security review (with warnings for issues)
- ✅ Updating documentation
- ✅ Adding code comments
- ✅ Providing prototype links (both formats)
- ✅ Running read-only git commands (`git status`, `git diff`, `git log`)
- ✅ Analyzing code for issues
- ✅ Generating commit messages (but not committing)

**Ask First (Always Require User Approval):**
- 🤚 Git commits (prepare message, then ASK)
- 🤚 Git pushes (local to remote)
- 🤚 Version tagging (creating release tags)
- 🤚 Deleting files or data
- 🤚 Destructive git operations (filter-branch, reset --hard, etc.)
- 🤚 Modifying configuration files
- 🤚 Installing dependencies
- ❓ **When uncertain about user's intent** - Always ask for clarification

**Key Principle:**
- **Automate quality checks** (tests, security, docs)
- **Ask for destructive operations** (commits, pushes, deletes)
- **Ask when uncertain** (ambiguous requirements, multiple approaches)

This ensures Claude is proactive about quality while maintaining user control over git history and critical operations.

---

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
