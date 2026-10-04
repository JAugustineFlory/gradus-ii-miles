# 04 — Frontend foundations

> **Where this fits.** The backend from lessons 02–03 now speaks a new
> shape (companies nested in applications, fixed statuses). Before any
> screen can deliver a story, the frontend needs to speak it too. This
> lesson builds the layer every component relies on: the types, and the
> API module that carries each request across the arrow from React to
> FastAPI in the lesson 00 diagram.
>
> | Story | What delivers it here |
> | --- | --- |
> | **US-8** clear message when something fails | `request` throws an error carrying the backend's `detail` |
> | **US-9** refuse nonsense | a `Status` type the editor checks before code runs |
>
> Every file this lesson creates is named in its **Contract** section,
> with its full path under `frontend/src/`.

**Goal:** shared types that match the new API, `formatStatus` rebuilt,
and an API module with one generic `request` helper — fully tested by
**mocking `fetch`**. **12 frontend tests** green.

Work in `frontend/`. Copy commands run from `frontend/`, so paths start
with `../starter-tests/`.

---

## Step 1 — Types

No test file for this step: types are checked by `npm run typecheck`,
and every later test depends on them.

### Contract — `src/types.ts`

| Export | What |
| --- | --- |
| `STATUSES` | the four statuses, in order: `applied`, `interviewing`, `offer`, `rejected` |
| `Status` | a type allowing only those four strings, **derived from `STATUSES`** |
| `Company` | `{ id: number; name: string }` |
| `Application` | `id`, `role`, `status: Status`, `applied_on: string`, `company: Company` |
| `NewApplication` | `company_id: number`, `role`, `status: Status`, `applied_on: string` |

### New concept: deriving a type from a constant

You need the list of statuses twice: as **values** (to draw the
`<option>`s) and as a **type** (so `status: 'ghosted'` is a type error).
Writing them twice means they can drift apart. Instead, write the values
once and derive the type:

```ts
export const STATUSES = ['applied', /* … */] as const
export type Status = (typeof STATUSES)[number]
```

- **`as const`** tells TypeScript "this array will never change," so it
  remembers the exact strings instead of widening them to `string`.
- **`typeof STATUSES`** gets the *type* of that constant: a read-only
  list of those exact strings.
- **`[number]`** means "the type of any item in it" — which is
  `'applied' | 'interviewing' | 'offer' | 'rejected'`, a **union type**.

This is the TypeScript twin of the backend's `Literal`.

Docs:
<https://www.typescriptlang.org/docs/handbook/2/indexed-access-types.html>

### Connect the dots

`Application` changed shape since Tiro: the company is now a nested
object. Compare with `ApplicationRead` and `CompanyRead` in
`backend/app/schemas.py` — the TypeScript types should mirror them
exactly. `NewApplication` mirrors `ApplicationCreate`.

<details>
<summary>Hint — why can't NewApplication use Omit anymore?</summary>

In Tiro, `NewApplication` was `Application` without `id`. Now the
request sends `company_id` while the response has `company`, so the
shapes differ in more than one field. It's clearer to write
`NewApplication` out in full.
</details>

**Checkpoint:** `npm run typecheck` passes.

---

## Step 2 — `formatStatus` (Tiro repeat)

```bash
mkdir -p src/utils
cp ../starter-tests/frontend/src/utils/formatStatus.test.ts src/utils/
npm test
```

📄 Write `frontend/src/utils/formatStatus.ts` (Tiro lesson 07, Steps
5–6). 🟢 `2 passed`.

---

## Step 3 — The API module

### Contract — `src/api.ts`

| Function | Request | Resolves with |
| --- | --- | --- |
| `fetchApplications(status?)` | `GET /applications`, or `GET /applications?status=…` when given | `Application[]` |
| `createApplication(data)` | `POST /applications` with JSON body | `Application` |
| `updateStatus(id, status)` | `PATCH /applications/{id}` with `{ status }` | `Application` |
| `deleteApplication(id)` | `DELETE /applications/{id}` | `undefined` |
| `fetchCompanies()` | `GET /companies` | `Company[]` |
| `createCompany(name)` | `POST /companies` with `{ name }` | `Company` |

Rules for all of them:

- The base URL is `import.meta.env.VITE_API_URL`, falling back to
  `http://localhost:8000`.
- On a non-OK response, **reject with an `Error`** whose message is the
  server's `detail` **if it's a string**, otherwise
  `Request failed: <status code>`.
- On `204 No Content`, **don't call `.json()`** — there is no body.

### 🔴 Red

```bash
cp ../starter-tests/frontend/src/api.test.ts src/
npm test
```

🔴 `Failed to resolve import "./api"`.

### New concept: mocking `fetch`

Open `api.test.ts` and read `mockFetch` at the top.

- **`vi.spyOn(globalThis, 'fetch')`** wraps the global `fetch` function
  so the test can watch every call.
- **`.mockResolvedValue(fakeResponse)`** replaces what it does: instead
  of making a network request, it immediately returns the fake.
- The fake has only what your code uses: `ok`, `status`, and `json()`.
- **`vi.restoreAllMocks()`** (in `afterEach`) puts the real `fetch`
  back.

Then each test checks two things: what your function **returned**, and
what it **asked `fetch` for** (`lastRequest` reads the URL, method, and
body from the recorded call).

