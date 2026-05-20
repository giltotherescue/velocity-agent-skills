---
name: vl-stage
description: Use when a branch, worktree, local app, or cloud-agent task needs a staged test environment without disturbing the main checkout, especially for browser-facing web app work. Helps agents choose and set up the right strategy for browser/app testing across JavaScript/TypeScript, Python, PHP, Docker Compose, local framework servers, cloud sandboxes, and other project runtimes. Covers worktree placement, dev servers, ports, environment isolation, database/cache/queue isolation, verification URLs, logs, artifacts, and safe teardown.
version: 1.0.0
---

# Velocity Stage

Use this skill when work needs to run somewhere real: a local URL, dev server, container, framework-specific local environment, isolated worktree, or cloud-agent sandbox. It is especially useful for web apps, where browser-facing behavior needs to be tested like a user without disrupting the user's main checkout.

Prefer the simplest strategy that proves the work:
- Existing checkout + dev server when there is no isolation risk.
- Existing git worktree when one already exists.
- New git worktree when the main checkout is busy or the user asks for parallel work.
- Framework dev server for most JS, Python, Rails, or PHP apps.
- Docker Compose when the project already uses it.
- Framework-specific local hosting when that is clearly the project's convention.
- Existing cloud-agent environment when the task is already running in a remote sandbox.

## Cloud-Agent Compatibility

Cloud agents such as Claude Code on the web, Cursor cloud agents, and Codex web often already run each task in an isolated cloud environment. In that context, the cloud environment is usually the stage.

Before doing local-machine setup, detect whether the session is remote or ephemeral:

```bash
env | sort | rg -i 'CODEX|CLAUDE|CURSOR|CODESPACE|GITHUB_ACTIONS|CI|REMOTE|CONTAINER|DEVCONTAINER'
pwd
hostname
git worktree list
```

When running in a cloud-agent environment:
- Prefer the existing checkout/sandbox over creating or moving git worktrees.
- Do not assume access to the user's local browser, `localhost` from their machine, Herd/Valet, desktop apps, keychain, or parked site directories.
- Prefer project setup scripts, checked-in devcontainer/Dockerfile config, package scripts, and documented test commands.
- Start servers on `127.0.0.1` or `0.0.0.0` only when the platform supports local port access or browser automation from inside the sandbox.
- Use headless browser tools when available. If they are not available, run build/test/static checks and document that interactive browser verification was not possible in the cloud environment.
- Treat secrets and network access as environment-scoped. Do not ask the user to paste secrets into chat; ask them to configure environment secrets/settings when needed.
- Save review artifacts inside the repository or a clearly named artifact folder so they can be included in the branch, PR, or handoff.
- Make teardown lightweight: stop processes you started, but do not remove the cloud checkout unless the platform explicitly requires it.

## 1. Identify The Target

Inspect:

```bash
pwd
git status --short
git branch --show-current
git worktree list
rg --files | rg '(^package.json$|pyproject.toml|requirements.txt|manage.py|app.py|composer.json|artisan|Gemfile|docker-compose|compose.yaml|vite.config|next.config)'
```

Determine:
- Target branch or worktree path.
- Whether the current checkout is safe to use.
- Whether this is local, remote over SSH/devcontainer, CI, or a cloud-agent sandbox.
- App stack and expected staging command.
- Required services: database, Redis, queue worker, web socket server, object storage, external APIs.
- Whether local `.env` or secrets exist and must remain uncommitted.

Never delete, reset, or move a dirty worktree without explicit approval.

## 2. Choose A Staging Strategy

Use this order:

1. Existing cloud-agent sandbox when already running remotely.
2. Existing project command if the checkout can be used directly.
3. Existing worktree if main checkout is busy.
4. New worktree when parallel testing is needed and the environment is local or worktree-friendly.
5. Docker Compose if the repo already uses it for local development.
6. Framework-specific local hosting if that is clearly the local convention.

For a new worktree in a local/worktree-friendly environment:

```bash
git worktree add /path/to/stage-worktree branch-name
git -C /path/to/stage-worktree status --short
```

For moving an existing worktree, prefer `git worktree move` from the main checkout so Git metadata stays correct.

In cloud-agent sandboxes, avoid `git worktree move` and local parked-directory setup unless the platform documentation explicitly supports it. Cloud tasks are already isolated and usually produce a branch or PR as the review boundary.

## 3. Detect The Runtime

### JavaScript / TypeScript

Inspect `package.json` scripts and lockfiles. Prefer the repo's scripts over guessing:

```bash
npm install
npm run dev -- --host 127.0.0.1 --port 5173
npm run build
npm test
```

Use `pnpm`, `yarn`, or `bun` when the lockfile indicates it. Pick a free port and record it.

