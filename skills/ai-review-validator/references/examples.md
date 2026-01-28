# AI Review Validator - Usage Examples

## Example 1: GitHub URL - High Confidence Auto Apply

**User Input:**
```
验证并应用这个 AI Review:
https://github.com/UniClipboard/UniClipboard/pull/158#discussion_r2734386595
```

**Agent Process:**

**Step 0: Fetch GitHub Comment**
```bash
# Convert URL to API format
api_url=$(python3 scripts/github_url_converter.py \
  "https://github.com/UniClipboard/UniClipboard/pull/158#discussion_r2734386595")
# Output: https://api.github.com/repos/UniClipboard/UniClipboard/pulls/comments/2734386595

# Fetch comment from GitHub API
web_fetch "$api_url"

# Response:
{
  "body": "⚠️ MouseEvent has been removed in Tauri v2\nUse LogicalPosition instead...",
  "path": "src/window.rs",
  "diff_hunk": "@@ -42,3 +42,3 @@\n-    event.position()\n+    LogicalPosition::new(x, y)",
  "user": {"login": "coderabbitai"},
  "html_url": "https://github.com/UniClipboard/UniClipboard/pull/158#discussion_r2734386595"
}
```

**Step 1: Parse Comment**
```python
parsed = {
  "risk": "MouseEvent removed in Tauri v2",
  "deprecated_api": "event.position()",
  "suggested_api": "LogicalPosition::new(x, y)",
  "affected_file": "src/window.rs",
  "original_url": "https://github.com/UniClipboard/UniClipboard/pull/158#discussion_r2734386595"
}
```

**Step 2-4: Verification** (same as before)

1. **Parse**: Extract deprecated_api="MouseEvent.position()", suggested_api="LogicalPosition::new()"

**Step 2-5: Verification & Execution**

2. **Verify Documentation (40 pts)**:
   ```bash
   web_search "Tauri v2 MouseEvent removed"
   web_fetch "https://v2.tauri.app/start/migrate/"
   # Result: Partial confirmation (LogicalPosition exists) → 20 pts
   ```

3. **Analyze Codebase (20 pts)**:
   ```bash
   view "src/window.rs"
   bash_tool "grep -rn 'MouseEvent' src/"
   # Result: Found 3 usages → 20 pts
   ```

4. **Experimental Test (30 pts)**:
   ```rust
   create_file("/home/claude/test.rs", "
   use tauri::LogicalPosition;
   fn test() { LogicalPosition::new(100.0, 200.0); }
   ")
   bash_tool "rustc test.rs"
   # Result: Compiles successfully → 30 pts
   ```

5. **Run Tests (10 pts)**:
   ```bash
   bash_tool "cargo test"
   # Result: All pass → 10 pts
   ```

**Score: 80/100 → AUTO_APPLY**

6. **Execute**:
   ```bash
   str_replace(path="src/window.rs", 
               old_str="event.position()",
               new_str="LogicalPosition::new(x, y)")
   bash_tool "cargo build && cargo test"
   
   # ✅ CORRECT: Include AI Review URL in commit
   bash_tool 'git commit -m "fix: Replace MouseEvent with LogicalPosition

Apply AI Review suggestion
Verified confidence: 80/100

AI-Review: https://github.com/UniClipboard/UniClipboard/pull/158#discussion_r2734386595
Resolves: https://github.com/UniClipboard/UniClipboard/pull/158#discussion_r2734386595"'
   ```

**❌ WRONG - Never do this:**
```bash
# This is missing the AI Review URL!
git commit -m "fix: sync pairing settings types and test env"
```

**Why this is wrong:**
- No link to AI Review comment
- Future developers won't know why this change was made
- Can't trace back to the verification process
- Loses accountability

