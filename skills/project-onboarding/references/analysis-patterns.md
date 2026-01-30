# Analysis Patterns for Different Project Types

This reference provides specialized analysis approaches for common project archetypes.

## Node.js/JavaScript Projects

### Quick identification
```bash
ls package.json yarn.lock pnpm-lock.yaml
cat package.json | grep '"type":'  # Check if module or commonjs
```

### Key files to examine
- `package.json` - Dependencies, scripts, entry point
- `tsconfig.json` / `jsconfig.json` - TypeScript/module config
- `.eslintrc.*` / `.prettierrc` - Code style
- `webpack.config.js` / `vite.config.js` - Build config

### Common entry patterns
```bash
# Find main entry
cat package.json | grep '"main":\|"exports":'

# Common start patterns
grep -r "app.listen\|server.listen\|createServer" --include="*.js" --include="*.ts"
```

### Framework detection
```bash
# Check dependencies for frameworks
cat package.json | grep -E "express|fastify|koa|nest|next|nuxt|react|vue|angular"
```

## Python Projects

### Quick identification
```bash
ls requirements.txt setup.py pyproject.toml Pipfile
python --version  # Check system Python
```

### Key files to examine
- `requirements.txt` / `pyproject.toml` - Dependencies
- `setup.py` / `setup.cfg` - Package configuration
- `pytest.ini` / `tox.ini` - Test configuration
- `.python-version` - Python version requirement

### Common entry patterns
```bash
# Find main entry
grep -r "if __name__ == '__main__':" --include="*.py"

# Framework detection
grep -r "from flask\|from django\|from fastapi" --include="*.py" | head -5
```

## Java/Kotlin Projects

### Quick identification
```bash
ls pom.xml build.gradle settings.gradle
cat pom.xml | grep "<groupId>\|<artifactId>"  # Maven
cat build.gradle | grep "group\|version"      # Gradle
```

### Key files
- `pom.xml` - Maven dependencies
- `build.gradle` / `settings.gradle` - Gradle config
- `application.properties` / `application.yml` - Spring config

### Common patterns
```bash
# Find main class
find . -name "*.java" -exec grep -l "public static void main" {} \;

# Spring Boot detection
grep -r "@SpringBootApplication" --include="*.java"
```

## Go Projects

### Quick identification
```bash
ls go.mod go.sum
go version
```

### Key files
- `go.mod` - Module definition and dependencies
- `Makefile` - Common build tasks
- `cmd/` - Entry points (convention)

### Entry detection
```bash
# Find main packages
find . -name "main.go"
grep -r "func main()" --include="*.go"
```

## Rust Projects

### Quick identification
```bash
ls Cargo.toml Cargo.lock
rustc --version
```

### Key files
- `Cargo.toml` - Project manifest
- `build.rs` - Build script
- `src/main.rs` or `src/lib.rs` - Entry points

## Monorepo Projects

### Identification
```bash
# Lerna
ls lerna.json

# Nx
ls nx.json workspace.json

# Turborepo
ls turbo.json

# Yarn/pnpm workspaces
cat package.json | grep '"workspaces"'
```

### Analysis approach
1. Identify workspace structure from root config
2. List all sub-projects
3. Find shared dependencies
4. Identify inter-package dependencies

## Microservices

### Detection patterns
- Multiple `Dockerfile` files
- `docker-compose.yml` with multiple services
- Directories named like services (api/, web/, worker/)

### Analysis focus
1. Service boundaries (what does each service do?)
2. Communication patterns (REST/gRPC/message queue)
3. Shared infrastructure (databases, caches)
4. Service dependencies

## Frontend Applications

### React
```bash
grep "react" package.json
ls src/App.js src/App.tsx
```

### Vue
```bash
grep "vue" package.json
ls src/App.vue
```

### Angular
```bash
grep "@angular" package.json
ls angular.json
```

### Analysis focus
- Component structure
- State management (Redux/Vuex/Context)
- Routing configuration
- API integration patterns
- Build/bundle configuration

## CLI Tools

### Detection
```bash
# Check for bin entries
cat package.json | grep '"bin":'

# Python CLI
grep -r "click\|argparse\|typer" --include="*.py"

# Go CLI
grep -r "cobra\|cli" --include="*.go"
```

### Analysis focus
- Command structure
- Argument parsing
- Configuration file support
- Output formatting

## API Services

### REST API
```bash
# Route definitions
grep -r "router\|@app.route\|@Get\|@Post" --include="*.ts" --include="*.py" --include="*.java"
```

### GraphQL
```bash
grep -r "graphql\|@Resolver\|type Query" --include="*.ts" --include="*.graphql"
```

### Analysis focus
- Authentication/authorization
- Request validation
- Error handling
- Rate limiting
- API documentation (Swagger/OpenAPI)

## Database-Centric Applications

### ORM detection
```bash
# TypeORM
grep "typeorm" package.json

# Sequelize
grep "sequelize" package.json

# Prisma
ls prisma/schema.prisma

# SQLAlchemy
grep "sqlalchemy" requirements.txt

# Django ORM
find . -name "models.py"
```

### Analysis focus
- Schema definitions
- Migration strategy
- Connection pooling
- Query optimization patterns

## Legacy/Poorly Maintained Code Indicators

### High-risk signals
```bash
# Very old dependencies
cat package.json | grep '"[^"]*": "[~^]0\.[0-9]'

# No tests
[ -d test ] || [ -d tests ] || [ -d __tests__ ] || echo "No test directory"

# Git history gaps
git log --since="1 year ago" --oneline | wc -l

# Massive files
find . -type f -name "*.js" -exec wc -l {} \; | awk '$1 > 2000' | sort -rn
```

### Adaptation strategies
- Increase time estimates 2-3x
- Focus on getting it running first
- Document assumptions heavily
- Test changes more thoroughly
- Look for "God objects" or files doing everything
