# 03 — Companies and relationships (Phase 2)

**Goal:** companies become their own table. Each application belongs to
one company, the API returns the company nested inside each application,
and a second migration changes the existing `applications` table.
**35 tests** green.

Work in `backend/`.

---

## The concepts first

### Foreign keys

A **foreign key** is a column that holds another table's primary key.
`applications.company_id = 3` means "this application belongs to the
company whose `id` is 3." The database can **enforce** it: no
`company_id` pointing at a company that doesn't exist.

Why not just keep the company's name as text? Because then "Acme",
"ACME", and "Acme Corp" are three different companies, renaming a
company means editing every application, and there's no list of
companies to choose from. Storing each fact **once** and referring to it
by id is called **normalization**.

### Relationships

A foreign key is a plain integer. A SQLAlchemy **`relationship`** adds a
convenient Python attribute on top of it:

```text
application.company_id   → 3                    (the column)
application.company      → <Company id=3 Acme>  (the relationship)
company.applications     → [<Application>, …]   (the other direction)
```

**`back_populates`** links the two directions, so setting
`application.company = acme` also adds the application to
`acme.applications`.

By default, `application.company` isn't loaded until you touch it — then
SQLAlchemy quietly runs a second query. That's called **lazy loading**.
It's simple and fine at this size; GRADUS III looks at when it becomes a
problem.

Docs:
<https://docs.sqlalchemy.org/en/20/orm/basic_relationships.html#one-to-many>

### Nested response schemas

A Pydantic schema can have a field whose type is *another schema*.
Because `ApplicationRead` has `from_attributes=True`, Pydantic reads
`application.company` (the relationship) and builds a `CompanyRead` from
it automatically.

---

## Step 1 — Copy the phase 2 tests

```bash
cp ../starter-tests/backend/phase-2/tests/*.py tests/
uv run pytest
```

This **overwrites** `test_models.py` and `test_applications.py`, and adds
`test_companies.py`. The other files are unchanged.

🔴 Import errors — `Company` doesn't exist yet.

> **Requirements changed, so the tests changed.** In real projects,
> replacing a test because the *specification* changed is normal. What's
> never OK is weakening a test to hide a bug.

---

## Step 2 — Models

### Contract

- **`Company`** — table `companies`: `id` (primary key), `name`
  (string, 100, **unique**), `applications` (relationship to
  `Application`).
- **`Application`** — remove the `company` string column. Add
  `company_id` (foreign key to `companies.id`, required) and `company`
  (relationship to `Company`). Both relationships use `back_populates`.

### Pseudocode

```text
class Company(Base):
    table name "companies"
    id: int, primary key
    name: str, String(100), unique
    applications: list of Application — relationship, back-populates "company"

class Application(Base):
    ... (id, role, status, applied_on as before, no more "company" string)
    company_id: int — ForeignKey to "companies.id"
    company: Company — relationship, back-populates "applications"
```

`Company` refers to `Application` before `Application` is defined. With
typed relationships, write the type as a string —
`Mapped[list["Application"]]` — and Python won't complain.

<details>
<summary>Hint 1 — imports</summary>

`ForeignKey` from `sqlalchemy`; `relationship` from `sqlalchemy.orm`.
</details>

<details>
<summary>Hint 2 — the relationship lines</summary>

```python
applications: Mapped[list["Application"]] = relationship(
    back_populates="company",
)
```

and on `Application`:

```python
company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"))
company: Mapped[Company] = relationship(back_populates="applications")
```
</details>

🟢 `test_models.py` passes (3 tests). Everything using the API still
fails. Commit: `feat(backend): company model and relationship`.

---

## Step 3 — Make SQLite enforce foreign keys

Surprise: **SQLite ignores foreign keys by default**, for
backward-compatibility reasons. Without the next step, it would happily
store `company_id = 999`.

### New concept: connection events

SQLAlchemy can run your code every time it opens a database connection.
You'll use that to send SQLite the command `PRAGMA foreign_keys=ON`.

