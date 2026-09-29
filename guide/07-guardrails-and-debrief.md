# 07 — Guardrails and debrief

**Goal:** every check running before each commit, proof that a
classmate can clone and run your repo, and an honest debrief.

This lesson is short on purpose: it's all things you did in Tiro lesson
08. Use the checklist; open Tiro's lesson only if you're stuck.

---

## Checklist

### Checks

- [ ] `.husky/pre-commit` runs, in order: backend lint, frontend lint
      and types, backend tests, frontend tests
- [ ] Root `package.json` has a `check` script that runs the hook by
      hand
- [ ] `npm run check` passes from the repo root

### Fresh clone

In a folder **outside** your repo:

- [ ] Clone your repo and run `npm install` at the root
- [ ] Backend: `uv sync`, `uv run alembic upgrade head`,
      `uv run pytest -q` → **35 passed**
- [ ] Frontend: `npm install`, copy `.env.example` to `.env`,
      `npm run test:run` → **38 passed**
- [ ] Both dev servers start and the app works

If something fails only in the fresh clone, a file is missing from Git
(or hidden by `.gitignore`). Fix it in your real repo and push.

<details>
<summary>Hint — a fresh-clone migration fails</summary>

Check both migration files are committed in `backend/migrations/versions/`.
Alembic runs them in order, from an empty database, so each one must
work on its own.
</details>

### README

- [ ] A **Running the finished app** section (like Tiro's), now also
      mentioning the `.env.example` step

### Coverage

```bash
cd backend && uv run pytest -q && cd ..
cd frontend && npm run coverage && cd ..
```

- [ ] Backend at 100%
- [ ] Frontend at or near 100%. If a line is red, you can explain why —
      or you write the test that covers it.

Compare with Tiro, where `App.tsx` and `api.ts` sat at 0%. Mocking is
what closed that gap.

Commit and push: `chore: full checks and run instructions`.

---

## After Action Review

Same four questions as Tiro. Write the answers down.

1. **What was supposed to happen?**
2. **What actually happened?**
3. **Why was there a difference?**
4. **What will you sustain, and what will you improve?**

One more, specific to Miles:

5. **Compare lesson 01's debrief list** (the scaffold items you needed
   hints for) with how the rest of Miles went. Did the same weak spots
   show up again? Those are what to review before Veteranus.

---

## Self-check before GRADUS III

Without looking:

- [ ] Explain why config comes from environment variables, and test it
      with `monkeypatch`
- [ ] Split routes into an `APIRouter` and include it
- [ ] Restrict a field to fixed values in Python (`Literal`) and
      TypeScript (`as const` + indexed type)
- [ ] Strip and length-check strings with `StringConstraints`
- [ ] Add a one-to-many relationship with `ForeignKey` and
      `relationship`
- [ ] Explain why constraint naming conventions matter to migrations
- [ ] Explain batch mode and when SQLite needs it
- [ ] Choose between `404`, `409`, and `422` for a given failure
- [ ] Write a generic `request<T>()` helper
- [ ] Mock `fetch` with `vi.spyOn`, and a module with `vi.mock`
- [ ] Choose between `getBy`, `findBy`, and `waitFor`
- [ ] Use functional state updates and `try`/`catch` around `await`

---

## What's next

**GRADUS III — Veteranus.** You'll rebuild once more — this time from
**requirements only**. No provided tests: you write them first. New
layers:

- **PostgreSQL in Docker**, and what changes when you leave SQLite
- A **status-history** table and a **data migration** that moves
  existing data safely
- **Pagination** for long lists
- **Custom React hooks** to pull data logic out of `App`
- **Continuous integration** with GitHub Actions, so every push runs
  your checks in the cloud

*Miles* no longer. On to *veteranus*.
