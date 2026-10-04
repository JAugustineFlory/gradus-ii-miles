# 03 — Companies and relationships (Phase 2)

> **Where this fits.** **US-6**: *"As a job seeker, I want to pick a
> company from a list instead of retyping it, so that 'Acme' and 'ACME'
> don't become two companies."* That needs a `companies` table, with
> every application pointing at one company. This lesson builds it in
> the backend; lesson 05 builds the picker on screen. It also extends
> **US-9** (refuse nonsense): no application can point at a company that
> doesn't exist.

**Goal:** companies become their own table. Each application belongs to
one company, the API returns the company nested inside each application,
and a second migration changes the existing `applications` table.
**37 tests** green.

Database running (`docker compose up -d --wait` at the repo root); work
in `backend/`.

---

## The concepts first

### Foreign keys

A **foreign key** is a column that holds another table's primary key.
`applications.company_id = 3` means "this application belongs to the
company whose `id` is 3." PostgreSQL **enforces** it: it refuses any
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

Docs:
<https://docs.sqlalchemy.org/en/20/orm/basic_relationships.html#one-to-many>

### Loading related objects in async code

This is the concept that catches almost everyone, so read it twice.

When you load an application, its company is in a **different table**.
Getting it means a **second query**. *When* that query runs is called
the **loading strategy**:

| Strategy | When the company is fetched | In async code |
| --- | --- | --- |
| **Lazy** (the default) | The moment your code first touches `application.company` | ❌ **Fails** |
| **`selectin`** (eager) | Right after the applications themselves, in one extra query for all of them | ✅ Works |

Why does lazy loading fail? Touching an attribute is plain Python —
`application.company` — with **no `await`**. But a query *must* be
awaited in async code. SQLAlchemy can't sneak an `await` in, so it
raises:

```text
sqlalchemy.exc.MissingGreenlet: greenlet_spawn has not been called;
can't call await_only() here.
```

When you see `MissingGreenlet`, read it as: **"you touched a related
object that was never loaded."**

The fix is to load it **eagerly** — ask for it up front, while you're
already awaiting. Two ways:

1. **On the relationship, for every query:**

   ```python
   company: Mapped[Company] = relationship(..., lazy="selectin")
   ```

   Good when you *always* need it. An application is never shown
   without its company, so this fits `Application.company`.

2. **On one query, when you ask for it:**

   ```python
   select(Company).options(selectinload(Company.applications))
   ```

   Good when you only *sometimes* need it. A company's whole list of
   applications is rarely needed, so `Company.applications` stays lazy
   and individual queries opt in. Read
   `starter-tests/backend/phase-2/tests/test_models.py`, test 2 — it
   does exactly this.

One more case: after a **commit that changes `company_id`**, the
`company` attribute still points at the *old* company object. A
**refresh** reloads it:

```python
await db.refresh(application, ["company"])
```

The optional second argument names which attributes to reload.

Docs:
<https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html#preventing-implicit-io-when-using-asyncsession>

### Nested response schemas

A Pydantic schema can have a field whose type is *another schema*.
Because `ApplicationRead` has `from_attributes=True`, Pydantic reads
`application.company` (the relationship) and builds a `CompanyRead` from
it automatically. **That's an attribute access** — so the company must
already be loaded, or serializing the response raises `MissingGreenlet`.

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

📄 `backend/app/models.py`:

- **`Company`** — table `companies`: `id` (primary key), `name`
  (string, 100, **unique**), `applications` (relationship to
  `Application`; default lazy loading).
- **`Application`** — remove the `company` string column. Add
  `company_id` (foreign key to `companies.id`, required) and `company`
  (relationship to `Company`, **`lazy="selectin"`**). Both relationships
  use `back_populates`.

### Connect the dots

Read the three tests in `tests/test_models.py`:

- Test 2 loads a company and its applications with `selectinload`. That
  works whatever `Company.applications`'s strategy is.
- Test 3 loads an application with a **plain** `select`, then reads
  `saved.company.name`. `session.expunge_all()` (line before the query)
  empties the session, so nothing is already in memory. *Which
  strategy must `Application.company` have for that to work?*

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
    company: Company — relationship, back-populates "applications",
                       loaded eagerly with "selectin"
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

On `Company`:

```python
applications: Mapped[list["Application"]] = relationship(
    back_populates="company",
)
```

On `Application`:

```python
company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"))
company: Mapped[Company] = relationship(
    back_populates="applications",
    lazy="selectin",
)
```
</details>

<details>
<summary>Hint 3 — test 3 fails with MissingGreenlet</summary>

`Application.company` is missing `lazy="selectin"`. Without it, reading
`saved.company` tries to lazy-load.
</details>

🟢 `test_models.py` passes (3 tests). Everything using the API still
fails. Commit: `feat(backend): company model and relationship`.

### Your first self-written test (optional, recommended)

No provided test checks that PostgreSQL enforces the foreign key — so
write one. 📄 In `backend/tests/test_models.py`, add a test at the
**end of the file** that:

1. adds an `Application` with `company_id=999` (no such company) to the
   `session`;
2. expects **`await session.commit()`** to raise an **`IntegrityError`**
   (from `sqlalchemy.exc`).

To prove it can fail: temporarily remove `ForeignKey("companies.id")`
from the model (the test fixtures build tables from the models), run
it, watch it fail, then put it back.

<details>
<summary>Hint</summary>

```text
with pytest.raises(IntegrityError):
    await session.commit()
```

Docs: <https://docs.pytest.org/en/stable/how-to/assert.html#assertions-about-expected-exceptions>
</details>

---

## Step 3 — The companies router

### Contract

📄 `backend/app/schemas.py` — add:

