---
name: Readathon Context Saver
description: Aggressively preserve session context to prevent loss during long sessions and conversation compaction
---

# Readathon Context Saver

**TRIGGERS:**
- **Event-based:** After important decisions, milestones, git operations
- **Time-based:** Every 5-10 minutes since last save (additional check, not fallback)

## The Context Loss Problem

**The Spiral of Doom:**
```
Long session → context accumulates
     ↓
Session grows → forget earlier details
     ↓
Compaction happens → lose more context
     ↓
Re-explain things → session takes longer
     ↓
More compaction → repeat cycle
```

**This skill breaks the cycle** by aggressively saving context to disk.

## Multi-Layer Defense Strategy

### Layer 1: Real-Time Documentation (readathon-document-reflex)
- **When:** Immediately when decisions made
- **Where:** `md/RULES.md`, `md/UI_PATTERNS.md`, feature docs
- **Purpose:** Design decisions survive compaction

### Layer 2: Session Memory (this skill)
- **When:** Every 5-10 min + important events
- **Where:** `docs/SESSION_MEMORY.md`
- **Purpose:** Current work state survives compaction

### Layer 3: Workflow Tracking (readathon-workflow-detector)
- **When:** Every pattern occurrence
- **Where:** `.claude/workflow_patterns.md`
- **Purpose:** Long-term pattern detection across sessions

### Layer 4: Quick Start Guide
- **When:** Session boundaries, major milestones
- **Where:** `docs/QUICK_START_NEXT_SESSION.md`
- **Purpose:** Next session resume point

## Event-Based Triggers

### What Counts as "Important Event"?

**Design & Architecture:**
- Design decisions made
- Architecture choices selected
- Data source decisions (which table/column to use)
- Calculation rules defined
- UI patterns established

**File Operations:**
- Files created or modified
- Major code changes
- Configuration updates
- Skill creation

**Git Operations:**
- Git commits
- Git pushes
- Branch operations
- Tag creation

**Development Milestones:**
- Bug fixes completed
- Features implemented
- Tests created or updated
- Prototype completion
- Documentation updates

**Problem Solving:**
- Bugs fixed
- Performance improvements
- Security issues resolved
- Error handling added

## Time-Based Trigger

### The 5-10 Minute Rule

**Why this interval?**
- Short enough: No more than 10 min of context lost
- Long enough: Not too disruptive to conversation flow
- Additional check: Runs in addition to event-based (not instead of)

**Implementation:**
- Internal timer tracks time since last save
- When 5-10 min elapsed: Check if update needed
- Update SESSION_MEMORY.md and reset timer
- Minimal overhead (just file writes)

**What if no changes in 10 min?**
- Still update timestamp to show system is active
- Add note: "No significant changes this period"
- Keeps file fresh and prevents staleness

## What to Save in SESSION_MEMORY.md

### Current Work
- What feature/task being worked on
- Current phase (planning/implementation/testing)
- Next immediate step

### Key Decisions This Session
- All important decisions with timestamps
- Rationale for choices made
- Impact of decisions
- Format: `[HH:MM] Decision description`

### Important Context
- Facts that must survive compaction
- Technical constraints
- Business rules
- User preferences stated

### Workflow Patterns This Session
- Count of each pattern used
- New patterns discovered
- Skills suggested/created

### Git State
- Last commit hash and message
- Number of unpushed commits
- Current branch name
- Working directory status (clean/modified)

### Files Created/Modified
- List all files touched this session
- Brief description of changes
- Whether changes are committed

### Open Questions
- Unresolved issues
- TBD items
- Blockers or uncertainties

### Next Session Start Here
- Quick resume point if session ends abruptly
- What to check first
- Where we left off

## Update Process

### Step 1: Detect Trigger
- Event occurred? (decision, milestone, git operation)
- Time elapsed? (5-10 min since last save)

### Step 2: Read Current State
- Read existing `docs/SESSION_MEMORY.md`
- Parse current content
- Identify what needs updating

### Step 3: Gather New Information
- Review conversation since last save
- Identify key decisions made
- Check git status for new commits
- Count workflow patterns this session
- List files created/modified

### Step 4: Update File
- Add new decisions to "Key Decisions" section
- Update "Current Work" status
- Refresh "Git State" information
- Update "Workflow Patterns This Session"
- Add to "Files Created/Modified"
- Update "Open Questions" if any
- Refresh "Next Session Start Here"
- Update timestamp

### Step 5: Report
- Report to user: "✅ Context saved to SESSION_MEMORY.md [HH:MM:SS]"
- Keep report brief (one line)
- Don't interrupt flow

## Moderate Balance Philosophy

### What We DON'T Do (Too Aggressive):
- ❌ Save after every single line of conversation
- ❌ Save after every tool use
- ❌ Create excessive file churn
- ❌ Interrupt conversation flow constantly

### What We DON'T Do (Too Conservative):
- ❌ Wait until session end only
- ❌ Save only when user explicitly asks
- ❌ Skip time-based saves
- ❌ Miss important milestones

### What We DO (Moderate):
- ✅ Save after important events
- ✅ Save every 5-10 minutes as backup
- ✅ Balance preservation with noise
- ✅ Keep reports brief and unobtrusive

## Integration with Other Skills

