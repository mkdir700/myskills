# MySkills

A collection of custom skill modules for Claude AI assistant, designed to automate and standardize development workflows.

## Overview

MySkills is a modular skill library that extends Claude's capabilities with predefined workflows and best practices. Each skill encapsulates domain-specific knowledge and procedures that can be triggered during development tasks.

## Directory Structure

```
myskills/
├── README.md
└── skills/
    └── <skill-name>/
        └── SKILL.md      # Skill definition file
```

## Available Skills

| Skill | Description | User Invocable |
|-------|-------------|----------------|
| `archive-and-cleanup-vibe-docs` | Consolidates engineering knowledge from temporary documents, generates PR-ready summaries, and removes planning artifacts before merge | No (auto-triggered) |

## Skill Format

Each skill is defined in a `SKILL.md` file with YAML frontmatter:

```yaml
---
name: skill-name
version: "1.0.0"
description: Brief description of what the skill does
user-invocable: true/false
allowed-tools:
  - Read
  - Write
  - Edit
  # ... other tools
---

# Skill content in Markdown
```

### Frontmatter Fields

- **name**: Unique identifier for the skill
- **version**: Semantic version number
- **description**: What the skill does
- **user-invocable**: Whether users can explicitly invoke this skill
- **allowed-tools**: List of tools the skill is permitted to use

## Adding a New Skill

1. Create a new directory under `skills/` with your skill name:
   ```bash
   mkdir skills/my-new-skill
   ```

2. Create a `SKILL.md` file with the required frontmatter and documentation

3. Define:
   - When to trigger the skill
   - Required inputs
   - Execution steps
   - Output requirements
   - Success criteria

## Usage

Skills are automatically loaded by Claude Code when configured. To use this skill library:

1. Clone this repository
2. Configure Claude Code to use the skills directory
3. Skills will be available based on their `user-invocable` setting

## Contributing

Contributions are welcome! When adding new skills:

- Follow the existing skill format
- Include clear trigger conditions
- Document all execution steps
- Define explicit success criteria
- Test the skill thoroughly before submitting

## License

MIT License
