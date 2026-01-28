# AI Review Validator - Usage Examples

## Example 1: High Confidence - Auto Apply

**User Input:**
```
验证并应用这个 AI Review:
https://github.com/user/repo/pull/123#discussion_r456

评论内容:
⚠️ MouseEvent 在 Tauri v2 中已移除
建议: 使用 LogicalPosition

代码示例:
- event.position()
+ LogicalPosition::new(x, y)

Prompt: 替换所有 MouseEvent.position() 为 LogicalPosition
```

**Agent Process:**

1. **Parse**: Extract deprecated_api="MouseEvent.position()", suggested_api="LogicalPosition::new()"

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

6. **Score: 80/100 → AUTO_APPLY**

7. **Execute**:
   ```bash
   str_replace(path="src/window.rs", 
               old_str="event.position()",
               new_str="LogicalPosition::new(x, y)")
   bash_tool "cargo build && cargo test"
   bash_tool 'git commit -m "fix: Replace MouseEvent with LogicalPosition

Verified confidence: 80/100
Resolves: https://github.com/user/repo/pull/123#discussion_r456"'
   ```

**Output:**
```markdown
✅ AI Review Suggestion Verified and Applied

Confidence Score: 80/100

Verification:
- ⚠️ Official Docs: Partially confirmed (LogicalPosition API exists)
- ✅ Codebase: Found 3 usages in src/window.rs
- ✅ Compilation: Builds successfully
- ✅ Tests: All 15 tests passing

Changes: src/window.rs (3 replacements)
Commit: abc123f
```

---

## Example 2: Medium Confidence - Apply with Review

**User Input:**
```
Check this AI Review:

⚠️ Performance: Unnecessary collect()
- let sum: i32 = numbers.iter().collect::<Vec<_>>().iter().sum();
+ let sum: i32 = numbers.iter().sum();
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