**Why mock?** A test that hits a real server is slow, fails when the
server is down, and can't easily produce a `500` on demand. Mocking
lets you test *your* code's behavior for every response the server might
give.

Docs: <https://vitest.dev/guide/mocking/functions>

### New concept: generic functions

Tiro's `api.ts` repeated the same `if (!response.ok)` block four times.
Now you'll write it once, in a helper every function calls. But each
caller expects a different result type — `Application[]`,
`Company`, nothing… A **generic** function takes the type as a
parameter:

```ts
async function request<T>(path: string, options?: RequestInit): Promise<T>
```

`T` is a placeholder. `request<Company[]>('/companies')` means "this
call returns `Company[]`." One implementation, correctly typed for every
caller.

Docs: <https://www.typescriptlang.org/docs/handbook/2/generics.html>

### New concept: environment variables in Vite

Vite exposes environment variables whose names start with **`VITE_`** on
`import.meta.env`. They're read from `.env` files in `frontend/`:

- Create **`frontend/.env.example`** containing
  `VITE_API_URL=http://localhost:8000` and **commit it** — it documents
  the setting.
- Copy it to **`frontend/.env`** for real local values. `.env` is in
  `.gitignore`; it can hold things that differ per machine.

> ⚠️ Anything in a `VITE_` variable ends up in the JavaScript sent to
> the browser. **Never put a secret in one.**

Docs: <https://vite.dev/guide/env-and-mode>

### Connect the dots

- Build the query string with **`URLSearchParams`** rather than gluing
  strings together — it handles escaping for you.
- `response.json()` on an error might itself fail (not every error body
  is JSON). Plan for that.
- `detail` from FastAPI is a **string** for your own `HTTPException`s,
  but a **list** for validation (`422`) errors. The contract says: use
  it only if it's a string.

### Pseudocode

```text
API_URL = VITE_API_URL env var, or "http://localhost:8000"

async function request<T>(path, options = {}):
    response = await fetch(API_URL + path, options,
                           adding a JSON Content-Type header)
    if response is not ok:
        throw new Error(await errorMessage(response))
    if response.status is 204:
        return undefined (as T)
    return await response.json()

async function errorMessage(response):
    try:
        data = await response.json()
        if data.detail is a string: return data.detail
    catch:
        ignore — fall through
    return "Request failed: " + response.status

fetchApplications(status?):
    query = "?status=" + status   if status given, else ""
    return request<Application[]>("/applications" + query)

createApplication(data):
    return request<Application>("/applications",
        method POST, body = data as JSON)

… and so on for the other four.
```

<details>
<summary>Hint 1 — the fallback URL</summary>

`import.meta.env.VITE_API_URL ?? 'http://localhost:8000'` — `??` uses
the right side only when the left is `null` or `undefined`.
</details>

<details>
<summary>Hint 2 — reading detail safely in TypeScript</summary>

`response.json()` returns `any`. Treat it as `unknown` and check before
using it:

```ts
const data: unknown = await response.json()
if (
  typeof data === 'object' &&
  data !== null &&
  'detail' in data &&
  typeof data.detail === 'string'
) {
  return data.detail
}
```

Each check **narrows** the type until TypeScript knows `data.detail` is
a string.
</details>

<details>
<summary>Hint 3 — the query string</summary>

```ts
const query = status
  ? `?${new URLSearchParams({ status })}`
  : ''
```
</details>

<details>
<summary>Hint 4 — the delete test fails with "Unexpected end of JSON input"</summary>

Your helper called `.json()` on the `204`. Check `response.status ===
204` and return before parsing.
</details>

🟢 `12 passed` (2 formatStatus + 10 api). `api.ts` at 100% coverage.

Commit: `feat(frontend): typed API module with mocked-fetch tests`.

---

## Step 4 — Guard the frontend

📄 **File:** `.husky/pre-commit` (repo root) — **edit**: add this
block **between** the backend lint and backend tests blocks:

```sh
echo "Frontend: lint and types"
(cd frontend && npm run lint && npm run typecheck)
```

and this block at the **end of the file**:

```sh
echo "Frontend: tests"
(cd frontend && npm run test:run)
```

Commit to try it: all five stages should run — database, backend lint,
frontend lint and types, backend tests, frontend tests. (The full hook
is listed in lesson 07.)

---

## Explain it back

**1. Why derive `Status` from `STATUSES` instead of writing the union by
hand?**

<details>
<summary>Answer</summary>

So there's one source of truth. Add a fifth status to the array and the
type updates automatically; nothing can drift out of sync.
</details>

**2. The test's fake `json()` throws on `204`. Why build the fake that
way?**

<details>
<summary>Answer</summary>

A real `204` response has no body, so calling `.json()` on it throws.
A fake that returns something harmless would let a real bug pass. Fakes
should behave like the real thing wherever your code depends on it.
</details>

**3. What does `request<T>` gain over four copies of the same code?**

<details>
<summary>Answer</summary>

One place for headers, error handling, and the `204` rule — fix it once
and every call benefits — while each caller still gets its own correct
return type.
</details>

**4. Why must you never put a secret in a `VITE_` variable?**

<details>
<summary>Answer</summary>

Vite copies those values into the JavaScript bundle that every visitor's
browser downloads. Anyone can read them.
</details>

Next: [05 — Components](05-components.md)
