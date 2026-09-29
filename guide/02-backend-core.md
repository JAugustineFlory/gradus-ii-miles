# 02 — Backend core (Phase 1)

**Goal:** Tiro's API rebuilt with four upgrades — configuration from
the environment, routes in a router, validated input, and filtering.
**27 tests** green.

Work in `backend/` unless told otherwise. Create the `tests/` folder
first:

```bash
mkdir tests
```

You'll copy the phase 1 test files in **one step at a time** (not all at
once), because `conftest.py` imports your app — until the app exists,
it would break every test, including ones that don't need it.

The copy commands below run from `backend/`, so paths start with
`../starter-tests/`.

---

## Step 1 — Configuration

### Contract

`app/config.py` exposes two functions:

| Function | Returns | Default |
| --- | --- | --- |
| `get_database_url()` | the `DATABASE_URL` environment variable | `"sqlite:///./miles.db"` |
| `get_frontend_origin()` | the `FRONTEND_ORIGIN` environment variable | `"http://localhost:5173"` |

### 🔴 Red

```bash
cp ../starter-tests/backend/phase-1/tests/test_config.py tests/
uv run pytest
```

🔴 `ModuleNotFoundError: No module named 'app.config'` (or `app` —
create `app/__init__.py` if you haven't).

### New concepts

**Environment variable** — a named value set *outside* your code, by the
terminal or the server that runs it. The same code can then use a local
SQLite file on your laptop and a PostgreSQL server in production,
without changing a line. This is the "config" factor of the widely used
[Twelve-Factor App](https://12factor.net/config) guidelines.

**`os.getenv(name, default)`** — reads an environment variable, or
returns `default` if it isn't set.

**Why functions instead of constants?** A constant is read once, when
the module is first imported. A function reads the environment every
time it's called — which is what lets the tests change it.

**`monkeypatch`** — a built-in pytest fixture that changes something for
one test and automatically undoes it afterward. Read the test file:
`monkeypatch.setenv(...)` and `monkeypatch.delenv(...)` set and remove
environment variables for just that test.

### Connect the dots

The tests set or remove an environment variable, then call your
function. *Which single standard-library function does all the work?*

### Pseudocode

```text
function get_database_url():
    return env var "DATABASE_URL", or "sqlite:///./miles.db" if unset

function get_frontend_origin():
    return env var "FRONTEND_ORIGIN", or "http://localhost:5173" if unset
```

<details>
<summary>Hint 1</summary>

`import os` at the top. Each function body is a single `return`.
</details>

<details>
<summary>Hint 2</summary>

```python
def get_database_url() -> str:
    return os.getenv("DATABASE_URL", "sqlite:///./miles.db")
```
</details>

🟢 `4 passed`. Commit: `feat(backend): read config from environment`.

Docs: <https://docs.pytest.org/en/stable/how-to/monkeypatch.html>

---

## Step 2 — Database setup with a naming convention

### Contract

`app/database.py` exposes:

| Name | What |
| --- | --- |
| `engine` | created from `get_database_url()` |
| `SessionLocal` | a session factory bound to `engine`, `autoflush=False` |
| `Base` | the declarative base, whose metadata has a **naming convention** that includes at least `fk`, `uq`, and `pk` |
| `get_db()` | yields a session and always closes it |

### 🔴 Red

```bash
cp ../starter-tests/backend/phase-1/tests/test_database.py tests/
uv run pytest
```

### New concept: constraint naming conventions

A **constraint** is a rule the database enforces: a **primary key**
(`pk`), a **unique** rule (`uq`), a **foreign key** (`fk`, arriving in
lesson 03). Every constraint has a name. If you don't give one, each
database invents its own — or, in SQLite, leaves it blank.

That becomes a problem the first time you need to *change* a
constraint: Alembic has to refer to it by name, and "blank" isn't a
name. A **naming convention** tells SQLAlchemy how to name every
constraint automatically, so names are predictable everywhere.

Set it on `Base` **now**, before your first migration. Adding it later
means your existing tables have unnamed constraints that no longer match.

### Connect the dots

`Base` already has a `metadata` attribute (Tiro used it for
`create_all`). You'll replace it with a `MetaData` object you build
yourself, passing a `naming_convention` dictionary.

### Pseudocode

```text
NAMING_CONVENTION = {
    "ix": pattern for indexes,
    "uq": pattern for unique constraints,
    "ck": pattern for check constraints,
    "fk": pattern for foreign keys,
    "pk": pattern for primary keys,
}

class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING_CONVENTION)

engine = create_engine(get_database_url(), SQLite thread setting)
```

The patterns are a standard recipe — copy them from the SQLAlchemy docs
linked below, or from Hint 2.

<details>
<summary>Hint 1</summary>

`MetaData` is imported from `sqlalchemy`. Assigning `metadata = ...` as
a class attribute inside `Base` replaces the default.
</details>

<details>
<summary>Hint 2 — the standard convention</summary>

```python
NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}
```
</details>

<details>
<summary>Hint 3 — the SQLite thread setting</summary>

It's the same `connect_args` as Tiro's `database.py`. It only applies to
SQLite, which matters in GRADUS III — for now, one line is fine.
</details>

🟢 `6 passed`. Commit: `feat(backend): database setup with naming
convention`.

Docs:
<https://docs.sqlalchemy.org/en/20/core/constraints.html#configuring-constraint-naming-conventions>

---

## Step 3 — Model, app, health, and CORS

Everything here is a Tiro repeat, except that the CORS origin now comes
from config.

### Contract

- `app/models.py` — `Application` model, table `applications`: `id`,
  `company` (string, 100), `role` (string, 100), `status` (string, 20,
  default `"applied"`), `applied_on` (date). Same as Tiro.
- `app/main.py` — `app` with CORS middleware allowing
  **`get_frontend_origin()`**, and `GET /health` returning
  `{"status": "ok"}`.

### 🔴 Red

```bash
cp ../starter-tests/backend/phase-1/tests/conftest.py tests/
cp ../starter-tests/backend/phase-1/tests/test_models.py tests/
cp ../starter-tests/backend/phase-1/tests/test_health.py tests/
cp ../starter-tests/backend/phase-1/tests/test_cors.py tests/
uv run pytest
```

Checklist:

- [ ] `models.py` (Tiro lesson 04, Step 4)
- [ ] `main.py` with health (Tiro lesson 03, Step 7)
- [ ] CORS middleware using `get_frontend_origin()` (Tiro lesson 07,
      Step 6)

🟢 `10 passed`. Commit: `feat(backend): model, health, and CORS`.

---

## Step 4 — Validated schemas and an applications router

### Contract

`app/schemas.py`:

| Name | What |
| --- | --- |
| `Status` | a type allowing only `"applied"`, `"interviewing"`, `"offer"`, `"rejected"` |
| `CleanStr` | a string type that strips surrounding whitespace, then requires 1–100 characters |
| `ApplicationCreate` | `company: CleanStr`, `role: CleanStr`, `status: Status = "applied"`, `applied_on: date` |
| `ApplicationUpdate` | the same fields, all optional (`None` by default) |
| `ApplicationRead` | `id` plus every field, readable from a model (`from_attributes`) |

`app/routers/applications.py` (plus an empty `app/routers/__init__.py`):

- a `router` with prefix `/applications`
- the five endpoints from Tiro, plus `GET /applications` accepting an
  optional **`status`** query parameter (typed `Status`) that filters the
  list
- a `404` detail of exactly `"Application not found"`

`app/main.py` includes the router.

### 🔴 Red

```bash
cp ../starter-tests/backend/phase-1/tests/test_applications.py tests/
uv run pytest
```

🔴 17 failures. Work through them top to bottom, group by group: create,
list, get, update, delete.

### New concept: `Literal`

```python
from typing import Literal

Status = Literal["applied", "interviewing", "offer", "rejected"]
```

A `Literal` type allows *only* the listed values. Pydantic rejects
anything else with `422` — you write no `if` statements. Use `Status`
anywhere a status appears: request bodies **and** query parameters.

### New concept: constrained strings

```python
from typing import Annotated
from pydantic import StringConstraints

CleanStr = Annotated[
    str,
    StringConstraints(...),   # your rules go here
]
```

**`Annotated[type, extra]`** attaches extra information to a type.
Pydantic reads `StringConstraints` from it and applies the rules. Look
up the parameters that strip whitespace and set minimum and maximum
length. Stripping happens *before* the length check, which is why
`"   "` becomes `""` and fails `min_length=1`.

Docs: <https://docs.pydantic.dev/latest/api/types/#pydantic.types.StringConstraints>

### New concept: `APIRouter`

As an API grows, one `main.py` becomes unreadable. An **`APIRouter`**
is a mini-app holding related routes. `main.py` then just plugs routers
in:

```text
routers/applications.py:
    router = APIRouter with prefix "/applications" and tag "applications"

    @router.get("")               ← becomes GET /applications
    @router.get("/{application_id}")  ← becomes GET /applications/{id}

main.py:
    app.include_router(applications.router)
```

> ⚠️ Use `""`, **not** `"/"`, for the collection routes. With a prefix,
> `"/"` makes the path `/applications/` (trailing slash), and requests
> to `/applications` get redirected — which breaks `POST` in confusing
> ways.

The **tag** groups the routes under a heading in `/docs`.

Docs: <https://fastapi.tiangolo.com/tutorial/bigger-applications/>

### New concept: query parameters

A function parameter that isn't in the path and isn't a schema becomes a
**query parameter** — read from `?name=value` in the URL:

```text
function list_applications(status: Status or None = None, db):
    query = select applications, ordered by id
    if status is not None:
        query = query filtered to rows where Application.status == status
    return every row from query
```

Because `status` is typed `Status`, `?status=ghosted` is rejected with
`422` automatically.

Docs:
- Query parameters: <https://fastapi.tiangolo.com/tutorial/query-params/>
- Filtering with `where`:
  <https://docs.sqlalchemy.org/en/20/tutorial/data_select.html#the-where-clause>

<details>
<summary>Hint 1 — create group fails with 404</summary>

Did you `include_router` in `main.py`? Check `/docs` in the browser to
see which paths actually exist.
</details>

<details>
<summary>Hint 2 — the whitespace test fails</summary>

`StringConstraints(strip_whitespace=True, min_length=1, max_length=100)`
</details>

<details>
<summary>Hint 3 — the filter</summary>

`query = query.where(models.Application.status == status)` — calling
`.where` returns a *new* query, so reassign it.
</details>

<details>
<summary>Hint 4 — importing the router</summary>

In `main.py`: `from app.routers import applications`, then
`app.include_router(applications.router)`.
</details>

🟢 `27 passed`. Commit after each group turns green (e.g. `feat(backend):
validated create`, `feat(backend): filter by status`, …).

---

## Step 5 — Alembic from config

### Contract

- `alembic.ini` no longer holds the database URL; `migrations/env.py`
  reads it from **`get_database_url()`**.
- `env.py` enables **batch mode** (`render_as_batch=True`).
- One migration creating `applications`.

### New concept: batch mode

SQLite can't change or drop most things in an existing table. To do it,
Alembic's **batch mode** copies the table: create a new one with the
change, copy every row over, drop the old one, rename the new one.
Turning it on now means every future migration is written in a form that
works on SQLite. PostgreSQL (GRADUS III) runs batch migrations fine too.

### Connect the dots

In `env.py`:

- `config = context.config` is Alembic's settings object, filled from
  `alembic.ini`. It has a `set_main_option(name, value)` method.
- There are **two** places that call `context.configure(...)` — one for
  offline mode, one for online mode. Both need batch mode.

### Pseudocode

```text
in migrations/env.py, after "config = context.config":
    import models (to register tables), Base, and get_database_url
    set config's "sqlalchemy.url" option to get_database_url()
    target_metadata = Base.metadata

in BOTH context.configure(...) calls:
    add render_as_batch=True
```

Then autogenerate, **read** the migration, and upgrade (Tiro lesson 04,
Step 6).

<details>
<summary>Hint</summary>

```python
config.set_main_option("sqlalchemy.url", get_database_url())
```

In `alembic.ini`, you can delete the `sqlalchemy.url = ...` line or
leave it; `env.py` overrides it either way.
</details>

**Checkpoint:**

- `uv run alembic upgrade head` creates `miles.db`
- `uv run fastapi dev app/main.py` → `/docs` shows the routes grouped
  under **applications**
- Try `POST` with `"status": "ghosted"` in `/docs` → `422`

Docs:
<https://alembic.sqlalchemy.org/en/latest/batch.html>

Commit: `feat(backend): alembic reads config, batch mode, first
migration`.

---

## Step 6 — Guard the backend

Replace `.husky/pre-commit` at the repo root:

```sh
echo "Backend: lint"
(cd backend && uv run ruff check . && uv run ruff format --check .)

echo "Backend: tests"
(cd backend && uv run pytest -q)
```

Commit and push.

---

## Explain it back

**1. Why does the app read config through functions instead of module
constants?**

<details>
<summary>Answer</summary>

A constant is read once at import time, so tests couldn't change it.
A function reads the environment each call, so `monkeypatch` works —
and a deployment can change the value without code changes.
</details>

**2. You wrote no `if` statement to reject `"ghosted"`. What rejected
it?**

<details>
<summary>Answer</summary>

Pydantic, because the field is typed `Literal[...]`. FastAPI validates
the request against the type and returns `422` before your function
runs.
</details>

**3. Why set the naming convention before the first migration?**

<details>
<summary>Answer</summary>

Constraints get their names when tables are created. If the convention
is added later, existing constraints keep their old (or missing) names,
and future migrations that need to refer to them by name break.
</details>

**4. What's the difference between `@router.get("")` and
`@router.get("/")` under the prefix `/applications`?**

<details>
<summary>Answer</summary>

`""` gives `/applications`; `"/"` gives `/applications/`. Requests to
the other form are redirected, which can drop or mangle request bodies.
</details>

Next: [03 — Companies and relationships](03-companies.md)
