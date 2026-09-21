# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **Flask web application** for managing an elementary school read-a-thon event. It's a browser-based GUI for tracking 411 students' reading minutes and fundraising, with all data stored locally in SQLite (no server deployment required).

## Development Commands

### Setup & Installation
```bash
pip3 install -r requirements.txt  # Flask, pytest, beautifulsoup4 (tests)
python3 init_data.py 2026         # Create + register db/readathon_2026.db from roster.csv, class_info.csv, grade_rules.csv
                                  # (or in the app: Admin -> Database Registry -> Create New Database)
```

### Running the Application
```bash
# Default: Uses last database choice (or sample if first run)
python3 app.py

# Explicitly use sample database
python3 app.py --db sample

# Use specific database by name (case-insensitive)
python3 app.py --db "2026 Read-a-Thon"

# Use specific database by filename
python3 app.py --db readathon_2026.db
```

**Database Selection:**
- App uses **Database Registry** (`db/readathon_registry.db`) to manage multiple year databases
- CLI argument supports: display name, filename, or alias ("sample")
- Case-insensitive matching for all CLI arguments
- App remembers last database choice in `.readathon_config` (gitignored)
- Priority: CLI argument > Config file > Default (sample)
- Registry is auto-created on first start and seeded with the sample DB (real DBs + registry are gitignored for PII)
- **Naming convention:** one database per event year, `db/readathon_<YEAR>.db`, display name "<YEAR> Read-a-Thon"
- Any `db/readathon_<YEAR>.db` copied into `db/` is auto-registered at startup (`DatabaseRegistry.register_year_databases`)
- `./package_data.sh` zips `db/` (app must be stopped) for moving data between computers; code moves via git
- Can switch databases via UI dropdown in header (persists to config file)
- Startup shows which database is active and why
- Sample database displays with yellow/amber banner for visual distinction

### Testing
```bash
pytest                             # Run all tests (484 tests; tests needing db/readathon_2025.db skip if it's absent)
pytest tests/test_specific.py      # Run specific test file
```

**⚠️ CRITICAL: Stop Flask Before Running Tests**
```bash
# Kill all Flask instances before running tests
lsof -ti:5001 | xargs kill

# Then run tests
pytest
```

**Why this is important:**
- Running tests while Flask is active causes **database locking errors**
- Tests may **fail intermittently** with Flask running (observed 36+ failures)
- Same tests **pass consistently** when Flask is stopped (all 335 pass)
- Flask holds database connections that conflict with test database operations

**Before running pre-commit tests:**
1. Stop Flask: `lsof -ti:5001 | xargs kill`
2. Run tests: `pytest` (or let pre-commit hook run them)
3. All 463 tests should pass

### Database Operations
```bash
python3 clear_all_data.py         # Reset database tables (keeps schema)
```

## Claude Skills (Automated Enforcement)

This project uses **Claude Skills** for automated enforcement of best practices. Skills are model-invoked - Claude automatically uses them when relevant conditions are detected.

### Active Skills

**1. Readathon Pre-Commit Check** (`.claude/skills/readathon-precommit-check/`)
- **Triggers:** When preparing git commits
- **Enforces:** Testing discipline, security scans, documentation updates
- **Actions:** Kills Flask, runs pytest, checks for security issues, validates docs updated
- **Replaces:** Manual checklist from "Post-Implementation Checklist" section

**2. Readathon Database Safety** (`.claude/skills/readathon-database-safety/`)
- **Triggers:** Before database modification operations (INSERT, UPDATE, DELETE, DROP, clear_all_data.py)
- **Enforces:** Protection against accidental production database changes
- **Actions:** Warns before production operations, blocks destructive operations, recommends sample DB
- **Replaces:** Manual database safety checks

**3. Readathon Document Reflex** (`.claude/skills/readathon-document-reflex/`)
- **Triggers:** When design decisions made, patterns discovered, rules defined
- **Enforces:** Immediate documentation (prevents context loss during conversation compaction)
- **Actions:** Auto-updates RULES.md, UI_PATTERNS.md, feature docs when decisions occur
- **Replaces:** Manual "remember to document" reminders

**4. Readathon Workflow Detector** (`.claude/skills/readathon-workflow-detector/`) **[META-SKILL]**
- **Triggers:** After every user request + at session start
- **Detects:** Repetitive workflow patterns and complex tasks that should be automated
- **Suggests:** Creating new skills when patterns reach threshold (2/3/5 based on expertise)
- **Tracks:** All patterns in `.claude/workflow_patterns.md`
- **Respects:** "Track but don't make skill" user overrides
- **Meta-concept:** A skill that creates other skills by watching user behavior