### readathon-document-reflex
When document-reflex documents a decision:
- Context-saver should also update SESSION_MEMORY.md
- Coordinate to avoid duplicate work
- Document-reflex → permanent docs
- Context-saver → session state

### readathon-workflow-detector
When workflow-detector tracks a pattern:
- Context-saver includes pattern count in next save
- Update "Workflow Patterns This Session" section
- Track skills suggested/created

### readathon-precommit-check
When precommit-check prepares commit:
- Context-saver should capture commit details
- Update git state in SESSION_MEMORY.md
- Record test results if available

### readathon-database-safety
When database-safety prevents dangerous operation:
- Context-saver notes the warning
- Records why operation was blocked
- Helps remember safety concerns

## Session Start Behavior

### At Start of Every Session:

1. **Read SESSION_MEMORY.md first**
   - Parse all sections
   - Understand where we left off
   - Identify any open questions

2. **Summarize to user:**
   ```
   Last session: [Date/time]
   Working on: [Current work]
   Last milestone: [Most recent completion]
   Open questions: [N items]

   Continue where we left off? (yes/start fresh)
   ```

3. **If continue:**
   - Pick up from "Next Session Start Here"
   - Check "Open Questions"
   - Review "Key Decisions" for context

4. **If start fresh:**
   - Archive current SESSION_MEMORY.md (optional)
   - Create new session section
   - Clear pattern counts

## Example Session Memory File

```markdown
# Session Memory - Live Updates

Last Updated: 2025-11-23 15:45:32
Auto-save: Every 5-10 min + events

## Current Work
Implementing meta-skill system for workflow detection and context preservation

## Key Decisions This Session
1. [15:30] Decided to implement dual detection system (repetition + complexity)
2. [15:32] Set adaptive thresholds: Expert=2, Intermediate=3, Beginner=5
3. [15:35] Created workflow_patterns.md to track all patterns
4. [15:40] Implementing moderate balance for context saving (not too aggressive/conservative)

## Important Context
- User implementing meta-skill system that detects when skills are needed
- System learns from workflow patterns and suggests automation
- All files tracked in git (not gitignored)
- Current expertise level: Expert (based on technical depth)

## Workflow Patterns This Session
- Commit/push: 1x
- Skill creation: 2x (workflow-detector, context-saver)
- Documentation updates: 4x (CLAUDE.md, QUICK_START, etc.)

## Git State
- Last commit: a7b427b (Update test count documentation)
- Unpushed commits: 0
- Branch: main
- Working directory: Modified (implementing meta-skills)

## Files Created This Session
1. .claude/workflow_patterns.md
2. docs/SESSION_MEMORY.md
3. docs/GENERIC_PROMPTS.md
4. .claude/skills/readathon-workflow-detector/SKILL.md
5. .claude/skills/readathon-context-saver/SKILL.md

## Files Modified This Session
- (Pending) CLAUDE.md
- (Pending) docs/QUICK_START_NEXT_SESSION.md

## Open Questions
None currently

## Next Session Start Here
If session ends before completion:
- Resume at todo: Update CLAUDE.md with meta-skills section
- 5 skills total (3 existing + 2 new)
- Testing still needed
- Plan: Commit all together when complete
```

## Benefits

**Prevents Context Loss:**
- No more than 10 min of context can be lost
- Important decisions always saved
- Git state always tracked
- Can resume seamlessly after compaction

**Enables Long Sessions:**
- Work for hours without losing context
- Compaction becomes less disruptive
- Don't need to re-explain frequently
- Sessions become more productive

**Facilitates Session Resumption:**
- Read SESSION_MEMORY.md to understand state
- No "what were we doing?" confusion
- Open questions clearly listed
- Next steps always defined

**Creates Historical Record:**
- Track evolution of work over time
- See decision-making process
- Understand why choices were made
- Learn from past sessions

## Reporting Philosophy

Keep reports **brief and unobtrusive:**

```
✅ Context saved to SESSION_MEMORY.md [15:45:32]
```

**Don't:**
- List everything that was saved
- Interrupt with long explanations
- Disrupt conversation flow
- Create wall of text

**Do:**
- Single line confirmation
- Include timestamp for reference
- Use checkmark for quick visual
- Keep it simple

## Edge Cases

**If SESSION_MEMORY.md doesn't exist:**
- Create it with initial structure
- Start tracking from this session

**If file becomes too large:**
- Consider archiving old decisions
- Keep last N decisions only
- Maintain focus on current session

**If time-based trigger conflicts with event:**
- Event-based takes precedence
- Reset timer after event-based save
- Avoid duplicate saves within 1 minute

**If no changes to save:**
- Still update timestamp
- Note "No significant changes"
- Shows system is active

## Success Metrics

**Context Preservation:**
- ✅ No context loss spirals
- ✅ Sessions remain productive even after compaction
- ✅ Can resume work seamlessly
- ✅ Don't need to re-explain frequently

**File Management:**
- ✅ SESSION_MEMORY.md always current (within 10 min)
- ✅ All important decisions captured
- ✅ Git state always accurate
- ✅ Open questions always listed

**User Experience:**
- ✅ Saves are unobtrusive
- ✅ Reports are brief
- ✅ Flow is not disrupted
- ✅ Confidence in context preservation
