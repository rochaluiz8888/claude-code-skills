---
name: quality-gate
description: >
  Unified codebase quality audit with 9 non-overlapping scopes. Covers AI/LLM usage,
  accessibility, architecture, security, structural health, test quality, testing
  infrastructure, documentation, and repository health. Produces a structured report
  with maturity ratings and prioritized recommendations.
  Use when the user asks to audit, review, assess, or analyze any aspect of code quality:
  "audit the app", "check security", "review tests", "how maintainable is this",
  "check accessibility", "codebase health", "what should we refactor". Adapts scope
  based on arguments — run with no args for a full audit, or specify a focus area.
argument-hint: [security|testing|ai|a11y|architecture|docs|repo-health|structure|quick]
---

# Quality Gate — Unified Codebase Audit

Produce a structured analysis report. Scope is determined by `$ARGUMENTS`:

| Argument | Scopes Activated | When to Use |
|----------|-----------------|-------------|
| _(empty)_ | All 9 scopes | Full audit |
| `security` | S1 + S2 | Security posture + config hygiene |
| `testing` | T1 + T2 + T3 | Test quality + infrastructure + coverage |
| `ai` | A1 | AI/LLM integration |
| `a11y` | A2 | Accessibility & inclusive design |
| `architecture` | A3 | Cloud-native architecture & scalability |
| `docs` | M1 | Documentation strategy |
| `repo-health` | M2 | Repository & project health |
| `structure` | H1 | Structural health (LOC, duplication, coupling) |
| `quick` | Top-3 critical findings across all scopes | Fast triage |

## Before You Start

1. **Explore the codebase.** Use `Glob`, `Grep`, `Read`, `Bash` to understand structure,
   stack, dependencies, deployment, tests, docs, and git history.
2. **Detect the stack.** Check `package.json`, `requirements.txt`, `pyproject.toml`,
   `go.mod`, `Cargo.toml`. Note test runner, framework, TypeScript config.
3. **Read the reference files** for activated scopes:
   - [references/criteria.md](references/criteria.md) — detailed evaluation criteria per scope
   - [references/benchmarks.md](references/benchmarks.md) — industry standards, thresholds, anti-patterns
4. **Run the auto-enhance scanner** for dependency-aware hazard detection:
   ```bash
   python3 ${CLAUDE_SKILL_DIR}/scripts/auto_enhance.py .
   ```

## The 9 Scopes

### APPLICATION QUALITY

**A1 — AI/LLM Usage** _(when app integrates any AI model)_
- Model selection appropriateness per task
- Prompt quality (structured, few-shot, output format)
- Architecture (grounding/RAG, caching, retry, circuit breaker)
- Cost & efficiency (token optimization, smart-skip, batch vs sequential)
- AI output accessibility and security (sanitization, prompt injection)
- Auth middleware placement (OAuth only for Google API routes, rate limiting for AI-only)

**A2 — Accessibility & Inclusive Design** _(when app has UI)_
- WCAG 2.2 conformance (minimum AA)
- Semantic HTML, keyboard navigation, color contrast, zoom/reflow
- Animation library a11y (Motion/Framer: `useReducedMotion()`)
- Skip navigation, landmark patterns, heading hierarchy
- Modal accessibility (focus trap, focus return, Escape handling)
- Inclusive design (slow connections, neurodiversity, i18n)

**A3 — Scalable Cloud-Native Architecture** _(always)_
- 12-Factor App adherence
- Containerization, CI/CD, deploy strategy
- Resilience (health checks, circuit breakers, timeouts, graceful shutdown)
- Performance (caching, rate limiting, lazy loading, auto-scaling)
- Observability (structured logging, metrics, tracing, alerts)

### SECURITY

**S1 — Application Security** _(always)_
- OWASP Top 10 coverage (injection, XSS, CSRF, SSRF, broken access control)
- CSP and HTTP security headers
- Authentication & authorization (OAuth2, session management, RBAC)
- Data protection (encryption at rest/transit, PII handling)
- File upload validation (MIME, size, path traversal)
- Environment variable injection in server templates

**S2 — Config & Secrets Hygiene** _(always)_
- Configuration validation (Pydantic Settings / fail-fast on missing keys)
- Secret leakage prevention (.gitignore, no client-side exposure)
- Cookie security (encryption, httpOnly, secure, sameSite, centralized helpers)
- Rate limiting strategy (tiered: general + AI endpoints)
- Health check and graceful shutdown (SIGTERM, forced exit timeout)
- SSRF protection on URL-accepting endpoints
- Dependency and supply chain security

### STRUCTURAL HEALTH

