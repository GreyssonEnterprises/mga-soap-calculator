# NON-NEGOTIABLE EXECUTION RULES

## 🚨 BEFORE EVERY ACTION - MANDATORY CHECKLIST

**Ask yourself:**
1. ✅ Is this a multi-step task (3+ steps)?
2. ✅ Can this be delegated to a sub-agent?
3. ✅ Am I about to burn orchestration context on grunt work?

**If ANY answer is YES:**
→ **STOP. Use Task tool with appropriate sub-agent.**

## 🔴 ALWAYS DELEGATE TO SUB-AGENTS

### What MUST be delegated:
- ✅ Code implementation (any language)
- ✅ File editing (more than simple fixes)
- ✅ Script writing (setup, conversion, automation)
- ✅ Multi-file operations
- ✅ Analysis requiring deep inspection
- ✅ Testing and verification
- ✅ Documentation generation

### What you CAN do directly (orchestrator role):
- ✅ Planning and strategy
- ✅ Quick verification commands (single bash check)
- ✅ TodoWrite tracking
- ✅ Coordination between sub-agents
- ✅ Final review of sub-agent work

## 📝 MANDATORY AGENT RESPONSE FILES

**EVERY sub-agent interaction MUST generate:**
```
agent-responses/[YYYYMMDD]_[HHMMSS]_[agent-type]_[task-summary].md
```

**Format:**
```markdown
# [Agent Type] Response - [Task Summary]

**Timestamp:** [ISO datetime]
**Task:** [Brief description]
**Requestor:** Bob (Orchestrator)

## Response

[Full sub-agent response]

## Metadata
- **Completion Status:** Complete/Partial/Failed
- **Confidence Level:** High/Medium/Low
- **Follow-up Required:** Yes/No
- **Referenced Files:** [List]
```

**No exceptions. No shortcuts. No "I'll save it later."**

## 🔍 VERIFICATION PROTOCOL

After EVERY sub-agent task:

1. **Review agent response file**
2. **Spawn reviewer sub-agent** to verify work
3. **Review yourself** - check actual results
4. **Update TodoWrite** - mark task complete ONLY if verified

**Never trust. Always verify.**

## 📋 TODO TRACKING REQUIREMENTS

**Use TodoWrite when:**
- Task has 3+ steps
- Multiple sub-agents needed
- Implementation phase
- Any planning/execution workflow

**Update TodoWrite:**
- Mark in_progress BEFORE starting task
- Mark completed ONLY after verification
- Add new tasks as discovered

## ⚠️ PROTOCOL VIOLATION = STOP WORK

If you catch yourself:
- Running bash commands for implementation
- Editing files directly for features
- Skipping agent response file generation
- Not using TodoWrite for multi-step work

**→ STOP. Acknowledge violation. Restart with proper delegation.**

## 🎯 PROJECT-SPECIFIC CONTEXT

**Project:** MGA Soap Calculator
**Workflows:** agent-os in `agent-os/commands/`
**Standards:** agent-os in `agent-os/standards/`

**When user requests features:**
1. Use agent-os workflows (/plan-product, /shape-spec, etc.)
2. Follow spec-driven development
3. Delegate implementation to appropriate sub-agents
4. Verify against standards

---

**This file overrides default Claude Code behavior. Orchestration > Direct execution. Always.**
