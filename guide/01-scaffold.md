# 01 — Scaffold from memory

**Goal:** the same skeleton you built across Tiro lessons 02, 03, and
06 — but from memory, with a checklist instead of step-by-step
instructions. No app code yet.

This is **retrieval practice**. Try each item before opening its hint.
Struggling to remember is the part that makes it stick.

---

## Part A — The repo

Work at the **repo root**.

- [ ] `.gitignore` covering Python caches, `.venv`, coverage reports,
      `*.db`, `node_modules`, `dist`, `.env`, and OS clutter
- [ ] `.gitattributes` forcing `LF` line endings
- [ ] Root `package.json` with Husky installed as a dev dependency
- [ ] Husky initialized, with `.husky/pre-commit` that only prints
      `Husky pre-commit hook ran.` (real checks come once tests exist)
- [ ] `.vscode/settings.json` — pytest settings, Coverage Gutters
      settings, format-on-save with Ruff and Prettier

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

## Part B — The backend skeleton

- [ ] A uv project in `backend/` using Python 3.12, with no README, no
      nested Git repo, and the sample `main.py` deleted
- [ ] Runtime dependencies: FastAPI (with the `standard` extra),
      SQLAlchemy, Alembic
- [ ] Dev dependencies: pytest, pytest-cov, Ruff
- [ ] `pyproject.toml` configured so that:
  - pytest looks in `tests/`, can import `app`, and always reports
    coverage for `app` to the terminal (with missing lines) **and** to
    `coverage.xml`
  - Ruff uses line length 88, checks `E`, `F`, and `I`, and skips the
    `migrations` folder
- [ ] An `app/` package (it needs one special empty file)
- [ ] VS Code's Python interpreter set to `backend/.venv`

<details>
<summary>Hint — uv commands</summary>

```bash
uv init backend --no-readme --vcs none --python 3.12
cd backend
uv add "fastapi[standard]" sqlalchemy alembic
uv add --dev pytest pytest-cov ruff
```
</details>

<details>
<summary>Hint — pyproject.toml settings</summary>

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["."]
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

## Part C — The frontend skeleton

From the **repo root**:

- [ ] A Vite **React + TypeScript** app in `frontend/`
- [ ] Demo content removed: `App.css` and `assets/` deleted, `App.tsx`
      showing only an `<h1>` reading **Job tracker**
- [ ] A small readable `index.css` (reuse Tiro's)
- [ ] `.prettierrc` matching Vite's style (single quotes, no semicolons)
- [ ] Dev dependencies: Vitest, V8 coverage, jsdom, and the four Testing
      Library packages (`react`, `dom`, `user-event`, `jest-dom`)
- [ ] `vite.config.ts` with the Vitest reference line and a `test`
      block: jsdom, a setup file, and coverage reporting `text` and
      `lcov` for `src/**/*.{ts,tsx}` (excluding `main.tsx`, the setup
      file, and test files)
- [ ] `src/setupTests.ts` loading jest-dom's Vitest matchers and running
      `cleanup()` after each test
- [ ] Scripts: `test`, `test:run`, `coverage`, and `typecheck`
- [ ] `coverage` added to ESLint's ignored folders

<details>
<summary>Hint — where to look</summary>

Tiro lesson 06, Steps 1–4, and Tiro lesson 08, Steps 1–2.
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

## Commit

```bash
git add .
git commit -m "chore: scaffold backend and frontend"
git push
```

---

## Debrief

Before moving on, answer honestly: **which items did you need a hint
for?** Write them down. Those are your weakest links, and they're
exactly what to review before GRADUS III.

Next: [02 — Backend core](02-backend-core.md)