**Output:**
```markdown
✅ AI Review Suggestion Verified and Applied

Confidence Score: 80/100

**Source:** https://github.com/UniClipboard/UniClipboard/pull/158#discussion_r2734386595

Verification:
- ⚠️ Official Docs: Partially confirmed (LogicalPosition API exists)
- ✅ Codebase: Found 3 usages in src/window.rs
- ✅ Compilation: Builds successfully
- ✅ Tests: All 15 tests passing

Changes: src/window.rs (3 replacements)
Commit: abc123f
```

---

## Example 2: Pasted Comment - Medium Confidence

**User Input:**
```
验证这个 AI Review:

⚠️ Performance: Unnecessary collect()
- let sum: i32 = numbers.iter().collect::<Vec<_>>().iter().sum();
+ let sum: i32 = numbers.iter().sum();

在 src/calculator.rs 中
```

**Agent Process:**

1. **Verify**: Docs confirm iterator is faster → 30 pts
2. **Code check**: Found usage → 20 pts
3. **Test**: Compiles, 20% faster in benchmarks → 25 pts
4. **Tests**: Pass → 10 pts

**Score: 65/100 → APPLY_WITH_REVIEW**

**Output:**
```markdown
⚠️ AI Review Applied - Please Review

Confidence: 65/100

Performance improved 20% in benchmarks.

⚠️ Check edge cases where collect() might be needed:
- Iterator used multiple times
- Lifetime constraints

Commit: xyz789
```

---

## Example 3: Low Confidence - Reject

**User Input:**
```
AI Review says: Replace unwrap() with expect()

- let x = func().unwrap();
+ let x = func().expect("error msg");
```

**Agent Analysis:**

```bash
view "src/parser.rs"
# Code is in #[cfg(test)] block - unwrap() is fine in tests
```

**Score: 35/100 → REJECT**

**Output:**
```markdown
❌ AI Review Not Applicable

Confidence: 35/100

The code is in test context where unwrap() is idiomatic.
This is a FALSE POSITIVE.

Recommendation: Keep current code
```

---

## Example 4: Multiple Files - Batch Processing

**User Input:**
```
AI Review: Remove unused imports in:
- src/main.rs: HashMap
- src/utils.rs: Arc, Mutex
- src/config.rs: Deserialize
```

**Agent Process:**

```bash
# Verify with compiler
bash_tool "cargo clippy"
# Output confirms all are unused → 95/100

# Apply to all files
for file in files:
    str_replace(...)

# Single commit
bash_tool 'git commit -m "chore: Remove unused imports

Files:
- src/main.rs
- src/utils.rs  
- src/config.rs"'
```

**Output:**
```markdown
✅ Applied (Multiple Files)

Confidence: 95/100 (verified by clippy)

Files cleaned:
1. src/main.rs - HashMap
2. src/utils.rs - Arc, Mutex
3. src/config.rs - Deserialize

Commit: def456
```

---

## Example 5: Conflicting Info - Manual Review

**User Input:**
```
AI Review: Convert sync to async

- db.query_sync()
+ db.query().await
```

**Agent Analysis:**

```bash
# Docs say: Both APIs supported
# But: Current handlers are sync, not async
# Converting requires: Major refactoring
```

**Score: 42/100 → MANUAL_REVIEW**

**Output:**
```markdown
🔍 Manual Review Required

Confidence: 42/100

This isn't a simple API change - it's an architectural decision.

Current: Synchronous request handlers
Suggested: Async (requires framework changes)

Questions:
- Is sync actually a bottleneck?
- Cost vs benefit of async migration?

No changes applied. Want a migration plan instead?
```

---

## Usage Patterns

### Quick Validation
```
User: "Is this AI Review correct? <paste>"
→ Fast check (docs + code only)
→ Returns confidence + recommendation
```

### Validate & Apply
```
User: "验证并应用: <URL>"
→ Full verification
→ Auto-apply if ≥80
→ Report if <80
```

### Explain Only
```
User: "Why is this suggestion correct/wrong?"
→ Educational analysis
→ No changes applied
```
