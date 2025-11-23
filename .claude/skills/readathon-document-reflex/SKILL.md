---
name: Readathon Document Reflex
description: Automatically document design decisions and patterns immediately when discovered in the readathon project
---

# Readathon Document Reflex

**TRIGGER:** When design decisions are made, patterns discovered, or rules defined.

## The Documentation Problem

From CLAUDE.md "Immediate Documentation (REFLEX ACTION)":

> Context is lost during conversation compaction. Important decisions/rules are forgotten if not documented immediately.

**Solution:** Document important information **immediately** when discovered, not "later" or "at the end."

## Automatic Documentation Triggers

### Trigger 1: Data Source Decision

**When:** User asks or decision is made about which table/column to use

**Examples:**
- "Should fundraising be capped or uncapped?"
- "Which table has the reading minutes?"
- "Do we use Daily_Logs or Reader_Cumulative?"

**Action:** Immediately update `md/RULES.md`

**Format:**
```markdown
## [Section: Data Source Rules / Calculation Rules]

**[Metric Name]:**
- Source: [table_name].[column_name]
- Reason: [why this source]
- Notes: [capped/uncapped, calculations, etc.]

Last Updated: [YYYY-MM-DD]
```

**Report:** "✅ Documented in md/RULES.md lines [X-Y]: [summary]"

### Trigger 2: UI Pattern Discovery

**When:** A consistent pattern is noticed across pages

**Examples:**
- "I notice all pages use the same filter dropdown pattern"
- "Team badges are always rounded rectangles with team colors"
- "Winner highlights use gold for school-wide, silver for grade/team"

**Action:** Immediately update `md/UI_PATTERNS.md`

**Format:**
```markdown
## [Pattern Name]

**Description:** [what the pattern is]

**Used in:** [list of pages/files]

**Implementation:**
```html
[code example]
```

**Colors/Styles:**
- [specific hex codes, CSS classes, etc.]

Last Updated: [YYYY-MM-DD]
```

**Report:** "✅ Added [pattern] to md/UI_PATTERNS.md lines [X-Y]"

### Trigger 3: Feature Design Decision

**When:** Specific implementation choice is made for a feature

**Examples:**
- "Students page should use capped minutes"
- "Detail view shows daily breakdown with charts"
- "Banner metrics appear in this specific order"

**Action:** Update appropriate feature design doc: `docs/STUDENTS_PAGE_DESIGN.md`, `docs/features/feature-XX.md`

**Format:**
```markdown
## Design Decisions

**[Decision Topic]:**
- Decision: [what was decided]
- Rationale: [why this choice]
- Impact: [what this affects]
- Date: [YYYY-MM-DD]
```

**Report:** "✅ Documented in docs/[feature].md lines [X-Y]: [summary]"

### Trigger 4: Calculation Rule

**When:** Formula or calculation method is defined

**Examples:**
- "Participation rate = (students with minutes / total students) * 100"
- "Reading goals are grade-specific from Grade_Rules table"
- "Team totals use capped minutes, max 120 per day"

**Action:** Update `md/RULES.md` in appropriate section

**Format:**
```markdown
## Calculation Rules

**[Metric Name]:**
- Formula: [mathematical formula or SQL logic]
- Special cases: [edge cases, caps, rounding]
- Example: [sample calculation]

Last Updated: [YYYY-MM-DD]
```

**Report:** "✅ Documented calculation in md/RULES.md lines [X-Y]: [summary]"

### Trigger 5: Open Question / TBD Item

**When:** Uncertainty identified that needs user input later

**Examples:**
- "Should export be CSV or Excel?"
- "TBD: Add charts or keep table-only?"
- "Need to decide: Individual prizes or team only?"

**Action:** Add to feature design doc with TBD marker

**Format:**
```markdown
## Open Questions

- **[Question]:** [description of uncertainty]
  - Options: [list alternatives]
  - Status: TBD
  - Added: [YYYY-MM-DD]
```

**Report:** "✅ Added TBD item to docs/[feature].md for later resolution"

## Documentation Workflow

1. **Detect Trigger:** Recognize when decision/pattern occurs
2. **Choose File:** Determine which documentation file to update
3. **Edit Immediately:** Use Edit tool to add/update content
4. **Update Date:** Change "Last Updated" timestamp
5. **Report Location:** Tell user exactly where documented (file + line numbers)

## Key Principle

**NEVER say:** "I'll document this later" or "We should add this to docs"

**ALWAYS do:** Edit the documentation file immediately, then report what was added

## Files to Update (Quick Reference)

| Decision Type | File |
|---------------|------|
| Data source (which table/column) | `md/RULES.md` |
| Calculation formula | `md/RULES.md` |
| UI pattern / styling | `md/UI_PATTERNS.md` |
| Team colors, winner highlights | `md/RULES.md` or `md/UI_PATTERNS.md` |
| Feature design choice | `docs/[FEATURE]_DESIGN.md` |
| Report-specific logic | `docs/features/feature-XX.md` |
| New pattern across pages | `md/UI_PATTERNS.md` |
| Open question / TBD | Feature design doc |

## Compaction Reality

**Conversation compaction happens transparently** - there's no warning, no pre-compaction hook.

By documenting **immediately as reflex action**, we minimize context loss and ensure decisions persist across sessions.

**Best Practice:** When uncertain whether to document, **ask user** then document immediately after confirmation.

## Integration with Meta-Skills

This skill is part of the multi-layer context preservation system:

### Coordination with readathon-context-saver

When this skill documents a decision:
- **Also trigger:** readathon-context-saver to update `docs/SESSION_MEMORY.md`
- **Purpose:** Permanent docs (this skill) + session state (context-saver)
- **Avoid:** Duplicate work - coordinate the update
- **Division:**
  - document-reflex → permanent project documentation
  - context-saver → temporary session state

### Coordination with readathon-workflow-detector

When documenting patterns/decisions:
- **Check:** Does this represent a workflow pattern worth tracking?
- **If yes:** Update `.claude/workflow_patterns.md` as well
- **Examples:**
  - Documenting "prototype workflow" pattern → track as workflow
  - Documenting data source decision → just documentation (not workflow)
  - Documenting testing approach → could be workflow pattern

### Layer in Context Preservation Strategy

This skill is **Layer 1** in the multi-layer defense:
- **Layer 1 (this skill):** Real-time docs - immediate
- **Layer 2:** Session memory - moderate frequency
- **Layer 3:** Workflow patterns - every occurrence
- **Layer 4:** Quick start guide - session boundaries
