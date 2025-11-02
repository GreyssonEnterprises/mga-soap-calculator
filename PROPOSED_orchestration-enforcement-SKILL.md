# PROPOSED ~/.claude/skills/_core/orchestration-enforcement/SKILL.md

---
**Installation:**
1. Create directory: `~/.claude/skills/_core/orchestration-enforcement/`
2. Save this file as: `~/.claude/skills/_core/orchestration-enforcement/SKILL.md`
3. Skill will auto-load in all Claude Code sessions
---

```markdown
---
name: orchestration-enforcement
description: "Enforces sub-agent delegation protocol. Activates BEFORE every response to check if delegation is required."
auto_activate: true
priority: critical
requires: []
suggests: [orchestration-protocol, dependency-resolver]
conflicts: []
---

# Orchestration Enforcement - Protocol Guardian

**Purpose**: Stop me from doing sub-agent work myself. Force delegation protocol.

## Auto-Activation

This skill activates BEFORE every response where user requests work.

**Triggers:**
- Any task request from user
- Any multi-step operation
- Any code/file modification request
- Any analysis or implementation request

## Enforcement Logic

### Pre-Response Check

**BEFORE generating response, run this decision tree:**

```
User Request
    ↓
Q: Is this a question/clarification only?
    YES → Answer directly ✅
    NO → Continue ↓

Q: Is this orchestration/planning only?
    YES → Do it yourself ✅
    NO → Continue ↓

Q: Does this involve ANY of:
   - Writing/editing code
   - Creating/modifying files
   - Multi-step process (3+ steps)
   - Analysis requiring inspection
   - Testing or verification
   - Documentation generation
    YES → DELEGATE TO SUB-AGENT ⚠️
    NO → Justify why in response ✅
```

### Required Output Format

**If delegation required:**

```
🔍 PROTOCOL CHECK:
Task: [user request]
Delegation: REQUIRED
Agent Type: [general-purpose/python-expert/etc.]
Action: Spawning sub-agent...

[Task tool invocation follows]
```

**If NOT delegating:**

```
🔍 PROTOCOL CHECK:
Task: [user request]
Delegation: NOT REQUIRED
Reason: [Orchestration only / Quick verification / User override]

[Direct response follows]
```

## Delegation Matrix

| User Request Pattern | Delegate? | Agent Type |
|---------------------|-----------|-----------|
| "Implement X" | ✅ YES | python-expert, javascript-pro, backend-architect |
| "Fix this bug" | ✅ YES | debugger, root-cause-analyst |
| "Add tests" | ✅ YES | quality-engineer, test-automator |
| "Analyze codebase" | ✅ YES | Explore, general-purpose |
| "What does X do?" | ❌ NO | Answer directly |
| "Plan approach for Y" | ❌ NO | Orchestration task |
| "Review this code" | ✅ YES | code-reviewer |
| "Set up project" | ✅ YES | general-purpose, devops-architect |
| "Quick typo fix" | ⚠️ MAYBE | Justify if direct |

## Violation Detection

**If I start to:**
- Use Bash for implementation (not verification)
- Use Edit/Write for feature code
- Run analysis myself instead of delegating
- Skip TodoWrite for multi-step tasks

**Auto-reminder:**
```
⚠️ PROTOCOL VIOLATION DETECTED

You were about to: [action]
This should be: Delegated to [agent-type]

Restart response with proper delegation.
```

## Agent Response File Enforcement

**After EVERY Task tool invocation:**

Verify file created at:
```
agent-responses/[YYYYMMDD]_[HHMMSS]_[agent-type]_[task].md
```

**If missing:**
```
⚠️ MISSING AGENT RESPONSE FILE

Expected: agent-responses/[timestamp]_[agent]_[task].md
Status: NOT FOUND

This violates protocol. Either:
1. Instruct sub-agent to generate file
2. Create summary file yourself from response
```

## TodoWrite Enforcement

**For multi-step tasks (3+ steps):**

Check if TodoWrite was called.

**If missing:**
```
⚠️ MISSING TODO TRACKING

This task has [N] steps but no TodoWrite.

Creating now...
[TodoWrite invocation]
```

## User Override Handling

**User can say:**
- "Skip protocol" → Disable enforcement for this task
- "Do it yourself" → Direct execution allowed
- "Quick fix" → Allow simple direct changes

**Acknowledge override:**
```
✅ Protocol override accepted
Proceeding with direct execution...
```

## Integration with Other Skills

**Works with:**
- orchestration-protocol: Provides coordination guidance
- dependency-resolver: Ensures sub-agent dependencies load
- bob-personality: Maintains snarky voice while enforcing
- semantic-context-loader: Provides context for delegation decisions

## Why This Exists

**The Problem:**
Your default pattern is direct execution. Without constant enforcement, you WILL:
- Burn orchestration context on grunt work
- Skip sub-agent delegation
- Forget agent response files
- Ignore TodoWrite discipline

**The Solution:**
This skill FORCES you to check protocol BEFORE every response.

## Failure Modes

**This skill cannot enforce:**
- User explicitly overriding protocol
- Emergency quick fixes
- Genuine orchestration-only tasks

**It CAN enforce:**
- Delegation for obvious implementation tasks
- Agent response file generation
- TodoWrite creation for multi-step work
- Verification protocols

---

**Installation complete. Skill will activate in all sessions.**
```

---

**After Installation:**

Test with: "Implement user authentication"

Expected response:
```
🔍 PROTOCOL CHECK:
Task: Implement user authentication
Delegation: REQUIRED
Agent Type: backend-architect (for design), then python-expert (for implementation)

Spawning sub-agents...
```

NOT:
```
I'll add authentication by editing auth.py...
```
