# Quality Gate — Evaluation Criteria Reference

Detailed criteria for each of the 9 scopes. Read the relevant sections before analyzing.

---

## SCOPE A1 — AI/LLM USAGE

### Model Selection
- Is the model appropriate for task complexity? Frontier model for classification = wasteful.
- Opportunities to use smaller/cheaper models without quality loss?
- Vendor lock-in? Abstraction layer to swap providers?

### Prompt Quality
- Follows provider best practices (structured system prompt, few-shot, output format)?
- Appropriate parameterization (temperature, max_tokens, top_p)?
- Chain-of-thought, task decomposition, or structured output where beneficial?
- Prompts versioned and manageable, or hardcoded and scattered?

### AI Architecture
- Grounding/RAG used where helpful? Absent where needed?
- Data flow before/after model calls (input validation, output parsing, error handling)?
- Redundant calls that could be consolidated or cached?
- Retry with exponential backoff + jitter for 429/5xx? Centralized `retryWithBackoff()`?
  - Formula: `delay = min(maxDelay, initialDelay × 2^attempt) + random(0, delay)`
  - Max 3-5 retries, initial 1s, max 60s, jitter mandatory
  - Retryable: 429, 5xx, timeout, network. Non-retryable: 400, 401, 403, content blocked
  - Per-retry logging with attempt, delay, error code
- Parallel batch processing? Items split into 10-20 chunks, `Promise.allSettled()`,
  per-chunk retry, partial success handling?

### Cost & Efficiency
- Sequential API calls in loops? Replace with bounded concurrency pool (3-5 simultaneous)
- Smart-skip/staleness logic? Track `enrichedAt`, skip fresh items, `force=true` rare
- Cache effectiveness? Keys designed for hit rate, TTL aligned, survives restart?
- Token optimization? `temperature: 0` for extraction, `thinkingBudget: 0` for non-CoT,
  `maxOutputTokens` capped, `responseMimeType: 'application/json'` for structured output
- Frontend `fetch()` has `AbortController` timeout matching server-side timeout?

### AI Accessibility
- AI outputs presented with proper HTML semantics?
- AI-generated media has alt text?
- Prompts instruct accessible content when output is user-facing?
- AI response times communicated with aria-live and processing indicators?

### AI Security
- User inputs sanitized against prompt injection (direct and indirect)?
- Model outputs treated as untrusted data before rendering (XSS via LLM)?
- Tool/function calling follows least privilege?
- PII filtered before sending to model?
- AI route auth: OAuth only for Google API routes, rate limiting for server-key-only routes

---

## SCOPE A2 — ACCESSIBILITY & INCLUSIVE DESIGN

### Conformance
- WCAG 2.2 adherence (minimum AA). Critical (A) violations vs improvement (AA/AAA)
- WAI-ARIA: roles/states applied correctly? Excessive ARIA where semantic HTML suffices?
- Legal: ADA, EAA, Brazilian Inclusion Law 13.146/2015 (per target market)

### Technical Implementation
- Semantic HTML: landmarks, headings, lists, tables, labeled forms
- Keyboard: all interactive elements focusable/operable, logical tab order, no focus traps
- Contrast: 4.5:1 normal text, 3:1 large text and UI components
  - Tailwind opacity classes (e.g., `text-white/40`) often fail — calculate actual ratios
- Responsive: works at 200% zoom, content reflows
- Media: captions, transcripts, `prefers-reduced-motion` respected
- Forms: errors programmatically associated, validations communicated accessibly
- Dynamic components: modals/tabs/accordions follow APG

### Animation Library A11y (Motion/Framer Motion)
- CSS animations use `prefers-reduced-motion` media query
- JS animations (motion.div) require explicit `useReducedMotion()` check
- Ease arrays need `as const` for TypeScript tuple compatibility

### Skip Navigation & Landmarks
- Skip-to-content link as first focusable element
- `<main id="main-content">` matching skip link href
- `<html lang="pt-BR">` (or correct lang) for screen reader pronunciation
- Heading hierarchy without gaps

### Modal Accessibility
- All modals use shared accessible Modal primitive (if one exists)
- Focus trap: Tab wraps, Shift+Tab wraps, Escape closes, focus returns to trigger

### Inclusive Design
- Diversity of contexts (slow connections, old devices, small screens, noisy environments)
- No sole reliance on color to convey information
- Neurodiversity considerations (predictable interfaces, information density control)
- i18n: RTL support, long-word behavior, localized formats

