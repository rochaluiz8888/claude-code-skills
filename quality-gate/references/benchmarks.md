# Industry Benchmarks & Anti-Pattern Catalog

This reference contains verified industry benchmarks, quality thresholds, and testing
anti-patterns. All numbers come from published sources — cite them in the report.

## Table of Contents
1. [Coverage Standards](#1-coverage-standards)
2. [Testing Trophy Distribution](#2-testing-trophy-distribution)
3. [Quality Metrics Beyond Coverage](#3-quality-metrics-beyond-coverage)
4. [Peer App Benchmarks](#4-peer-app-benchmarks)
5. [Testing Anti-Patterns](#5-testing-anti-patterns)
6. [Security Testing (OWASP 2025)](#6-security-testing-owasp-2025)
7. [Accessibility Testing (WCAG 2.2)](#7-accessibility-testing-wcag-22)
8. [TypeScript Strictness](#8-typescript-strictness)
9. [Full Reference List](#9-full-reference-list)

---

## 1. Coverage Standards

### Google Engineering (Testing Blog)
- **60%** = "acceptable"
- **75%** = "commendable"
- **90%** = "exemplary"
- Per-commit new code: 99% target, 90% minimum for frequently changing code
- Google computes coverage for 1 billion lines of code daily across 7 languages
- Only 45% of developers use coverage frequently when authoring changes

Sources:
- ["Code Coverage Best Practices"](https://testing.googleblog.com/2020/08/code-coverage-best-practices.html) (2020)
- ["Code coverage goal: 80% and no less!"](https://testing.googleblog.com/2010/07/code-coverage-goal-80-and-no-less.html) (2010)
- ["Code Coverage at Google"](https://research.google/pubs/code-coverage-at-google/) (research paper)

### Microsoft Engineering
- Teams typically aim for **~80%** overall
- Azure Pipelines defaults to **70%** on changed lines
- Reduced test flakiness by 18% with "fix or remove within 2 weeks" policy

### Bullseye Research
- **70-80%** is "reasonable for most projects"
- Unit testing: 10-20% higher (80-90%)
- Above 70-80%, bug detection rate slows significantly
- Even 100% coverage only exposes ~half the faults in a system

Source: ["Minimum Acceptable Code Coverage"](https://www.bullseye.com/minimum.html)

### Summary Table (use in report Section 2.1)

| Source | Acceptable | Commendable | Exemplary |
|--------|-----------|-------------|-----------|
| Google Engineering | 60% | 75% | 90% |
| Bullseye Research | 70% | 80% | Diminishing returns |
| Microsoft Engineering | ~70% changed lines | ~80% overall | — |
| Excalidraw (production) | 60% lines | 63% functions | 70% branches |
| General Industry | 70% | 80% | 90% |

---

## 2. Testing Trophy Distribution

From Kent C. Dodds' Testing Trophy model. Key principle: **"Write tests. Not too
many. Mostly integration."**

| Layer | Description | Ideal Share |
|-------|------------|-------------|
| Static Analysis | TypeScript, ESLint | Foundation (not counted in %) |
| Unit Tests | Isolated function/component tests | ~25% |
| Integration Tests | Multiple modules with real providers | ~50% (the bulk) |
| E2E Tests | Full browser, real backend | ~15% |
| Accessibility Tests | axe-core, keyboard nav | ~10% |

Integration tests provide the best confidence-to-effort ratio for frontend apps.

Sources:
- ["The Testing Trophy and Testing Classifications"](https://kentcdodds.com/blog/the-testing-trophy-and-testing-classifications)
- ["Write tests. Not too many. Mostly integration."](https://kentcdodds.com/blog/write-tests)

Martin Fowler's Test Pyramid (complementary):
- Many small, fast unit tests at the base
- Some coarse-grained integration tests in the middle
- Very few high-level E2E/UI tests at the top
- Fowler discourages fixed numeric coverage targets

Sources:
- ["The Practical Test Pyramid"](https://martinfowler.com/articles/practical-test-pyramid.html)
- ["TestPyramid"](https://martinfowler.com/bliki/TestPyramid.html)

---

## 3. Quality Metrics Beyond Coverage

Use this table in report Section 2.3. Mark each as measured or not-measured.

| Metric | Industry Target | Source |
|--------|----------------|--------|
| Test-to-Code Ratio | 1:1 – 1.5:1 | Google |
| TypeScript Strict Mode | `strict: true` + `noUncheckedIndexedAccess` | TS team |
| `any` type count | 0–5 | TypeScript best practices |
| Cyclomatic complexity | <10 per function | NIST |
| Cognitive complexity | <15 per function | SonarQube |
| Code duplication ratio | <5% | SonarQube |
| Mutation testing score | >60–70% | Industry guidance |
| React Error Boundaries | Required for production | React docs |
| A11y test coverage | 100% interactive components | WCAG 2.2 / Deque |
| A11y automated detection | 30–57% of issues caught | Deque Systems (2025) |
| E2E user journey coverage | All critical paths | Kent C. Dodds |
| CI pipeline duration | <10 min target, <15 min max | TestDino benchmarks |
| Flakiness rate | Fix within 2 weeks | Microsoft policy |
| Min tap target size | 24×24 CSS pixels | WCAG 2.2 AA |
| OAuth access token TTL | 5–15 minutes | OWASP |
| Dependency depth | Average ~4, concern at >10 | Snyk research |
| Context switch threshold | ~20-25 min CI max before devs lose focus | Industry research |
| Sequential API loops | 0 (all should use concurrency pools) | Runtime efficiency |
| Batch operation skip rate | >70% on re-runs (staleness-based) | AI cost optimization |
| Cache hit rate | >60% for repeated queries | Performance engineering |
| API calls per user action | Minimize; track per-feature | Cost observability |
| Retry with backoff coverage | All external API calls wrapped in `retryWithBackoff()` | [Google Cloud LLM 429 Guide](https://cloud.google.com/blog/products/ai-machine-learning/learn-how-to-handle-429-resource-exhaustion-errors-in-your-llms) |
| Parallel batch chunk size | 10-20 items per chunk for AI batch ops | AI cost optimization |
| Frontend fetch timeout | `AbortController` on all `fetch()` calls matching server timeout | Reliability |
| Batch partial success rate | `Promise.allSettled()` for batch ops; failed chunks logged, not fatal | Error isolation |
| React Error Boundary compat | Test with React 19 types installed | React 19 migration |
| Cookie encryption coverage | All cookie ops use encrypt/decrypt helpers | Security testing |
| Firestore rules test coverage | All collections + validation rules tested | Firebase emulator |
| Motion reduced-motion coverage | `useReducedMotion()` in all animated components | Accessibility |
| CSP header completeness | All CDN/API/auth domains whitelisted | Security headers |

---

## 4. Peer App Benchmarks

These are verified numbers from open-source React/TypeScript apps:

### Excalidraw (excalidraw/excalidraw)
- **Coverage thresholds**: Lines 60%, Statements 60%, Functions 63%, Branches 70%
- **Actual coverage**: Lines ~66.8%, Statements ~66.8%, Functions ~64.6%, Branches ~80.3%
- **Test framework**: Vitest, jsdom
- Sources: [Issue #6553](https://github.com/excalidraw/excalidraw/issues/6553), [PR #8149](https://github.com/excalidraw/excalidraw/pull/8149)

### Cal.com (calcom/cal.com)
- **Coverage %**: Not publicly displayed
- **Test framework**: Vitest (unit), Playwright (E2E), Checkly (monitoring)
- **Migration**: Jest→Vitest with 85.3% decrease in test execution time
- Source: [PR #9035](https://github.com/calcom/cal.com/pull/9035)

### Key Observation
Most well-known open-source React/TypeScript apps do **not** publicly report or enforce
coverage percentages. Excalidraw is the exception with documented thresholds.

---

## 5. Testing Anti-Patterns

Detect these in the test files and report in Section 9.

### From Kent C. Dodds (React Testing Library)

| Anti-Pattern | Why It's Bad | Fix |
|-------------|-------------|-----|
| `fireEvent` instead of `userEvent` | Doesn't simulate real user behavior (hover, focus, etc.) | Use `@testing-library/user-event` |
| Querying by text (`getByText`) | Breaks when text changes or is translated | Use `getByRole`, `getByLabelText`, `getByTestId` |
| Destructuring from `render()` | Less discoverable, harder to debug | Use `screen.getByRole(...)` |
| Testing implementation details | Tests break on refactors that don't change behavior | Test behavior visible to the user |
| Nested test blocks with mutable vars | Shared state between tests causes coupling | Flat test structure with inline setup |

Sources:
- ["Common mistakes with React Testing Library"](https://kentcdodds.com/blog/common-mistakes-with-react-testing-library)
- ["Testing Implementation Details"](https://kentcdodds.com/blog/testing-implementation-details)
- ["Avoid Nesting when you're Testing"](https://kentcdodds.com/blog/avoid-nesting-when-youre-testing)

### From Yoni Goldberg (Node.js API Testing)

| Anti-Pattern | Why It's Bad | Fix |
|-------------|-------------|-----|
| Testing only responses | Misses side effects (DB writes, logs, outgoing calls) | Test 5 outcomes: response, DB state, outgoing calls, messages, observability |
| Starting real servers | Slow, port conflicts, flaky | Export `app` without `.listen()`, use supertest |
| No DB state verification | Passing test but corrupt data | Assert DB state after operations |
| Ignoring error cases | Only happy paths tested | Test error classification, retry behavior, partial failures |

Sources:
- ["Node.js Testing Best Practices"](https://github.com/goldbergyoni/nodejs-testing-best-practices) (2025)
- ["JavaScript Testing Best Practices"](https://github.com/goldbergyoni/javascript-testing-best-practices) (2025)

### Missing Infrastructure

| Missing Tool | Why It Matters |
|-------------|---------------|
| `eslint-plugin-testing-library` | Catches RTL anti-patterns at lint time |
| `eslint-plugin-jest-dom` | Suggests better assertions (`toBeDisabled()` vs `toHaveAttribute('disabled')`) |
| Accessibility testing (axe-core) | Catches 30-57% of WCAG violations automatically |
| E2E framework (Playwright) | Only way to test real user journeys end-to-end |

### Infrastructure Debt Anti-Patterns (from real audits)

| Anti-Pattern | Why It's Bad | Fix |
|-------------|-------------|-----|
| Missing `@types/react` with React 19 | Class components fail; `skipLibCheck` masks it | Install `@types/react@^19` + `@types/react-dom` |
| Stale test files for deleted components | CI fails or tests are silently skipped | Cross-reference test imports against existing source files |
| Hardcoded dashboard stats | Misleads users; indicates incomplete wiring | Compute values from actual data source |
| `package-lock.json` not committed | Non-reproducible builds; different deps in CI vs local | Always commit lock files |
| Inline modal bypassing shared primitive | Duplicated a11y logic; inconsistent focus management | Reuse the project's accessible Modal component |
| Plaintext OAuth tokens in cookies | Cookie theft = full account access | Encrypt with AES-256-GCM; centralize cookie helpers |
| No rate limiting on AI endpoints | API key abuse; cost explosion from unauthenticated callers | Add `express-rate-limit` with tiered limits |

---

## 6. Security Testing (OWASP 2025)

### OWASP Top 10 (2025 Edition)
1. A01: Broken Access Control
2. A02: Cryptographic Failures
3. A03: Injection
4. A04: Insecure Design
5. A05: Security Misconfiguration
6. A06: Vulnerable and Outdated Components
7. A07: Identification and Authentication Failures
8. A08: Software and Data Integrity Failures
9. A09: Security Logging and Monitoring Failures
10. A10: Server-Side Request Forgery (SSRF)

### OAuth Security Tests (per OWASP OAuth2 Cheat Sheet)
- PKCE implementation (mandatory per OAuth 2.1)
- `state` parameter CSRF protection
- Redirect URI exact-match validation
- Token storage (httpOnly cookies, no localStorage)
- Scope minimization
- Access token TTL (5-15 minutes)
- `code_verifier` not leaked in logs

Sources:
- ["OWASP Top 10: 2025"](https://owasp.org/Top10/2025/)
- ["OAuth2 Cheat Sheet"](https://cheatsheetseries.owasp.org/cheatsheets/OAuth2_Cheat_Sheet.html)
- ["Testing for OAuth Weaknesses"](https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/05-Authorization_Testing/05-Testing_for_OAuth_Weaknesses)

---

## 7. Accessibility Testing (WCAG 2.2)

### Key Facts
- Automated tools detect approximately **30-57%** of accessibility issues
- At least **33%** of issues are only detectable through manual testing
- WCAG 2.2 adds 9 new success criteria (published Oct 2023, ISO/IEC 40500:2025)
- Level AA requires minimum tap target size of **24×24 CSS pixels**

### Testing Approach (Layered)
1. Static analysis: `eslint-plugin-jsx-a11y`
2. Component tests: `jest-axe` or `vitest-axe` (run axe-core against rendered components)
3. Manual testing: keyboard navigation, screen reader

### What to Test
- 100% of interactive components (forms, modals, tabs, accordions)
- Focus management (trap and return)
- ARIA state communication
- Keyboard operability (Tab, Shift+Tab, Enter, Escape)
- Color contrast

Sources:
- [WCAG 2.2 Overview](https://www.w3.org/WAI/standards-guidelines/wcag/)
- ["What's New in WCAG 2.2"](https://www.w3.org/WAI/standards-guidelines/wcag/new-in-22/)
- Deque Systems (2025): ~57% automated detection rate
- ["Accessibility Auditing React"](https://web.dev/articles/accessibility-auditing-react)

---

## 8. TypeScript Strictness

### Recommended Production Settings
```json
{
  "compilerOptions": {
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "exactOptionalPropertyTypes": true,
    "noPropertyAccessFromIndexSignature": true
  }
}
```

`strict: true` enables: `alwaysStrict`, `strictNullChecks`, `strictBindCallApply`,
`strictFunctionTypes`, `strictPropertyInitialization`, `noImplicitAny`,
`noImplicitThis`, `useUnknownInCatchVariables`.

Every major framework ships strict by default. The TypeScript team is making `strict`
the default in future versions.

Sources:
- [TSConfig `strict`](https://www.typescriptlang.org/tsconfig/strict.html)
- ["TypeScript Strict Mode 2026 Guide"](https://www.mariorafaelayala.com/blog/typescript-strict-mode-2026)

---

## 9. Full Reference List

Use this when writing the report's Section 10. Organize by category.

### Coverage & Testing Strategy
1. Google Testing Blog — "Code Coverage Best Practices" (2020)
2. Google Testing Blog — "Code coverage goal: 80% and no less!" (2010)
3. Google Research — "Code Coverage at Google"
4. Bullseye — "Minimum Acceptable Code Coverage"
5. Martin Fowler — "The Practical Test Pyramid" & "TestPyramid"

### React & Frontend Testing
6. Kent C. Dodds — "The Testing Trophy and Testing Classifications"
7. Kent C. Dodds — "Write tests. Not too many. Mostly integration."
8. Kent C. Dodds — "Common mistakes with React Testing Library"
9. Kent C. Dodds — "Testing Implementation Details"

### Node.js & API Testing
10. Yoni Goldberg — "Node.js Testing Best Practices" (2025)
11. Yoni Goldberg — "JavaScript Testing Best Practices" (2025)

### Benchmarks & Peers
12. Excalidraw — Coverage thresholds (Issue #6553)
13. Cal.com — Jest→Vitest migration (PR #9035)
14. Vitest — "Test Projects Guide"

### Quality Metrics
15. SonarQube — "Metric Definitions"
16. SonarSource — "5 Tips for Reducing Cognitive Complexity"
17. NIST — Cyclomatic complexity
18. TestDino — "E2E Test Performance Benchmarks"

### Security
19. OWASP — "Top 10: 2025"
20. OWASP — "OAuth2 Cheat Sheet"
21. OWASP — "Testing for OAuth Weaknesses"

### Accessibility
22. W3C — WCAG 2.2 Overview
23. W3C — "What's New in WCAG 2.2"
24. Deque Systems (2025) — Automated detection rates
25. web.dev — "Accessibility Auditing React"

### TypeScript
26. TypeScript — TSConfig `strict`
27. Mario Rafael Ayala — "TypeScript Strict Mode 2026 Guide"

### Structural Health (see also `references/complexity.md`)
28-41. Structural health references (Clean Code, Refactoring, SonarQube, ESLint,
React decomposition, architecture) — detailed in `complexity.md` Section 9.

---

## 10. Extended Test Categories

Beyond unit and integration tests, a mature codebase needs these additional categories.
Include them in the refactor plan phases 5-7.

### Usability Tests
Test user-facing interaction quality without a browser:
- **Keyboard navigation**: Tab flow through interactive elements, Enter/Escape handling,
  focus management across modals and forms
- **User feedback**: Loading spinners present during async operations, completion messages
  shown after workflows, empty states guide users, error states provide recovery paths
- **Auth flow usability**: Sign-out completes fully (Firebase + server), OAuth popup
  flow handles blocked popups gracefully, timeout produces clear error

**Where to test:** Component tests with @testing-library/react, using `userEvent.keyboard`
for keyboard interactions and asserting on visible text/aria-labels for feedback.

### Functional Tests
Test complete feature workflows within the unit test framework (no browser):
- **Import pipeline**: Full flow from scan → extract → review → confirm → save → enrich → done.
  Test partial selection, empty results, extraction errors, save errors, cancel/resume.
- **Inventory operations**: CRUD as integrated operations — search filtering (partial,
  case-insensitive), tag filtering (intersection), combined filters, enrichment success/failure.
- **Export pipeline**: Sheets creation, row generation, dimension normalization, detail tabs,
  installation guide data in export, boundary validation (empty array, >500 items).

**Where to test:** renderHook for hooks, supertest for API routes. Mock external APIs
but test the full internal logic chain.

### E2E-Style Integration Tests
Test complete API journeys via supertest — the closest to real E2E without a browser:
- **API journeys**: Full auth flow (URL → callback → session → status → picker-token),
  full scan-to-export pipeline, enrichment chain
- **Error resilience**: Expired tokens, rate limits, safety blocks, timeouts, network
  failures, invalid inputs, concurrent token refresh race conditions
- **Data integrity**: Brazilian date/price normalization through pipeline, model uppercasing,
  whitespace collapsing, mm→cm conversion in exports, cache consistency, existing field
  preservation during enrichment

**Where to test:** supertest with session setup, mocked googleapis and gemini-client.

### Test Distribution Target (with all categories)

| Category | Ideal Share | Purpose |
|----------|------------|---------|
| Unit | ~20% | Isolated functions, pure logic |
| Component | ~15% | UI rendering + basic interaction |
| Integration | ~20% | Cross-provider, middleware chains |
| Usability | ~10% | Keyboard nav, feedback, a11y |
| Functional | ~15% | Complete feature workflows |
| E2E-style | ~10% | API journeys, error resilience |
| Security | ~5% | OWASP, auth, input validation |
| Accessibility | ~5% | axe-core, WCAG 2.2 |

### Proven Progression: Coverage Impact by Phase

Based on verified results from a real 4,600 LOC TypeScript/React+Express codebase:

| Phase | Tests Added | Coverage Before → After | Key Impact |
|-------|------------|------------------------|------------|
| Foundation | ~94 | 48% → 68% | Contexts, services, routes |
| Components | ~53 | 68% → 76% | Dashboard, Grid, Modal, Card |
| Integration | ~33 | 76% → 87% | Scanner, auth middleware |
| A11y + Security | ~47 | 87% → 88% | WCAG, OWASP, edge cases |
| Usability | ~32 | 88% → 89% | Keyboard, feedback, auth UX |
| Functional | ~28 | 89% → 91% | Pipelines, CRUD, export |
| E2E-style | ~28 | 91% → 92% | Journeys, resilience, integrity |
| **Total** | **~315** | **48% → 92%** | **3x test cases, 44pp coverage** |
