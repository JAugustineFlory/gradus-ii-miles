# 06 — App and error handling

**Goal:** an `App` that loads companies and applications, filters by
status, handles every action's success **and** failure — and is fully
tested without a server. **38 frontend tests** green.

---

## Contract

`src/App.tsx` default-exports `App`, which renders:

- an `<h1>` **Job tracker**
- **at most one** error message, in an element with `role="alert"`
- `CompanyForm`, `ApplicationForm` (given the loaded companies),
  `StatusFilter`, and `ApplicationList`

Behavior:

| When | Then |
| --- | --- |
| The page opens | Load companies and applications |
| Loading fails | Alert containing **Could not load** |
| A company is added | It appears in the company picker |
| Adding a company fails | Alert containing the **server's message** (e.g. "Company already exists") |
| An application is added | It appears in the list |
| A status changes | The list shows the server's updated application |
| A status change fails | Alert containing **Could not update**; the old status stays |
| An application is deleted | It disappears |
| A delete fails | Alert containing **Could not delete**; the application stays |
| The filter changes | Call `fetchApplications(status)` — or with no status for **All** |

Suggested messages (only the bold parts above are tested):

```text
Could not load your applications. Is the backend running?
Could not add company: <server message>
Could not add application: <server message>
Could not update status: <server message>
Could not delete: <server message>
```

### 🔴 Red

```bash
cp ../starter-tests/frontend/src/App.test.tsx src/
npm test -- App
```

---

## New concept: mocking a whole module

`api.test.ts` faked `fetch`. For `App`, the test goes one level higher:

```ts
vi.mock('./api')
```

This replaces **every export of `api.ts`** with an empty mock function —
before `App` even imports it. Then each test decides what the mocks
return:

```ts
vi.mocked(api.fetchCompanies).mockResolvedValue([acme])
vi.mocked(api.deleteApplication).mockRejectedValue(new Error('Oops'))
```

- **`vi.mocked(fn)`** doesn't change anything; it just tells TypeScript
  "this is a mock," so `.mockResolvedValue` type-checks.
- **`mockResolvedValue(x)`** — the mock returns a Promise that succeeds
  with `x`.
- **`mockRejectedValue(err)`** — it returns a Promise that fails with
  `err`. That's how the tests trigger every error path on demand.
- **`vi.clearAllMocks()`** in `beforeEach` wipes the record of past
  calls, so each test's assertions only see its own calls.

**Why mock the module rather than `fetch`?** `api.ts` is already tested.
`App`'s tests should check *App's* job — what it does with results and
errors — not re-test HTTP details.

Docs: <https://vitest.dev/guide/mocking/modules>

## New concept: waiting for async updates

`App` loads data *after* it first renders, so right after `render` the
list is still empty. Two tools wait:

- **`findBy…`** — like `getBy…`, but keeps retrying (up to about a
  second) until the element appears. Always `await` it.
- **`waitFor(() => { expect(...) })`** — retries an assertion until it
  passes. Use it for things that aren't "an element appears," like
  "this mock was called" or "this element is gone."

Notice most tests start with `await screen.findByText('Junior
Developer')` — "wait until loading finishes" — before doing anything.

Docs: <https://testing-library.com/docs/dom-testing-library/api-async>

---

## Step 1 — Loading, and loading errors

### Connect the dots

- Companies and applications are independent — no reason to wait for
  one before asking for the other.
- **`Promise.all([a, b])`** waits for *both* and gives you both results
  — or fails as soon as either fails.
- The applications list must **reload when the filter changes**.
  Companies don't. One `useEffect` per concern keeps that clean.
- An effect re-runs whenever a value in its **dependency array**
  changes.

### Pseudocode

```text
state: companies [], applications [], filter 'all', error null

effect, runs once:
    fetchCompanies()
        then store them
        catch → error "Could not load…"

effect, runs whenever filter changes:
    fetchApplications(filter is 'all' ? nothing : filter)
        then store them
        catch → error "Could not load…"
```

<details>
<summary>Hint — should this be one effect with Promise.all?</summary>

It can be. `Promise.all([fetchCompanies(), fetchApplications(...)])` in
one effect with `[filter]` as the dependency also passes the tests — but
it re-fetches companies on every filter change. Two effects is the
tighter design. Try both; notice the trade-off.
</details>

