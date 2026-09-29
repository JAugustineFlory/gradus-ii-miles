# Glossary (Miles)

New terms in GRADUS II. For everything from Tiro, see **Tiro's
`guide/glossary.md`**. The lesson where each term first appears is in
brackets.

---

**`Annotated`** [02] — Attaches extra information to a type:
`Annotated[str, StringConstraints(...)]` is "a string, with these
rules." Pydantic and FastAPI read the extra part.

**`APIRouter`** [02] — A group of related FastAPI routes, usually one
file per resource, plugged into the app with `include_router`.

**`as const`** [04] — Tells TypeScript a value will never change, so it
keeps exact literal types (`'applied'`) instead of widening them
(`string`).

**Back-populates** [03] — Links the two sides of a SQLAlchemy
relationship so changing one side updates the other.

**Batch mode** [02] — Alembic's way of changing a SQLite table: build a
new copy with the change, copy the rows, swap it in.

**Connection event** [03] — Code SQLAlchemy runs every time it opens a
database connection.

**Constraint** [02] — A rule the database enforces: primary key, unique,
foreign key, check.

**Data migration** [03] — A migration that moves or transforms existing
*data*, not just structure. (Covered in GRADUS III.)

**Dependency array** [06] — The list at the end of `useEffect`. The
effect re-runs whenever a value in it changes.

**Environment variable** [02] — A named setting provided by the
environment (terminal, server) rather than written in code.

**Foreign key** [03] — A column holding another table's primary key,
linking a row to a row in that table.

**Functional update** [06] — Passing a function to a state setter
(`setX((current) => …)`) so the new state is computed from the latest
state.

**Generic** [04] — A function or type with a type parameter, like
`request<T>`, so one implementation works for many types.

**Lazy loading** [03] — Fetching related objects only when code first
accesses them.

**`Literal`** [02] — A Python type allowing only specific values.

**`monkeypatch`** [02] — A pytest fixture that temporarily changes
environment variables, attributes, and more, undoing it after the test.

**Mock module** [06] — Replacing every export of a module with mock
functions, via `vi.mock('./path')`.

**Naming convention** [02] — Rules SQLAlchemy uses to name constraints
automatically and predictably.

**Narrowing** [04] — Checks (`typeof`, `in`, `instanceof`) that let
TypeScript treat an `unknown` or union value as a more specific type.

**Nested schema** [03] — A Pydantic schema with a field whose type is
another schema, producing nested JSON.

**Normalization** [03] — Storing each fact once and referring to it by
id, instead of copying it into many rows.

**One-to-many** [03] — A relationship where one row (a company) relates
to many rows (applications), and each of those relates back to one.

**`Promise.all`** [06] — Runs several Promises at once and waits for all
of them; fails as soon as any one fails.

**Query parameter** [02] — A value in the URL after `?`, like
`?status=offer`.

**Spy** [04] — A mock that wraps an existing function to record its
calls (`vi.spyOn`).

**`StringConstraints`** [02] — Pydantic rules for strings: strip
whitespace, minimum and maximum length, and more.

**Type assertion** [05] — `value as Type`: telling TypeScript to trust
you about a type. Checks nothing at runtime.

**Union type** [04] — A type that can be one of several:
`'applied' | 'offer'`, or `Status | 'all'`.

**`unknown`** [04] — TypeScript's "could be anything" type. Unlike
`any`, you must narrow it before using it.

**`URLSearchParams`** [04] — Builds and escapes URL query strings.

**`409 Conflict`** [03] — The request is valid but clashes with existing
data, like a duplicate name.

---

## Latin

| Word | Meaning |
| --- | --- |
| *gradus* | step, rank |
| *tiro* | recruit, beginner |
| *miles* | soldier |
| *veteranus* | veteran |
