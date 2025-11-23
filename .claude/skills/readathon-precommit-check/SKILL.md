---
name: Readathon Pre-Commit Check
description: Enforce pre-commit testing and validation before any git commit in the readathon project
---

# Readathon Pre-Commit Check

**TRIGGER:** Automatically when preparing to make a git commit in the readathon project.

## Critical Pre-Commit Checklist

Before ANY commit, complete ALL steps:

### 1. Stop Flask Server (Prevent Database Locking)

```bash
# Kill all Flask instances on port 5001
lsof -ti:5001 | xargs kill -9 2>/dev/null
```

**Why:** Running Flask causes database locking that makes tests fail intermittently.

### 2. Run Full Test Suite

```bash
pytest -v
```

**Expected:** All tests passing (currently 463 tests in the suite)

**If failures occur:**
- ❌ BLOCK commit
- Report which tests failed
- Investigate and fix before committing

### 3. Automated Security Scan

Check for common security issues:

**SQL Injection:**
- ❌ Flag: `f"SELECT * FROM {variable}"` (string formatting in queries)
- ❌ Flag: `query = "..." + variable` (concatenation)
- ✅ Pass: `cursor.execute(query, (param1, param2))` (parameterized)

**XSS (Cross-Site Scripting):**
- ⚠️ Warn: `{{ variable | safe }}` in templates (ask for justification)
- ✅ Pass: `{{ variable }}` (auto-escaped)

**Error Exposure:**
- ❌ Flag: `return f"Database error: {str(e)}"` (exposes internals)
- ✅ Pass: `return "Operation failed"` (generic message)

**Path Traversal:**
- ❌ Flag: `open(user_input)` without validation
- ✅ Pass: Path validation and sanitization present

### 4. Documentation Verification

Prompt the user:
- "Which documentation files did you update for this change?"
- Common files: CLAUDE.md, md/RULES.md, md/UI_PATTERNS.md, docs/features/

If none updated but feature/pattern changed, suggest updates.

### 5. Generate Commit Message

Follow project style (from CHANGELOG.md):

```
<Short descriptive title>

- Bullet point of change 1
- Bullet point of change 2
- Bullet point of change 3

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>
```

### 6. Present Summary and Ask for Approval

Format:
```
✅ Pre-commit checks complete:

Tests: X/X passing ✅ (or Y failing ⚠️)
Security scan: [No issues found ✅ / Found N issues ⚠️]
Documentation: [files updated]

Proposed commit message:
[generated message]

Approve this commit? (yes/no)
```

**NEVER auto-commit without user approval.**

## Two-Tier Testing Note

In Claude Code Web environment:
- ✅ Tier 1 (Automated): pytest, HTTP checks, SQL verification
- ⚠️ Tier 2 (Manual): Visual browser testing done by user on desktop

Commits from Claude Code Web should be tagged: `[Automated tests pass - needs visual verification]` if visual testing is required.

## Enforcement

This skill enforces the testing discipline from CLAUDE.md "Post-Implementation Checklist" and "Testing Discipline (MANDATORY)" sections.

All checks must pass before proceeding with commit.

## Integration with Meta-Skills

This skill works alongside the workflow detection system:

### Coordination with readathon-workflow-detector

When preparing a commit:
- **Check:** `.claude/workflow_patterns.md` for commit/push pattern counts
- **Track:** Each commit execution as a "Commit and Push" workflow occurrence
- **Suggest:** If commit/push pattern reaches threshold, detector may suggest post-commit automation skill
- **Purpose:** Identify opportunities to streamline commit → push workflow

### Coordination with readathon-context-saver

After successful commit:
- **Trigger:** readathon-context-saver to update `docs/SESSION_MEMORY.md`
- **Capture:** Commit hash, message, test results, files modified
- **Update:** Git state in session memory
- **Purpose:** Preserve commit context in case session ends before push

### Pattern Detection Opportunity

If user frequently commits and pushes, the workflow-detector may suggest creating a "readathon-quick-commit" skill that:
- Automates commit message generation (handled by this skill)
- Runs tests automatically (handled by this skill)
- Asks for approval (this skill's responsibility)
- **NEW:** Automatically pushes to remote after successful commit

This pre-commit skill focuses on commit preparation; a post-commit skill could handle the push workflow.
