---
name: Readathon Workflow Detector
description: Meta-skill that detects workflow patterns and suggests creating skills to automate them
---

# Readathon Workflow Detector

**TRIGGER:** After every user request (categorize and track patterns) and at session start (read existing patterns)

## The Meta-Skill Concept

This is a "meta-skill" - a skill designed to detect when other skills would be useful. It watches user workflow patterns and proactively suggests automation opportunities.

## Two Detection Methods

### 1. Repetition-Based Detection
Tracks when user does the same thing multiple times:
- **Expert users:** Suggest skill at 2 occurrences
- **Intermediate users:** Suggest at 3 occurrences
- **Beginner users:** Suggest at 5 occurrences
- Continue suggesting at doubled intervals (6, 12, 24...)

### 2. Immediate Complexity Detection
Recognizes complex tasks that should be automated on first request:
- Multi-step analysis (performance + security + maintainability)
- Domain expertise applications
- Complex workflows spanning multiple tools/systems
- Comprehensive evaluation requests
- Multi-phase project workflows

## Core Workflow

### At Session Start:
1. Read `.claude/workflow_patterns.md` (if exists)
2. Read all `.claude/skills/*/SKILL.md` files to know existing skills
3. Summarize to user: "Tracking [N] patterns across [M] skills"
4. Begin monitoring this session's patterns

### After Every User Request:
1. **Categorize request:**
   - Workflow (commit/push, prototyping, testing, deployment)
   - Question (how does X work, explain Y)
   - Bug Fix (fix error, troubleshoot, debug)
   - Feature (add capability, implement functionality)
   - Analysis (code review, performance, security)
   - Creative (documentation, writing, design)
   - Administrative (planning, organization, research)

2. **Check for existing skills:**
   - Read all `.claude/skills/*/SKILL.md` files
   - If pattern matches existing skill → don't suggest duplicate
   - Note existing coverage in workflow_patterns.md

3. **Semantic matching:**
   - Check if request matches any existing pattern (even with different wording)
   - Example: "commit changes" = "commit and push" = "save to git"
   - Group similar requests under same pattern

4. **Update workflow_patterns.md:**
   - Increment count for matched pattern OR create new pattern
   - Update timestamp
   - Add contextual notes

5. **Check threshold:**
   - Repetition-based: Has count reached adaptive threshold?
   - Complexity-based: Is this immediately complex enough?
   - Status check: Is pattern marked TRACK_NO_SKILL?

6. **Suggest skill if appropriate:**
   - Format depends on detection method (see below)
   - Wait for user response
   - Update status based on response

7. **Report tracking:**
   - Repetition: "✅ Tracked [pattern] (X times, threshold: [N])"
   - Complexity: "💡 Complex workflow detected: [pattern]"

### When User Responds to Suggestion:

**If "yes":**
1. Create skill directory: `.claude/skills/[skill-name]/`
2. Create SKILL.md with proper format (YAML frontmatter)
3. Update workflow_patterns.md: Status = "Skill Created"
4. Report: "✅ Created [skill-name] skill"

**If "no":**
- Continue tracking (count still increments)
- Will suggest again at next threshold (doubling)

**If "track but don't make skill":**
- Update workflow_patterns.md: Status = "TRACK_NO_SKILL"
- Never suggest again for this pattern
- Continue incrementing count for visibility

## Skill Suggestion Formats

### Repetition-Based:
```
🤖 Pattern Detected: You've asked me to [pattern] X times.

Should I create a skill to automate this workflow?

Proposed: [skill-name]
- [What it would do]
- [Why it's useful for your workflow]
- [Time/effort savings expected]
- [How it aligns with your expertise]

Create this skill? (yes/no/track but don't make skill)
```

### Complexity-Based:
```
💡 Skill Opportunity: This looks like a reusable framework.

Proposed: [skill-name]
- [What it would automate]
- [Domain expertise it would capture]
- [How it fits your technical background]
- [Consistency benefits]

Create this skill now? (yes/no/track but don't make skill)
```

## Adaptive Expertise Detection

Automatically detect user expertise level from conversation patterns:

**Beginner Indicators:**
- Simple, single-tool requests
- Basic terminology
- Step-by-step guidance needed
- Threshold: 5 occurrences

**Intermediate Indicators:**
- Multi-step processes
- Some domain terminology
- Combines multiple tools
- Threshold: 3 occurrences

