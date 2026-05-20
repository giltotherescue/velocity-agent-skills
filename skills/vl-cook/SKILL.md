---
name: vl-cook
description: Use when the user wants an agent to autonomously build, fix, or improve web-app software end-to-end with the strongest reasonable development, staging, verification, review-artifact, and handoff loop. Trigger on requests like "use /vl-cook", "cook", "run with this", "just build it", "iterate on this", "take it as far as you can", or long-running feature work where stopping after the first patch would be insufficient. Consider vl-stage, vl-screenshot, and vl-handoff when they help prove or package the work.
version: 1.0.0
---

# Velocity Cook

Use this skill when the user wants execution, not just a plan. Keep working through implementation, tests, app/browser checks, review, and handoff until the work is ready for human review.

You are the executing agent. Do not write a prompt for another agent. Do not stop because the first patch compiles. Continue until the requested outcome behaves correctly, is verified, and is easy to review.

## Operating Mode

- Act autonomously when the request is clear enough.
- Ask at most 1-3 questions only when the answer materially changes what to build.
- Read project instructions first: `AGENTS.md`, `CLAUDE.md`, README files, and relevant docs.
- Follow existing project conventions before adding new architecture.
- Preserve user work and avoid destructive git commands.
- Keep a task plan for multi-step work.
- Prefer small, reversible slices over one large speculative rewrite.

## Decide The Max Useful Loop

Default to the strongest reasonable loop for the task:
- Code changes.
- Focused tests.
- Typecheck, lint, format, or build checks.
- Local staging or browser checks when the work has an app surface.
- Contact sheets or other review artifacts when the work is visual.
- A handoff when another person or agent will review or continue.

Skip expensive steps only when they do not prove the outcome, would spend real provider budget unnecessarily, or the user explicitly limits scope.

Use `/vl-stage` when any of these are true:
- The main checkout is being used for other testing.
- The work needs a stable local URL, dev server, or app runtime.
- A worktree, branch, container, database, cache, session, queue, or port needs isolation.
- Browser testing is part of proving the work.
- The agent is running in a cloud/remote environment and needs to decide what "staged" can realistically mean there.

Decide whether staging should use a worktree:
- Use the current checkout for small changes, documentation, narrow fixes, or work that the user is already doing in this checkout.
- Infer that a worktree is appropriate when the main checkout is dirty with unrelated work, the user mentions parallel testing, the work will take multiple iterations, or local services/state could interfere with another task.
- Ask one brief question when the choice is ambiguous and the setup cost is meaningful, for example: "Should I keep this in the current checkout, or create/use a worktree so it can run separately?"
- If the user has already implied isolation, proceed with `/vl-stage` and a worktree without asking again.
- In cloud-agent sandboxes, usually keep the existing checkout and let `/vl-stage` define the available staged environment instead of creating local worktrees or assuming access to the user's machine.

Use `/vl-screenshot` near the end when any of these are true:
- The change affects a browser-facing UI, app flow, dashboard, editor, onboarding, wizard, or visual output.
- The user asks for UI/UX review, screenshots, stakeholder review, QA review, or team review.
- The flow is hard to evaluate from text alone.
- A contact sheet would save reviewers from clicking through the same browser flow manually.

Use `/vl-handoff` at the end when the work needs to be passed to another developer, reviewer, stakeholder, team, or agent.

## Loop

### 1. Frame The Goal

Identify:
- The user-visible outcome.
- The required slices needed to complete the whole request.
- The risky surfaces: auth, billing, data writes, migrations, queues/jobs, external APIs, browser flows, public UI.
- The verification loop that would actually prove the work.
- Whether this should stay in the current checkout or use a worktree through `/vl-stage`.

### 2. Research The Project

Find the current patterns before editing:

```bash
rg "relevant term"
rg --files
git status --short
```

Inspect the relevant surfaces for the detected stack:
- Routes, controllers, handlers, API clients, services, jobs, models, schemas, and migrations.
- UI components, templates, styles, state management, and browser entrypoints.
- Existing tests around the same behavior.
- Package scripts and framework commands.

When framework APIs matter, check version-specific documentation before changing code.

### 3. Plan All Slices

Write a short implementation plan with:
- Every required slice in dependency order.
- Files likely to change.
- Tests or checks to add or update.
- Staging, browser, queue/job, database, or migration checks needed.
- Whether `/vl-stage`, `/vl-screenshot`, or `/vl-handoff` applies.
- What "ready for review" means for this request.

Implement every required slice. Do not stop after the first slice unless the user explicitly asked for a partial spike.

### 4. Build And Verify Each Slice

Use the stack's normal tools and existing project style.

Common checks by ecosystem:

```bash
# JavaScript / TypeScript
npm test
npm run typecheck
npm run lint
npm run build

# Python
pytest
ruff check .
mypy .
pyright

# PHP / Laravel
vendor/bin/pint --dirty --format agent
php artisan test --compact --filter=RelevantTest
npm run build

# Ruby / Rails
bundle exec rspec
bin/rails test
bundle exec rubocop
```

Use the project's actual scripts when they differ. Run the narrowest useful check first, then broaden when the risk or blast radius justifies it.

### 5. Verify In The App

For app UI, use it like a customer:
- Start or locate the local stage URL.
- Log in or seed stable test data when needed.
- Exercise the happy path and the most likely failure path.
- Check browser console and network errors.
- Check responsive layouts when the UI is customer-facing.

If isolation matters, use `/vl-stage` before browser checks.

For visual work, consider `/vl-screenshot` after the flow is stable. Capture real loaded states, not only loading placeholders unless loading is intentionally under review.

### 6. Review The Diff

Before declaring done, review your own work:
- Does the implementation satisfy the original request?
- Are validation, authorization, tenant/user scope, and error handling correct where relevant?
- Are async jobs idempotent enough for retries?
- Are external calls timeout/retry/error-handled?
- Are tests proving behavior rather than implementation details?
- Is there avoidable complexity, dead code, or naming drift?

Fix issues immediately.

### 7. Iterate

When verification fails:
1. Name the specific failure.
2. Map it to the smallest likely code area.
3. Patch that area.
4. Re-run the narrowest check that proves the fix.

If the loop stalls, report the blocker with evidence and the best next move.

### 8. Handoff

Finish with:
- What changed.
- Files or areas touched.
- Tests/build/browser checks run.
- Stage URL, contact sheet, screenshot folder, zip, logs, or worker commands when applicable.
- Known tradeoffs or follow-up risks.
- Whether the work was committed or left unstaged.

If the user asked for a commit, commit only the relevant files with a clear message.

## Done Means

The work is not done until:
- Every planned slice needed for the request is complete.
- The implementation follows local conventions.
- Relevant automated checks pass or failures are clearly explained.
- The user-facing flow was exercised when UI is involved.
- Staging, contact sheet, or handoff artifacts exist when they are part of proving or reviewing the work.
