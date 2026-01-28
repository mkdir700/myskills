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

### Step 5: Write Decision Log to File & Stage It

**CRITICAL: Do this BEFORE the actual commit**

```bash
# Create .decisions directory if it doesn't exist
mkdir -p .decisions

# Append decision log to today's file
cat >> .decisions/$(date +%Y-%m-%d).md << 'EOF'
[14:30] Sync pairing settings types across test env
- Why: Test suite needed updated Setting type to match production
- Risk: May break other tests expecting old type structure

EOF

# Stage the decision log file so it's included in this commit
git add .decisions/
```

**Why this order matters:**

1. Write decision log file
2. `git add .decisions/` ← **This is key**
3. Then `git commit` ← Decision log file is now part of this commit

### Step 6: Execute Commit

**Only after user confirms AND decision log file is staged**, run:

```bash
git commit -m "fix: sync pairing settings types and test env

[Decision Log]
[2026-01-28 14:30] Sync pairing settings types across test env
- Why: Test suite needed updated Setting type to match production
- Risk: May break other tests expecting old type structure"
```

**Result:**

- Commit includes both code changes AND the `.decisions/YYYY-MM-DD.md` file
- Commit message also contains the decision log
- No second commit needed

**If user says "no":** Ask what to change (message or decision log)

## Complete Example Workflow

```
User: "commit"

Claude:
[Step 1] Reviewing staged changes...

[Step 2]
Files to commit:
- src/types/setting.ts (modified)
- src/test/setup.ts (modified)

Key changes:
- Added cursorPairing field to Setting type
- Updated test environment setup

[Step 3 & 4]
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
[Step 5] Writing decision log...
$ mkdir -p .decisions
$ cat >> .decisions/2026-01-28.md << 'EOF'
[14:30] Sync pairing settings types across test env
- Why: Test suite needed updated Setting type to match production
- Risk: May break other tests expecting old type structure

EOF
$ git add .decisions/

[Step 6] Committing...
$ git commit -m "fix: sync pairing settings types and test env

[Decision Log]
[2026-01-28 14:30] Sync pairing settings types across test env
- Why: Test suite needed updated Setting type to match production
- Risk: May break other tests expecting old type structure"

✓ Committed: 71a4b06
✓ Decision log included in commit (.decisions/2026-01-28.md)
```

## Alternative: Silent Mode

If user says "commit --silent" or "commit -q":

- Skip the confirmation prompt
- Still write decision log file and stage it
- Auto-commit with decision log included

## Special Cases

### Case 1: User Already Provided Commit Message

```
User: "commit with message 'fix tests'"
```

Response:

1. Still run Steps 2-3 (review diff, generate log)
2. Use their message as the title
3. Append decision log to message
4. Write log file and stage it (Step 5)
5. Confirm before committing

### Case 2: Empty Decision Log

If you genuinely cannot determine "why" from context:

```
[Decision Log]
- Why: See commit diff for details
- Risk: none
```

**DO NOT** skip the decision log section entirely.

### Case 3: .gitignore Excludes .decisions/

If `.decisions/` is in `.gitignore`:

- Warn the user
- Ask if they want to force-add with `git add -f .decisions/`
- Or suggest removing `.decisions/` from `.gitignore`

## Anti-Patterns (DO NOT DO)

❌ **Skip staging decision log file:** Writing to `.decisions/` but not running `git add .decisions/`
❌ **Stage after commit:** Running `git commit` then `git add .decisions/`
❌ **Skip diff review:** "Sure, committing now..."
❌ **Skip confirmation:** Commit without asking
❌ **Empty decision log:** Commit without the [Decision Log] section

## Verification

After commit, you can verify the decision log was included:

```bash
# Check last commit includes .decisions/ file
git show --name-only HEAD | grep .decisions

# View the decision log from the commit
git show HEAD:.decisions/2026-01-28.md
```

## Integration with .gitignore

**Recommended:** Do NOT ignore `.decisions/` directory

Add to your `.gitignore` if you have it:

```
# Keep decision logs in git
# .decisions/  ← Do NOT uncomment this
```

Decision logs are valuable documentation and should be version-controlled alongside code.

## Resources

This skill includes a helper script for manual decision log extraction.
