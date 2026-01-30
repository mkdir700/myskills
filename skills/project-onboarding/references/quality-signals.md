# Code Quality Signals Detection

Commands and patterns for identifying code quality issues, especially in poorly maintained codebases.

## Structural Quality Signals

### File Size Analysis
```bash
# Find large files (complexity indicator)
find . -type f \( -name "*.js" -o -name "*.ts" -o -name "*.py" -o -name "*.java" \) \
  -exec wc -l {} \; | awk '$1 > 500 {print $1 " " $2}' | sort -rn

# Interpretation:
# 500-1000 lines: Medium complexity, consider splitting
# 1000-2000 lines: High complexity, likely needs refactoring
# 2000+ lines: God object, significant technical debt
```

### Directory Depth (over-engineering indicator)
```bash
# Find deeply nested directories
find . -type d | awk -F/ 'NF > 8 {print NF-1 " " $0}' | sort -rn | head -10

# Interpretation:
# >8 levels: Possible over-abstraction
# >10 levels: Definitely over-engineered
```

## Code Maintenance Signals

### TODO/FIXME Density
```bash
# Count by file
find . -type f \( -name "*.js" -o -name "*.ts" -o -name "*.py" \) \
  -exec grep -c "TODO\|FIXME\|HACK\|XXX\|BUG" {} \; \
  2>/dev/null | awk -F: '$2 > 0 {sum+=$2; count++} END {print "Total:", sum, "Avg per file:", sum/count}'

# Get top files
find . -type f \( -name "*.js" -o -name "*.ts" -o -name "*.py" \) \
  -exec grep -Hn "TODO\|FIXME\|HACK\|XXX" {} \; | \
  cut -d: -f1 | sort | uniq -c | sort -rn | head -10

# Interpretation:
# 1-5 per file: Normal development
# 5-20 per file: Moderate technical debt
# 20+ per file: High technical debt, needs cleanup
```

### Commented-Out Code
```bash
# JavaScript/TypeScript
find . -name "*.js" -o -name "*.ts" | xargs grep -c "^[[:space:]]*\/\/" | \
  awk -F: '$2 > 30 {print $1 ": " $2 " comment lines"}' | sort -t: -k2 -rn

# Python
find . -name "*.py" | xargs grep -c "^[[:space:]]*#" | \
  awk -F: '$2 > 30 {print $1 ": " $2 " comment lines"}' | sort -t: -k2 -rn

# Check for commented-out blocks
grep -rn "\/\*.*\*\/" --include="*.js" --include="*.ts" | wc -l

# Interpretation:
# High comment density might indicate:
# - Dead code not removed
# - Debugging statements left in
# - Fear of deleting old code
```

### Dead Code Artifacts
```bash
# Find backup/old/temp files
find . \( \
  -name "*backup*" -o \
  -name "*old*" -o \
  -name "*.bak" -o \
  -name "*~" -o \
  -name "*.orig" -o \
  -name "*temp*" -o \
  -name "*tmp*" -o \
  -name "Copy of*" \
  \) -type f 2>/dev/null

# Find duplicate files (by name pattern)
find . -type f -name "*.js" | sed 's/\.[0-9]*\.js$/.js/' | sort | uniq -d

# Interpretation:
# Presence indicates:
# - Poor cleanup habits
# - Lack of version control confidence
# - Fear of losing code
```

## Naming and Convention Issues

### Inconsistent File Naming
```bash
# Check for mixed naming conventions
find src -name "*.ts" -o -name "*.js" | while read f; do
  basename "$f" | sed 's/\.[^.]*$//'
done | awk '
  /-/ { kebab++ }
  /_/ { snake++ }
  /^[a-z][a-zA-Z0-9]*$/ && !/-/ && !/_/ { camel++ }
  /^[A-Z]/ { pascal++ }
  END {
    print "camelCase:", camel
    print "kebab-case:", kebab
    print "snake_case:", snake
    print "PascalCase:", pascal
  }
'

# Interpretation:
# All same: Good consistency
# 2 styles with clear pattern: Acceptable if intentional
# 3+ styles mixed randomly: Inconsistent team practices
```

