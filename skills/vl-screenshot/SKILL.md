---
name: vl-screenshot
description: Use when frontend work needs a shareable folder of screenshots for design, product, QA, stakeholder, or non-technical team review. Captures a whole feature flow across states/pages, creates a two-column clickable index.html contact sheet, and documents how to refresh the folder after UI changes. Works for any web project with a browser-accessible local or remote URL.
version: 1.0.0
---

# Velocity Screenshot

Create a review folder that lets the team see an entire frontend flow at a glance, click through screenshots in-page, and download the screenshots as a zip for sharing.

## Output Standard

The folder should contain:
- Numbered screenshots, using names like `01-start.png`, `02-empty-state.png`, `03-results.png`.
- `index.html`, a clickable contact sheet with a two-column desktop grid and in-page previous/next screenshot viewer.
- `screenshots.zip`, a downloadable zip of the matched screenshots for sharing in Slack, email, or issue comments.
- Screenshots large enough to inspect real UI, preferably full-page for long flows.
- Real loaded content where possible, not loading placeholders, unless the loading state itself is part of the review.

Default folder naming:

```text
~/Desktop/<feature-name>-screenshots
```

## Workflow

1. Identify the review audience and what they need to judge.
2. List the states/pages that tell the feature story from start to finish.
3. Prepare stable test data so screenshots show realistic content.
4. Capture numbered screenshots with the available browser tool: Playwright, Cypress, Puppeteer, Selenium, agent-browser, framework browser tests, or the agent's built-in browser.
5. Build `index.html` with `scripts/build_contact_sheet.py`.
6. Open the folder and `index.html`.
7. Spot-check the most important screenshots visually before handing off.
8. If the feature requires staged backend state, document the refresh steps next to the implementation.

## Capture Guidance

Prefer full-page screenshots for flows with cards, lists, or long forms.

Example with an agent-browser style CLI:

```bash
agent-browser open "$URL"
agent-browser wait 1200
agent-browser screenshot --full "$OUT/01-start.png"
```

Use a named browser session when auth or cookies matter:

```bash
AGENT_BROWSER_SESSION=feature-review agent-browser open "$URL"
AGENT_BROWSER_SESSION=feature-review agent-browser screenshot --full "$OUT/01-start.png"
```

If the UI depends on queued jobs, external services, or backend states, create a temporary staging helper that:
- Mutates only local/test data.
- Can stage each state deterministically.
- Restores the record to a stable final state after capture.
- Is referenced in handoff notes if another person needs to refresh screenshots.

Do not hand off screenshots that only show loading states unless those states are intentionally under review.

## Build The Contact Sheet

From the skill directory, run:

```bash
python3 scripts/build_contact_sheet.py \
  ~/Desktop/<feature-name>-screenshots \
  --title "<Feature Name> Review" \
  --subtitle "Full flow screenshots. Click any image for detail."
```

The generated `index.html` uses a responsive two-column grid on desktop and one column on small screens. Clicking a screenshot opens an in-page viewer with previous, next, close, Escape, left-arrow, and right-arrow controls. By default it also creates `screenshots.zip` and adds a download link at the top of the page.

Useful options:

```bash
--columns 2
--pattern '*.png'
--zip-name screenshots.zip
--no-zip
--open
```

## Available Scripts

- `scripts/build_contact_sheet.py` creates a responsive `index.html` contact sheet from screenshots in a review folder.

## Handoff Notes

When asked to make a handoff document, include:
- Worktree, branch, deployment path, or staged app path.
- Local/stage URL and auth details, if safe for local test use.
- Screenshot folder path.
- Contact sheet path.
- Downloadable zip path.
- Exact command sequence to refresh screenshots after changes.
- Any data staging helper path and how to restore state.
- What the reviewer should focus on.
- Known concerns or tradeoffs.
- Test/build commands that should pass before sharing.

## Quality Bar

Before final response:
- Confirm `index.html` exists and opens.
- Confirm `screenshots.zip` exists unless `--no-zip` was used.
- Confirm the folder contains the expected screenshots.
- View at least one image-heavy or high-risk screenshot.
- Mention any state that could not be captured.