### Contract

In `app/database.py`, a function registered with
`@event.listens_for(Engine, "connect")` that turns on foreign keys —
**only when the connection is SQLite**.

### Pseudocode

```text
when any engine opens a new connection (dbapi_connection, record):
    if the connection is a sqlite3 connection:
        open a cursor
        execute "PRAGMA foreign_keys=ON"
        close the cursor
```

Why the SQLite check? In GRADUS III you switch to PostgreSQL, which
enforces foreign keys already — and doesn't understand `PRAGMA`.

<details>
<summary>Hint</summary>

Imports: `import sqlite3`, `from sqlalchemy import event`,
`from sqlalchemy.engine import Engine`. The check is
`isinstance(dbapi_connection, sqlite3.Connection)`.
</details>

### Your first self-written test (optional, recommended)

No provided test checks this — so write one. In `tests/test_models.py`,
add a test that:

1. adds an `Application` with `company_id=999` (no such company) to the
   `session` and commits;
2. expects an **`IntegrityError`** (from `sqlalchemy.exc`).

Remove the event listener and the test should fail; put it back and it
passes. That's how you know your test tests something.

<details>
<summary>Hint</summary>

`with pytest.raises(IntegrityError):` wraps code that must raise.
Docs: <https://docs.pytest.org/en/stable/how-to/assert.html#assertions-about-expected-exceptions>
</details>

Docs: <https://docs.sqlalchemy.org/en/20/dialects/sqlite.html#foreign-key-support>

---

## Step 4 — The companies router

### Contract

Schemas in `app/schemas.py`:

| Schema | Fields |
| --- | --- |
| `CompanyCreate` | `name: CleanStr` |
| `CompanyRead` | `id`, `name`; `from_attributes` |

`app/routers/companies.py` with prefix `/companies`, included in
`main.py`:

| Endpoint | Behavior |
| --- | --- |
| `POST /companies` | `201` with `{id, name}`; `409` with detail exactly `"Company already exists"` if the name is taken |
| `GET /companies` | every company, **sorted by name** |

### New concept: `409 Conflict`

`409` means "your request is valid, but it conflicts with what's already
there." A duplicate name is the classic case.

### Connect the dots

Two layers can catch a duplicate:

- **Your code** — look for an existing company with that name before
  inserting.
- **The database** — the `unique` constraint rejects the insert with an
  `IntegrityError`.

Checking first gives a clear `409`. The unique constraint is the
backstop if two requests race each other. Either can produce the `409`;
*which* is up to you.

### Pseudocode (check-first version)

```text
function create_company(payload, db):
    existing = first company where name == payload.name, or None
    if existing:
        raise 409 "Company already exists"
    add, commit, refresh, return the new company
```

<details>
<summary>Hint 1 — find one or none</summary>

`db.scalars(select(models.Company).where(...)).first()` returns the
first match or `None`.
</details>

<details>
<summary>Hint 2 — sorted list</summary>

`.order_by(models.Company.name)`
</details>

🟢 `test_companies.py` passes (6 tests). Commit: `feat(backend):
companies endpoints`.

---

## Step 5 — Applications belong to companies

### Contract

Schema changes:

| Schema | Change |
| --- | --- |
| `ApplicationCreate` | `company: CleanStr` becomes `company_id: int` |
| `ApplicationUpdate` | `company` becomes `company_id: int \| None = None` |
| `ApplicationRead` | `company` becomes `company: CompanyRead`. **No `company_id` field** — the tests compare the whole object |

Router changes:

- **Create** and **update** return `422` with detail exactly
  `"Company not found"` when a given `company_id` doesn't exist.
- **List** accepts an optional `company_id` query parameter, and both
  filters can be combined.

### Connect the dots

- You already have a helper that finds an application or raises `404`.
  You need its twin for companies — but raising **`422`**, because the
  *request* refers to something invalid, rather than the URL pointing
  at nothing.