**5. Readathon Context Saver** (`.claude/skills/readathon-context-saver/`)
- **Triggers:** Every 5-10 minutes + after important events
- **Prevents:** Context loss during long sessions and conversation compaction
- **Saves:** Session state to `docs/SESSION_MEMORY.md`
- **Captures:** Current work, key decisions, git state, workflow patterns, open questions
- **Purpose:** Break the context loss spiral (long session → compaction → re-explain → longer session)

### Meta-Skill System

**What's a meta-skill?** A skill designed to detect when other skills would be useful.

The `readathon-workflow-detector` uses dual detection:
1. **Repetition-based:** Tracks when you do the same thing 2-5 times (adaptive threshold)
2. **Complexity-based:** Immediately recognizes complex tasks worth automating (suggests at count 1)

**How it works:**
- Categorizes every request (Workflow, Question, Bug Fix, Feature, Analysis, Creative, Administrative)
- Tracks patterns in `.claude/workflow_patterns.md` with counts and status
- Suggests skill creation when threshold reached
- Learns user expertise level and adjusts timing
- Respects "track but don't make skill" overrides

**Context preservation strategy:**
Multi-layer defense against context loss:
- **Layer 1:** Real-time docs (document-reflex) - immediate
- **Layer 2:** Session memory (context-saver) - every 5-10 min + events
- **Layer 3:** Workflow patterns (workflow-detector) - every occurrence
- **Layer 4:** Quick start guide - session boundaries

### Why Skills vs. Documentation?

**Previous approach:** Detailed checklists in CLAUDE.md that rely on Claude remembering to follow them

**Skills approach:** Automated triggers that proactively enforce best practices when conditions are met

**Result:** Better enforcement, less reliance on discipline, systematic quality control

### Skill Files

Skills are stored in `.claude/skills/` directory:
- Each skill has its own subdirectory
- Core instructions in `SKILL.md` file with YAML frontmatter
- Skills can include helper scripts and templates
- Committed to repository (shared across all sessions)

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

2. **Contest Dates Come From the Data**
   - The contest range is the first..last date uploaded to Daily_Logs (2025 event: 10 days, Oct 10-19, 2025)
   - Never hard-code a year's dates or timestamps in page code
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
tests/                    # All test files (18 files, 463 tests)
  ├─ test_database_registry.py  # Database registry tests (13 tests)
  └─ ...                  # Other test files
templates/                # Jinja2 HTML (base, index, upload, reports, admin, workflows)
prototypes/               # HTML prototypes (sanitized with fictitious data)
docs/                     # Feature documentation (31 features + architecture)
  ├─ 00-INDEX.md          # Master index of all features
  ├─ QUICK_START_NEXT_SESSION.md  # Current work status
  ├─ SESSION_MEMORY.md    # Live session state (auto-saved every 5-10 min)
  ├─ GENERIC_PROMPTS.md   # Generic prompts for workflow detection & context preservation
  └─ features/            # Individual feature specs
  └─ screenshots/         # Screenshots (sanitized for privacy)
.claude/                  # Claude Code configuration
  ├─ workflow_patterns.md # Workflow pattern tracking (meta-skill data)
  └─ skills/              # Claude skills
      ├─ readathon-precommit-check/
      ├─ readathon-database-safety/
      ├─ readathon-document-reflex/
      ├─ readathon-workflow-detector/  # Meta-skill for pattern detection
      └─ readathon-context-saver/      # Context preservation skill
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

## Testing Discipline (Enforced by Skills)

**See Skill:** `.claude/skills/readathon-precommit-check/` for automated enforcement.

**Core Principle:** NEVER claim a feature is "working" or "complete" without running automated tests and verifying functionality.

### Two-Tier Testing (Claude Code Web vs. Desktop)

**Tier 1: Automated Testing** (Claude Code Web can do)
- ✅ Create and run pytest tests
- ✅ Start Flask, verify HTTP 200 responses
- ✅ Check for exceptions in logs
- ✅ Verify database query results
- ✅ Commit with tag: `[Automated tests pass]`

**Tier 2: Visual Testing** (User does on desktop)
- ❌ Visual browser verification (Claude Code Web cannot do)
- ❌ Prototype side-by-side comparison
- ❌ UI/UX validation
- ❌ Interactive element testing

**Workflow:** Claude completes Tier 1 → commits/pushes → User performs Tier 2 on desktop → approves or requests changes

