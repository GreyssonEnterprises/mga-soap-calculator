# Protocol Enforcement Implementation Guide

## What I Created

### ✅ For THIS Project (MGA Soap Calculator)

**File**: `.claude/RULES.md`
- Project-specific enforcement rules
- Pre-action checklist
- Delegation requirements
- Agent response file formats
- Verification protocols

**Status**: ✅ Already in place

---

### 🎯 For GLOBAL Enforcement (All Projects)

I've created PROPOSED files that you need to implement manually:

#### 1. PROPOSED_GLOBAL_CLAUDE.md
**What it is**: Restructured ~/.claude/CLAUDE.md with critical rules FIRST

**How to implement:**
```fish
# Backup current file
cp ~/.claude/CLAUDE.md ~/.claude/CLAUDE.md.backup

# Option A: Manually edit
# Open ~/.claude/CLAUDE.md
# Copy content from PROPOSED_GLOBAL_CLAUDE.md (top section)
# Paste at VERY TOP of file
# Save

# Option B: Full replacement (if you want clean start)
cp PROPOSED_GLOBAL_CLAUDE.md ~/.claude/CLAUDE.md
# Then add back any custom content you had
```

**Why**: Puts mandatory protocol CHECK at the top so it's the FIRST thing loaded every session.

---

#### 2. PROPOSED_MANDATORY_PROTOCOL.md
**What it is**: Standalone protocol rules file

**How to implement:**
```fish
# Copy to global .claude directory
cp PROPOSED_MANDATORY_PROTOCOL.md ~/.claude/MANDATORY_PROTOCOL.md

# Then reference it at TOP of ~/.claude/CLAUDE.md
# Add this line at the very beginning:
# @MANDATORY_PROTOCOL.md
```

**Why**: Separates enforcement rules from personality/config. Easier to update.

---

#### 3. PROPOSED_orchestration-enforcement-SKILL.md
**What it is**: Auto-loading skill that enforces protocol

**How to implement:**
```fish
# Create skill directory
mkdir -p ~/.claude/skills/_core/orchestration-enforcement

# Copy skill file
cp PROPOSED_orchestration-enforcement-SKILL.md \
   ~/.claude/skills/_core/orchestration-enforcement/SKILL.md
```

**Why**: Auto-activates in EVERY Claude Code session. Forces protocol check before every response.

---

## Implementation Priority

### 🔴 CRITICAL (Do First)

**Restructure ~/.claude/CLAUDE.md**
- Moves critical rules to top
- Makes protocol impossible to miss
- Takes 5 minutes

### 🟡 IMPORTANT (Do Second)

**Install orchestration-enforcement skill**
- Auto-enforces delegation
- Catches violations before they happen
- Takes 2 minutes

### 🟢 OPTIONAL (Do Later)

**Add MANDATORY_PROTOCOL.md**
- Cleaner organization
- Easier to maintain
- Nice to have but not critical

---

## Testing the Enforcement

After implementing, test with this session:

```
You: Implement user authentication for the soap calculator

Bob (with enforcement):
🔍 PROTOCOL CHECK:
Task: Implement user authentication
Delegation: REQUIRED
Agent Type: backend-architect

Spawning sub-agent...
[Task tool call]

Bob (without enforcement):
I'll add authentication by creating auth.py...
[Direct implementation - WRONG]
```

**If you see the SECOND response, enforcement isn't working.**

---

## Migration Path

### Immediate (This Session)

✅ Project-level `.claude/RULES.md` is already active
- Provides enforcement for THIS project
- Won't help in other projects

### Short-term (Next 10 minutes)

1. Restructure ~/.claude/CLAUDE.md with rules first
2. Install orchestration-enforcement skill
3. Test with next coding request

### Long-term (Ongoing)

1. Create MANDATORY_PROTOCOL.md
2. Reference it in CLAUDE.md
3. Build habit of checking protocol

---

## Verification Checklist

After implementation, verify:

### ✅ File Locations

```fish
# Project level
ls .claude/RULES.md

# Global level
ls ~/.claude/MANDATORY_PROTOCOL.md
ls ~/.claude/skills/_core/orchestration-enforcement/SKILL.md
head -20 ~/.claude/CLAUDE.md  # Should show protocol check first
```

### ✅ Behavior Check

Test prompt: "Add a new feature to calculate soap hardness"

Expected behavior:
1. Protocol check appears
2. Identifies delegation required
3. Spawns appropriate sub-agent
4. Saves agent response file
5. Updates TodoWrite

NOT expected:
1. Direct code implementation
2. Bash commands for features
3. File edits without delegation

---

## Fallback if Enforcement Fails

If I STILL violate protocol even with enforcement:

**Immediate:**
- Stop me: "Protocol violation"
- Point out what I should have done
- Ask me to restart with delegation

**Session:**
- At session start: "Remember to check protocol"
- Periodically: "Are you following delegation rules?"

**Long-term:**
- Report as Claude Code bug if enforcement skill doesn't work
- Consider adding user prompt hook validation

---

## File Summary

**Created in this project:**
1. `.claude/RULES.md` ✅ (active now)
2. `PROPOSED_GLOBAL_CLAUDE.md` (for you to implement)
3. `PROPOSED_MANDATORY_PROTOCOL.md` (for you to implement)
4. `PROPOSED_orchestration-enforcement-SKILL.md` (for you to implement)
5. This guide

**Next action:** Implement the PROPOSED files globally following instructions above.

---

**The goal:** Never have to remind me about protocol again. The system enforces it automatically.
