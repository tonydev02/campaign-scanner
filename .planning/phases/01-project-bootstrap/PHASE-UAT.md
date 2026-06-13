# Phase UAT: 01 Project Bootstrap

## Status

`not_started`

Allowed status values:

- `not_started`
- `in_progress`
- `blocked`
- `ready_for_uat`
- `uat_failed`
- `done`

## UAT objective

Verify that a developer can install the project, inspect a stable CLI command
surface, and confirm conservative configuration and repository protections
without triggering scraping, persistence, export, or private account access.

## Test environment

| Item | Value |
|---|---|
| OS | macOS / Windows / Linux |
| Python version | 3.11+ |
| Browser | Not used in this phase |
| Database | Not created in this phase |
| Test date | TODO |
| Tester | TODO |

## Preconditions

- [ ] Python 3.11 or newer is installed.
- [ ] Project and development dependencies are installed.
- [ ] No real `.env`, credentials, cookies, or browser profile is needed.
- [ ] The working tree contains no private financial data.

## Automated verification

```bash
python -m pytest
python -m ruff check .
python -m ruff format --check .
```

Expected result:

- All tests pass.
- Ruff reports no lint or formatting failures.
- Tests do not perform network or browser activity.

## UAT test cases

### UAT-001: Package and root CLI load

**Steps**

```bash
python -c "import vpoint_scanner"
python -m vpoint_scanner --help
```

**Expected result**

- Package import succeeds.
- Help lists `scrape`, `export`, and `summary`.
- No traceback or network request occurs.

**Actual result**

TODO

**Status**

`not_started`

### UAT-002: Future command options are discoverable

**Steps**

```bash
python -m vpoint_scanner scrape --help
python -m vpoint_scanner export --help
python -m vpoint_scanner summary --help
```

**Expected result**

- Scrape help includes `--source` and `--screenshots`.
- Export help includes `--format`, `--output`, and `--ending-within-days`.
- Summary help runs without required arguments.

**Actual result**

TODO

**Status**

`not_started`

### UAT-003: Placeholder commands are honest and side-effect free

**Steps**

```bash
python -m vpoint_scanner scrape --source vpoint_public
python -m vpoint_scanner export --format json
python -m vpoint_scanner summary
```

**Expected result**

- Each command exits successfully with a clear placeholder message.
- No browser opens, database appears, campaign is fetched, or export is written.
- Output does not claim that campaign work completed.

**Actual result**

TODO

**Status**

`not_started`

### UAT-004: Conservative defaults

**Steps**

Inspect the documented configuration and run its automated tests.

**Expected result**

- Extra spending allowed is `0`.
- Automatic campaign entry is disabled.
- New credit card applications are disabled.
- Default paths remain inside the local `data` directory.

**Actual result**

TODO

**Status**

`not_started`

### UAT-005: Sensitive artifacts are protected

**Steps**

Review `.gitignore`, `.env.example`, and the security tests.

**Expected result**

- `.env`, SQLite files, private raw data/screenshots, Playwright state, browser
  profiles, cookies, and session files are ignored.
- `.env.example` contains no credential values.
- No private data or generated database is committed.

**Actual result**

TODO

**Status**

`not_started`

### UAT-006: Documentation is sufficient

**Steps**

Follow the README setup and CLI instructions in a clean Python 3.11+
environment.

**Expected result**

- Installation and test commands are accurate.
- README clearly states that commands are placeholders in Phase 01.
- README states that automatic entry, extra spending, and credential storage are
  outside the application’s allowed behavior.

**Actual result**

TODO

**Status**

`not_started`

## Bug list

| Bug ID | Description | Severity | Status | Notes |
|---|---|---|---|---|
| None | No bugs recorded yet | - | - | - |

## UAT result summary

### Final result

`not_started`

### Summary

TODO after testing.

## Sign-off checklist

- [ ] All automated checks pass.
- [ ] All must-have UAT cases pass.
- [ ] Known issues are documented.
- [ ] Phase plan tasks and statuses are updated.
- [ ] `.planning/STATE.md` records results and the next phase.
