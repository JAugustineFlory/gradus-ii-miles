# 01 — Scaffold from memory

> **Where this fits.** No new behavior yet, but **US-5** (data that
> survives) starts here: the database comes up before any app code
> exists. Everything else in this lesson is the toolbox every later
> story depends on.

**Goal:** the same skeleton you built across Tiro lessons 02, 03, 04,
05, and 07 — but from memory, with a checklist instead of step-by-step
instructions. No app code yet.

This is **retrieval practice**. Try each item before opening its hint.
Struggling to remember is the part that makes it stick.

---

## Part A — The repo

Work at the **repo root**.

- [ ] 📄 `.gitignore` covering Python caches, `.venv`, coverage reports,
      `node_modules`, `dist`, `.env`, and OS clutter
- [ ] 📄 `.gitattributes` forcing `LF` line endings
- [ ] 📄 `package.json` (root) with Husky installed as a dev dependency
      (tidy the `"description"` if `npm init` copied README text into it)
- [ ] 📄 `.husky/pre-commit` that only prints
      `Husky pre-commit hook ran.` (real checks come once tests exist)
- [ ] 📄 `.vscode/settings.json` — pytest settings, Coverage Gutters
      settings, format-on-save with Ruff and Prettier, and Python pinned
      to 4-space indentation

<details>
<summary>Hint — where to look</summary>

Tiro lesson 02, Steps 2–5. You may copy `.vscode/settings.json` from
your Tiro repo — it's configuration, not a skill.
</details>

<details>
<summary>Hint — Husky commands</summary>

```bash
npm init -y
npm install --save-dev husky
npx husky init
```
</details>

**Checkpoint:** `git add .` then `git commit -m "chore: scaffold repo"`
prints `Husky pre-commit hook ran.`, and `node_modules/` isn't
committed.

---

## Part B — The database (US-5)

Still at the **repo root**. Miles gets its **own** database server,
separate from Tiro's, on a different host port so both can run at once.

| Setting | Value |
| --- | --- |
| Image | `postgres:17` |
| User / password / database | `miles` / `miles` / `miles` |
| Host port → container port | **5434** → 5432 |
| Named volume | `miles-data` |
| Test database (created by an init script) | `miles_test` |
| Health check | `pg_isready` for user `miles`, database `miles` |

- [ ] 📄 `compose.yaml` — one `db` service matching the table, with the
      data volume, the init-script folder mounted read-only, and a
      health check
- [ ] 📄 `docker/postgres-init/01-create-test-database.sql` — creates
      `miles_test`
- [ ] `docker compose up -d --wait` reports the service **healthy**
- [ ] `psql` inside the container lists both `miles` and `miles_test`

<details>
<summary>Hint — where to look</summary>

Tiro lesson 04, Steps 1–4. Your Tiro `compose.yaml` differs only in
names and one port number.
</details>

<details>
<summary>Hint — the psql command</summary>

```bash
docker compose exec db psql -U miles -d miles -c "\l"
```
</details>

> **Already ran `up` before adding the init script?** It won't run on an
> existing volume. `docker compose down -v`, then `up` again (there's no
> data to lose yet).

---

## Part C — The backend skeleton

- [ ] A uv project in `backend/` using Python 3.12: an **app** (not a
      package), with no README, no nested Git repo, and the sample
      `main.py` deleted. **No `[build-system]` section** in
      `pyproject.toml`.
- [ ] Runtime dependencies: FastAPI (with the `standard` extra),
      SQLAlchemy (with the `asyncio` extra), asyncpg, Alembic
- [ ] Dev dependencies: pytest, pytest-asyncio, pytest-cov, Ruff
- [ ] 📄 `backend/pyproject.toml` configured so that:
  - pytest looks in `tests/`, can import `app`, runs async tests and
    fixtures automatically with a fresh event loop per test, and always
    reports coverage for `app` to the terminal (with missing lines)
    **and** to `coverage.xml`
  - Ruff uses line length 88, checks `E`, `F`, and `I`, and skips the
    `migrations` folder
