# Recovery Strategies for Poorly Documented Projects

Tactics for understanding projects that lack documentation, tests, or clear structure.

## When Documentation is Missing

### Reverse Engineer from Git History
```bash
# Find the initial commit
git log --reverse --oneline | head -5

# Check initial file structure
git show $(git rev-list --max-parents=0 HEAD):

# Find when key files were added
git log --diff-filter=A --name-only --pretty=format: | \
  grep -E "server\.|app\.|main\.|index\." | head -10

# Read early commit messages for context
git log --reverse --oneline -20
```

**Rationale**: Early commits often reveal the project's original intent and core architecture before complexity accumulated.

### Extract Intent from Package Names
```bash
# Analyze dependency purposes
cat package.json | jq -r '.dependencies | keys[]' | while read pkg; do
  echo "$pkg: $(npm info $pkg description 2>/dev/null | head -1)"
done

# Group by category
cat package.json | jq -r '.dependencies | keys[]' | \
  grep -E "express|koa|fastify" && echo "→ Web framework" || true
cat package.json | jq -r '.dependencies | keys[]' | \
  grep -E "sequelize|typeorm|prisma" && echo "→ ORM/Database" || true
```

**Rationale**: Dependencies reveal architectural decisions and technical approach.

### Mine Tests for Examples
```bash
# Find test files
find . -name "*.test.*" -o -name "*.spec.*"

# Extract tested functions to understand API
grep -rh "describe\|it\|test(" --include="*.test.*" --include="*.spec.*" | \
  head -30 | sed 's/.*[("'"'"']//' | sed 's/["'"'"'].*//'

# Look for integration tests (reveal workflows)
grep -rn "request\|supertest\|http" --include="*.test.*" -A 5
```

**Rationale**: Tests document expected behavior and usage patterns.

### Trace from Entry Points
When README is useless, work backward from execution:

```bash
# 1. Find entry point
cat package.json | jq -r '.main'
cat package.json | jq -r '.scripts.start'

# 2. Open that file and trace imports
# For each import, open and repeat

# 3. Build a call graph manually or using tools:
npm install -g madge
madge --image graph.png src/index.ts
```

**Strategy**: Map the code by following execution flow rather than reading alphabetically.

## When Code Structure is Chaotic

### Create Your Own Map
```bash
# Generate directory tree with line counts
tree -L 3 --du -h src/ > structure.txt

# Or more detailed:
find src -type f -name "*.ts" -o -name "*.js" | while read f; do
  lines=$(wc -l < "$f")
  printf "%5d lines  %s\n" "$lines" "$f"
done | sort -rn > code_inventory.txt
```

**Use this to**:
1. Identify the largest files (likely core functionality)
2. Find naming patterns
3. Spot missing organization

### Group Files by Coupling
```bash
# Find files that frequently import each other
grep -rh "^import.*from ['\"]\..*['\"]" src/ | \
  sed "s/.*from ['\"]//;s/['\"].*//" | sort | uniq -c | sort -rn | head -20

# This reveals:
# - Core modules (imported everywhere)
# - Tight coupling (mutual imports)
# - Module boundaries (or lack thereof)
```

### Identify Architectural Layers (When Unclear)
```bash
# Look for layer indicators in imports
grep -rh "import.*from" src/ | grep -oE "(model|service|controller|route|util|helper|lib)" | \
  sort | uniq -c

# Even in chaos, patterns emerge:
# High count of "service" → Likely service layer
# "controller" + "route" → MVC-ish
# Only "util" → Functional/unstructured
```

## When Tests are Absent

### Create Smoke Tests First
Before understanding the system, verify it works at all:

```bash
# 1. Can it start?
timeout 10s npm start

# 2. Does it respond?
curl -f http://localhost:3000 || echo "Failed"

# 3. What endpoints exist?
# If Express:
grep -rn "app\.\(get\|post\|put\|delete\)" src/ | \
  sed 's/.*\.\(get\|post\|put\|delete\)(['"'"'"]/\1 /' | \
  sed 's/['"'"'"].*//' | sort -u

# 4. Try each endpoint manually
```

### Generate Test Hypotheses from Code
```bash
# Find functions that look testable
grep -rn "^export \(function\|const\)" --include="*.ts" | \
  grep -v "\.test\." | head -20

# For each, infer:
# - What inputs does it take?
# - What does it return?
# - What are edge cases?

# Write minimal tests to validate understanding
```

### Use Runtime Observation
```bash
# Add logging to understand behavior
# Insert at strategic points:
console.log('DEBUG: function X called with:', JSON.stringify(args))

# Run the app and exercise features
# Watch logs to understand flow
```

**When safe to add logs**:
- Before return statements
- At function entry points
- Around external calls (DB, API)

## When Architecture is Unclear

### Infer from Data Flow
```bash
# 1. Find database/ORM usage
grep -rn "SELECT\|INSERT\|UPDATE\|DELETE" --include="*.ts" | head -5
grep -rn "\.find\|\.create\|\.update\|\.save" --include="*.ts" | head -5

# 2. Find HTTP requests (external APIs)
grep -rn "fetch\|axios\|request\|http\." --include="*.ts" | head -5

# 3. Find file I/O
grep -rn "readFile\|writeFile\|fs\." --include="*.ts" | head -5

# Architecture emerges:
# DB + HTTP → Backend service
# Many fetches → API aggregator
# File I/O → Data processing
```

