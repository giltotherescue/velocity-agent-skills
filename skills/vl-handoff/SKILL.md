---
name: vl-handoff
description: Use when current work needs to be handed off to another developer, agent, reviewer, manager, client, stakeholder, or team. Produces a context-rich handoff tailored to the recipient and delivery medium, including current status, decisions, changed files, verification, open risks, artifacts, and recommended next steps. Trigger on requests like "handoff", "write this up for", "brief the next person", "summarize progress for Slack", "prepare a review handoff", or "pass this to another agent".
version: 1.0.0
---

# Velocity Handoff

Create a handoff that lets the next person or agent continue from the current state without reconstructing context from chat history, diffs, terminal output, or guesswork.

## Operating Mode

Be efficient. If the recipient or medium is obvious from the user's request, infer it and continue. Ask at most one clarifying question only when the answer materially changes the format or content.

Useful question when needed:

```text
Who is this handoff for, and where will you send it?
```

If the user does not answer or the context is still unclear, default to a developer-to-developer handoff in Markdown.

## Determine Audience And Medium

Identify:
- Recipient: another AI agent, senior developer, frontend developer, backend developer, product/design reviewer, QA, manager, client, or general team.
- Medium: Slack message, GitHub PR/comment, issue tracker, email/doc, README-style handoff, agent continuation prompt, or internal review note.
- Goal: continue implementation, review UI/UX, test a feature, make a go/no-go decision, debug an issue, or understand status.

Shape the output to the medium:
- Slack: concise, skimmable, action-oriented, with links/artifacts near the top.
- GitHub PR/comment: structured, technical, with files, tests, risks, and review focus.
- Issue tracker: status, reproduction/verification steps, acceptance criteria, next owner.
- Agent handoff: exact current state, constraints, commands run, commands not run, files changed, next task list.
- Non-technical review: plain language, visible behavior, screenshots, review questions, and what feedback is needed.

## Gather Context

Use available local context before writing:
- `git status --short`
- `git diff --stat`
- Relevant staged/unstaged diffs.
- Recent commits if the work was committed.
- Test/build/browser commands run and their outcomes.
- Local URLs, worktree paths, queue/worker commands, logs, screenshot contact sheets, zip files, demos, or generated artifacts.
- Explicit decisions or constraints from the conversation.

Do not include secrets, `.env` values, tokens, private customer data, or irrelevant implementation churn.

## Handoff Content

Include the pieces that matter for the recipient:
- Current status: done, partially done, blocked, needs review, or needs testing.
- Goal and user-facing outcome.
- What changed, grouped by area.
- Important decisions and why they were made.
- Files or modules touched.
- Verification completed: tests, build, browser checks, queue/job checks, smoke tests.
- Verification not completed and why.
- Artifacts: stage URL, branch, PR, screenshot folder, contact sheet, zip file, logs, demo video, generated output.
- Known risks, tradeoffs, and edge cases.
- Recommended next steps in priority order.
- Clear ask: what the recipient should review, test, decide, or do next.

If the work used `/vl-stage`, include:
- Stage URL.
- Worktree or project path.
- Stack and staging strategy.
- Environment/data/cache/queue isolation notes.
- Worker commands, if relevant.
- Teardown or cleanup notes.

If the work used `/vl-screenshot`, include:
- Screenshot folder path.
- `index.html` contact sheet path.
- `screenshots.zip` path.
- What states/pages were captured.
- Any states that could not be captured.

If the work came from `/vl-cook`, include:
- Implementation slices completed.
- Verification loop attempted.
- What remains before the work is truly done, if anything.

## Output Templates

### Developer / Agent Handoff

```markdown
## Handoff

**Status:** Done / In progress / Blocked / Ready for review
**Goal:** ...
**Branch/worktree:** ...

### What Changed
- ...

### Decisions
- ...

### Verification
- Passed: ...
- Not run: ...

### Artifacts
- URL: ...
- Screenshots/contact sheet/zip: ...

### Risks / Open Questions
- ...

### Recommended Next Steps
1. ...
2. ...
3. ...
```

### Slack / Team Review

```markdown
Quick handoff on <feature>:

Status: ...
What changed: ...
Review link/artifacts: ...
What I need feedback on: ...
Known caveats: ...
Next step: ...
```

### Non-Technical Review

```markdown
Here is what is ready to review:

- What changed:
- Where to review it:
- Screenshots/contact sheet:
- What feedback would be most helpful:
- Known issues:
- What happens next:
```

## Quality Bar

Before finalizing:
- The recipient can tell what happened, what matters, and what to do next.
- Links, file paths, URLs, screenshots, and zip paths are included when available.
- The handoff is short enough for the medium but complete enough to continue the work.
- Uncertainty is labeled clearly instead of hidden.
- The handoff does not leak secrets or unnecessary private data.