- [ ] 📄 `backend/app/__init__.py` (empty — what does it do?)
- [ ] VS Code's Python interpreter set to `backend/.venv`

<details>
<summary>Hint — uv commands</summary>

```bash
uv init backend --app --no-package --no-readme --vcs none --python 3.12
cd backend
uv add "fastapi[standard]" "sqlalchemy[asyncio]" asyncpg alembic
uv add --dev pytest pytest-asyncio pytest-cov ruff
```
</details>

<details>
<summary>Hint — pyproject.toml settings</summary>

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["."]
asyncio_mode = "auto"
asyncio_default_fixture_loop_scope = "function"
addopts = [
    "--cov=app",
    "--cov-report=term-missing",
    "--cov-report=xml",
]

[tool.ruff]
line-length = 88
extend-exclude = ["migrations"]

[tool.ruff.lint]
select = ["E", "F", "I"]
```
</details>

**Checkpoint:** from `backend/`, `uv run pytest` runs and reports
`no tests ran`. That's correct — there are no tests yet.

---

## Part D — The frontend skeleton

From the **repo root**:

- [ ] A Vite **React + TypeScript** app in `frontend/`
- [ ] Demo content removed: `frontend/src/App.css` and
      `frontend/src/assets/` deleted; 📄 `frontend/src/App.tsx` showing
      only an `<h1>` reading **Job tracker**
- [ ] 📄 `frontend/src/index.css` — a small readable baseline (reuse
      Tiro's)
- [ ] 📄 `frontend/.prettierrc` matching Vite's style (single quotes, no
      semicolons)
- [ ] Dev dependencies: Vitest, V8 coverage, jsdom, and the four Testing
      Library packages (`react`, `dom`, `user-event`, `jest-dom`)
- [ ] 📄 `frontend/vite.config.ts` with the Vitest reference line and a
      `test` block: jsdom, a setup file, and coverage reporting `text`
      and `lcov` for `src/**/*.{ts,tsx}` (excluding `main.tsx`, the
      setup file, and test files)
- [ ] 📄 `frontend/src/setupTests.ts` loading jest-dom's Vitest matchers
      and running `cleanup()` after each test
- [ ] 📄 `frontend/package.json` scripts: `test`, `test:run`,
      `coverage`, and `typecheck`
- [ ] 📄 `frontend/eslint.config.js` — `coverage` added to the ignored
      folders

<details>
<summary>Hint — where to look</summary>

Tiro lesson 07, Steps 1–4, and Tiro lesson 09, Steps 1–2.
</details>

<details>
<summary>Hint — install commands</summary>

```bash
npm create vite@latest frontend -- --template react-ts
cd frontend
npm install
npm install -D vitest @vitest/coverage-v8 jsdom
npm install -D @testing-library/react @testing-library/dom
npm install -D @testing-library/user-event @testing-library/jest-dom
```
</details>

<details>
<summary>Hint — the four scripts</summary>

```json
"test": "vitest",
"test:run": "vitest run",
"coverage": "vitest run --coverage",
"typecheck": "tsc -b"
```
</details>

**Checkpoint:** `npm run dev` shows **Job tracker**; `npm run lint` and
`npm run typecheck` pass.

---

## Part E — The hook starts the database

📄 **File:** `.husky/pre-commit` (repo root) — **edit**: replace the
placeholder with the first real stage. From lesson 02 on, every backend
test needs PostgreSQL running.

- [ ] The hook starts the database and **waits until it's healthy**

<details>
<summary>Hint</summary>

```sh
echo "Starting the database..."
docker compose up -d --wait
```

Tiro lesson 05, Step 8. You'll add test and lint stages as each suite
appears; the full hook is in lesson 07.
</details>

---

## Commit

```bash
git add .
git commit -m "chore: scaffold database, backend, and frontend"
git push
```

---

## Debrief

Before moving on, answer honestly: **which items did you need a hint
for?** Write them down. Those are your weakest links, and they're
exactly what to review before GRADUS III.

Next: [02 — Backend core](02-backend-core.md)
