# 05 — Components

> **Where this fits.** These are the screens the job seeker actually
> touches. Each component delivers part of a story; `App` (lesson 06)
> connects them to the API.
>
> | Component | Story |
> | --- | --- |
> | `StatusFilter` | **US-7** filter by status |
> | `CompanyForm` | **US-6** build the list of companies (and **US-9**: no blank names) |
> | `ApplicationList` | **US-2** see all, **US-3** update status, **US-4** delete |
> | `ApplicationForm` | **US-1** record, with **US-6**'s company picker |

**Goal:** four presentational components, each driven by its provided
test file: `StatusFilter`, `CompanyForm`, `ApplicationList`, and
`ApplicationForm`. **27 frontend tests** green at the end.

All four follow the rule from Tiro: **props in, callbacks out**. None of
them import `api.ts`.

```bash
mkdir -p src/components
```

---

## Component 1 — `StatusFilter` (new, US-7)

### Contract

📄 `frontend/src/components/StatusFilter.tsx` — **new**. Exports
`StatusFilter` and the type `StatusFilterValue`.

```text
StatusFilter({ value, onChange })
  value:    Status | 'all'
  onChange: (value: Status | 'all') => void
```

- A `<select>` labeled **Show**.
- Options, in order: **All** (value `all`), then one per status,
  displayed with `formatStatus`.

### 🔴 Red

```bash
cp ../starter-tests/frontend/src/components/StatusFilter.test.tsx src/components/
npm test -- StatusFilter
```

### New concept: a union with a literal

`Status | 'all'` means "any status, **or** the exact string `'all'`."
It's a common pattern for filters: the real values plus one "no filter"
option. Define it once and export it:

```ts
export type StatusFilterValue = Status | 'all'
```

### Connect the dots

`event.target.value` from a `<select>` is typed as plain `string`, but
`onChange` promises a `StatusFilterValue`. You know the value can only be
one of your options, but TypeScript doesn't. You'll need to tell it —
with a **type assertion** (`as`).

<details>
<summary>Hint 1 — the options</summary>

One hard-coded `<option value="all">All</option>`, then
`STATUSES.map(...)` for the rest — the same pattern as Tiro's status
select.
</details>

<details>
<summary>Hint 2 — the assertion</summary>

`onChange(event.target.value as StatusFilterValue)`. An assertion
doesn't check anything at runtime; it's a promise from you to the
compiler. Use it only when you *know* it's true — as here, where the
only possible values are the options you rendered.
</details>

🟢 `3 passed`. Commit: `feat(frontend): StatusFilter`.

---

## Component 2 — `CompanyForm` (new, US-6)

### Contract

📄 `frontend/src/components/CompanyForm.tsx` — **new**. Exports
`CompanyForm`.

```text
CompanyForm({ onSubmit })
  onSubmit: (name: string) => void
```

- One text input labeled **Company name**.
- A submit button labeled **Add company**.
- Calls `onSubmit` with the name **trimmed** of surrounding spaces.
- **Doesn't** call `onSubmit` if the trimmed name is empty.
- Clears the input after a successful submit.

### 🔴 Red

```bash
cp ../starter-tests/frontend/src/components/CompanyForm.test.tsx src/components/
```

### Connect the dots

The browser's `required` attribute blocks an *empty* field — but `"   "`
isn't empty, so the browser lets it through. The backend would reject it
with a `422`, but it's better to stop it before the request is ever
sent. Where does that check belong?

### Pseudocode

```text
state: name (string, starts "")

on submit(event):
    prevent the page reload
    trimmed = name without surrounding spaces
    if trimmed is empty: stop here
    onSubmit(trimmed)
    reset name to ""
```

<details>
<summary>Hint</summary>

JavaScript strings have a `.trim()` method.
</details>

🟢 `3 passed`. Commit: `feat(frontend): CompanyForm`.

---

## Component 3 — `ApplicationList` (Tiro repeat, new shape; US-2, 3, 4)

### Contract

📄 `frontend/src/components/ApplicationList.tsx` — **new**. Exports
`ApplicationList`. (Tiro lesson 08, Step 2.)

```text
ApplicationList({ applications, onDelete, onStatusChange })
  applications:   Application[]
  onDelete:       (id: number) => void
  onStatusChange: (id: number, status: Status) => void
```

- Empty list: the text **No applications yet. Add your first one
  above.**
- Otherwise a `<ul>` with one `<li>` per application showing, each in
  its **own element**: the role, the company's name, and the
  `applied_on` date.