### Variable Naming Quality
```bash
# Find single-letter variables (outside loops)
grep -rn "\b[a-z]\s*=" --include="*.js" --include="*.ts" | \
  grep -v "for.*i\s*=" | grep -v "for.*j\s*=" | head -20

# Find excessive abbreviations
grep -rn "\b[a-z]{1,2}[A-Z]" --include="*.js" --include="*.ts" | head -20

# Interpretation:
# Many single-letter vars outside loops: Poor readability
# Lots of abbreviations: Inconsistent naming standards
```

## Dependency Health

### Outdated Dependencies
```bash
# npm
npm outdated --depth=0

# Check for ancient versions (< 1.0 or very old)
cat package.json | grep -E '"[^"]*": "[~^]0\.[0-9]'

# Python
pip list --outdated 2>/dev/null || echo "pip check failed"

# Interpretation:
# Red/major version behind: Security risks
# Many outdated: Not actively maintained
# 0.x versions: Unstable dependencies
```

### Dependency Count
```bash
# npm
cat package.json | jq '.dependencies | length'
cat package.json | jq '.devDependencies | length'

# Python
cat requirements.txt | grep -v '^#' | grep -v '^$' | wc -l

# Interpretation:
# <20 dependencies: Lean
# 20-50: Normal
# 50-100: Heavy, audit needed
# 100+: Dependency hell, likely bloated
```

### Duplicate Dependencies
```bash
# npm duplicates
npm dedupe --dry-run

# Check for similar packages
cat package.json | jq -r '.dependencies | keys[]' | sort | \
  awk '{a=$0; gsub(/-/,"",a); print a, $0}' | sort | \
  uniq -w 10 -D | cut -d' ' -f2-

# Interpretation:
# Many duplicates: Inefficient bundling
# Similar packages: Might consolidate functionality
```

## Testing Quality

### Test Coverage Indicators
```bash
# Find test files
find . \( \
  -name "*.test.js" -o \
  -name "*.test.ts" -o \
  -name "*.spec.js" -o \
  -name "*.spec.ts" -o \
  -name "*_test.py" \
  \) 2>/dev/null | wc -l

# Source to test ratio
src_files=$(find src -name "*.ts" -o -name "*.js" | wc -l)
test_files=$(find . -name "*.test.ts" -o -name "*.spec.ts" | wc -l)
echo "Source files: $src_files, Test files: $test_files"

# Interpretation:
# Test ratio < 0.3: Low coverage, risky changes
# Test ratio 0.3-0.7: Decent coverage
# Test ratio > 0.7: Good coverage
# No tests at all: Legacy code, test before touching
```

### Test Quality
```bash
# Find empty test files
find . -name "*.test.*" -o -name "*.spec.*" | \
  xargs wc -l | awk '$1 < 10 {print $2 " (too small)"}'

# Find skipped tests
grep -rn "describe.skip\|it.skip\|test.skip\|@skip" --include="*.test.*" --include="*.spec.*"

# Mock density (might indicate brittleness)
grep -rn "mock\|stub\|spy" --include="*.test.*" --include="*.spec.*" | wc -l

# Interpretation:
# Empty test files: Scaffolding without implementation
# Many skipped tests: Flaky or broken tests
# High mock density: Possibly over-mocked, brittle tests
```

## Security Warning Signs

### Hardcoded Secrets
```bash
# Find potential secrets (not exhaustive!)
grep -rni "password\s*=\s*['\"]" --include="*.js" --include="*.ts" --include="*.py"
grep -rni "api[_-]key\s*=\s*['\"]" --include="*.js" --include="*.ts" --include="*.py"
grep -rni "secret\s*=\s*['\"]" --include="*.js" --include="*.ts" --include="*.py"
grep -rni "token\s*=\s*['\"]" --include="*.js" --include="*.ts" --include="*.py"

# Check for .env in git
git ls-files | grep "\.env$"

# Interpretation:
# Any hardcoded credentials: Critical security issue
# .env in git: Secrets exposed in history
```