**Expert Indicators:**
- Complex analysis requests
- Specialized terminology
- Advanced methodology
- Sophisticated workflows
- Threshold: 2 occurrences

**Current Project:** Detected as Expert based on:
- Advanced Python/Flask development
- Database architecture knowledge
- Git workflow sophistication
- Comprehensive testing practices

## Pattern Categories & Examples

**Development Workflows:**
- Version control (commit, push, branch, merge)
- Dependency management (pip, requirements.txt)
- Test execution (pytest, coverage)
- Build and deployment

**Analysis Workflows:**
- Code review and quality assessment
- Performance profiling
- Security vulnerability scanning
- Database optimization

**Creative Workflows:**
- Documentation generation
- Technical writing
- Design and prototyping

**Administrative Workflows:**
- Project planning
- Research and information gathering
- Decision-making frameworks

## Integration with Existing Skills

### readathon-document-reflex
When document-reflex documents decisions, workflow-detector should:
- Check if documentation represents a pattern
- Update workflow_patterns.md accordingly
- Avoid duplicate tracking

### readathon-precommit-check
When precommit-check runs tests before commit, workflow-detector should:
- Track commit/push patterns
- Suggest post-commit automation if threshold reached

### readathon-database-safety
When database-safety warns about operations, workflow-detector should:
- Track database operation patterns
- Suggest database management skills if appropriate

## Semantic Grouping Examples

**Debugging Workflow:**
- "debug this error"
- "troubleshoot the issue"
- "fix this bug"
- "investigate the problem"
→ All grouped under "Debugging Workflow"

**Code Analysis:**
- "analyze performance"
- "check security vulnerabilities"
- "review code quality"
- "assess maintainability"
→ All grouped under "Comprehensive Code Analysis"

**Git Operations:**
- "commit changes"
- "commit and push"
- "save to git"
- "push to github"
→ All grouped under "Commit and Push Workflow"

## User Context Learning

Track and learn from interactions:
- **Domain expertise:** Flask, Python, SQLite, testing
- **Technologies:** Git, pytest, Bootstrap, Jinja2
- **Goals:** Build read-a-thon tracking application
- **Behavioral patterns:** Thorough testing, documentation-focused, git discipline
- **Quality standards:** Pre-commit testing, security scanning, comprehensive coverage

This context informs:
- Which patterns are most relevant
- How to phrase skill suggestions
- What domain expertise to capture in skills
- Timing of suggestions (expert users get earlier suggestions)

## File Management

**Read these files:**
- `.claude/workflow_patterns.md` - Current pattern counts and status
- `.claude/skills/*/SKILL.md` - All existing skills (avoid duplicates)
- `docs/SESSION_MEMORY.md` - Current session context

**Write/Update:**
- `.claude/workflow_patterns.md` - Update counts, add patterns, change status
- `.claude/skills/[new-skill]/SKILL.md` - Create new skills when approved

## Error Handling

**If workflow_patterns.md doesn't exist:**
- Create it with initial structure
- Start tracking from scratch

**If skill directory already exists:**
- Don't overwrite
- Warn user and ask for different name

**If user gives ambiguous response:**
- Ask for clarification
- Options: yes/no/track but don't make skill

## Reporting

Keep user informed but not overwhelmed:
- Silent tracking for counts 1-2 (below threshold)
- Report when threshold approaches
- Always report after updating workflow_patterns.md
- Summarize at session start if patterns exist

## Example Session Flow

```
User: "commit and push these changes"
Claude: ✅ Tracked commit/push (1 time, threshold: 2)
[Executes commit and push]

User: "commit and push"
Claude: 🤖 Pattern Detected: You've asked me to commit/push 2 times.
Should I create a skill to automate this workflow?
Proposed: readathon-quick-commit
- Generates commit message from changes
- Asks for approval
- Commits and pushes to main
Create this skill? (yes/no/track but don't make skill)

User: "yes"
Claude: ✅ Created readathon-quick-commit skill
[Creates skill files]
[Updates workflow_patterns.md]
```

## Benefits

**For users:**
- Automation opportunities discovered automatically
- No need to identify patterns manually
- Skills aligned with actual workflow needs
- Learning system adapts to expertise level

**For the project:**
- Growing library of project-specific skills
- Documented workflow patterns
- Shared knowledge across sessions
- Consistent automation approaches
