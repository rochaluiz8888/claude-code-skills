import os
import sys
import json
import logging
from pathlib import Path

logging.basicConfig(level=logging.WARNING, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# Directories to skip during filesystem walk
SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv", ".tox", "dist", "build"}

# File extensions to scan for dangerous patterns
SCANNABLE_EXTENSIONS = {".py", ".js", ".ts", ".tsx", ".jsx", ".mjs", ".cjs", ".html"}

# --- Best Practice Knowledge Base (Audit Pillar 0) ---
HAZARD_DATABASE = {
    "libraries": {
        "fastapi": {
            "hazards": ["N+1 SQL queries with background tasks", "Blocking async event loop with sync drivers"],
            "best_practices": ["Use run_in_threadpool for sync DB calls", "Prefer aiosqlite for SQLite"]
        },
        "sqlite": {
            "hazards": ["Transaction locks during parallel writes", "N+1 SELECT patterns"],
            "best_practices": ["Enable WAL mode (PRAGMA journal_mode=WAL)", "Use 'IN' clauses for bulk fetching"]
        },
        "google-genai": {
            "hazards": ["Uncapped parallel calls (429 Overflow)", "Prompt token bloating", "Missing grounding cache (duplicate searches)"],
            "best_practices": ["Use Semaphore(N) for parallel uploads", "Implement content hashing/caching (Smart Skip)", "Cache grounding results with 24h TTL"]
        },
        "google-drive": {
            "hazards": ["Memory saturation on large downloads", "Token expiration race conditions"],
            "best_practices": ["Use stream=True for downloads", "Validate access_token before each batch"]
        },
        "express": {
            "hazards": ["Missing rate limiting on API routes", "No graceful shutdown (SIGTERM)", "No health check endpoint", "Missing CSP/HSTS headers"],
            "best_practices": ["Add express-rate-limit with tiered limits", "Register SIGTERM/SIGINT handlers", "Add /healthz endpoint", "Set CSP, HSTS, X-Content-Type-Options headers"]
        },
        "firebase": {
            "hazards": ["Missing Firestore rules for new collections", "OAuth tokens in plaintext cookies", "skipLibCheck masking missing @types/react"],
            "best_practices": ["Add rules for every collection including backups", "Encrypt cookie values with AES-256-GCM", "Install @types/react@^19 for React 19 projects"]
        },
        "googleapis": {
            "hazards": ["OAuth callback XSS via APP_URL injection", "Token refresh race conditions on concurrent requests"],
            "best_practices": ["Sanitize APP_URL before injecting into HTML", "Serialize token refresh with mutex/lock"]
        },
        "motion": {
            "hazards": ["JS animations ignore prefers-reduced-motion", "Ease arrays cause TS errors without 'as const'"],
            "best_practices": ["Use useReducedMotion() hook in every animated component", "Type ease arrays with 'as const' for tuple compatibility"]
        },
        "tailwindcss": {
            "hazards": ["Opacity-based text colors fail WCAG contrast (text-white/40 on dark bg)", "Missing focus-visible indicators"],
            "best_practices": ["Use text-white/60+ minimum for readable text on dark backgrounds", "Add :focus-visible styles with 2px solid outline"]
        }
    },
    "patterns": {
        "setInterval": {
            "hazard": "Stacking/Freezing during network latency",
            "best_practice": "Replace with recursive setTimeout"
        },
        "innerHTML": {
            "hazard": "Slow DOM reflows with large datasets",
            "best_practice": "Use DocumentFragments or throttled rendering"
        },
        "dangerouslySetInnerHTML": {
            "hazard": "XSS vulnerability if content is not sanitized",
            "best_practice": "Sanitize with DOMPurify or use safe rendering patterns"
        },
        "JSON.stringify(tokens)": {
            "hazard": "Plaintext sensitive data in cookies",
            "best_practice": "Encrypt with AES-256-GCM before storing in cookies"
        },
        "for (": {
            "hazard": "Potential sequential await-in-loop (check for await inside)",
            "best_practice": "Use Promise.allSettled() with bounded concurrency for independent operations"
        }
    }
}

def analyze_project(root_path):
    findings = {
        "libraries_found": [],
        "relevant_hazards": [],
        "recommended_checks": []
    }

    # 1. Scan requirements.txt / package.json
    for filename in ["requirements.txt", "package.json"]:
        p = Path(root_path) / filename
        if p.exists():
            try:
                content = p.read_text(encoding="utf-8").lower()
                for lib, data in HAZARD_DATABASE["libraries"].items():
                    if lib in content:
                        findings["libraries_found"].append(lib)
                        findings["relevant_hazards"].extend(data["hazards"])
                        findings["recommended_checks"].extend(data["best_practices"])
            except (OSError, UnicodeDecodeError) as e:
                logger.warning("Could not read %s: %s", p, e)

    # 2. Grep for dangerous patterns
    for root, dirs, files in os.walk(root_path):
        # Prune directories that should never be scanned
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]

        for f in files:
            if Path(f).suffix in SCANNABLE_EXTENSIONS:
                f_path = Path(root) / f
                try:
                    text = f_path.read_text(encoding="utf-8", errors="replace")
                    for pattern, data in HAZARD_DATABASE["patterns"].items():
                        if pattern in text:
                            findings["relevant_hazards"].append(
                                f"Pattern detected ({pattern}) in {f}: {data['hazard']}"
                            )
                            findings["recommended_checks"].append(
                                f"Fix for {pattern}: {data['best_practice']}"
                            )
                except OSError as e:
                    logger.warning("Could not read %s: %s", f_path, e)

    # Deduplicate while preserving order
    findings["libraries_found"] = list(dict.fromkeys(findings["libraries_found"]))
    findings["relevant_hazards"] = list(dict.fromkeys(findings["relevant_hazards"]))
    findings["recommended_checks"] = list(dict.fromkeys(findings["recommended_checks"]))

    return findings

if __name__ == "__main__":
    project_root = sys.argv[1] if len(sys.argv) > 1 else "."
    if not Path(project_root).is_dir():
        print(f"Error: '{project_root}' is not a valid directory", file=sys.stderr)
        sys.exit(1)

    report = analyze_project(project_root)
    print("\n--- AUTO-ENHANCED AUDIT CONTEXT ---")
    print(json.dumps(report, indent=2))
    print("-----------------------------------")