- In **update**, only check the company if the client actually sent a
  `company_id`. Where did you learn which fields were sent? (Tiro lesson
  05, Cycle 5.)
- Filters stack: each `.where(...)` narrows the query further.

### Pseudocode

```text
function require_company(db, company_id):
    company = get Company by id
    if none: raise 422 "Company not found"
    return company

create:
    require_company(db, payload.company_id)
    ... create as before

update:
    changes = fields actually sent
    if "company_id" in changes:
        require_company(db, changes["company_id"])
    ... apply changes as before

list(status = None, company_id = None):
    query = applications ordered by id
    if status given: narrow by status
    if company_id given: narrow by company_id
    return rows
```

<details>
<summary>Hint 1 — the response shape is wrong</summary>

Compare the test's expected dictionary with what you return. Is
`company_id` still in `ApplicationRead`? Is `company` typed
`CompanyRead`?
</details>

<details>
<summary>Hint 2 — `company` in the response is missing or an error</summary>

`ApplicationRead` needs `from_attributes`, **and** so does `CompanyRead`
— Pydantic reads the nested object the same way.
</details>

🟢 **`35 passed`**, 100% coverage. Commit: `feat(backend): applications
belong to companies`.

---

## Step 6 — The second migration

### ⚠️ Reset your development database first

This migration adds a **required** `company_id` column to
`applications`. Any rows already in your `miles.db` have no value for
it, so the migration would fail on them. Converting old free-text
company names into company rows is a **data migration** — a GRADUS III
skill. For now, start clean:

```bash
uv run alembic downgrade base
```

`base` means "before the first migration": every table is dropped.

### Generate, read, apply

```bash
uv run alembic revision --autogenerate -m "add companies"
```

Open the new file and **read it**. You should find:

- `op.create_table('companies', ...)` including a unique constraint
  named `uq_companies_name` — your naming convention at work
- a `with op.batch_alter_table('applications') as batch_op:` block that:
  - adds `company_id`
  - creates a foreign key named `fk_applications_company_id_companies`
  - drops the old `company` column
- a `downgrade()` that undoes all of it in reverse order

If the foreign key's name is `None`, your naming convention isn't being
used — check `Base` in `database.py`.

```bash
uv run alembic upgrade head
uv run alembic downgrade -1
uv run alembic upgrade head
```

✅ All three succeed. Testing the downgrade *now*, while it's fresh, is
cheaper than discovering it's broken when you need it.

### Try it

`uv run fastapi dev app/main.py`, then in `/docs`:

1. Create a company.
2. Create an application with its `company_id` — the response nests the
   company.
3. Create an application with `company_id: 999` → `422 Company not found`.
4. Create the same company twice → `409`.

Commit: `feat(backend): migration adding companies`.

---

## Explain it back

**1. Why is "Company not found" a `422` here, when "Application not
found" is a `404`?**

<details>
<summary>Answer</summary>

`404` means the URL points at nothing: `/applications/999`. With
`company_id: 999` in the body, the URL is fine — the *request content*
refers to something that doesn't exist, so the request can't be
processed: `422`.
</details>

**2. Why does the migration use `batch_alter_table`?**

<details>
<summary>Answer</summary>

SQLite can't add a foreign key to, or drop a column from, an existing
table in place. Batch mode rebuilds the table with the changes and
copies the rows across.
</details>

**3. What would happen without `PRAGMA foreign_keys=ON`?**

<details>
<summary>Answer</summary>

SQLite would accept `company_id` values that point at no company. The
API's own check would still catch it, but anything writing to the
database another way (a script, a future bug) could store broken data.
</details>

**4. What is lazy loading?**

<details>
<summary>Answer</summary>

Related objects (like `application.company`) aren't fetched until the
code first uses them; then SQLAlchemy runs an extra query on the spot.
</details>

Next: [04 — Frontend foundations](04-frontend-foundations.md)