### Dangerous Patterns
```bash
# SQL injection risks
grep -rni "execute.*\+\|query.*\+" --include="*.js" --include="*.ts" --include="*.py" | head -10

# Command injection risks
grep -rni "exec\|system\|spawn" --include="*.js" --include="*.ts" --include="*.py" | \
  grep -v "execSync" | head -10

# eval usage
grep -rni "\beval\(" --include="*.js" --include="*.ts" | head -10

# Interpretation:
# String concatenation in queries: SQL injection risk
# User input in exec: Command injection risk
# eval usage: Code injection risk
```

## Git History Signals

### Activity Patterns
```bash
# Recent activity
git log --since="6 months ago" --oneline | wc -l

# Contributor count
git log --format='%ae' | sort -u | wc -l

# Large commits (might indicate bulk changes or merges)
git log --oneline --all --shortstat | \
  awk '/files? changed/ {files+=$1; inserted+=$4; deleted+=$6} \
       /^[a-f0-9]{7}/ {if (files>100) print commit, files, inserted, deleted; files=0; inserted=0; deleted=0; commit=$0}'

# Interpretation:
# <10 commits in 6 months: Abandoned project
# 1 contributor: Bus factor of 1
# Many massive commits: Poor commit hygiene
```

### Commit Message Quality
```bash
# Check commit message patterns
git log --oneline -50 | awk '{$1=""; print $0}' | sort | uniq -c | sort -rn | head -10

# Find vague messages
git log --oneline -50 | grep -iE "fix|update|changes|stuff|wip|tmp"

# Interpretation:
# Generic messages: Poor documentation
# Many "WIP" commits: Messy history
# No pattern: No commit conventions
```

## Configuration Issues

### Missing Configuration Examples
```bash
# Check for env examples
ls .env.example .env.sample .env.template 2>/dev/null || \
  echo "⚠️ No environment variable examples"

# Check if .env is gitignored
git check-ignore .env 2>/dev/null && echo "✅ .env is gitignored" || \
  echo "❌ .env is NOT gitignored (RISK)"

# Interpretation:
# No .env.example: New developers struggle with setup
# .env not ignored: Risk of committing secrets
```

### Build Configuration Complexity
```bash
# Count build config files
find . -maxdepth 2 \( \
  -name "webpack*.js" -o \
  -name "rollup*.js" -o \
  -name "vite*.js" -o \
  -name "tsconfig*.json" -o \
  -name "babel*.js" \
  \) | wc -l

# Interpretation:
# 0-2 files: Simple build
# 3-5 files: Moderate complexity
# 6+ files: Complex build, multiple environments
```

## Performance Indicators

### Bundle Size Concerns
```bash
# Check for large dependencies
du -sh node_modules/* 2>/dev/null | sort -rh | head -10

# Find large source files
find src -type f -name "*.js" -o -name "*.ts" | \
  xargs du -h | sort -rh | head -10

# Interpretation:
# node_modules > 500MB: Heavy dependencies
# Source files > 1MB: Minification issues or data in code
```

### Database Query Patterns
```bash
# Find potential N+1 queries
grep -rn "for.*await\|\.map.*await" --include="*.js" --include="*.ts"

# Find missing indexes (naive check)
grep -rni "where.*=.*and\|where.*like" --include="*.sql" | wc -l

# Interpretation:
# Loops with async: Potential N+1 queries
# Many complex WHERE clauses: Check if indexed
```

## Documentation Quality

### README Quality
```bash
# Check README length
wc -l README.md 2>/dev/null || echo "No README"

# Check for key sections
grep -i "installation\|setup\|getting started\|usage\|examples" README.md

# Interpretation:
# <50 lines: Minimal docs
# No setup section: Hard for new developers
```

### Inline Documentation
```bash
# JSDoc/TSDoc coverage
grep -r "\/\*\*" --include="*.ts" --include="*.js" | wc -l

# Python docstrings
grep -r '"""' --include="*.py" | wc -l

# Functions without docs
grep -rn "^function \|^export function \|^async function" --include="*.ts" | wc -l

# Interpretation:
# Low doc-to-function ratio: Poor inline documentation
```
