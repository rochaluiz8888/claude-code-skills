# Google Style Guides — Complete Reference

Consolidated from Brain/conductor/code_styleguides/. These are summaries of the
official Google Style Guides with the most actionable rules.

Sources:
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- [Google TypeScript Style Guide](https://google.github.io/styleguide/tsguide.html)
- [Google JavaScript Style Guide](https://google.github.io/styleguide/jsguide.html)
- [Google HTML/CSS Style Guide](https://google.github.io/styleguide/htmlcssguide.html)

---

## Python

### Language Rules
- **Linting:** Run `pylint` to catch bugs and style issues
- **Imports:** `import x` for packages/modules. `from x import y` only when `y` is a submodule
- **Exceptions:** Use built-in exception classes. No bare `except:` clauses
- **Global State:** Avoid mutable global state. Module constants: `ALL_CAPS_WITH_UNDERSCORES`
- **Comprehensions:** Simple cases only. Full loop for complex logic
- **Default Arguments:** No mutable objects (`[]`, `{}`) as defaults
- **True/False:** Implicit false (`if not my_list:`). `if foo is None:` for None checks
- **Type Annotations:** Strongly encouraged for all public APIs

### Style Rules
- **Line Length:** Max 80 characters
- **Indentation:** 4 spaces. Never tabs
- **Blank Lines:** 2 between top-level definitions, 1 between methods
- **Whitespace:** No extraneous. Surround binary operators with single spaces
- **Docstrings:** `"""triple double quotes"""`. One-line summary + `Args:`, `Returns:`, `Raises:`
- **Strings:** f-strings for formatting. Be consistent with quote style
- **TODOs:** `TODO(username): Fix this.` format
- **Import Formatting:** Separate lines, grouped: stdlib → third-party → local

### Naming
- `snake_case`: modules, functions, methods, variables
- `PascalCase`: classes
- `ALL_CAPS`: constants
- `_leading_underscore`: internal/private

### Main
- Executable files: `main()` function called from `if __name__ == '__main__':` block

---

## TypeScript

### Language Features
- `const`/`let` only. **`var` is forbidden**
- ES6 modules (`import`/`export`). **No `namespace`**
- Named exports. **No default exports**
- `private` modifier, not `#private` fields. `readonly` for never-reassigned props
- **Never use `public`** modifier (it's the default)
- Function declarations for named functions. Arrow functions for anonymous/callbacks
- Single quotes (`'`). Template literals for interpolation
- `===` / `!==` always

### Disallowed
- `any` type — use `unknown` or specific type
- Wrapper objects (`new String()`, etc.)
- ASI reliance — explicit semicolons required
- `const enum` — use plain `enum`
- `eval()` / `Function(...string)`

### Naming
- `UpperCamelCase`: classes, interfaces, types, enums, decorators
- `lowerCamelCase`: variables, parameters, functions, methods, properties
- `CONSTANT_CASE`: global constants, enum values
- **No `_` prefix/suffix** on identifiers

### Type System
- Rely on inference for simple types, be explicit for complex
- Prefer `?` optional over `| undefined`
- `T[]` for simple, `Array<T>` for complex union types
- **No `{}` type** — use `unknown`, `Record<string, unknown>`, or `object`

### Comments
- `/** JSDoc */` for documentation, `//` for implementation
- **No types in JSDoc** `@param`/`@return` blocks (redundant in TS)
- Comments must add information, not restate code

---

## JavaScript

### Basics
- Lowercase filenames with `_` or `-`. Extension: `.js`
- UTF-8 encoding. Spaces only (no tabs)
- ES modules (`import`/`export`). Named exports only

### Formatting
- Braces required for all control structures, even single-line
- K&R style ("Egyptian brackets")
- 2-space indentation
- Explicit semicolons on every statement
- 80-character column limit
- +4 space continuation indent

### Language Features
- `const` default, `let` if reassigned. **`var` forbidden**
- Trailing commas in arrays and objects
- Shorthand object properties
- Arrow functions for nested functions (preserve `this`)
- Single quotes. Template literals for multi-line/interpolation
- `for-of` preferred. `for-in` only for dict-style objects
- `===` / `!==` only

### Disallowed
- `with` keyword
- `eval()` / `Function(...string)`
- ASI reliance
- Modifying builtins (`Array.prototype.foo = ...`)

### Naming
- `UpperCamelCase`: classes
- `lowerCamelCase`: methods, functions, variables
- `CONSTANT_CASE`: constants

### JSDoc
- Required on all classes, fields, methods
- Type annotations in braces (`@param {string} name`)

---

## HTML/CSS

### General
- HTTPS for all embedded resources
- 2-space indent. No tabs
- All lowercase
- No trailing whitespace
- UTF-8 encoding (`<meta charset="utf-8">`)

### HTML
- `<!doctype html>`
- Semantic elements (purpose-based)
- `alt` text on images, captions on media
- Separate structure/presentation/behavior
- Omit `type` on `<link>` and `<script>`
- Double quotes for attribute values

### CSS
- Valid CSS only
- Meaningful class names with hyphens (`.video-player`)
- **No ID selectors** for styling — use classes
- Shorthand properties where possible
- Omit units for `0` values
- Leading `0` for decimals (`0.8em`)
- 3-char hex where possible (`#fff`)
- **No `!important`**
- Alphabetize declarations
- Semicolon after every declaration
- Space after colon, space before opening brace
- Single quotes in selectors and values
- Separate rules with blank line

---

## Quick Violation Checklist

Use this for rapid scanning:

| Rule | Grep Pattern | Language |
|------|-------------|----------|
| `var` usage | `\bvar\b` | JS/TS |
| Bare except | `except:` | Python |
| `any` type | `: any` | TS |
| Default export | `export default` | JS/TS |
| `==` / `!=` | `[^!=]=[^=]` | JS/TS |
| Mutable default | `def.*=\[\]` or `def.*=\{\}` | Python |
| Missing semicolon | (AST check needed) | JS/TS |
| `!important` | `!important` | CSS |
| ID selector | `#[a-z]` in CSS | CSS |
| `eval()` | `\beval\(` | JS/TS |
| `namespace` | `\bnamespace\b` | TS |
| `#private` | `#[a-z]` in class | TS |
- **BE CONSISTENT.** When editing code, match the existing style.
