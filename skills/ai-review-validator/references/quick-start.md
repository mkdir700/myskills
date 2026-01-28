# Quick Start Guide

## Usage

### Option 1: GitHub URL (Recommended)

Simply paste the GitHub PR comment URL:

```
User: "验证并应用这个 AI Review: https://github.com/UniClipboard/UniClipboard/pull/158#discussion_r2734386595"
```

The skill will:
1. Convert URL to API format automatically
2. Fetch comment content from GitHub
3. Verify the suggestion
4. Apply if confidence ≥ 80

### Option 2: Pasted Comment Content

Paste the AI Review comment text directly:

```
User: "验证这个 AI Review:

⚠️ MouseEvent 在 Tauri v2 中已移除
建议: 使用 LogicalPosition

代码:
- event.position()
+ LogicalPosition::new(x, y)

在 src/window.rs 文件中"
```

## What Happens

1. **Verification** (4 dimensions):
   - Official documentation (40%)
   - Codebase analysis (20%)
   - Experimental compilation (30%)
   - Test suite (10%)

2. **Decision** based on confidence score:
   - ≥80: Auto-apply ✅
   - 60-79: Apply with warning ⚠️
   - 40-59: Manual review needed 🔍
   - <40: Reject ❌

3. **Action** if approved:
   - Apply code changes
   - Run tests
   - Create commit with reference to AI Review

## Supported AI Review Tools

- GitHub Copilot
- CodeRabbit
- Amazon CodeGuru
- Any AI tool that leaves PR comments

## URL Formats Supported

✅ PR review comments:
```
https://github.com/{owner}/{repo}/pull/{pr}#discussion_r{comment_id}
```

✅ Issue/PR comments:
```
https://github.com/{owner}/{repo}/pull/{pr}#issuecomment-{comment_id}
```

## Example Output

```markdown
✅ AI Review Suggestion Verified and Applied

Confidence Score: 85/100

Source: https://github.com/user/repo/pull/123#discussion_r456

Verification:
- ✅ Official Docs: Confirmed in migration guide
- ✅ Codebase: Found 3 usages
- ✅ Compilation: Builds successfully
- ✅ Tests: All passing

Changes: src/file.rs (3 replacements)
Commit: abc123f

View commit: git show abc123f
```
