# Structural Health & Complexity Reference

Thresholds, decomposition patterns, and structural quality benchmarks derived from
industry standards and verified refactoring practice. Cite these in the report.

## Table of Contents
1. [File Size Thresholds](#1-file-size-thresholds)
2. [Decomposition Patterns](#2-decomposition-patterns)
3. [Duplication Thresholds](#3-duplication-thresholds)
4. [Complexity Metrics](#4-complexity-metrics)
5. [Module Coupling](#5-module-coupling)
6. [Reliability Patterns](#6-reliability-patterns)
7. [Dead Code Indicators](#7-dead-code-indicators)
8. [Refactoring Decision Framework](#8-refactoring-decision-framework)
9. [Structural Health References](#9-structural-health-references)

---

## 1. File Size Thresholds

These thresholds come from empirical analysis of well-maintained open-source
TypeScript/React projects and software engineering research.

| LOC Range | Category | Signal | Action |
|-----------|----------|--------|--------|
| <150 | **Focused** | Single responsibility likely honored | None needed |
| 150-300 | **Moderate** | Acceptable if cohesive | Monitor for growth |
| 300-400 | **Large** | Likely has multiple responsibilities | Plan decomposition |
| 400-500 | **Oversized** | Almost certainly violates SRP | Decompose this cycle |
| >500 | **Bloated** | Multiple concerns entangled | Immediate priority |

### Key Insight
Files don't grow linearly — they attract more code over time because it's easier to
add to an existing file than create a new one. A 400-LOC file today becomes 600 LOC
in two months. Set the extraction trigger at 300-400 LOC to stay ahead of entropy.

### Well-Maintained OSS Benchmarks
- **Excalidraw**: Core component files average ~200 LOC, utils ~50 LOC
- **Cal.com**: Enforces component file limits in PR reviews
- **React core**: Most source files are <300 LOC despite extreme complexity
- **Express.js**: Router, application, request, response each <500 LOC, cleanly separated

Sources:
- Robert C. Martin — "Clean Code" (2008): functions should be small, classes focused
- SonarQube — Default file length threshold: 1000 LOC (very permissive)
- Industry consensus for TypeScript/React: 200-300 LOC per file is the sweet spot

---

## 2. Decomposition Patterns

When a file exceeds thresholds, apply these proven extraction patterns.
Each pattern was validated in production refactoring of real codebases.

### Pattern A: Extract Shared Utilities
**When:** Same function appears in 2+ files with identical or near-identical logic.
**How:** Move to `src/utils/<name>.ts`, import from both locations.
**Example:** `normalizeDimensionsToCm()` duplicated in a UI component and an API route
→ extracted to `src/utils/dimensions.ts`.
**Test:** Add unit tests for the shared utility. Existing tests should still pass.

### Pattern B: Extract Embedded Sub-Components
**When:** A component file defines 3+ named components, or an inner component exceeds ~30 LOC.
**How:** Move helper components to `<ParentName>Parts.tsx` or individual files.
Keep them in the same directory as the parent.
**Example:** `EnrichmentBadge`, `ConfidenceDot`, `DataCell` extracted from a 597-LOC
card component into `CardParts.tsx` (~50 LOC).
**Test:** Sub-components become independently testable.

### Pattern C: Extract Modal/Dialog to Own File
**When:** A modal/dialog component is defined inside the file that opens it.
**How:** Move to `<Name>Modal.tsx`. If the parent has a shared `<Modal>` primitive,
reuse it instead of duplicating focus-trap logic.
**Example:** `InstallationModal` (163 LOC) extracted from a card component, refactored
to use the shared `<Modal>` component — eliminated ~35 lines of duplicated a11y logic.
**Test:** Modal is now independently testable for rendering, a11y, and interaction.

### Pattern D: Extract Hook Logic from Components
**When:** A component manages complex state + async logic that isn't directly about rendering.
**How:** Move state + handlers to a custom hook in `src/hooks/use<Name>.ts`.
The component calls the hook and focuses on UI.
**Example:** Installation guide fetching (state + API call + Firestore persistence)
extracted from a card component into `useInstallationGuide.ts` (~45 LOC).
**Test:** Hook can be tested with `renderHook()` independently.

### Pattern E: Extract Service Logic from Hooks
**When:** A hook contains pure async business logic (no React state/effects) mixed
with React lifecycle management.
**How:** Move the pure async functions to `src/services/<name>Service.ts`. The hook
imports and calls the service.
**Example:** `enrichInBackground()` (batch processing with Firestore updates) extracted
from `useScanner` hook into `enrichmentService.ts` (~55 LOC).
**Test:** Service is testable without `renderHook()` — just async function tests.

### Pattern F: Abstract Repeated API Patterns
**When:** Multiple API routes follow the same structure (validate → search → structure → respond)
with only the prompts/schemas differing.
**How:** Create a generic helper that accepts configuration and executes the pattern.
Each route becomes: validate input → build config → call helper → respond.
**Example:** Four Gemini routes using a two-pass pattern (Google Search → JSON extraction)
abstracted into `twoPassGemini({ searchPrompt, structurePrompt, schema, cache })`.
Reduced ~220 LOC of duplication across 4 routes.
**Test:** The shared helper gets thorough tests; route tests become simpler.

### Pattern G: Extract Formatting/Presentation Logic
**When:** A route or controller file mixes data logic with presentation/formatting code.
**How:** Move formatting builders to `src/server/lib/<name>-formatting.ts` or similar.
**Example:** Google Sheets formatting requests (~160 LOC of cell styling, banding,
column widths) extracted from a 429-LOC sheets route into `sheet-formatting.ts`.
**Test:** Formatting functions are pure and independently testable.

### Pattern H: Decompose God Components
**When:** A single component file contains the entire page (layout + state + sub-views).
**How:** Extract page-level sections into their own component files. Extract non-React
logic (Picker initialization, API calls) into services.
**Example:** `App.tsx` (429 LOC) decomposed into `Dashboard.tsx` (~300 LOC),
`Landing.tsx` (~40 LOC), and `googlePicker.ts` (~55 LOC). App.tsx reduced to ~40 LOC.
**Test:** Each extracted piece is independently testable.

### Pattern I: Unify Duplicated Processing
**When:** Two functions in the same module do nearly the same thing with slight variations.
**How:** Extract the shared logic into a helper called by both, with parameters for
the differences.
**Example:** `processDriveItem` and `processDrivePickerFiles` both iterated files,
fetched content, extracted equipment, and collected errors. Unified into shared
`processFileList()` — eliminated ~40 LOC of duplication.

### Pattern J: Derive State Instead of Storing It
**When:** A state variable is always a function of another state variable.
**How:** Replace `useState` + manual sync with a derived value (const or `useMemo`).
**Example:** `isScanning` was a separate `useState` always set alongside `phase`.
Replaced with `const isScanning = phase === 'scanning' || phase === 'saving'`.
Eliminated a class of sync bugs.

### Pattern K: Concurrency Pool for Sequential API Calls
**When:** A loop processes items one at a time with `await` inside, and each iteration
makes independent API calls (no data dependency between iterations).
**How:** Replace with a bounded concurrency pool pattern:
```typescript
const CONCURRENCY = 3;
const pool: Promise<void>[] = [];
for (const item of items) {
  const p = processOne(item).then(() => { pool.splice(pool.indexOf(p), 1); });
  pool.push(p);
  if (pool.length >= CONCURRENCY) await Promise.race(pool);
}
await Promise.all(pool);
```
**Example:** File processing loop doing `fetch(file) → extractEquipment(file)` one at
a time for 20 files. With concurrency=3, reduces wall time from ~60s to ~20s.
**Variants:**
- `Promise.allSettled()` with fixed batches (simpler but less efficient — waits for
  slowest in each batch)
- `Promise.all()` for fully independent operations (no bound needed if count is small)

### Pattern L: Parallel Independent API Calls
**When:** Multiple API calls in sequence that don't depend on each other's results.
**How:** Wrap in `Promise.all()`.
**Example:** Sheets export doing `clear()` then `update()` then `getMeta()` sequentially.
The clear, update, and metadata fetch are independent → `Promise.all([clear, update, getMeta])`.
**Savings:** 3 sequential calls (~1.5s) → 1 parallel group (~0.5s).

### Pattern M: Combine Batch Operations
**When:** Multiple API calls to the same service that support batching.
**How:** Combine into a single batch call.
**Example:** Google Sheets `batchUpdate` supports multiple operations (delete tabs +
create tabs) in one call. Two separate `batchUpdate` calls → one combined call.

### Pattern N: Smart Skip with Staleness
**When:** A batch operation re-processes all items when most don't need updating.
**How:** Add a timestamp field (e.g., `enrichedAt`), filter items by staleness threshold,
skip items that are fresh and complete.
**Example:** "Refresh catalog" was re-enriching all 50 items (100 API calls). With
staleness check (30-day window) + missing-field detection, a typical re-run processes
only 5-10 items (10-20 API calls, 80-90% reduction).

### Pattern O: Centralize Cookie Operations
**When:** Multiple places in the codebase read/write cookies with inline
`JSON.stringify`/`JSON.parse` and manually setting cookie options.
**How:** Create `setTokenCookie(res, tokens)` and `readTokenCookie(cookieValue)`
helpers. Add encryption (AES-256-GCM) with backward-compatible plaintext fallback.
**Example:** OAuth callback, token refresh middleware, and session check all had
separate `res.cookie()` calls with inline options. Centralized into two helpers
with encryption — eliminated 3 places where cookie options could diverge.
**Test:** Test encrypt→decrypt roundtrip, plaintext fallback for migration,
tampered cookie rejection.

### Pattern P: Batch Processing with Error Isolation
**When:** A batch operation processes items and a single failure shouldn't abort
the entire batch.
**How:** Use `Promise.allSettled()` instead of `Promise.all()` for batch items.
Track `enriched`/`failed` counts separately. Update each item's status independently.
**Example:** Catalog refresh enriching 50 items. With `Promise.all()`, one timeout
aborts all 50. With `Promise.allSettled()` in batches of 5, 49 succeed and 1 is
marked as `failed` — user can retry just the failed item.

### Pattern R: Exponential Backoff with Jitter for API Calls
**When:** API calls can fail with transient errors (429 rate limit, 5xx server errors,
timeouts, network failures) and should be retried automatically.
**How:** Wrap each API call in a `retryWithBackoff()` utility that implements:
- Exponential delay: `initialDelay × 2^attempt` (e.g., 1s → 2s → 4s → 8s → 16s)
- Random jitter: `delay + random(0, delay)` to prevent thundering herd
- Max delay cap (e.g., 60s) to bound worst-case wait
- Max retry count (3-5 attempts)
- Immediate throw for non-retryable errors (400, 401, 403, content blocked)
- Per-retry logging with attempt number, delay, and error details
```typescript
async function retryWithBackoff<T>(fn: () => Promise<T>, opts): Promise<T> {
  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try { return await fn(); }
    catch (error) {
      if (attempt >= maxRetries || !isRetryable(error)) throw error;
      const delay = Math.min(maxDelay, initialDelay * 2 ** attempt);
      const jitter = Math.random() * delay;
      await sleep(delay + jitter);
    }
  }
}
```
**Example:** Mass-fix endpoint splits 200 items into chunks of 15, fires all chunks
in parallel via `Promise.allSettled()`, each chunk wrapped in `retryWithBackoff()`.
A 429 on chunk 3 retries with backoff while other chunks complete normally.
**Reference:** [Google Cloud — Handling 429 Resource Exhaustion Errors](https://cloud.google.com/blog/products/ai-machine-learning/learn-how-to-handle-429-resource-exhaustion-errors-in-your-llms)

### Pattern S: Frontend Fetch Timeout with AbortController
**When:** Frontend `fetch()` calls to backend API endpoints have no timeout,
causing the UI to hang indefinitely if the server is slow or unresponsive.
**How:** Add an `AbortController` with a configurable timeout to every `fetch()` call:
```typescript
async function apiPost<T>(url: string, body: unknown, timeoutMs = 120_000): Promise<T> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);
  const res = await fetch(url, { signal: controller.signal, ... }).finally(() => clearTimeout(timer));
}
```
**Example:** `geminiPost()` wrapper now has a 120s timeout matching the server-side
Gemini client timeout, so the frontend aborts cleanly instead of hanging.

### Pattern Q: React Error Boundary with React 19
**When:** Adding error boundaries to React 19 apps.
**How:** React 19 does not bundle TypeScript types. The `Component` class requires
`@types/react@^19` installed separately. Without it, `this.state` and `this.props`
cause TS errors even though the runtime works.
**Pattern:** Create ErrorBoundary in its own file. Use `constructor(props)` +
`super(props)` pattern with explicit interface types for props and state.
**Common pitfall:** `skipLibCheck: true` hides the missing types until a class
component is added.

---

## 3. Duplication Thresholds

| Metric | Target | Source |
|--------|--------|--------|
| Code duplication ratio | <5% of codebase | SonarQube default |
| Duplicated block threshold | >3 lines identical in 2+ places | SonarQube |
| New code duplication | <3% on new/changed code | SonarQube "Clean as You Code" |

### What Counts as Duplication
- **Exact clones**: Identical code blocks (even with whitespace differences)
- **Parametric clones**: Same structure with different variable names or literal values
- **Structural clones**: Same algorithm/pattern implemented independently

### Where Duplication Hides
- Utility functions copy-pasted between frontend and backend
- Validation logic duplicated between client and server
- API call patterns repeated across route handlers
- Error handling boilerplate copied between modules
- UI sub-components re-implementing shared patterns (focus traps, modals)

Sources:
- SonarQube — ["Metric Definitions"](https://docs.sonarsource.com/sonarqube-server/10.8/user-guide/code-metrics/metrics-definition)
- ["Clean as You Code"](https://www.sonarsource.com/solutions/clean-as-you-code/)

---

## 4. Complexity Metrics

| Metric | Threshold | Risk | Source |
|--------|-----------|------|--------|
| Cyclomatic complexity | <10 per function | Functions with >15 are hard to test | NIST |
| Cognitive complexity | <15 per function | High values = hard to understand | SonarQube |
| Max function length | <50 lines | Long functions usually do too much | Clean Code |
| Max parameters | <5 per function | Many params = missing abstraction | Clean Code |
| Nesting depth | <4 levels | Deep nesting = hard to follow | Industry |

### How to Estimate Without Tooling
If SonarQube or ESLint complexity rules aren't configured, you can estimate:
- Count `if/else/switch/for/while/catch/&&/||/?.` per function → approximates cyclomatic
- Count nesting levels → relates to cognitive complexity
- Functions >50 lines almost always exceed both thresholds

Sources:
- NIST — Cyclomatic complexity guidance
- SonarQube — ["Cognitive Complexity"](https://www.sonarsource.com/blog/5-clean-code-tips-for-reducing-cognitive-complexity/)
- Robert C. Martin — "Clean Code" (2008)

---

## 5. Module Coupling

| Metric | Threshold | Signal |
|--------|-----------|--------|
| Import count per file | <10 | Files with >10 imports are coupling hotspots |
| Circular dependencies | 0 | Any cycle = architecture smell |
| Layer violations | 0 | e.g., utility importing from component |
| Fan-out (files a module depends on) | <8 | High fan-out = fragile to changes |
| Fan-in (files that depend on a module) | Monitor | High fan-in = change is risky, test thoroughly |
| God module | None | No single file should be imported by >50% of codebase |

### Clean Layer Hierarchy
Components/Pages → Hooks → Services → Utils (each layer only imports from same or lower)

| Layer | May Import From |
|-------|----------------|
| Components | Hooks, Services, Utils, UI primitives, Types |
| Hooks | Services, Utils, Context, Types |
| Services | Utils, Types, External APIs |
| Server Routes | Server Libs, Server Middleware, Types |
| Server Libs | Utils, Types, External SDKs |
| Utils | Types only (or nothing) |

Violations of this hierarchy indicate architectural drift.

---

## 6. Reliability Patterns

Every production application should have these. Rate each as:
Present & Tested | Present & Untested | Partial | Missing

### Frontend
| Pattern | What to Look For |
|---------|-----------------|
| React Error Boundary | Class component with `componentDidCatch` wrapping app |
| Loading states | Every async operation has a visible loading indicator |
| Empty states | Every list/grid handles the zero-items case |
| Error states | Failed API calls show user-friendly messages |
| Offline handling | Graceful behavior when network is unavailable |
| Resource cleanup | `useEffect` cleanup functions for listeners/timers |
| Optimistic updates | Or at minimum, eventual consistency with feedback |

### Backend
| Pattern | What to Look For |
|---------|-----------------|
| Global error handler | Express catch-all middleware (4-arg function) |
| Structured logging | Pino, Winston, or equivalent with request correlation |
| Input validation | At every system boundary (API endpoints, form submissions) |
| Rate limiting | Per-endpoint or per-user throttling |
| Retry with backoff | For external API calls (AI, OAuth, third-party) |
| Graceful shutdown | SIGTERM handler that drains connections |
| Health endpoint | `/health` or `/healthz` for load balancer probes |
| Request timeouts | For outgoing HTTP calls |
| Cookie encryption | OAuth tokens encrypted at rest in cookies (AES-256-GCM) |
| CSP headers | Content-Security-Policy configured for all CDN/API/auth domains |
| HSTS header | Strict-Transport-Security set in production |
| Rate limiting (tiered) | General + AI-specific rate limits with different thresholds |
| Session auth for AI routes | Lightweight session check (cookie exists) for server-key-only routes |

---

## 7. Dead Code Indicators

| Indicator | How to Detect |
|-----------|--------------|
| Unused exports | Function/component exported but never imported by any other file |
| Orphaned test files | Test files for source files that no longer exist |
| Commented-out code | Large blocks of `//` or `/* */` around functional code |
| Unused dependencies | Packages in `package.json` never imported in source |
| Feature flag remnants | Config/flags for features that have shipped or been abandoned |
| TODO/FIXME/HACK comments | Track count and age — old ones are debt signals |
| Unused CSS classes | Defined in stylesheets but never referenced |

**Rule:** If dead code has existed for >2 releases without being used, it should be
removed rather than kept "just in case." Version control preserves history.

---

## 8. Refactoring Decision Framework

Use this to prioritize which structural improvements to tackle first.

### Risk × Impact Matrix

|  | Low Impact | High Impact |
|--|-----------|-------------|
| **Low Risk** | Do if convenient | **Do first** (quick wins) |
| **High Risk** | Skip or defer | Do with tests first |

### Risk Classification
- **Low risk:** Extracting utilities, deleting dead code, moving sub-components
- **Medium risk:** Abstracting API patterns, unifying processing logic
- **High risk:** Changing state management, modifying auth flows, refactoring data pipelines

### Safety Checklist Before Refactoring
1. Tests pass before starting
2. File has test coverage (or add tests first)
3. Change is mechanical (rename, move, extract) not behavioral
4. Each extraction is a separate commit
5. Tests pass after each commit
6. Visual verification for UI changes

### Impact Estimation
For each proposed extraction, estimate:
- **LOC reduced** from the original file
- **LOC relocated** to new focused files
- **LOC eliminated** (dead code, duplication removed)
- **New test surface** exposed by the extraction

---

## 9. Structural Health References

### Books & Foundational Works
28. Robert C. Martin — "Clean Code" (2008): functions <20 lines, classes focused
29. Martin Fowler — ["Refactoring"](https://refactoring.com/) (2018 2nd ed): catalog of refactoring patterns
30. Michael Feathers — "Working Effectively with Legacy Code" (2004): test-first refactoring

### Code Quality Tooling
31. SonarQube — ["Metric Definitions"](https://docs.sonarsource.com/sonarqube-server/10.8/user-guide/code-metrics/metrics-definition)
32. SonarSource — ["Clean as You Code"](https://www.sonarsource.com/solutions/clean-as-you-code/): quality gates on new code
33. SonarSource — ["5 Tips for Reducing Cognitive Complexity"](https://www.sonarsource.com/blog/5-clean-code-tips-for-reducing-cognitive-complexity/)
34. ESLint — [max-lines rule](https://eslint.org/docs/rules/max-lines): configurable file length limits
35. ESLint — [complexity rule](https://eslint.org/docs/rules/complexity): cyclomatic complexity threshold

### React Decomposition
36. React docs — ["Thinking in React"](https://react.dev/learn/thinking-in-react): component decomposition principles
37. React docs — ["Extracting State Logic into a Reducer"](https://react.dev/learn/extracting-state-logic-into-a-reducer)
38. Kent C. Dodds — ["When to break up a component"](https://kentcdodds.com/blog/when-to-break-up-a-component-into-multiple-components)
39. Dan Abramov — ["Writing Resilient Components"](https://overreacted.io/writing-resilient-components/)

### Architecture
40. NIST — Software complexity metrics and cyclomatic complexity
41. Snyk — ["npm Registry Package Behavior"](https://snyk.io/blog/how-much-do-we-really-know-about-how-packages-behave-on-the-npm-registry/): dependency depth analysis
