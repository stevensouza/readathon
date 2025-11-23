# Workflow Pattern Tracking

**Last Updated:** 2025-11-23

**User Domain Context:** (Learning from interactions)
**User Goals/Objectives:** (Identified from conversations)
**User Expertise Level:** Expert (Auto-detected based on technical depth and domain knowledge)
**User Behavioral Patterns:** (Preferred approaches, methodologies)

---

## How This Works

This file tracks repetitive workflow patterns and suggests creating Claude skills to automate them. It uses two detection methods:

1. **Repetition-Based:** Tracks when you do the same thing multiple times (threshold: 2-5 based on expertise)
2. **Complexity-Based:** Immediately recognizes complex tasks that should be automated (suggests at count 1)

**Adaptive Thresholds:**
- Beginner: 5 occurrences before suggestion
- Intermediate: 3 occurrences
- Expert: 2 occurrences (current level)

**Override:** Say "track but don't make skill" to mark pattern as TRACK_NO_SKILL

---

## Existing Skills (Don't Suggest These)

- `readathon-precommit-check` - Pre-commit testing and validation
- `readathon-database-safety` - Database operation protection
- `readathon-document-reflex` - Immediate documentation of decisions
- `readathon-workflow-detector` - This pattern detection system
- `readathon-context-saver` - Session context preservation

---

## Tracked Patterns

### Commit and Push (Count: 1, Status: Tracking, Complexity: Low)
**Pattern:** User requests to commit and push changes to GitHub
**Detection Method:** Repetition
**Threshold:** 2 (expert level)
**Next Suggestion:** At count 2
**Domain Context:** Development workflow
**Technologies/Tools Involved:** git, GitHub
**Frequency:** Multiple times per session
**Impact:** Time saved on repetitive git operations
**Goal Alignment:** Streamline development workflow
**Notes:** Pre-commit skill handles commit prep, but no post-commit push automation yet

---

## Pattern Categories

**Workflow:** Development, deployment, version control operations
**Question:** How does X work, explain Y
**Bug Fix:** Fix error, troubleshoot issue, debug problem
**Feature:** Add new capability, implement functionality
**Analysis:** Code review, performance analysis, security audit
**Creative:** Documentation, writing, design
**Administrative:** Project planning, organization, research

---

## Session Statistics

**This Session:**
- Patterns tracked: 1
- Skills suggested: 0
- Skills created: 0
- User overrides: 0

**All Time:**
- Total patterns: 1
- Active skills: 5
- TRACK_NO_SKILL patterns: 0