### Mandatory Tests for ALL Pages
See `md/RULES.md` lines 228-320 for complete test requirements:
- test_page_loads_successfully (HTTP 200)
- test_no_error_messages (scan for exceptions)
- test_percentage_formats, test_currency_formats
- test_sample_data_integrity (verify DB calculations)
- test_team_badges_present, test_winning_value_highlights
- test_headline_banner (6 metrics present)

---

## Immediate Documentation (Enforced by Skills)

**See Skill:** `.claude/skills/readathon-document-reflex/` for automated enforcement.

**Core Principle:** Document important information **immediately** when discovered, not "later" or "at the end". This prevents context loss during conversation compaction.

### When Documentation Triggers Automatically

The `readathon-document-reflex` skill automatically triggers when:
- User asks about data sources ("Should X be capped or uncapped?")
- Design decisions made ("Students page will use X")
- Patterns discovered ("I notice all pages use Y pattern")
- Calculation rules defined ("Metric Z is calculated as...")

### Quick Reference: Which Files to Update

| Decision Type | File to Update |
|---------------|----------------|
| Data source, calculation rules | `md/RULES.md` |
| UI patterns, styling | `md/UI_PATTERNS.md` |
| Feature design | `docs/[FEATURE]_DESIGN.md` |
| Open questions / TBD items | Feature design docs |

The skill handles the immediate editing and reports back with file location and line numbers.

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
See `VERSION` (v2026.14.3 was the code used for the 2025 event; 2026-event work continues from v2026.15.0).
Requirements summary: `md/REQUIREMENTS.md`

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
  - All 18 test files updated (463 tests passing)
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

## Post-Implementation Checklist (Enforced by Skills)

**See Skill:** `.claude/skills/readathon-precommit-check/` for automated enforcement before commits.

After ANY feature implementation, Claude automatically performs:

### 1. Testing ✅
- Create test file using pytest framework
- Run full test suite to check for regressions
- Report: "✅ X tests created, Y/Z passing"

### 2. Security Review ⚠️
- Scan for SQL injection, XSS, path traversal, error exposure
- Warn about issues (don't block)
- Report: "✅ No issues found" or "⚠️ Found N issues" + recommendations

### 3. Documentation 📝
- Update feature documentation (`docs/features/`, design docs)
- Add code comments for complex logic
- Update QUICK_START_NEXT_SESSION.md if major change
- **Handled automatically by `readathon-document-reflex` skill**

### 4. Prepare Commit 🤚 ASK FIRST
- Run `git status` and `git diff`
- Generate commit message (project style from CHANGELOG.md)
- Present summary and **ASK for approval**
- **NEVER auto-commit without user approval**

### Commit Message Format
```
<Short descriptive title>

- Bullet point of change 1
- Bullet point of change 2
- Bullet point of change 3

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>
```

### When to Ask vs. Act

**Act Automatically:**
- ✅ Tests, security scans, documentation updates
- ✅ Read-only git commands
- ✅ Generate commit messages (but not committing)

**Ask First:**
- 🤚 Git commits/pushes
- 🤚 Destructive operations
- 🤚 Configuration changes
- ❓ When uncertain about intent

---

## Versioning Scheme

**Event-Year Calendar Versioning**: `vYYYY.MINOR.PATCH`

### Format
- **YYYY**: Read-a-thon **event year** (Oct 2026 event = v2026.x, Oct 2027 event = v2027.x)
- **MINOR**: Feature additions and improvements (1, 2, 3, ...)
- **PATCH**: Bug fixes and small updates (0, 1, 2, ...)

**Historical note:** v2026.1.0-v2026.14.3 were created under an earlier school-year scheme and are the code used
for the **2025** event (tag `readathon-2025-final`). Work for the 2026 event continues from v2026.15.0 rather than
restarting at v2026.1.0 (those tags already exist). From v2027.1.0 on, MINOR restarts at 1 each event year.

### When to Increment
- **Year (2026 → 2027)**: First release for the next event year
- **Minor (1 → 2)**: New features, reports, UI changes, significant improvements
- **Patch (0 → 1)**: Bug fixes, documentation updates, minor tweaks
- **End of an event:** add an annotated tag `readathon-<YEAR>-final` on the code used for that event

### Examples
```
v2026.15.0 → v2026.15.1  (bug fix or small update)
v2026.15.0 → v2026.16.0  (new feature added)
v2026.x.y  → v2027.1.0   (first release for the 2027 event)
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
- "Create new event year version" → v2026.x.y → v2027.1.0

Claude will:
1. Update VERSION file
2. Update CHANGELOG.md with changes
3. Create git tag with release notes
4. Push tag to GitHub