### Detect Patterns from Naming
```bash
# Look for convention hints
ls src/ | grep -i "controller\|service\|repository\|model"

# Even if inconsistent, majority rules:
find src -type f | sed 's|.*src/||;s|/.*||' | sort | uniq -c | sort -rn
```

### Analyze Import Graphs
```bash
# Create dependency graph
npm install -g dependency-cruiser
depcruise --output-type dot src | dot -T svg > deps.svg

# Layers emerge as clusters:
# - Controllers import services
# - Services import repositories  
# - Repositories import models
```

## When Debugging is Difficult

### Instrument Liberally
Add logging at every layer boundary:

```javascript
// Wrap all async functions
const original = SomeService.someMethod
SomeService.someMethod = async (...args) => {
  console.log(`[${new Date().toISOString()}] someMethod called:`, args)
  const result = await original.apply(this, args)
  console.log(`[${new Date().toISOString()}] someMethod returned:`, result)
  return result
}
```

### Use Git Bisect to Understand History
```bash
# When did this feature break/change?
git bisect start
git bisect bad HEAD
git bisect good <known-good-commit>

# Git will help you find when behavior changed
# Reading that commit explains the feature
```

### Leverage IDE Tools
```bash
# VS Code: Find all references
# - Right-click function → "Find All References"
# - Shows where/how it's used

# TypeScript: Use "Go to Definition" aggressively
# - Even without tests, types document intent
```

## When Dependencies are Broken

### Lock Down Working Versions
```bash
# If it works now, preserve it
npm ci  # Use exact versions from lock file

# If lock file is broken:
npm install --package-lock-only  # Regenerate lock
git add package-lock.json
git commit -m "Lock working dependency versions"
```

### Isolate Dependency Issues
```bash
# Remove all deps and add back one by one
mv node_modules node_modules.bak
mv package-lock.json package-lock.json.bak

npm install <one-critical-dep>
npm start  # Does it work?

# Binary search to find the problematic dep
```

### Use Docker for Consistency
```bash
# Create Dockerfile to encapsulate working environment
cat > Dockerfile << 'EOF'
FROM node:14
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
CMD ["npm", "start"]
EOF

# Now environment is reproducible
docker build -t myapp .
docker run -p 3000:3000 myapp
```

## When Environment Setup Fails

### Discover Required Environment Variables
```bash
# Grep for process.env usage
grep -rn "process\.env\." --include="*.ts" --include="*.js" | \
  sed 's/.*process\.env\.//' | sed 's/[^A-Z_].*//' | sort -u

# Create .env with placeholders
grep -rn "process\.env\." --include="*.ts" --include="*.js" | \
  sed 's/.*process\.env\.//' | sed 's/[^A-Z_].*//' | sort -u | \
  awk '{print $0 "=CHANGEME"}' > .env.template
```

### Find Minimal Working Config
```bash
# Start with empty .env
touch .env

# Run and collect errors
npm start 2>&1 | grep -i "undefined\|not found\|missing"

# Add variables one by one until it starts
```

### Check for Implicit Requirements
```bash
# Global packages needed?
grep -rn "require.*\^" --include="*.js"

# System packages?
cat package.json | grep -A 10 "engines\|os"

# Database?
grep -rn "DATABASE\|POSTGRES\|MONGO\|REDIS" --include="*.ts" --include="*.js"
```

## When You're Completely Lost

### Talk to Git
```bash
# Who knows this code?
git shortlog -sn

# Contact them: git log --author="Name" --format="%ae" | head -1

# What were they doing recently?
git log --author="Name" --oneline -20

# Read their commit messages for context
git log --author="Name" --grep="<keyword>" -p
```

### Find Similar Projects
```bash
# Use dependencies to find similar projects
cat package.json | jq -r '.dependencies | keys[]' | \
  head -5 | xargs -I {} echo "https://github.com/search?q={}"

# Study their structure
# Copy their patterns
```

### Reduce Scope Drastically
```bash
# Strip everything to minimal:
# 1. Comment out all routes except one
# 2. Comment out all middleware
# 3. Hard-code config
# 4. Remove external dependencies (mock them)

# Get THIS to work:
curl http://localhost:3000/health
# Response: {"status":"ok"}

# Then add back one piece at a time
```

## Documenting Your Findings

As you discover things, document immediately:

```bash
# Create DISCOVERY.md in repo root
cat > DISCOVERY.md << 'EOF'
# Project Discovery Notes

## Architecture (as discovered)
[Your findings]

## Setup Process (that actually works)
[Step by step]

## Key Files
[List with explanations]

## Gotchas
[Problems and solutions]

## Questions
[Unanswered questions]
EOF

# Update as you learn
# Share with team
```

This becomes the documentation the project lacked.

## Recovery Checklist

When faced with undocumented code:

- [ ] Clone and try to run (document exact steps)
- [ ] Check git history for context
- [ ] Map dependencies to understand tech stack
- [ ] Find entry point and trace execution
- [ ] Create architectural diagram (even rough)
- [ ] Identify and list all environment variables
- [ ] Document a working setup process
- [ ] Write smoke tests to prevent regression
- [ ] Start DISCOVERY.md to capture learnings
- [ ] Ask git blame for code authors if stuck

Remember: The goal isn't to understand everything immediately, but to create enough scaffolding to make progress safely.
