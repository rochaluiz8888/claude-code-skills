---
name: ai-resilience
description: >
  Add production-grade AI/LLM integration patterns: exponential backoff with jitter
  for 429/5xx, content-hash smart-skip caching, batch processing with bounded
  concurrency, token optimization, and structured JSON output. Works with Gemini
  (google-genai SDK) in both Python and TypeScript. Use when the user says "add retry",
  "add backoff", "optimize AI calls", "add caching to gemini", "batch AI requests",
  "smart-skip", or when auditing AI integration resilience.
argument-hint: [retry|batch|cache|optimize|all]
---

# AI Resilience — LLM Integration Hardening

Apply production-grade patterns to AI/LLM integration code. Detect the stack
(Python or TypeScript) and the specific pattern requested via `$ARGUMENTS`.
If `$ARGUMENTS` is `all` or empty, apply all applicable patterns.

Read [references/patterns.md](references/patterns.md) for complete implementation templates.

## Pattern Detection

Before applying patterns, scan the codebase for existing AI integration:

```bash
# Find Gemini SDK usage
grep -rn "google.genai\|@google/genai\|GenerativeModel\|generateContent" --include="*.ts" --include="*.tsx" --include="*.py" src/ app/ services/ . 2>/dev/null
```

## Pattern 1: Retry with Exponential Backoff + Jitter

**When:** Any code that calls `generateContent()`, `transcribe()`, or any AI API.

**Formula:** `delay = min(maxDelay, initialDelay * 2^attempt) + random(0, delay)`

**Retryable errors:** 429 (rate limit), 500, 502, 503, 504, ECONNRESET, ETIMEDOUT
**Non-retryable:** 400 (bad request), 401, 403, content blocked — throw immediately

**Config:** max 3-5 retries, initial delay 1s, max delay 60s, jitter is mandatory.

**Log each retry:** attempt number, delay, error code, error message.

## Pattern 2: Smart-Skip / Content Hashing

**When:** Batch operations that re-process items (transcription, enrichment, extraction).

**Approach:**
1. Hash the input content: `shake_256(content).hexdigest(16)` (Python) or `crypto.createHash('sha256')` (Node)
2. Check if hash exists in cache/DB with status `done`
3. If yes: return cached result, skip API call
4. If no: process, store result keyed by hash

**From LabTranscription:** Every uploaded file is content-hashed. If a hash already has a `done` job, processing is skipped and the previous result reused. This eliminates redundant Gemini API calls on re-uploads.

**Staleness:** Track `processedAt` timestamp. Skip items processed within configurable window (default 30 days). `force=true` should be rare — never the default.

## Pattern 3: Batch Processing with Bounded Concurrency

**When:** Processing multiple items through AI (bulk enrichment, mass transcription).

**Approach:**
1. Split items into chunks of 10-20
2. Process chunks in parallel with bounded concurrency (3-5 simultaneous)
3. Use `Promise.allSettled()` (TS) or `asyncio.gather(return_exceptions=True)` (Python)
4. Wrap each chunk in retry logic (Pattern 1)
5. Merge successful results; log and skip failed chunks
6. Return partial results rather than total failure

**Anti-pattern:** `for (item of items) { await processItem(item) }` — sequential processing.
**Fix:** Concurrency pool with 3-5 simultaneous calls.

## Pattern 4: Token Optimization

**When:** Any Gemini API call.

| Setting | When to Use |
|---------|-------------|
| `temperature: 0` | Deterministic extraction (structured data, classification) |
| `responseMimeType: 'application/json'` | When output must be structured JSON |
| `responseSchema: {...}` | Enforce exact output shape |
| `maxOutputTokens: N` | Cap output for known-size responses |
| `thinkingBudget: 0` | Extraction tasks that don't need chain-of-thought |

**Minimize input tokens:**
- Send only needed fields, not full objects
- Truncate long text to relevant sections
- Use batch endpoints when available (`batchGenerateContent`)

## Pattern 5: Structured JSON Output

**When:** Extracting structured data from AI responses.

```python
# Python
from google import genai
model = genai.GenerativeModel("gemini-2.5-flash")
response = model.generate_content(
    prompt,
    generation_config={
        "response_mime_type": "application/json",
        "response_schema": {"type": "object", "properties": {...}},
        "temperature": 0,
    }
)
data = json.loads(response.text)
```

```typescript
// TypeScript
const result = await model.generateContent({
  contents: [{ role: 'user', parts: [{ text: prompt }] }],
  generationConfig: {
    responseMimeType: 'application/json',
    responseSchema: { type: 'object', properties: {...} },
    temperature: 0,
  },
});
const data = JSON.parse(result.response.text());
```

## Application Order

When applying all patterns to existing code:

1. **Audit** — find all AI API call sites
2. **Retry** — wrap each call site in retryWithBackoff
3. **Cache** — add content hashing before API calls
4. **Batch** — refactor sequential loops into concurrency pools
5. **Optimize** — tune generation config per call site
6. **Test** — add tests for retry behavior, cache hits/misses, partial failures
