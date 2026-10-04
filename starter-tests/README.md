# Starter tests

These are the **provided tests** for GRADUS II. They are the
specification: when every test passes, your app is done.

**Don't edit them to make them pass.** If you believe a test is wrong,
re-read the lesson's contract first; if it still looks wrong, report it
(see the main README).

## What's here

```text
starter-tests/
├── backend/
│   ├── phase-1/tests/   ← lesson 02: rebuild the core API
│   └── phase-2/tests/   ← lesson 03: add companies (replaces some phase 1 files)
└── frontend/
    └── src/             ← lessons 04–06: copy in file by file, as each lesson says
```

## How to copy them in

The lessons tell you *when*. The commands (from the **repo root**, in
Git Bash or a macOS/Linux terminal) look like this:

```bash
# Backend, phase 1 — copies the whole tests/ folder
cp -r starter-tests/backend/phase-1/tests backend/

# Backend, phase 2 — overwrites test_models.py and
# test_applications.py, and adds test_companies.py
cp starter-tests/backend/phase-2/tests/*.py backend/tests/

# Frontend — one file at a time, e.g.
cp starter-tests/frontend/src/api.test.ts frontend/src/
```

Copy a test file in **before** you write the code it tests, and run it
to watch it fail. Red first, every time.

## Before running backend tests

The backend tests are **async** and run against the real PostgreSQL
test database (`miles_test`, port 5434). Start it first, from the repo
root:

```bash
docker compose up -d --wait
```

They also need `pytest-asyncio` installed and `asyncio_mode = "auto"`
in `backend/pyproject.toml` (lesson 01, Part C).
