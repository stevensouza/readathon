# Generic Prompts for Workflow Detection & Context Preservation

**Purpose:** These are generalized prompts that can be shared with others (e.g., Reddit posts) or used in different projects. They don't contain project-specific details.

**Last Updated:** 2025-11-23

---

## Prompt 1: Workflow Pattern Detection & Skill Suggestion System

```markdown
# Workflow Pattern Detection & Skill Suggestion System

Implement a comprehensive workflow pattern detection system that learns from user behavior patterns and suggests automation opportunities through both repetition tracking and intelligent single-request analysis. The system dynamically adapts to user expertise and maintains awareness of user context, patterns, goals, and objectives to generate relevant skills.

## CORE REQUIREMENTS:

### 1. CREATE TRACKING FILE: `.claude/workflow_patterns.md`
- Track every workflow pattern used (commit/push, prototyping, testing, analysis, etc.)
- Increment count each time the same workflow is requested
- Categorize requests: Workflow, Question, Bug Fix, Feature, Analysis, Creative, Administrative
- Include: Pattern name, count, threshold, status, notes, complexity score, domain context
- Maintain user context profile including expertise areas, goals, and behavioral patterns

### 2. DUAL DETECTION SYSTEM:

**A. REPETITION-BASED DETECTION:**
- Adaptive thresholds based on detected user expertise level
- Allow override: If user says "track but don't make skill", mark as TRACK_NO_SKILL and never suggest again

**B. IMMEDIATE COMPLEXITY DETECTION:**
Suggest skills immediately (count = 1) when detecting:
- Multi-step analysis requests combining 3+ evaluation criteria
- Tasks requiring domain expertise application
- Complex workflows spanning multiple tools/files/systems
- Comprehensive evaluation or review requests
- Tasks involving specialized knowledge patterns
- Multi-phase project workflows

### 3. ENHANCED PATTERN RECOGNITION:

**Semantic Grouping:**
- Group similar requests under broader patterns
- Example: "debug X", "troubleshoot Y", "fix Z" → "Debugging Workflow"
- "analyze performance", "check security", "review code quality" → "Comprehensive Code Analysis"

**Dynamic Context Awareness:**
- Learn user's domain expertise from conversation history and stated background
- Recognize domain-specific triggers based on user's professional context
- Track technologies, tools, and methodologies frequently mentioned
- Identify recurring project types and structures
- Note specialized terminology and frameworks user employs
- Understand user's goals and objectives to align skill suggestions
- Recognize user's behavioral patterns and preferred approaches

### 4. SKILL SUGGESTION FORMAT:

**For Repetition-Based:**
```
🤖 Pattern Detected: You've asked me to [pattern] X times.
Should I create a skill to automate this workflow?
Proposed: [skill-name]
- [What it would do]
- [Why it's useful for your workflow and goals]
- [Time/effort savings expected]
- [How it aligns with your expertise/patterns]
Create this skill? (yes/no)
```

**For Immediate Complexity-Based:**
```
💡 Skill Opportunity: This looks like a reusable framework that could benefit from automation.
Proposed: [skill-name]
- [What it would automate]
- [Domain expertise it would capture]
- [How it fits your technical background and objectives]
- [Consistency benefits for your workflow patterns]
Create this skill now? (yes/no)
```

### 5. ADAPTIVE PATTERN EXAMPLES:

**Development Workflows:**
- Version control operations (commit, push, branching strategies)
- Dependency management and updates
- Performance profiling and optimization
- Security vulnerability scanning
- Code review and quality assessment processes
- Test suite execution and analysis
- Build and deployment automation

**Analysis Workflows:**
- Comprehensive codebase evaluation (performance/security/maintainability/architecture)
- System monitoring setup and configuration
- Database optimization and analysis
- Application health checks and diagnostics
- Documentation review and generation

**Creative/Communication Workflows:**
- Content editing with consistent style guidelines
- Technical documentation generation
- Presentation or report creation
- Review processes for written content

**Administrative Workflows:**
- Project planning and organization
- Meeting preparation and follow-up
- Research and information gathering
- Decision-making frameworks

### 6. FILE FORMAT:
```markdown
# Workflow Pattern Tracking
Last Updated: [timestamp]
User Domain Context: [Learned from interactions]
User Goals/Objectives: [Identified from conversations]
User Expertise Level: [Beginner/Intermediate/Expert - Auto-detected]
User Behavioral Patterns: [Preferred approaches, methodologies]

## [Pattern Name] (Count: X, Status: Tracking/TRACK_NO_SKILL/Skill Created, Complexity: High/Medium/Low)
Pattern: [Description]
Detection Method: Repetition/Complexity/Both
Threshold: [Adaptive based on expertise] (suggest skill) OR Immediate (complex task)
Next Suggestion: At count [N] OR N/A (immediate)
Domain Context: [User's relevant expertise area]
Technologies/Tools Involved: [List]
Frequency: [Daily/Weekly/Monthly/Project-based]
Impact: [Time saved/Consistency gained/Quality improvement]
Goal Alignment: [How this supports user's objectives]
Notes: [Context and reasoning]
```

### 7. CONTEXTUAL SKILL DETECTION TRIGGERS:

**Immediate Suggestion Triggers:**
- Requests combining multiple evaluation criteria
- Multi-step technical analysis workflows
- Domain expertise applications (based on learned user context)
- Comprehensive project or system evaluation requests
- Style-consistent creative or technical feedback requests
- Complex decision-making processes
- Multi-tool workflow coordination

**Dynamic Domain Recognition:**
- Learn user's expertise areas from conversation patterns
- Identify specialized knowledge domains user frequently references
- Recognize when user applies professional methodology
- Detect recurring technical stacks or frameworks
- Note consistent quality standards or evaluation criteria
- Understand user's current projects and long-term goals

### 8. UPDATE RULES:
- Increment count every time pattern is used
- Update timestamp and add contextual notes
- Learn and update user domain context, goals, and patterns from each interaction
- For repetition-based: Report "✅ Tracked [pattern] (X times, threshold: [adaptive])"
- For complexity-based: Report "💡 Complex workflow detected: [pattern]"
- At session start, read file to know existing patterns and learned user context
- Group semantically similar requests under broader pattern categories
- Adapt detection sensitivity based on user's expertise level and objectives

### 9. SEMANTIC ANALYSIS:
- Detect variations of same underlying task using different terminology
- Recognize when different phrasings represent same workflow intent
- Identify complex workflows that span multiple requests within sessions
- Track workflow evolution (simple request → complex systematic approach)
- Learn user's preferred terminology and methodology patterns

### 10. LEARNING SYSTEM:
- Build understanding of user's professional background from conversations
- Identify recurring themes, technologies, and methodologies
- Recognize user's quality standards and evaluation criteria
- Adapt suggestion timing based on user's workflow complexity preferences
- Learn from user feedback on skill suggestions to improve future detection
- Maintain awareness of user's current projects and strategic objectives
- Track user's evolving expertise and adjust recommendations accordingly

### 11. ADAPTIVE THRESHOLD SYSTEM:
- **Beginner Detection:** Simple, single-tool requests, basic terminology
  - Higher repetition threshold (5 occurrences before suggestion)
  - Focus on fundamental workflow automation
- **Intermediate Detection:** Multi-step processes, some domain terminology
  - Standard threshold (3 occurrences)
  - Balance between automation and learning opportunities
- **Expert Detection:** Complex analysis, specialized terminology, advanced methodology
  - Lower repetition threshold (2 occurrences)
  - Immediate suggestions for sophisticated workflows
- **Dynamic Adjustment:** Modify thresholds as user expertise becomes apparent through interactions
- **Context-Aware Timing:** Consider user's current goals and project phases when suggesting skills

## INITIALIZATION:
Start tracking now. Create the workflow_patterns.md file and begin monitoring all workflow patterns using both detection methods. Learn user context dynamically from interactions including expertise level, goals, behavioral patterns, and objectives. Adapt detection criteria accordingly and maintain ongoing awareness of who the user is, their patterns, and what they're trying to accomplish. Prioritize immediate suggestions for complex analysis tasks while building repetition history for simpler workflows. Always consider how proposed skills align with the user's broader objectives and working style.
```

---

## Prompt 2: Aggressive Context Preservation System

```markdown
# Context Preservation System

Implement an aggressive context preservation system to prevent context loss during long sessions and conversation compaction.

## THE PROBLEM:
Long sessions → context loss → compaction → re-explain things → longer sessions → more compaction (spiral of doom)

## THE SOLUTION:
Multi-layer context saving with time + event triggers

## REQUIREMENTS:

### 1. CREATE SESSION MEMORY FILE: `docs/SESSION_MEMORY.md`

**Structure:**
```markdown
# Session Memory - Live Updates
Last Updated: [timestamp] | Auto-save: Every 5-10 min + events

## Current Work
[What we're working on right now]

## Key Decisions This Session
1. [Decision with timestamp]

## Important Context
- [Facts that must survive compaction]

## Workflow Patterns This Session
- [Pattern]: Nx

## Git State
- Last commit: [hash] [message]
- Unpushed commits: [count]
- Branch: [name]

## Open Questions
[TBD items]

## Next Session Start Here
[Quick resume point if session ends]
```

### 2. UPDATE TRIGGERS (Moderate Balance):

**Event-based:** After important decisions, milestones, git operations
**Time-based:** Every 5-10 minutes (in addition to events, not instead of)

### 3. TIME-BASED LOGIC:
- Set internal timer for 5-10 minutes
- When timer expires: Check if session memory needs update
- Update file and reset timer
- This ensures no more than 10 min of context can be lost

### 4. EVENT-BASED LOGIC (What counts as "important"):
- Design decisions made
- Architecture choices
- Data source selections
- Calculation rules defined
- Files created/modified
- Git commits/pushes
- Bug fixes completed
- Tests created
- Milestones reached

### 5. CONTEXT LAYERS (All must work together):
- Layer 1: Real-time docs (RULES.md, UI_PATTERNS.md) - immediate
- Layer 2: Session memory (this file) - moderate frequency
- Layer 3: Quick start guide (QUICK_START_NEXT_SESSION.md) - session boundaries
- Layer 4: Workflow patterns (workflow_patterns.md) - every occurrence

### 6. REPORT FORMAT:
After each save: "✅ Context saved to SESSION_MEMORY.md [HH:MM:SS]"

### 7. SESSION START BEHAVIOR:
At start of every session:
- Read SESSION_MEMORY.md first
- Summarize what we were working on
- Offer to continue or start fresh

### 8. BALANCE:
- NOT every conversation line (too noisy)
- NOT just at session end (too risky)
- MODERATE: Milestones + 5-10 min intervals

## INITIALIZATION:
Start preserving context now. Create the file and begin auto-saving every 5-10 minutes + after important events.
```

---

## Usage Instructions

**For Prompt 1 (Workflow Detection):**
- Copy and paste at start of any session where you want workflow tracking
- Claude will create `.claude/workflow_patterns.md` and start monitoring
- Works independently - doesn't require Prompt 2

**For Prompt 2 (Context Preservation):**
- Copy and paste at start of any long session where context loss is a risk
- Claude will create `docs/SESSION_MEMORY.md` and auto-save throughout
- Works independently - doesn't require Prompt 1

**For Both Together:**
- Use both prompts in sequence for complete system
- They complement each other but can work separately
- Workflow tracking helps identify automation opportunities
- Context preservation prevents losing progress

**Best Practice:**
- Add these to a project's CLAUDE.md or README so every session uses them
- Can reference them: "Use the workflow detection system from CLAUDE.md"

---

## Reddit Post (Concise Version)

**Title:** "Meta-Skill: Teaching Claude to Detect When You Need Custom Skills"

**Body:**

I created a "meta-skill" that watches my workflow patterns and suggests when other skills would be useful. It works two ways: tracks repetitive tasks (ask for code reviews 3+ times → suggests a Code Review skill) and immediately recognizes complex requests that should be automated (ask for "performance + security analysis" once → suggests a Comprehensive Analysis skill).

**Key features:**
- Learns your expertise level and adjusts timing
- Understands your domain context
- Groups similar requests (debugging, troubleshooting → Debugging workflow)
- Adapts to your goals and working style

The ironic part: it's a skill designed to create other skills by watching how you work.

[Prompts attached above]

Anyone else experimenting with meta-automation like this?
