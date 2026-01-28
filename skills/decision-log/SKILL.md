---
name: decision-log
description: "Automatically generate lightweight decision logs during vibe coding sessions. Use when: (1) User writes/modifies code rapidly, (2) User wants to track why behind code changes without interrupting flow, (3) User needs to understand old vibe-coded projects later, (4) User commits code and wants auto-generated context in commit messages or .decisions/ logs"
---

# Decision Log

Automatically capture the reasoning behind code changes during vibe coding without breaking flow.

## Core Principle

Vibe coding prioritizes **speed over polish**. This skill doesn't slow you down—it runs AFTER code is written to auto-generate minimal "why" documentation.

## Output Format

Generate a 3-line decision log entry:

```
[YYYY-MM-DD HH:MM] <one-line summary of change>
- Why: <core decision point, 1 sentence>
- Risk: <known gaps/shortcuts, 1 sentence or "none">
```

### Example

```
[2026-01-28 10:30] Added citation deduplication
- Why: Prevent duplicate citations in search results
- Risk: Doesn't handle null IDs, will fail silently
```

## Storage Options

### Option 1: Commit Message (default)
Append to git commit message:
```bash
git commit -m "Add citation dedup

[Decision Log]
- Why: Prevent duplicate citations
- Risk: Null ID handling missing"
```

### Option 2: `.decisions/` Directory
Create dated log files:
```
.decisions/
├── 2026-01-28.md
└── 2026-01-27.md
```

Each entry appends to the day's file.

### Option 3: Inline Comments
Add decision as a code comment at change point:
```python
# [2026-01-28] Dedup by ID to avoid citation repeats
# Risk: null IDs not handled
citations = list(set(c.id for c in citations if c.id))
```

## Automatic Triggers

When Claude writes code in a vibe coding session, automatically:

1. **After code generation**: Silently draft a decision log (don't show unless asked)
2. **On commit/save**: Inject decision log into commit message or append to `.decisions/YYYY-MM-DD.md`
3. **On request**: Show accumulated decisions when user asks "what did we change?" or "show decision log"

## Usage Patterns

### Pattern 1: Silent Background Logging
```
User: "Add a cache for API responses"
Claude: [writes code + silently stores decision]
User: "git commit"
Claude: [auto-injects decision into commit message]
```

### Pattern 2: Explicit Review
```
User: "Show me today's decisions"
Claude: [displays all logged decisions from 2026-01-28.md]
```

### Pattern 3: Project Archaeology
```
User: "Why did we use a Set here?"
Claude: [searches .decisions/ or git log for relevant entry]
```

## Key Rules

1. **Never interrupt flow**: Don't ask "should I log this?" Just log it.
2. **3 lines max**: Force brevity. No essays.
3. **Honest about risks**: If you took a shortcut, say it.
4. **Timestamped**: Always include date/time for future sorting.
5. **Searchable**: Use consistent format so `grep` works.

## Integration with MemOS

If user has MemOS enabled, decision logs can feed into long-term memory:
- Extract "why" from `.decisions/` into MemOS facts
- Surface relevant decisions when user asks "how does X work?"

## Resources

### scripts/
Contains `generate_decision_log.py` to extract decisions from git history or conversation context.