Common URLs:
- Vite: `http://127.0.0.1:5173`
- Next.js: `http://127.0.0.1:3000`
- Astro/SvelteKit/Nuxt: use the printed dev server URL.

### Python

Inspect `pyproject.toml`, `requirements.txt`, and app entrypoints. Prefer the repo's documented command:

```bash
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
pytest
```

Common servers:

```bash
python manage.py runserver 127.0.0.1:8000
flask --app app run --host 127.0.0.1 --port 5000
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

### PHP / Laravel

If `artisan` and `composer.json` are present, follow the app's local convention: built-in PHP server, Valet, Herd, Sail, Docker, or the documented team setup.

If a Laravel Valet/Herd-style `.test` URL is available and the user wants that kind of local site, detect the actual parked path instead of assuming `~/Sites`. First check which CLI exists, then use only commands for the installed tool:

```bash
command -v herd
herd parked --json
herd parked
herd links
herd paths
command -v valet
valet paths
valet parked
valet links
```

Use one obvious parked root, or ask the user if multiple roots are plausible. A Laravel/PHP worktree can be moved under the parked root or explicitly linked when supported by the local tool:

```bash
git -C /path/to/main worktree move /path/to/worktree /path/to/herd-root/site-name
cd /path/to/worktree
# use the installed local-site tool
herd link site-name
valet link site-name
```

Set local-only `.env` values such as `APP_URL`, `SESSION_COOKIE`, database name/path, cache prefix, Redis prefix, and queue connection so this staged app does not collide with another checkout.

For Vite-backed Laravel apps:

```bash
npm ci
npm run build
test -f public/build/manifest.json
php artisan optimize:clear --no-interaction
```

### Docker Compose

If the project uses Compose for local development, prefer the documented service names:

```bash
docker compose up -d
docker compose ps
docker compose logs --tail=100 app
```

Avoid changing shared ports without checking the compose file. Use project names or env files if multiple checkouts need to run at once.

### Cloud Sandbox

For cloud agents, prefer commands that work in a fresh clone:

```bash
# discover project setup
rg -n 'setup|install|dev|test|build|start' README.md package.json pyproject.toml composer.json Gemfile Makefile justfile Taskfile.yml

# common verification pattern
npm install && npm run build && npm test
pytest
composer install && vendor/bin/phpunit
```

If the platform exposes forwarded ports, start the app with the normal dev command and verify the printed or forwarded URL. If not, verify with local `curl` from inside the sandbox:

```bash
curl -I --max-time 10 "http://127.0.0.1:PORT"
```

If no browser automation is available, record that limitation and produce the strongest available proof: passing tests, successful build, server logs, static HTML output, screenshots from available headless tools, or a clear handoff with commands for local visual review.

## 4. Isolate State

Prevent collisions with the main checkout:
- Use a unique port.
- Use local-only env files.
- Use a separate database or copied test database.
- Use unique Redis/cache/session prefixes.
- Use separate object storage buckets/prefixes or local fakes where possible.
- Run queue workers from the staged checkout, not from another checkout's worker process.

In cloud sandboxes, collision risk is usually lower because the task environment is isolated, but secrets, network access, and external services are often more constrained. Prefer local fakes, test databases, SQLite, mocked services, or documented sandbox credentials.

For queues/jobs, prefer a worker tied to the staged environment:

```bash
# generic examples
npm run worker
python -m celery -A app worker
php artisan queue:work --queue=default
```

Do not point a staged app at production services unless the user explicitly asks and the repo's safety docs allow it.

## 5. Start And Verify

Start the app with a long-running terminal session or the project's normal process manager. Then verify:

```bash
curl -I --max-time 10 "$URL"
```

Open the URL in a browser automation tool and check:
- Page loads without server errors.
- Browser console has no new blocking errors.
- Auth or seeded test data works.
- The target feature can be reached.

If the environment cannot expose a browser or forwarded URL, do not pretend the browser check happened. State the limitation and include the exact command a local reviewer can run.

For frontend work, `/vl-screenshot` is the natural next step after staging verification.

## 6. Teardown

Document how to stop what you started:
- Dev server session id or command.
- Docker Compose project/service stop command.
- Queue worker command to stop.
- Framework local-site link or parked path cleanup.
- Worktree move/remove instructions.
- Cloud sandbox limitations or artifact locations.

Before removing a worktree:

```bash
git -C /path/to/worktree status --short
```

Never remove a dirty worktree without explicit approval.

## Final Response Checklist

Report:
- Stage path and branch/worktree.
- URL.
- Stack and staging strategy used.
- Commands used to install/build/start.
- Env/data/cache/queue isolation notes.
- Browser or curl verification result.
- Whether the stage ran locally or in a cloud-agent sandbox.
- Teardown commands.
- Anything not verified and why.