---

## SCOPE A3 — SCALABLE CLOUD-NATIVE ARCHITECTURE

### Architecture Principles
- 12-Factor App adherence (which factors met, which not)
- Stateless? If state exists, where and how managed?
- Separation of concerns (presentation, business logic, data, integration)
- Horizontal scaling support? Vertical bottleneck components?

### Infrastructure & Deploy
- IaC (Terraform, Pulumi, CDK)?
- Containerized? Dockerfile best practices (multi-stage, minimal, non-root, .dockerignore)?
- CI/CD with tests, linting, security scanning, automated deploy?
- Deploy strategy (blue-green, canary, rolling)? Fast rollback?
- Environment isolation/parity (dev, staging, prod)?

### Resilience & Availability
- Health checks (liveness + readiness probes)?
- Circuit breaker for external dependencies?
- Timeouts for network calls?
- Graceful shutdown: SIGTERM handler → `server.close()` → forced exit after timeout
- In-memory state inventory: what's lost on restart? Externalize if critical
- Dead letter queues? Idempotency?

### Performance & Scalability
- Caching: where used, where should be, invalidation strategy?
- Database: optimized queries, indexes, connection pooling?
- CDN for static assets?
- Rate limiting on exposed APIs?
- Lazy loading and code splitting (frontend)?

### Observability
- Structured logging with correlation IDs?
- Business + technical metrics (Prometheus, CloudWatch, etc.)?
- Distributed tracing (OpenTelemetry)?
- Alerts for critical SLIs/SLOs?

---

## SCOPE S1 — APPLICATION SECURITY

### AppSec (OWASP Top 10)
- Input validation: all user inputs validated server-side
- Injection (SQL, NoSQL, OS command, LDAP)
- Broken auth and session management
- XSS (stored, reflected, DOM-based)
- Broken access control / IDOR
- Security misconfiguration
- Sensitive data exposure
- CSRF, SSRF

### Headers & Policy
- CSP properly configured (Firebase/Google apps need specific connect-src, frame-src)
- HSTS, X-Content-Type-Options, X-Frame-Options, Referrer-Policy, Permissions-Policy
- Environment variable injection in server templates → XSS if attacker-controlled

### Authentication & Authorization
- OAuth 2.0/OIDC, MFA, brute force protection
- Token expiration, refresh rotation, revocation
- RBAC/ABAC with server-side checks on every endpoint
- Least privilege consistently applied

### Data Protection
- Encryption at rest and in transit (TLS 1.2+)
- PII per applicable regulations (LGPD, GDPR)
- Sensitive data excluded from logs/errors/stack traces
- Backup encryption, data retention/deletion mechanism

### File Upload
- Server-side MIME whitelist (never trust client)
- Size limits enforced server-side
- Magic byte validation
- No path traversal in filenames

---

## SCOPE S2 — CONFIG & SECRETS HYGIENE

### Configuration Validation
- Validated config objects (Pydantic Settings, Joi, Zod)?
- Centralized secret lookups in single module?
- Fail-fast on missing required secrets at startup?

### Secret Leakage Prevention
- `.gitignore` covers `.env`, `credentials.json`, `*.key`, `history.db`?
- No private keys exposed in frontend JS?
- Multi-tenant safety: user tokens separate from system tokens?

### Cookie Security
- Values encrypted server-side (AES-256-GCM)?
- Migration-safe decryption (fallback to plaintext for rollout)?
- Every `res.cookie()` sets `secure: true` in prod?
- `sameSite: 'lax'` minimum. `'none'` requires `secure: true`
- All cookie ops through centralized helpers (`setTokenCookie`/`readTokenCookie`)

### Rate Limiting
- Per-route tiered limits (general 200/15min + AI 60/15min)?
- `X-RateLimit-*` headers for graceful client backoff?
- Applied to unauthenticated endpoints too?

### Auth Middleware Placement
| Route needs... | Auth approach |
|----------------|---------------|
| Google API tokens (Gmail, Drive, Sheets) | Full OAuth middleware |
| Server-side API key only (Gemini) | Rate limiter + optional session check |
| Public data (health, static) | No auth |

### Health & Shutdown
- `/healthz` returns quickly without external deps (liveness)?
- SIGTERM handler → `server.close()` → forced exit (10s)?
- In-memory state inventory: Maps, caches, sessions — acceptable to lose?

