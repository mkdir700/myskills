# Pre-Commit Checklist

Before committing ANY changes from AI Review validation, verify ALL items:

## ✅ Required Information

- [ ] **AI Review URL saved**: Original GitHub comment URL is stored and accessible
- [ ] **Changes applied**: Code modifications are complete
- [ ] **Build passes**: `cargo build` or equivalent succeeds
- [ ] **Tests pass**: All tests still passing

## ✅ Commit Message Requirements

**MANDATORY fields in commit message:**

1. [ ] **Summary line**: Clear description of what changed
2. [ ] **Body**: "Apply AI Review suggestion"
3. [ ] **Confidence score**: "Verified with confidence: XX/100"
4. [ ] **AI-Review field**: `AI-Review: <github_url>`
5. [ ] **Resolves field**: `Resolves: <github_url>`

**Template:**
```
git commit -m "fix: <summary>

Apply AI Review suggestion
Verified with confidence: <score>/100

AI-Review: <original_github_url>
Resolves: <original_github_url>"
```

## ❌ Common Mistakes to Avoid

### Mistake 1: Generic commit without AI Review link
```bash
# ❌ WRONG
git commit -m "fix: sync pairing settings types and test env"
```
**Missing:** AI Review URL reference

### Mistake 2: Missing confidence score
```bash
# ❌ WRONG
git commit -m "fix: replace MouseEvent

Resolves: https://github.com/..."
```
**Missing:** Confidence score and "Apply AI Review suggestion" line

### Mistake 3: URL in wrong format
```bash
# ❌ WRONG
git commit -m "fix: replace MouseEvent

See: https://github.com/..."
```
**Missing:** Proper `AI-Review:` and `Resolves:` fields

## ✅ Correct Examples

### Example 1: Single file change
```bash
git commit -m "fix: Replace MouseEvent with LogicalPosition

Apply AI Review suggestion
Verified with confidence: 85/100

AI-Review: https://github.com/user/repo/pull/123#discussion_r456
Resolves: https://github.com/user/repo/pull/123#discussion_r456"
```

### Example 2: Multiple files
```bash
git commit -m "fix: Remove unused imports

Apply AI Review suggestion  
Verified with confidence: 95/100

Modified files:
- src/main.rs
- src/utils.rs

AI-Review: https://github.com/user/repo/pull/123#discussion_r789
Resolves: https://github.com/user/repo/pull/123#discussion_r789"
```

### Example 3: With review needed
```bash
git commit -m "perf: Remove unnecessary collect()

Apply AI Review suggestion with review needed
Verified with confidence: 68/100

⚠️ Please review edge cases where collect() might be needed

AI-Review: https://github.com/user/repo/pull/123#discussion_r999
Resolves: https://github.com/user/repo/pull/123#discussion_r999"
```

## 🔍 Verification

After commit, verify the commit message:
```bash
git log -1 --pretty=format:"%B"
```

Check that it contains:
1. ✅ "Apply AI Review suggestion" line
2. ✅ "Verified with confidence: XX/100"
3. ✅ "AI-Review: https://github.com/..."
4. ✅ "Resolves: https://github.com/..."

If ANY of these are missing, amend the commit:
```bash
git commit --amend
```