- A status `<select>` with accessible name
  **`Status for {role} at {company name}`**, showing the current status.
- A delete button with visible text **Delete** and accessible name
  **`Delete {role} at {company name}`**.

### 🔴 Red

```bash
cp ../starter-tests/frontend/src/components/ApplicationList.test.tsx src/components/
```

### What changed since Tiro, and why

- **Accessible names now include the role.** In Tiro, one company meant
  one application, so "Delete Acme" was unique. Now a company can have
  several; "Delete Acme" could mean any of them. Names must identify one
  thing.
- **The date appears.** Show it in a `<time>` element with a
  `dateTime` attribute — that's the HTML element for machine-readable
  dates.
- **`onStatusChange` takes a `Status`**, not a `string` — the same
  assertion situation as `StatusFilter`.

<details>
<summary>Hint — "Found multiple elements with the text: Acme"</summary>

The test uses `getAllByText('Acme')` and expects exactly two — one per
application. If you get more, the company name appears in extra places
(like inside an accessible name that's rendered as text).
</details>

🟢 `5 passed`. Commit: `feat(frontend): ApplicationList with companies`.

---

## Component 4 — `ApplicationForm` (Tiro repeat, new field; US-1, 6)

### Contract

📄 `frontend/src/components/ApplicationForm.tsx` — **new**. Exports
`ApplicationForm`. (Tiro lesson 08, Step 3.)

```text
ApplicationForm({ companies, onSubmit })
  companies: Company[]
  onSubmit:  (application: NewApplication) => void
```

- If `companies` is empty, render only the text **Add a company
  first.** — no form.
- Otherwise a form with:
  - a `<select>` labeled **Company**: a first placeholder option
    **Choose a company** with value `""`, then one option per company
    (text = name, value = id);
  - inputs labeled **Role** and **Date applied**;
  - a submit button labeled **Add application**.
- Submits a `NewApplication` with **`company_id` as a number** and
  `status: 'applied'`.
- Clears Role and Date applied after submitting.

### 🔴 Red

```bash
cp ../starter-tests/frontend/src/components/ApplicationForm.test.tsx src/components/
```

### Connect the dots

- Every form value — including a `<select>`'s — is a **string**. The
  selected company arrives as `"2"`, but `NewApplication` wants `2`.
- So the **form's state** and the **submitted object** have different
  shapes. It's fine (and clear) to give the form state its own type,
  and convert when submitting.
- The placeholder has value `""`. Adding `required` to the `<select>`
  makes the browser refuse to submit until a real company is picked.

### Pseudocode

```text
type FormState = { company_id: string; role: string; applied_on: string }
EMPTY = all three ""

if no companies: return "Add a company first."

on submit(event):
    prevent reload
    onSubmit({
        company_id: form.company_id converted to a number,
        role: form.role,
        status: 'applied',
        applied_on: form.applied_on,
    })
    reset the form
```

<details>
<summary>Hint 1 — converting</summary>

`Number('2')` is `2`.
</details>

<details>
<summary>Hint 2 — where the early return goes</summary>

Hooks (`useState`) must run on **every** render, in the same order —
React tracks them by position. So call `useState` first, *then* return
early if there are no companies. Returning before a hook breaks this
rule, and ESLint's `react-hooks` plugin will flag it.
</details>

🟢 `4 passed`. **Total: 27 frontend tests.** Commit: `feat(frontend):
ApplicationForm with company picker`.

---

## Explain it back

**1. Why check for a blank company name in `CompanyForm` when the
backend already rejects it?**

<details>
<summary>Answer</summary>

Faster, clearer feedback and one less pointless request. The backend
check stays as the real safeguard — never trust the client alone — but
catching it early is better for the user.
</details>

**2. What does `as StatusFilterValue` do at runtime?**

<details>
<summary>Answer</summary>

Nothing. Type assertions are erased when the code runs. It only tells
the compiler to trust you, so it's safe only when you can guarantee the
value really has that type.
</details>

**3. Why must `useState` come before the "Add a company first." early
return?**

<details>
<summary>Answer</summary>

React identifies hooks by their call order. If a hook is skipped on some
renders, every hook after it gets mixed up. Hooks must be called
unconditionally, at the top of the component.
</details>

Docs:

- Rules of Hooks: <https://react.dev/reference/rules/rules-of-hooks>
- `<time>`:
  <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/time>
- Type assertions:
  <https://www.typescriptlang.org/docs/handbook/2/everyday-types.html#type-assertions>

Next: [06 — App and error handling](06-app.md)
