---
name: style-guide
description: >
  Review code against Google's official style guides for Python, TypeScript,
  JavaScript, and HTML/CSS. Detects the language from file extension or project
  stack, then checks naming, formatting, imports, type safety, documentation,
  and disallowed patterns. Use when the user says "check style", "review code style",
  "does this follow Google style", "lint this", or after writing new code.
  Also auto-triggers as a reference when Claude is writing code in projects
  that use these style guides.
argument-hint: [file-path or language]
user-invocable: true
---

# Style Guide — Google Style Enforcement

Review code against the applicable Google Style Guide. Auto-detect language from
`$ARGUMENTS` (file path or language name), or scan the project to determine stack.

Read the applicable style reference from [references/](references/) before reviewing.

## Review Process

1. **Detect language** from file extension, `$ARGUMENTS`, or project files
2. **Read the reference** for that language from `references/google-styles.md`
3. **Scan the target** — if `$ARGUMENTS` is a file, review that file; if empty, review recently changed files (`git diff --name-only HEAD~1`)
4. **Report violations** in this format:

```
## Style Review: <filename>

### Violations Found

| Line | Rule | Issue | Fix |
|------|------|-------|-----|
| 12 | Naming | `myFunc` should be `my_func` (snake_case) | Rename to `my_func` |
| 45 | Imports | Bare `except:` clause | Catch specific exception |

### Summary
- X violations found (Y auto-fixable)
- Severity: <clean / minor / needs attention>
```

5. **If user says "fix"** — apply the fixes directly using Edit tool

## Key Rules by Language

### Python (Google Python Style Guide)
- snake_case for functions/variables, PascalCase for classes, ALL_CAPS for constants
- 80-char line length, 4-space indent, no tabs
- Type annotations on public APIs
- `"""Docstrings"""` with Args/Returns/Raises sections
- f-strings for formatting
- Grouped imports: stdlib, third-party, local
- No bare `except:`, no mutable default arguments
- `if foo is None:` not `if foo == None:`

### TypeScript (Google TypeScript Style Guide)
- `const`/`let` only — `var` forbidden
- Named exports only — no default exports
- No `any` — use `unknown` or specific types
- `===` always, semicolons required, single quotes
- `private` visibility — not `#private` fields
- No `_` prefix/suffix on identifiers
- `T[]` for simple types, `Array<T>` for complex unions
- JSDoc for documentation, `//` for implementation comments

### JavaScript (Google JavaScript Style Guide)
- `const` by default, `let` if reassigned — `var` forbidden
- Named exports, no default exports
- 2-space indent, 80-char column limit
- K&R brace style, trailing commas in arrays/objects
- Arrow functions for nested/anonymous functions
- `for-of` preferred, `for-in` only for dict-style objects
- Explicit semicolons, no ASI reliance

### HTML/CSS (Google HTML/CSS Style Guide)
- All lowercase for elements, attributes, selectors
- 2-space indent, no tabs
- Semantic HTML elements, `alt` text on images
- No ID selectors for styling — use classes
- Hyphenated class names (`.video-player` not `.videoPlayer`)
- No `!important`
- Alphabetize CSS declarations
- Shorthand properties where possible

### Cross-Language Principles
- **Consistency** — match existing patterns in the file
- **Readability** — avoid clever/obscure constructs
- **Simplicity** — prefer simple over complex
- **Document why** — not what
