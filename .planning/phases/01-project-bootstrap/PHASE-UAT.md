# Phase UAT: 01 Project Bootstrap

## Status

`done`

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
| OS | macOS |
| Python version | 3.12.1 |
| Browser | Not used in this phase |
| Database | Not created in this phase |
| Test date | 2026-06-14 |
| Tester | Codex |

## Preconditions

- [x] Python 3.11 or newer is installed.
- [x] Project and development dependencies are installed.
- [x] No real `.env`, credentials, cookies, or browser profile is needed.
- [x] The working tree contains no private financial data.

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

Package import returned version `0.1.0`; root help loaded successfully and
listed all three commands. No network or browser activity occurred.

**Status**

`done`

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

All subcommand help screens loaded. Scrape and export displayed every required
future option, and summary required no arguments.

**Status**

`done`

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

All placeholders exited with code 0 and explicitly reported that no campaigns
were processed and no external action was taken. No database or export appeared.

**Status**

`done`

### UAT-004: Conservative defaults

**Steps**

Inspect the documented configuration and run its automated tests.

**Expected result**

- Extra spending allowed is `0`.
- Automatic campaign entry is disabled.
- New credit card applications are disabled.
- Default paths remain inside the local `data` directory.

**Actual result**

Automated tests confirmed zero extra spending, disabled automatic entry,
disabled new-card applications, and repository-local default data paths.

**Status**

`done`

### UAT-005: Sensitive artifacts are protected

**Steps**

Review `.gitignore`, `.env.example`, and the security tests.

**Expected result**

- `.env`, SQLite files, private raw data/screenshots, Playwright state, browser
  profiles, cookies, and session files are ignored.
- `.env.example` contains no credential values.
- No private data or generated database is committed.

**Actual result**

Ignore rules were checked with both automated tests and `git check-ignore`.
The example environment file contains path examples only and no secrets.

**Status**

`done`

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

README setup and CLI commands were exercised with uv. It documents the Phase 01
placeholder boundary and prohibited credential, spending, and entry behavior.

**Status**

`done`

## Bug list

| Bug ID | Description | Severity | Status | Notes |
|---|---|---|---|---|
| None | No bugs recorded yet | - | - | - |

## UAT result summary

### Final result

`done`

### Summary

All 14 tests passed. Ruff lint and format checks passed. All six UAT cases
passed with no known bugs and no scraping, browser, database, or export side
effects.

## Sign-off checklist

- [x] All automated checks pass.
- [x] All must-have UAT cases pass.
- [x] Known issues are documented.
- [x] Phase plan tasks and statuses are updated.
- [x] `.planning/STATE.md` records results and the next phase.
