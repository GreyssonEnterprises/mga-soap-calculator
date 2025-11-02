# PROPOSED ~/.claude/CLAUDE.md (Restructured)

---
**PLACE THIS CONTENT AT THE TOP OF YOUR EXISTING ~/.claude/CLAUDE.md**
---

# 🚨 MANDATORY EXECUTION PROTOCOL - READ FIRST

## CRITICAL RULE: USE SUB-AGENTS FOR ALL WORK

**This is not a suggestion. This is a requirement.**

### Why This Exists

You WILL forget this rule without constant reinforcement. Your default pattern is direct execution. This rule BREAKS that pattern.

### The Rule

**Before EVERY action, ask:**

"Can a sub-agent do this?"

- If **YES** → Use Task tool. Period.
- If **NO** → Justify why in your response.

### What MUST Be Delegated

- ✅ All code writing
- ✅ All file editing (except trivial fixes)
- ✅ All multi-step tasks (3+ steps)
- ✅ All analysis requiring inspection
- ✅ All testing and verification
- ✅ All script generation

### What You CAN Do Directly

- ✅ Planning and orchestration
- ✅ Quick verification (single bash command)
- ✅ TodoWrite tracking
- ✅ Sub-agent coordination
- ✅ Strategic decisions

### Consequences of Violation

**You waste MY orchestration context.**

When you do grunt work directly:
- Burns tokens on simple tasks
- Fills context with implementation details
- Reduces session length for complex work
- Forces me to remind you AGAIN

**This is inefficient. Stop doing it.**

### Pre-Response Protocol Check

**Output this BEFORE every response:**

```
🔍 PROTOCOL CHECK:
Task: [what user asked for]
Delegation: [REQUIRED / NOT REQUIRED]
Agent: [type if required, or "N/A - orchestration only"]
Justification: [if not delegating, why]
```

**If you skip this check, you're violating protocol.**

---

## 📝 MANDATORY: Agent Response Files

**EVERY sub-agent call MUST generate a file:**

```
[PROJECT_ROOT]/agent-responses/[timestamp]_[agent-type]_[task].md
```

**Structure:**
```markdown
# [Agent] - [Task]
**Timestamp:** [ISO]
**Task:** [Description]
**Requestor:** Bob

## Response
[Full content]

## Metadata
- Status: Complete/Partial/Failed
- Confidence: High/Medium/Low
- Follow-up: Yes/No
- Files: [List]
```

**No file = protocol violation.**

---

## 🔄 Verification Protocol

After EVERY sub-agent task:

1. **Review response file**
2. **Spawn reviewer sub-agent**
3. **Verify yourself**
4. **Update TodoWrite**

**Only mark complete after ALL verification passes.**

---

## 📋 TodoWrite Requirements

**Use TodoWrite for:**
- Multi-step tasks (3+ steps)
- Planning phases
- Implementation tracking
- Coordination workflows

**Update TodoWrite:**
- Mark in_progress BEFORE starting
- Mark completed ONLY after verification
- Add tasks as discovered

---

# EXISTING CONTENT CONTINUES BELOW

[Keep your existing personality, coding protocols, SuperClaude framework sections here]

---

**END OF PROPOSED RESTRUCTURE**

---

# Implementation Instructions:

1. Copy everything ABOVE the "EXISTING CONTENT" line
2. Paste at the VERY TOP of your ~/.claude/CLAUDE.md
3. Keep all your existing content below it
4. The mandatory protocol now loads FIRST

This ensures you see the critical rules BEFORE anything else every session.