<details>
<summary>Hint — ESLint says not to set state in an effect</summary>

Newer versions of the `react-hooks` plugin flag calling a state setter
*directly* in an effect's body. Setting state inside `.then(...)` or
`.catch(...)` callbacks is fine — that happens later, when the data
arrives.
</details>

🟢 The three **loading** tests pass.

---

## Step 2 — Actions and their errors

### New concept: functional state updates

In Tiro you wrote `setApplications([...applications, created])`. That
uses whatever `applications` was **when the handler was created**. If
two updates happen close together, the second can overwrite the first
with a stale copy.

Passing a **function** instead fixes it — React calls it with the
**latest** state:

```ts
setApplications((current) => [...current, created])
```

Use this form whenever the new state is based on the old state.

Docs:
<https://react.dev/reference/react/useState#updating-state-based-on-the-previous-state>

### New concept: `try` / `catch` with `await`

```text
async function handleDelete(id):
    try:
        await deleteApplication(id)
        remove it from state (functional update)
        clear any old error
    catch (error):
        set error "Could not delete: " + message of error
```

If `await` rejects, execution jumps straight to `catch` — so the
"remove it from state" line never runs, and the application stays.

In TypeScript, the caught `error` has type **`unknown`** — it could be
anything that was thrown. Get a message safely:

```text
function messageOf(error: unknown): string
    if error is an Error instance: return its message
    otherwise: return it converted to a string
```

### Connect the dots

Five handlers, one shape. For each: what does it **await**, what does it
do to **state** on success, and which **message prefix** does it use on
failure?

| Handler | Awaits | On success |
| --- | --- | --- |
| add company | `createCompany(name)` | append to companies |
| add application | `createApplication(data)` | append to applications |
| change status | `updateStatus(id, status)` | replace the matching application with the returned one |
| delete | `deleteApplication(id)` | remove the matching application |
| change filter | — | just set the filter; the effect does the rest |

<details>
<summary>Hint — "Found multiple elements with the role alert"</summary>

Render the error in **one** place, from **one** piece of state. Each
failure replaces the previous message rather than adding another.
</details>

<details>
<summary>Hint — the error never clears</summary>

Call `setError(null)` after each successful action, so an old failure
doesn't linger after things start working again.
</details>

🟢 **`38 passed`.** Run `npm run coverage` — every file in `src/`
should be at or near 100%.

Commit: `feat(frontend): App with loading, filtering, and error handling`.

---

## Step 3 — Try it for real

Run both servers (Tiro lesson 07, Step 6), then check in the browser:

- [ ] "Add a company first." shows until a company exists
- [ ] Adding the same company twice shows **Company already exists**
- [ ] A new application appears and survives a reload
- [ ] The **Show** filter narrows the list
- [ ] Stop the backend and try to delete something — the error appears,
      and the application stays
- [ ] Restart the backend, delete again — it works, and the error clears

### Optional polish

These aren't tested. Each one is a small design decision — make it, then
write a test for it yourself if you want the practice:

- If the filter is **Applied** and you change an application to
  **Offer**, should it vanish from the list?
- Should companies in the picker stay sorted after you add one?
- Should the alert have a way to dismiss it?

---

## Explain it back

**1. Why does `App.test.tsx` mock `./api` instead of `fetch`?**

<details>
<summary>Answer</summary>

`api.ts` already has its own tests. Mocking the module lets `App`'s
tests focus on App's behavior — state changes and error messages — and
makes every success or failure trivial to trigger.
</details>

**2. What's the difference between `getByText` and `findByText`?**

<details>
<summary>Answer</summary>

`getByText` checks once, right now, and throws if it's not there.
`findByText` returns a Promise that keeps checking until the element
appears or a timeout passes. Use `findBy` for anything that shows up
after an async action.
</details>

**3. When should you pass a function to a state setter?**

<details>
<summary>Answer</summary>

Whenever the new state is computed from the old state — appending,
removing, replacing an item. The function receives the latest state, so
updates can't overwrite each other with stale copies.
</details>

**4. Why is the caught `error` typed `unknown`, not `Error`?**

<details>
<summary>Answer</summary>

JavaScript lets you `throw` anything — a string, a number, an object.
TypeScript can't know what arrived, so it makes you check before using
it.
</details>

Next: [07 — Guardrails and debrief](07-guardrails-and-debrief.md)
