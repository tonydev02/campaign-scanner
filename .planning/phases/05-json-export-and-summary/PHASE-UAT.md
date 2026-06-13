# Phase UAT: 05 JSON Export and Summary

## Status

`done`

## Objective

Verify clean UTF-8 JSON exports, inclusive ending-window filtering, atomic file
behavior, and accurate current-date CLI summaries.

## Environment

| Item | Value |
|---|---|
| Database | Seeded temporary SQLite |
| Network/browser | Not used |
| Test date | 2026-06-14 |
| Tester | Codex |

## Automated verification

```bash
uv run --extra dev pytest
uv run --extra dev ruff check .
uv run --extra dev ruff format --check .
```

## Cases

### UAT-501: Default export

Seed active, ending-soon, expired, and unknown-date campaigns and export without
a window.

**Expected:** Expired is excluded; active, ending-soon, and unknown are present
in deterministic order.

**Actual:** Active, ending-soon, and unknown-date records were exported in the
documented order; the explicitly expired record was excluded.

**Status:** `done`

### UAT-502: Ending-window export

Export with 0-day and 7-day windows around an injected current date.

**Expected:** Boundaries are inclusive; unknown and expired records are omitted.

**Actual:** Zero-day included today's deadline, seven-day excluded day eight,
and eight-day included it. Unknown and expired rows were omitted.

**Status:** `done`

### UAT-503: JSON shape and UTF-8

Read the output as UTF-8 and validate the envelope and campaign records.

**Expected:** Counts, ISO dates/timestamps, explicit nulls, and Japanese titles
are preserved without ASCII escaping.

**Actual:** The envelope, counts, ISO values, nulls, and Japanese evidence
validated after UTF-8 JSON parsing without Unicode escape output.

**Status:** `done`

### UAT-504: Atomic output

Replace an existing export and simulate a write/replace failure.

**Expected:** Successful output replaces atomically; failed output leaves the
existing file intact and removes temporary artifacts.

**Actual:** Atomic replacement succeeded normally. A forced replace failure left
the prior file unchanged and removed the temporary artifact.

**Status:** `done`

### UAT-505: Summary

Run summary against the seeded database.

**Expected:** Total, sources, active, ending soon, expired, and unknown counts
match current-date calculation.

**Actual:** Current-date recalculation produced one active, ending-soon,
expired, and unknown record with correct total/source counts.

**Status:** `done`

### UAT-506: CLI paths and errors

Run export with default/explicit paths, then run export and summary against a
missing database.

**Expected:** Valid paths succeed; missing database exits nonzero without
creating a database or export.

**Actual:** Seeded CLI export used the default output and summary reported
expected counts. Explicit paths were covered; missing database created nothing.

**Status:** `done`

## Final result

`done`

## Summary

All 77 tests and Ruff checks passed on Python 3.12.1. Export and summary made no
network/browser calls and applied no campaign judgment or recommendation.