### SSRF & Upload Protection
- URL-accepting endpoints validate against private IP ranges
- DNS resolution before IP check (hostname can resolve to private)
- Protocol: only http/https allowed

### Dependency Security
- Vulnerability scanning (Dependabot, Snyk, Trivy)?
- Lock files committed?
- Container base images from trusted sources?
- SBOM capability?

---

## SCOPE H1 — CODE STRUCTURE

### File Size Distribution
| LOC Range | Category | Action |
|-----------|----------|--------|
| <150 | Focused | None |
| 150-300 | Moderate | Monitor |
| 300-400 | Large | Plan decomposition |
| 400-500 | Oversized | Decompose this cycle |
| >500 | Bloated | Immediate priority |

OSS benchmarks: Excalidraw ~200 LOC avg, React core <300 LOC, Express <500 LOC per file.

### Duplication Detection
- Exact clones, parametric clones, structural clones
- Target: <5% duplication ratio (SonarQube)
- Check: utils copy-pasted between frontend/backend, validation logic, API call patterns

### Embedded Sub-Components
- Named components defined inside another component's file
- Helper components >30 LOC
- Modals embedded in trigger components

### Abstraction Opportunities
- Multiple API routes with identical structure
- Repeated state management across hooks
- Duplicated error handling chains

### Dead Code
- Exports with zero importers
- Orphaned test files for deleted sources
- Commented-out blocks, abandoned feature flags

### Module Coupling
- Files with >10 imports = coupling hotspots
- Circular dependencies = architecture smell
- Layer violations (utils importing from components)
- Clean hierarchy: Components → Hooks → Services → Utils

### Reliability Patterns
Rate each as: Present & Tested / Present & Untested / Partial / Missing
- Frontend: Error Boundary, loading/empty/error states, resource cleanup
- Backend: Global error handler, structured logging, input validation, rate limiting,
  retry with backoff, graceful shutdown, health endpoint, cookie encryption, CSP/HSTS

### Runtime Efficiency
- Sequential API calls in loops → concurrency pool
- Smart-skip/staleness for batch operations
- Cache hit rate and key design
- Cost per AI feature (calls per user action)

### Complexity Metrics
| Metric | Threshold | Source |
|--------|-----------|--------|
| Cyclomatic complexity | <10/function | NIST |
| Cognitive complexity | <15/function | SonarQube |
| Max function length | <50 lines | Clean Code |
| Max parameters | <5/function | Clean Code |
| Nesting depth | <4 levels | Industry |

---

## SCOPE T1 — TEST QUALITY

### Coverage Metrics
Run `npx vitest run --coverage` or `npx jest --coverage` or `pytest --cov`.
Extract: statements, branches, functions, lines — aggregate and per-file.

### Test-to-Source Mapping
For every source file: has test? Coverage %? Risk if untested?
- CRITICAL: state management, data pipelines, auth flows
- HIGH: primary UI, API routes, services
- MEDIUM: secondary UI, utilities with complexity
- LOW: simple components, types, config

### Anti-Pattern Detection
- `fireEvent` instead of `userEvent`
- Text queries instead of semantic queries (getByRole, getByLabelText)
- Heavy mocking (entire contexts/providers)
- Happy-path-only testing
- Stale test files for deleted source modules
- Hardcoded dashboard stats instead of computed values

### Testing Trophy Distribution
| Layer | Ideal | What counts |
|-------|-------|-------------|
| Static Analysis | Foundation | TypeScript, ESLint |
| Unit | ~25% | Isolated functions |
| Integration | ~50% | Multiple modules, real providers |
| E2E | ~15% | Full browser |
| Accessibility | ~10% | axe-core, keyboard nav |

---

## SCOPE T2 — TESTING INFRASTRUCTURE

### Framework & Tooling
- Appropriate for language/project? Current and maintained?
- Parallel execution, selective running, watch mode?
- Assertion library producing useful error messages?
- Mocking approach consistent? Not overused?

### CI/CD Pipeline
- Tests on every push/PR? Expensive tests gated differently?
- Speed: <10 min target, >30 min = serious drag
- Parallelism, caching, fail-fast, artifact storage?
- Branch protection: merge blocked on failures?

### Test Environment
- Isolation: tests run in parallel without interference?
- External deps: mocked, stubbed, containerized, or in-memory?
- Data setup/teardown reliable? Tests independent of order?
- Secrets managed safely in test environments?

