# Claude Code Skills

Reusable [Claude Code](https://claude.ai/code) skills extracted from cross-project patterns. Each directory is a standalone skill that can be installed globally or per-project.

## Skills

| Skill | Command | What It Does |
|-------|---------|--------------|
| **conductor** | `/conductor` | Project lifecycle: plan.md task tracking, TDD red/green/refactor, conventional commits + git notes, phase checkpoints |
| **quality-gate** | `/quality-gate [scope]` | Unified codebase audit with 9 scopes: ai, a11y, architecture, security, structure, testing, docs, repo-health, quick |
| **gcp-bootstrap** | `/gcp-bootstrap` | Google Cloud setup: auth, API enablement, Secret Manager, config validation scaffold |
| **ai-resilience** | `/ai-resilience` | AI/LLM hardening: retry + backoff, smart-skip caching, batch concurrency, token optimization |
| **style-guide** | `/style-guide` | Google style guide enforcement for Python, TypeScript, JavaScript, HTML/CSS |

## Installation

### Global (all projects)

```bash
# Install a single skill
cp -r <skill-name> ~/.claude/skills/

# Install all skills
cp -r conductor quality-gate gcp-bootstrap ai-resilience style-guide ~/.claude/skills/
```

### Per-project

```bash
# Copy into your project's .claude/skills/ directory
mkdir -p .claude/skills
cp -r <skill-name> .claude/skills/
```

## Quality Gate Scopes

The `/quality-gate` skill accepts an optional scope argument to focus the audit:

```
/quality-gate              # Full audit (all 9 scopes)
/quality-gate security     # Application security + config hygiene
/quality-gate testing      # Test quality + infrastructure + coverage
/quality-gate ai           # AI/LLM integration assessment
/quality-gate a11y         # Accessibility & inclusive design
/quality-gate architecture # Cloud-native architecture & scalability
/quality-gate docs         # Documentation strategy
/quality-gate repo-health  # Repository & project health
/quality-gate structure    # Code structure (LOC, duplication, coupling)
/quality-gate quick        # Top-3 critical findings only
```

## Skill Structure

Each skill follows the [Claude Code skill conventions](https://code.claude.com/docs/en/skills):

```
skill-name/
├── SKILL.md              # Main instructions (frontmatter + content)
├── references/           # Detailed reference material
│   └── *.md
└── scripts/              # Helper scripts (optional)
    └── *.py
```

- `SKILL.md` contains YAML frontmatter (`name`, `description`, `argument-hint`) and the skill instructions
- `references/` holds detailed criteria, benchmarks, and patterns — kept separate to stay under the 500-line SKILL.md guideline
- `scripts/` contains automation helpers (e.g., `auto_enhance.py` for dependency-aware hazard detection)