| Schema | Fields |
| --- | --- |
| `CompanyCreate` | `name: CleanStr` |
| `CompanyRead` | `id`, `name`; `from_attributes` |

📄 `backend/app/routers/companies.py` with prefix `/companies`, included
in `backend/app/main.py`:

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
async function create_company(payload, db):
    existing = first company where name == payload.name, or None
    if existing:
        raise 409 "Company already exists"
    add, await commit, await refresh, return the new company
```

<details>
<summary>Hint 1 — find one or none</summary>

```python
result = await db.scalars(
    select(models.Company).where(models.Company.name == payload.name)
)
existing = result.first()
```

`.first()` returns the first match, or `None`.
</details>

<details>
<summary>Hint 2 — sorted list</summary>

`.order_by(models.Company.name)`
</details>

🟢 `test_companies.py` passes (6 tests). Commit: `feat(backend):
companies endpoints`.

---

## Step 4 — Applications belong to companies

### Contract

📄 `backend/app/schemas.py` changes:

| Schema | Change |
| --- | --- |
| `ApplicationCreate` | `company: CleanStr` becomes `company_id: int` |
| `ApplicationUpdate` | `company` becomes `company_id: int \| None = None` |
| `ApplicationRead` | `company` becomes `company: CompanyRead`. **No `company_id` field** — the tests compare the whole object |

📄 `backend/app/routers/applications.py` changes:

- **Create** and **update** return `422` with detail exactly
  `"Company not found"` when a given `company_id` doesn't exist.
- **Create** and **update** return the application **with its company
  loaded** (see "Loading related objects in async code").
- **List** accepts an optional `company_id` query parameter, and both
  filters can be combined.

### Connect the dots

- You already have a helper that finds an application or raises `404`.
  You need its twin for companies — but raising **`422`**, because the
  *request* refers to something invalid, rather than the URL pointing
  at nothing.
- In **update**, only check the company if the client actually sent a
  `company_id`. Where did you learn which fields were sent? (Tiro lesson
  06, Cycle 5.)
- After **update** moves an application to another company, which
  attribute is now stale? (See the end of "Loading related objects.")
- Filters stack: each `.where(...)` narrows the query further.

### Pseudocode

```text
async function require_company(db, company_id):
    company = await get Company by id
    if none: raise 422 "Company not found"
    return company

create:
    await require_company(db, payload.company_id)
    add, await commit
    await refresh the application, including "company"
    return it

update:
    changes = fields actually sent
    if "company_id" in changes:
        await require_company(db, changes["company_id"])
    apply changes, await commit
    await refresh the application, including "company"
    return it

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

<details>
<summary>Hint 3 — MissingGreenlet when returning from create or update</summary>

The company wasn't loaded on the object you're returning. After the
commit: `await db.refresh(application, ["company"])`.
</details>

<details>
<summary>Hint 4 — moving to another company still shows the old one</summary>

Same fix: refresh `"company"` after the commit, so the relationship
follows the new `company_id`.
</details>

🟢 **`37 passed`**, 100% coverage. Commit: `feat(backend): applications
belong to companies`.

---

## Step 5 — The second migration

### ⚠️ Reset your development database first

This migration adds a **required** `company_id` column to
`applications`. Any rows already in your development database have no
value for it, so the migration would fail on them. Converting old
free-text company names into company rows is a **data migration** — a
GRADUS III skill. For now, start clean:

```bash
uv run alembic downgrade base
```

`base` means "before the first migration": every table Alembic created
is dropped.

### Generate, read, apply

```bash
uv run alembic upgrade head
uv run alembic revision --autogenerate -m "add companies"
```

(The `upgrade head` re-applies your first migration, so the database is
at the latest revision before autogenerate compares it to the models.)

Open the new file in `backend/migrations/versions/` and **read it**. You
should find, in `upgrade()`:

- `op.create_table('companies', ...)` including a unique constraint
  named `uq_companies_name` — your naming convention at work
- `op.add_column('applications', ...)` adding `company_id`
- `op.create_foreign_key(...)` named
  `fk_applications_company_id_companies`
- `op.drop_column('applications', 'company')`

…and a `downgrade()` that undoes all of it in reverse order.

If a constraint's name is `None`, your naming convention isn't being
used — check `Base` in `backend/app/database.py`.

```bash
uv run alembic upgrade head
uv run alembic downgrade -1
uv run alembic upgrade head
```

✅ All three succeed. Testing the downgrade *now*, while it's fresh, is
cheaper than discovering it's broken when you need it.

Check it in `psql` (repo root):

```bash
docker compose exec db psql -U miles -d miles -c "\d applications"
```

✅ Under **Foreign-key constraints**:
`fk_applications_company_id_companies`.

### Try it (US-6)

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

**2. What does `MissingGreenlet` almost always mean in this project?**

<details>
<summary>Answer</summary>

Code touched a related object that hadn't been loaded, so SQLAlchemy
tried to lazy-load it — a query without an `await`, which async code
can't do. Load it eagerly (`lazy="selectin"`, `selectinload`) or refresh
it.
</details>

**3. Why `lazy="selectin"` on `Application.company`, but not on
`Company.applications`?**

<details>
<summary>Answer</summary>

Every application response includes its company, so always loading it is
right. A company's full list of applications is rarely needed; loading
it every time would be wasted work, so individual queries opt in with
`selectinload`.
</details>

**4. The API checks `company_id` itself. Why does the foreign key in the
database still matter?**

<details>
<summary>Answer</summary>

The API check only protects requests that go through the API. A script,
a future bug, or a direct `psql` session could still store a broken
`company_id`. The foreign key makes the database refuse it no matter
where it comes from.
</details>

Next: [04 — Frontend foundations](04-frontend-foundations.md)
