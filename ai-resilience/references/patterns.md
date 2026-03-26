# Gemini Integration Pattern Templates

Complete, copy-paste-ready implementations for each pattern.

---

## 1. Retry with Exponential Backoff + Jitter

### Python

```python
import asyncio
import random
import logging

logger = logging.getLogger(__name__)

RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}

async def retry_with_backoff(
    fn,
    *args,
    max_retries: int = 4,
    initial_delay: float = 1.0,
    max_delay: float = 60.0,
    **kwargs,
):
    """Retry an async function with exponential backoff + jitter.

    Retries on: 429, 5xx, network errors.
    Throws immediately on: 400, 401, 403, content blocked.
    """
    last_error = None
    for attempt in range(max_retries + 1):
        try:
            return await fn(*args, **kwargs)
        except Exception as e:
            last_error = e
            status = getattr(e, "code", None) or getattr(e, "status_code", None)

            # Non-retryable errors
            if status and status < 500 and status != 429:
                raise

            if attempt == max_retries:
                raise

            delay = min(max_delay, initial_delay * (2 ** attempt))
            jitter = random.uniform(0, delay)
            total_delay = delay + jitter

            logger.warning(
                "Retry %d/%d after %.1fs (error: %s %s)",
                attempt + 1, max_retries, total_delay,
                status or "network", str(e)[:100],
            )
            await asyncio.sleep(total_delay)

    raise last_error
```

### TypeScript

```typescript
const RETRYABLE_CODES = new Set([429, 500, 502, 503, 504]);

async function retryWithBackoff<T>(
  fn: () => Promise<T>,
  {
    maxRetries = 4,
    initialDelay = 1000,
    maxDelay = 60000,
  } = {}
): Promise<T> {
  let lastError: Error;

  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      return await fn();
    } catch (error: any) {
      lastError = error;
      const status = error?.status || error?.code;

      // Non-retryable
      if (status && status < 500 && status !== 429) throw error;
      if (attempt === maxRetries) throw error;

      const delay = Math.min(maxDelay, initialDelay * 2 ** attempt);
      const jitter = Math.random() * delay;
      const totalDelay = delay + jitter;

      console.warn(
        `Retry ${attempt + 1}/${maxRetries} after ${(totalDelay / 1000).toFixed(1)}s ` +
        `(error: ${status || 'network'} ${String(error).slice(0, 100)})`
      );
      await new Promise(r => setTimeout(r, totalDelay));
    }
  }
  throw lastError!;
}
```

---

## 2. Smart-Skip / Content Hashing

### Python (SQLite-based, from LabTranscription pattern)

```python
import hashlib

def content_hash(data: bytes) -> str:
    """Generate a 32-char content hash for deduplication."""
    return hashlib.shake_256(data).hexdigest(16)

async def process_with_skip(file_path: str, db) -> dict:
    """Process a file, skipping if already done."""
    with open(file_path, "rb") as f:
        file_hash = content_hash(f.read())

    # Check cache
    cached = await db.execute(
        "SELECT result FROM jobs WHERE content_hash = ? AND status = 'done'",
        (file_hash,)
    )
    row = await cached.fetchone()
    if row:
        return json.loads(row[0])

    # Process
    result = await retry_with_backoff(transcribe, file_path)

    # Cache result
    await db.execute(
        "INSERT OR REPLACE INTO jobs (content_hash, status, result) VALUES (?, 'done', ?)",
        (file_hash, json.dumps(result))
    )
    await db.commit()
    return result
```

### TypeScript (in-memory cache with TTL)

```typescript
import { createHash } from 'crypto';
import NodeCache from 'node-cache';

const resultCache = new NodeCache({ stdTTL: 86400 }); // 24h

function contentHash(data: string): string {
  return createHash('sha256').update(data).digest('hex').slice(0, 32);
}

async function processWithSkip(input: string): Promise<Result> {
  const hash = contentHash(input);
  const cached = resultCache.get<Result>(hash);
  if (cached) return cached;

  const result = await retryWithBackoff(() => generateContent(input));
  resultCache.set(hash, result);
  return result;
}
```

---

## 3. Batch Processing with Bounded Concurrency

### Python

```python
import asyncio

async def process_batch(
    items: list,
    processor,
    concurrency: int = 5,
    chunk_size: int = 10,
) -> list:
    """Process items in parallel with bounded concurrency and per-chunk retry."""
    semaphore = asyncio.Semaphore(concurrency)
    results = []

    async def process_one(item):
        async with semaphore:
            return await retry_with_backoff(processor, item)

    chunks = [items[i:i + chunk_size] for i in range(0, len(items), chunk_size)]

    for chunk in chunks:
        tasks = [process_one(item) for item in chunk]
        settled = await asyncio.gather(*tasks, return_exceptions=True)

        for i, result in enumerate(settled):
            if isinstance(result, Exception):
                logger.error("Failed item %s: %s", chunk[i], result)
            else:
                results.append(result)

    return results
```

### TypeScript

```typescript
async function processBatch<T, R>(
  items: T[],
  processor: (item: T) => Promise<R>,
  { concurrency = 5, chunkSize = 10 } = {}
): Promise<{ results: R[]; errors: Error[] }> {
  const results: R[] = [];
  const errors: Error[] = [];

  const chunks: T[][] = [];
  for (let i = 0; i < items.length; i += chunkSize) {
    chunks.push(items.slice(i, i + chunkSize));
  }

  for (const chunk of chunks) {
    const promises = chunk.map(item =>
      retryWithBackoff(() => processor(item))
    );

    const settled = await Promise.allSettled(promises);

    for (const result of settled) {
      if (result.status === 'fulfilled') {
        results.push(result.value);
      } else {
        errors.push(result.reason);
        console.error('Batch item failed:', result.reason);
      }
    }
  }

  return { results, errors };
}
```

---

## 4. Token Optimization Presets

```python
# Deterministic extraction (structured data)
EXTRACT_CONFIG = {
    "response_mime_type": "application/json",
    "temperature": 0,
    "max_output_tokens": 4096,
}

# Creative generation (advisory, summaries)
GENERATE_CONFIG = {
    "temperature": 0.7,
    "max_output_tokens": 8192,
}

# Classification / yes-no decisions
CLASSIFY_CONFIG = {
    "response_mime_type": "application/json",
    "temperature": 0,
    "max_output_tokens": 256,
}

# Transcription (from LabTranscription)
TRANSCRIBE_CONFIG = {
    "temperature": 0,
    "max_output_tokens": 65536,  # long transcripts
}
```

---

## 5. Frontend Timeout (Critical for AI Endpoints)

```typescript
async function fetchWithTimeout(
  url: string,
  options: RequestInit = {},
  timeoutMs: number = 120_000
): Promise<Response> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);

  try {
    const response = await fetch(url, {
      ...options,
      signal: controller.signal,
    });
    return response;
  } finally {
    clearTimeout(timer);
  }
}
```

Without this, the UI hangs indefinitely on slow AI calls.
