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
# OR
./run_sample.sh

# Explicitly use production database
python3 app.py --db prod
# OR
./run_prod.sh
```

**Database Selection:**
- App remembers last database choice in `.readathon_config` (gitignored)
- Priority: CLI argument > Config file > Default (sample)
- Can switch databases via UI dropdown (persists to config file)
- Startup shows which database is active and why

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
- **Database:** SQLite 3 (local files: `readathon_prod.db` and `readathon_sample.db`)
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

## Universal Rules & UI Patterns

**MANDATORY READING before implementing ANY feature:**

1. **[RULES.md](RULES.md)** - Universal rules that apply across all pages
   - Data source rules (which tables for what data)
   - Team color assignments (alphabetical order: team 1 = blue, team 2 = yellow)
   - Winner highlighting rules (gold = school-wide, silver = grade/team level)
   - Banner metric order, state management, consistency principles

2. **[UI_PATTERNS.md](UI_PATTERNS.md)** - Established UI patterns from existing pages
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
- [ ] Read RULES.md completely
- [ ] Read the prototype HTML file completely
- [ ] Create element inventory: List ALL visual/functional features in prototype
- [ ] Check 2-3 existing pages (school.html, teams.html, grade_level.html) for similar patterns
- [ ] Consult UI_PATTERNS.md for styling, colors, component structures
- [ ] Plan implementation: Map each prototype element → production code

### Step 2: During Implementation
- [ ] Reference RULES.md for every data calculation
- [ ] Use UI_PATTERNS.md for consistent styling
- [ ] Check school/teams/grade pages when uncertain about patterns
- [ ] Add code comments for complex logic or rule applications

### Step 3: Before Saying "It's Working"
- [ ] Actually test with running Flask app (load URL, not just code review)
- [ ] Open page in browser and compare side-by-side with prototype
- [ ] Test ALL interactive elements (buttons, filters, sorting, dropdowns)
- [ ] Verify calculations against database queries
- [ ] Check RULES.md checklist (data sources, colors, consistency)

### Step 4: Testing Discipline
Instead of saying *"The banner now shows correct values"*, do this:
1. Read prototype banner section
2. Identify exact elements: 4 metrics? which ones? what order?
3. Implement using correct data sources (per RULES.md)
4. Test: Load actual URL in browser
5. Verify: Banner shows same 4 metrics as prototype, same order
6. Verify: Numbers match database (run SQL to confirm)
7. Status: ✅ Matches prototype, ✅ Follows RULES.md

## Critical Context

### Before Starting Work
1. **Read [RULES.md](RULES.md)** - Universal app rules
2. **Read [UI_PATTERNS.md](UI_PATTERNS.md)** - Established patterns from existing pages
3. **Read IMPLEMENTATION_PROMPT.md** - Complete requirements document
4. **Check docs/QUICK_START_NEXT_SESSION.md** - Current development status
5. **Consult docs/00-INDEX.md** - Searchable feature index

### Current Version
**v2026.1.1** - Database selection with persistent preference

See `VERSION` file for current version and `CHANGELOG.md` for release history.

### Recent Completions
- ✅ Database selection with persistent preference (v2026.1.1)
- ✅ Command-line arguments for database selection (--db sample/prod)
- ✅ Launcher scripts (run_sample.sh, run_prod.sh)
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
- **Multi-environment support:**
  - `readathon_prod.db` (production - real student data)
  - `readathon_sample.db` (sample - fictitious data for testing)
  - Persistent database preference stored in `.readathon_config`
  - Default: sample database (safer for development)
  - Override via CLI: `--db prod` or `--db sample`

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
