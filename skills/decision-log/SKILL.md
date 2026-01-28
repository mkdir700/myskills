---
name: decision-log
description: "MANDATORY pre-commit workflow for vibe coding. ALWAYS trigger when user says 'commit', 'git commit', or any commit-related command. Forces diff review and decision log generation BEFORE allowing commit to proceed."
---

# Decision Log - Pre-Commit Workflow

## CRITICAL: ALWAYS Execute This Workflow Before Any Commit

This skill is **mandatory** when user mentions commit. Do NOT skip to git commit directly.

## Workflow (Execute in Order)

### Step 1: STOP - Do Not Commit Yet

When user says "commit" or "git commit":
- **DO NOT** execute `git commit` immediately
- User wants a commit, but you must generate decision log FIRST

### Step 2: Review What's Being Committed

Run these commands in sequence:

```bash
# See what files are staged
git diff --cached --name-only

# See the actual changes
git diff --cached
```

Show the user:
- Which files changed
- Key changes (summarize if diff is >50 lines)

### Step 3: Generate Decision Log

Based on the diff, create a 3-line decision log:

```
[YYYY-MM-DD HH:MM] <one-line summary>
- Why: <core reason for this change>
- Risk: <known issues/shortcuts or "none">
```

**Rules:**
- Summary: Extract from user's recent messages or infer from code changes
- Why: The business/technical reason (not "user asked")
- Risk: Be honest about shortcuts, missing tests, or edge cases

**Example:**

```
[2026-01-28 14:30] Sync pairing settings types across test env
- Why: Test suite needed updated Setting type to match production
- Risk: May break other tests expecting old type structure
```

### Step 4: Show Proposed Commit

Present to user:

```
I'll commit these changes:

Files:
- src/types/setting.ts
- src/test/setup.ts
(+ 3 more files)

With message:
---
fix: sync pairing settings types and test env

[Decision Log]
[2026-01-28 14:30] Sync pairing settings types across test env
- Why: Test suite needed updated Setting type to match production
- Risk: May break other tests expecting old type structure
---

Proceed with commit? [y/n]
```

### Step 5: Execute Commit

**Only after user confirms**, run:

```bash
git commit -m "fix: sync pairing settings types and test env

[Decision Log]
[2026-01-28 14:30] Sync pairing settings types across test env
- Why: Test suite needed updated Setting type to match production
- Risk: May break other tests expecting old type structure"
```

**If user says "no":** Ask what to change (message or decision log)

## Alternative: Silent Mode

If user says "commit --silent" or "commit -q":
- Skip the confirmation prompt
- Auto-generate decision log and commit immediately
- Still show the commit message after it's done

## Special Cases

### Case 1: User Already Provided Commit Message

```
User: "commit with message 'fix tests'"
```

Response:
1. Still run Steps 2-3 (review diff, generate log)
2. Use their message as the title
3. Append decision log
4. Confirm before committing

### Case 2: Empty Decision Log

If you genuinely cannot determine "why" from context:

```
[Decision Log]
- Why: See commit diff for details
- Risk: none
```

**DO NOT** skip the decision log section entirely.

### Case 3: User Bypasses You

If user runs `git commit` directly in terminal:
- You can't intercept
- That's fine - this skill only applies when they ask YOU to commit

## Storage: Also Write to .decisions/

In addition to commit message, append to `.decisions/YYYY-MM-DD.md`:

```bash
# After successful commit
echo "[14:30] Sync pairing settings types across test env
- Why: Test suite needed updated Setting type
- Risk: May break other tests expecting old type structure

" >> .decisions/2026-01-28.md
```

This creates a searchable log independent of git history.

## Example Full Interaction

```
User: "commit"

Claude:
Reviewing staged changes...

Files to commit:
- src/types/setting.ts (modified)
- src/test/setup.ts (modified)
- src/contexts/__tests__/UpdateContext.test.tsx (modified)

Key changes:
- Added cursorPairing field to Setting type
- Updated test environment to include new field
- Synced test fixtures with type changes

I'll commit with this message:
---
fix: sync pairing settings types and test env

[Decision Log]
[2026-01-28 14:30] Sync pairing settings types across test env
- Why: Test suite needed updated Setting type to match production
- Risk: May break other tests expecting old type structure
---

Proceed? (y/n)

User: "y"

Claude:
[runs git commit]
✓ Committed: 71a4b06
✓ Appended to .decisions/2026-01-28.md
```

## Anti-Patterns (DO NOT DO)

❌ **Skip diff review:** "Sure, committing now..."
❌ **Skip confirmation:** Commit without asking
❌ **Empty decision log:** Commit without the [Decision Log] section
❌ **Assume context:** Generate log from old conversation instead of current diff

## Integration with CI/CD

If user's repo has a commit-msg hook, it might conflict. Suggest:

```bash
# Add to .git/hooks/commit-msg
# Skip if [Decision Log] already present
if grep -q "\[Decision Log\]" "$1"; then
    exit 0
fi
```

## Resources

This skill includes a helper script for manual decision log extraction.
