---
name: ai-review-validator
description: Autonomously validate and execute AI Review suggestions from PR comments. Use when users provide AI Review comments (from GitHub Copilot, CodeRabbit, etc.) that suggest code changes, API migrations, or fixes. The skill verifies suggestions against official docs, tests compilation, calculates confidence scores, and auto-applies changes when verified. Triggers on phrases like "verify this AI Review", "apply this suggestion", "validate AI Review comment", or when users paste AI Review URLs/content.
---

# Ai Review Validator

## Overview

Automate validation and execution of AI Review suggestions. This skill verifies AI-generated code review comments by checking official documentation, analyzing the codebase, testing compilation, and calculating confidence scores before automatically applying verified changes.

## Workflow

### Step 1: Parse AI Review Comment

Extract structured information from the comment:

```python
# Expected AI Review format:
# 1. Risk warning/description
# 2. Code example (before/after)
# 3. Modification prompt

comment_structure = {
    "risk_warning": str,      # e.g., "MouseEvent removed in Tauri v2"
    "deprecated_api": str,    # e.g., "MouseEvent.position()"
    "suggested_api": str,     # e.g., "LogicalPosition::new(x, y)"
    "code_examples": {
        "before": str,
        "after": str
    },
    "modification_prompt": str,  # Instructions for applying the change
    "affected_files": [str],
    "comment_url": str
}
```

### Step 2: Multi-Dimensional Verification

Run verification in parallel, scoring each dimension:

#### 2.1 Official Documentation (Weight: 40%)

```bash
# Search official sources
web_search "<framework> <deprecated_api> deprecated removed"
web_search "<framework> <suggested_api> migration guide"
web_fetch "official migration documentation URL"

# Scoring:
# - Explicit confirmation: 40 points
# - Partial confirmation: 20 points
# - No evidence: 0 points
```

#### 2.2 Codebase Analysis (Weight: 20%)

```bash
# Examine project state
view <affected_file>
bash_tool "grep -rn '<deprecated_api>' ."
bash_tool "cat package.json | grep <framework>"  # Check version

# Scoring:
# - API found + version matches: 20 points
# - API found but version unclear: 10 points
# - API not found: 0 points
```

#### 2.3 Experimental Verification (Weight: 30%)

```bash
# Test the suggested change
create_file "/home/claude/test_change.ext" "<test code with new API>"
bash_tool "<compile command>"  # e.g., rustc, tsc, npm build

# Scoring:
# - Compiles + no type errors: 30 points
# - Compiles with warnings: 15 points
# - Fails: 0 points
```

#### 2.4 Test Suite (Weight: 10%)

```bash
bash_tool "<test command>"  # e.g., cargo test, npm test

# Scoring:
# - All tests pass: 10 points
# - Tests fail: 0 points
```

### Step 3: Calculate Confidence & Decide

```python
confidence_score = (
    docs_score +
    codebase_score +
    experimental_score +
    test_score
)

if confidence_score >= 80:
    decision = "AUTO_APPLY"
elif confidence_score >= 60:
    decision = "APPLY_WITH_REVIEW"
elif confidence_score >= 40:
    decision = "MANUAL_REVIEW"
else:
    decision = "REJECT"
```

### Step 4: Execute Based on Confidence

#### AUTO_APPLY (≥80)

```bash
# Apply changes
str_replace(
    path=<file>,
    old_str=<deprecated_code>,
    new_str=<new_code>,
    description="Apply AI Review suggestion"
)

# Verify
bash_tool "<build_command>"
bash_tool "<test_command>"

# Commit with reference
bash_tool 'git add .'
bash_tool 'git commit -m "fix: <summary>

Apply AI Review suggestion
Verified with confidence: <score>/100

Verification:
- Docs: <status>
- Compilation: <status>
- Tests: <status>

Resolves: <comment_url>
Co-authored-by: AI Review Validator <agent@ai-review.dev>"'
```

Report format:
```markdown
✅ AI Review Suggestion Verified and Applied

Confidence Score: <score>/100

Verification Summary:
- ✓ Official Docs: <evidence>
- ✓ Compilation: Passes
- ✓ Tests: All passing

Changes: <file> (<n> replacements)
Commit: <hash>
Linked: <comment_url>
```

#### APPLY_WITH_REVIEW (60-79)

Apply changes but flag potential issues:

```markdown
⚠️ AI Review Suggestion Applied - Please Review

Confidence Score: <score>/100

Concerns:
- <specific issue to check>

Changes applied but recommend reviewing:
1. <area of concern>
2. <edge case>
```

#### MANUAL_REVIEW (40-59)

```markdown
🔍 AI Review Suggestion Requires Manual Review

Confidence Score: <score>/100

Issues:
- <conflicting information>
- <uncertainty>

Recommendation: Do not auto-apply
```

#### REJECT (<40)

```markdown
❌ AI Review Suggestion Not Verified

Confidence Score: <score>/100

Evidence shows this suggestion may be incorrect:
- <contradicting evidence>

Recommendation: Do NOT apply
```

## Edge Cases

### Multiple Files

Process all files, create single atomic commit:

```bash
for file in affected_files:
    str_replace(...)

bash_tool 'git commit -m "fix: <summary>

Modified files:
- <file1>
- <file2>

Resolves: <comment_url>"'
```

### Conflicting Information

```python
if docs_result != experimental_result:
    return "MANUAL_REVIEW", {
        "reason": "Conflicting evidence",
        "docs": docs_result,
        "experiments": experimental_result
    }
```

### Breaking Changes

```bash
# If tests fail after applying
bash_tool "git reset --hard HEAD"
return "REJECT", "Tests fail after applying suggestion"
```

## Safety Principles

1. **Never blindly trust AI Review** - Always verify before applying
2. **Provide evidence** - Show docs, compilation output, test results
3. **Be transparent** - Explain confidence scoring
4. **Safety first** - Verify builds/tests before committing
5. **Traceable** - Always link commits to AI Review comments
6. **Human-in-loop** - Flag uncertain cases for review

## Common Patterns

### Pattern 1: API Deprecation
```
⚠️ API deprecated in v2.0
Old: old_api()
New: new_api()
```

### Pattern 2: Security Risk
```
🔒 Security: Avoid unsafe code
Use: Safe alternative
```

### Pattern 3: Performance
```
⚡ Performance: Can be optimized
Use: Iterator instead of collect()
```

## When to Escalate

Escalate to human review when:
- Confidence < 60
- Breaking changes detected
- Tests fail after applying
- Conflicting information from sources
- Security-critical code
- Architectural changes

## Detailed Examples

For comprehensive examples of different scenarios, see `references/examples.md`:
- High confidence auto-apply (Tauri v2 migration)
- Medium confidence with warnings (performance optimization)
- Low confidence rejection (false positive detection)
- Multiple file batch processing
- Conflicting information handling


