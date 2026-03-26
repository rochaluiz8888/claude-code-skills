---
name: conductor
description: >
  Project lifecycle management: plan.md task tracking, TDD red/green/refactor,
  conventional commits with git notes, phase checkpoints with verification reports.
  Use when starting a new feature track, working through a plan, or when the user
  says "follow conductor", "use the workflow", "track this in plan.md", or
  "checkpoint this phase". Also auto-triggers when plan.md exists in the project root.
argument-hint: [task-name or phase-name]
---

# Conductor — Project Lifecycle Management

You are operating under the Conductor workflow. All work is tracked in `plan.md`,
committed with conventional commits, and verified at phase boundaries.

## Core Principles

1. **plan.md is the source of truth** — all work must be tracked there
2. **Tech stack is deliberate** — changes to stack must be documented before implementation
3. **TDD** — write failing tests before implementing
4. **>80% coverage** — for all new/modified modules
5. **Non-interactive & CI-aware** — use `CI=true` for watch-mode tools

## Task Workflow

When working on a task from `plan.md`:

### 1. Select & Mark In Progress
- Choose the next `[ ]` task in sequential order
- Change `[ ]` to `[~]` in `plan.md`

### 2. Red Phase (Write Failing Tests)
- Create test file for the feature/fix
- Write tests that define expected behavior
- **Run tests and confirm they FAIL** — do not proceed until red

### 3. Green Phase (Implement)
- Write minimum code to make tests pass
- Run tests and confirm all pass

### 4. Refactor (Optional)
- Improve clarity, remove duplication
- Re-run tests to confirm still green

### 5. Verify Coverage
```bash
# Python
pytest --cov=app --cov-report=html
# TypeScript
npx vitest run --coverage
```
Target: >80% on new code.

### 6. Document Deviations
If implementation differs from tech stack: **STOP**, update `tech-stack.md` with dated note, then resume.

### 7. Commit Code
Stage all task-related changes. Use conventional commit:
```
<type>(<scope>): <description>
```

**Types:** `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`, `conductor`

### 8. Attach Git Note
```bash
HASH=$(git log -1 --format="%H")
git notes add -m "<Task Summary>
- Task: <name>
- Changes: <summary>
- Files: <list>
- Why: <reasoning>" $HASH
```

### 9. Update plan.md
Change `[~]` to `[x]` and append first 7 chars of commit SHA:
```
- [x] **Task: Implement auth flow** a1b2c3d
```

### 10. Commit Plan Update
```bash
git add plan.md
git commit -m "conductor(plan): Mark task '<Task Name>' as complete"
```

## Phase Checkpoint Protocol

**Trigger:** when a task completion also concludes a phase in `plan.md`.

1. **Announce** — inform user that phase is complete, checkpoint protocol starting
2. **Ensure test coverage for all phase changes:**
   - Find previous checkpoint SHA from plan.md
   - `git diff --name-only <previous_sha> HEAD` to list changed files
   - Verify test file exists for each code file; create if missing
3. **Run automated tests** — announce exact command before running.
   If tests fail: attempt fix max 2 times, then ask user for guidance.
4. **Propose manual verification plan** — step-by-step with commands and expected outcomes
5. **Await explicit user confirmation** — do not proceed without "yes"
6. **Create checkpoint commit:**
   ```bash
   git commit --allow-empty -m "conductor(checkpoint): Checkpoint end of Phase <Name>"
   ```
7. **Attach verification report via git note** — include test command, manual steps, user confirmation
8. **Update plan.md** — append `[checkpoint: <sha>]` to phase heading
9. **Commit plan update:**
   ```bash
   git commit -m "conductor(plan): Mark phase '<Name>' as complete"
   ```

## Quality Gates (Before Marking Any Task Complete)

- [ ] All tests pass
- [ ] Coverage >80% on new code
- [ ] Code follows project style guide
- [ ] Public functions/methods documented
- [ ] Type safety enforced (type hints / TS types)
- [ ] No linting or static analysis errors
- [ ] No security vulnerabilities introduced

## Commit Message Reference

```bash
git commit -m "feat(audio): Integrate GCP Speech-to-Text V2 Batch API"
git commit -m "fix(api): Handle 404 Entity Not Found on missing recognizer"
git commit -m "test(ingestion): Add coverage for audio uploader endpoint"
git commit -m "conductor(plan): Mark task 'Create user model' as complete"
git commit -m "conductor(checkpoint): Checkpoint end of Phase 1"
```

## Initializing Conductor in a New Project

If no `plan.md` exists yet, create one:

```markdown
# Project Plan

## Phase 1: <Phase Name>
- [ ] **Task: <description>**
    - [ ] Write Tests: <what to test>
    - [ ] Implement: <what to build>
- [ ] **Task: Conductor - User Manual Verification 'Phase 1' (Protocol above)**

## Phase 2: <Phase Name>
...
```

Then follow the task workflow above from task 1.