**H1 — Code Structure** _(always)_
- File size distribution (focused <150 / moderate 150-300 / large 300-500 / bloated >500)
- Duplication detection (exact clones, parametric, structural)
- Embedded sub-component detection
- Abstraction opportunities (repeated API patterns, state management)
- Dead code (unused exports, orphaned tests, commented-out blocks)
- Module coupling (import count, circular deps, layer violations)
- Reliability patterns (error boundaries, input validation, resource cleanup)
- Runtime efficiency (sequential API loops, smart-skip gaps, cache effectiveness)

### TESTING

**T1 — Test Quality** _(always)_
- Coverage metrics (statements, branches, functions, lines)
- Test-to-source mapping and gap analysis (risk-classified)
- Anti-pattern detection (fireEvent, text queries, heavy mocking, happy-path-only)
- Testing Trophy distribution (unit ~25%, integration ~50%, E2E ~15%, a11y ~10%)
- Cross-reference with H1: files that are BOTH large AND zero-coverage = highest risk

**T2 — Testing Infrastructure** _(always)_
- Framework and tooling assessment
- CI/CD pipeline (triggers, parallelism, caching, speed, failure handling)
- Test environment management (isolation, data, teardown)
- Reliability and flakiness (timing deps, order deps, shared state)
- Developer workflow (local run, selective testing, watch mode, debugging)
- Stale test maintenance (orphaned files, outdated mocks)

**T3 — Test Coverage Dimensions** _(always)_
- Unit, integration, E2E, contract, performance, security, accessibility
- Error/edge case coverage (network failures, timeouts, race conditions)
- Regression test pipeline (bug-to-test)
- Runtime efficiency coverage (sequential API detection, cache tests, cost regression)
- Firestore/database rules coverage

### MAINTAINABILITY

**M1 — Documentation Strategy** _(always)_
- Code-level (naming quality, inline comments, type annotations, TODOs)
- API documentation (OpenAPI/Swagger, versioning, error codes)
- Architecture documentation (ADRs, system diagrams, data model, staleness)
- Operational documentation (runbooks, incident response, monitoring)
- Onboarding documentation (README, contributing guide, setup automation)

**M2 — Repository & Project Health** _(always)_
- Structure and navigability (directory org, naming, dead files)
- Git workflow (commit messages, branch strategy, PR discipline)
- GitHub features (issues, PR templates, Actions, releases, CODEOWNERS)
- Dependency management (lock files, freshness, vulnerability scanning)
- Contribution friction (clone-to-PR steps)

## Report Structure

```markdown
# Quality Gate Report

**Date:** YYYY-MM-DD
**Scope:** [Project Name] — [full | focused: <scope>]
**Stack:** [detected stack]

## 1. Executive Summary
Max 20 lines. One paragraph per activated scope.
Maturity rating per scope: initial / developing / established / optimized.
Maintainability risk score: what happens if a key contributor leaves tomorrow.

## 2-N. [One section per activated scope]
Each scope section follows its own structure from criteria.md.
Cite specific standards (WCAG 2.2, CWE, OWASP, Google Engineering, etc.)

## N+1. Documentation-Test Alignment Matrix
| Behavior | Documented? | Tested? | Risk |
Flag "neither documented nor tested" as Critical.

## N+2. Prioritized Recommendations
| # | Recommendation | Scope | Impact | Effort | Priority |
Group by: quick wins (<1 week), medium-term (1-4 weeks), strategic (1-3 months).

## N+3. Unified Refactor Plan (if structure + testing scopes active)
Interleave structural and test improvements — they reinforce each other.
Phase 1: Foundation → Phase 2: Decompose → Phase 3: Abstract → Phase 4: A11y+Security
→ Phase 5: Usability → Phase 6: Functional → Phase 7: E2E
Each phase: files affected, LOC change, new tests, coverage impact, effort.
```

## Analysis Guidelines

- **Do not implement changes.** Analysis and planning only.
- **Use exact numbers.** Measure, don't estimate.
- **Cite standards.** Every claim must reference a framework (WCAG 2.2, CWE, OWASP,
  Google Engineering, Testing Trophy, 12-Factor, etc.)
- **Signal uncertainty.** Say so clearly rather than guessing.
- **Prioritize impact over checklist.** Real users, not compliance checkboxes.
- **Adapt depth to scope.** Full audit = breadth. Single scope = depth.

## Adaptation Rules

- **Python/FastAPI**: Focus on async patterns, Pydantic validation, SQLite WAL, pytest
- **TypeScript/React**: Check `@types/react` with React 19, `skipLibCheck` masking, Vitest/Jest
- **Backend-only**: Skip a11y/component sections, expand API/security/infrastructure
- **Monorepo**: Audit each package separately, combined summary
- **No existing tests**: Focus on bootstrapping; structural improvements still apply
- **Already well-tested (>75%)**: Shift focus to structure, anti-patterns, advanced dimensions
