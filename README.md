# GRADUS II — Miles

> **🚧 Beta.** This guide and its provided tests have not yet been fully
> tested end to end by students. Tool versions change, and a command,
> output, or test may not behave exactly as described. Check
> [`guide/troubleshooting.md`](guide/troubleshooting.md) first, then
> [report it](#found-a-problem).

**GRADUS**: **G**uided **R**epetitions in **A**pplied **D**evelopment
**U**sing the **S**tack

*Miles* (Latin): a soldier. The second of three tiers.

| Tier | Latin | Guidance level |
| --- | --- | --- |
| I | *tiro* | Full worked examples. Every line explained. |
| **II** | ***miles*** | **Tests given to you. You write the code.** |
| III | *veteranus* | Requirements only. You write tests and code. |

---

## What you'll build

The same **job application tracker** from GRADUS I, rebuilt from an
empty folder on the same stack, then taken further.

### User stories

Tiro delivered **US-1** to **US-5** (record, see all, update, delete,
persist). Miles keeps all five and adds:

| ID | Story |
| --- | --- |
| **US-6** | As a job seeker, I want to **pick a company from a list** instead of retyping it, so that "Acme" and "ACME" don't become two companies. |
| **US-7** | As a job seeker, I want to **filter** my applications by status, so that I can focus on what needs action. |
| **US-8** | As a job seeker, I want a **clear message when something fails**, so that I know my change wasn't saved. |
| **US-9** | As a job seeker, I want the tracker to **refuse nonsense input** (blank names, made-up statuses), so that my data stays trustworthy. |

What that means in practice:

- **Companies** become their own table. An application belongs to one
  company; a company has many applications. (US-6)
- **Status** is limited to four values, checked on both ends. (US-9)
- **Blank and padded input** is cleaned or rejected. (US-9)
- The list can be **filtered** by status (and, in the API, by company).
  (US-7)
- **Every user action** shows a clear error if it fails. (US-8)
- **Every file** is covered by tests, including the ones that talk to
  the network.

## Prerequisite

Finish **GRADUS I — Tiro** first. Miles assumes you've done everything in
it once. When a step repeats something from Tiro, the guide gives you a
checklist and points back to the Tiro lesson rather than repeating the
explanation.

**No AI assistant required.** The provided tests tell you whether your
code is right. Each lesson gives you a **contract** (names, shapes,
labels the tests expect), pseudocode for every new concept, hints you can
reveal one at a time, and links to the official docs.

---

## The stack

The same as Tiro.

| Backend | Frontend | Workflow |
| --- | --- | --- |
| Python, uv | TypeScript | Git, GitHub |
| FastAPI, Pydantic | React, Vite | Husky |
| SQLAlchemy (async), asyncpg | Vitest, React Testing Library | Ruff, ESLint, Prettier |
| Alembic | | VS Code |
| PostgreSQL in Docker (port **5434**) | | |
| pytest, pytest-asyncio, pytest-cov | | |

Miles's database runs on host port **5434** (Tiro used 5433), so both
projects can run at the same time.

---

## How Miles is different from Tiro

In Tiro, you read a worked example, then typed it. In Miles:

1. You **copy in a provided test file** and run it. It fails.
2. You read the **contract** and the **pseudocode** for the new idea.
3. You **write the real code yourself**, in the file the contract names.
4. If you're stuck, open the **hints** in order. Each gives a little
   more. The last one is close to the answer — try hard before opening
   it.
5. The tests turn green. You commit.

New concepts still get a plain-English explanation the first time they
appear. Concepts you already practiced in Tiro get a checklist only.

---

## Skills

### Reinforced from Tiro (practice without the worked examples)

- uv project setup, dependencies, and `uv run`
- Docker Compose, PostgreSQL, a test database, and `psql`
- `async` / `await`, async SQLAlchemy sessions, asyncpg
- FastAPI routes, status codes, and `HTTPException`
- Async pytest fixtures and httpx's `AsyncClient`
- Alembic (async template) autogenerate and upgrade
- Pydantic schemas and `exclude_unset`
- Vite + React + TypeScript scaffolding, Vitest, React Testing Library
- Components, props, state, controlled inputs, callback props
- CORS middleware
- Husky pre-commit hooks, Ruff, ESLint, type-checking

### New in Miles

**Backend**

- **Configuration from environment variables** — one source of truth
  for the database URLs, used by the app, the tests, *and* Alembic
- **`monkeypatch`** — changing environment variables inside a test
- **`APIRouter`** — splitting routes into files by resource
- **`Literal` types** — restricting a field to fixed values
- **Constrained strings** — stripping whitespace and enforcing length
  with `StringConstraints`
- **Query parameters** — optional filters like `?status=offer`
- **One-to-many relationships** — `ForeignKey` and `relationship`
- **Loading related objects in async code** — why lazy loading fails
  (`MissingGreenlet`), and eager loading with `lazy="selectin"`,
  `selectinload`, and `refresh`
- **Nested response schemas** — returning a company inside an
  application
- **`409 Conflict`** — rejecting duplicates
- **Constraint naming conventions** — predictable names migrations can
  rely on
- **Changing an existing table** in a migration, and resetting a
  development database with `alembic downgrade base`

**Frontend**

- **Union types from constants** — `as const` and `(typeof X)[number]`
- **Generic functions** — one typed `request<T>()` helper instead of
  four copies
- **Environment variables in Vite** — `import.meta.env`
- **Mocking `fetch`** with `vi.spyOn` — testing the API module
- **Mocking a whole module** with `vi.mock` — testing `App`
- **Async queries** — `findBy…` and `waitFor`
- **Functional state updates** — `setItems((prev) => …)`
- **`Promise.all`** — loading two things at once
- **`try` / `catch` error handling** for every user action
- **Re-fetching when a filter changes** — effect dependencies

---

## Getting started

**Don't work directly in this repo.** On its GitHub page, click **Use
this template → Create a new repository**, then clone *your* copy. Your
work stays in your repo; the guide stays clean for everyone else.

Then start at [`guide/00-briefing.md`](guide/00-briefing.md).

| # | Lesson | Stories | You'll have at the end |
| --- | --- | --- | --- |
| 00 | [Briefing](guide/00-briefing.md) | all | The plan, the contracts, how to use hints |
| 01 | [Scaffold from memory](guide/01-scaffold.md) | US-5 | Repo, Husky, Docker database, backend and frontend skeletons |
| 02 | [Backend core](guide/02-backend-core.md) | US-1–5, 7, 9 | Phase 1: config, routers, validation, filtering — 29 tests |
| 03 | [Companies and relationships](guide/03-companies.md) | US-6 | Phase 2: a second table, async relationships, a migration — 37 tests |
| 04 | [Frontend foundations](guide/04-frontend-foundations.md) | US-8, 9 | Types, a generic `request`, mocked `fetch` |
| 05 | [Components](guide/05-components.md) | US-1–4, 6, 7 | Four tested components |
| 06 | [App and error handling](guide/06-app.md) | US-8 | A fully tested `App` — 38 frontend tests |
| 07 | [Guardrails and debrief](guide/07-guardrails-and-debrief.md) | all | Full checks, fresh-clone proof, AAR |

Also: [`guide/troubleshooting.md`](guide/troubleshooting.md) and
[`guide/glossary.md`](guide/glossary.md). Tiro's troubleshooting page
still applies to everything you set up the same way.

**Time:** plan on 10–16 hours.

---

## Why it's built this way

Tiro used **worked examples**. Miles uses **faded worked examples**:
the tests and the contract remain, but the solution steps are removed,
so you generate them yourself. Renkl and Atkinson showed that removing
steps gradually like this helps learners move from studying examples to
solving problems on their own.

Rebuilding the app from an empty folder is **retrieval practice** —
pulling what you learned out of memory, which strengthens it far more
than re-reading. Adding a new layer (companies, mocking) keeps the
rebuild from becoming recitation. Robert and Elizabeth Bjork call this
kind of productive struggle a **desirable difficulty**: it feels slower,
and it lasts longer.

---

## Found a problem?

On this repo's GitHub page, open **Issues → New issue** and include the
lesson and step, what you expected, what happened (with the full error
message), and your operating system.

---

## After Miles

**GRADUS III — Veteranus.** Requirements only: you write the tests
*and* the code. New layers include typed settings with pydantic-settings,
a test database built by your own migrations, a status-history table and
a data migration, pagination, custom React hooks, and continuous
integration with GitHub Actions.