### Reliability & Flakiness
- Timing-dependent tests (sleep, real clock)?
- Order-dependent tests?
- Network-dependent tests?
- Shared global state?
- Quarantine process for flaky tests?

### Stale Test Maintenance
- Orphaned test files importing deleted source modules
- Stale mock configurations for refactored APIs
- Process: search for importers when deleting/renaming source files

---

## SCOPE T3 — TEST COVERAGE DIMENSIONS

Multi-dimensional — a project with 90% line coverage can have zero integration tests.

- **Unit**: line/branch/function metrics, distribution, business logic, edge cases
- **Integration**: API endpoints, database, service interactions, message queues
- **E2E**: critical user journeys, cross-browser/device, scope discipline
- **Contract**: API schema validation, backward compatibility
- **Performance**: load tests, stress tests, performance regression detection
- **Security**: SAST, DAST, dependency scanning, auth/authz boundary tests
- **Accessibility**: automated (axe-core), screen reader, keyboard nav
- **Error/Edge**: failure scenarios, graceful degradation, retry idempotency, concurrency
- **Regression**: bug-to-test pipeline, release suite, visual regression
- **Runtime Efficiency**: sequential API detection, smart-skip tests, cache tests, cost regression
- **Firestore/DB Rules**: security rules tested with emulator, new collection rules

---

## SCOPE M1 — DOCUMENTATION STRATEGY

### Code-Level
- Naming quality: intent without comments?
- Inline comments: why, not what?
- Type annotations as documentation?
- Constants/enums for magic numbers?
- TODO/FIXME inventory: tracked? Owners?

### API Documentation
- OpenAPI/Swagger? Auto-generated or manual (stale risk)?
- Request/response examples? Error codes documented?
- Versioning documented? Deprecations communicated?

### Architecture Documentation
- ADRs: exist? Maintained? Capture why + alternatives + tradeoffs?
- System diagrams: current? (C4 model levels)
- Data model documented? Entity relationships? Lifecycle rules?
- Integration docs: contracts, SLAs, failure modes, fallbacks?
- Staleness: when last updated? Outdated docs actively mislead.

### Operational Documentation
- Runbooks for common ops (deploy, rollback, scale, rotate secrets)?
- Incident response process?
- Alert definitions with meaning, severity, response actions?

### Onboarding Documentation
- README answers: what? setup? run? test? contribute?
- Single-command setup (`make setup`, `docker compose up`)?
- `.env.example` with descriptions?
- Contributing guide (branch naming, commit conventions, PR process)?

---

## SCOPE M2 — REPOSITORY & PROJECT HEALTH

### Structure & Navigability
- Intuitive directory organization?
- Consistent naming conventions?
- Clear separation of source/test/config/docs/scripts/infra?
- Dead files, empty directories?

### Git Workflow
- Commit messages: descriptive, following convention (Conventional Commits)?
- Atomic commits (one logical change each)?
- Branch strategy (trunk-based, gitflow, GitHub flow)?
- PR discipline: small, focused, reviewed?
- Protected branches, no force-push to main?

### GitHub Features
- Issues for tracking work? Labels/categories?
- PR templates guiding reviewers?
- GitHub Actions for CI/CD, linting, security?
- Releases tagged with changelogs?
- CODEOWNERS mapping code areas to teams?

### Dependency Management
- Lock files committed and consistent?
- Dependency freshness? Known vulnerabilities?
- Automated updates (Dependabot, Renovate)?
- License compliance? Unused dependencies?

### Contribution Friction (Clone-to-PR Test)
1. Clone: special access needed?
2. Setup: how many manual steps? Automated?
3. Understand: can newcomer find what to change?
4. Test: can they verify locally?
5. Submit: PR process documented? Review turnaround?

Red flags: >3 manual setup steps, tests only in CI, no contributing guide, PRs sit unreviewed.

---

## CROSS-CUTTING: DOCUMENTATION-TEST ALIGNMENT

After analyzing docs and tests independently, cross-reference:

| Behavior | Documented? | Tested? | Risk |
|----------|-------------|---------|------|
| User auth | Yes | Yes | Low |
| Rate limiting rules | No | Yes | Medium — unverified |
| Data retention | Yes | No | Medium — undocumented |
| Failover behavior | No | No | **Critical — tribal knowledge only** |

Focus on the "neither documented nor tested" quadrant — highest risk.
