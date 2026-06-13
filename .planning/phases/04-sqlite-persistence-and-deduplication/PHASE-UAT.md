# Phase UAT: 04 SQLite Persistence and Deduplication

## Status

`done`

## Objective

Verify SQLite initialization and deterministic repeated upserts without losing
first-seen evidence or deleting unobserved campaigns.

## Environment

| Item | Value |
|---|---|
| Database | Temporary SQLite files |
| Network/browser | Mocked for CLI integration |
| Test date | 2026-06-14 |
| Tester | Codex |

## Automated verification

```bash
uv run --extra dev pytest
uv run --extra dev ruff check .
uv run --extra dev ruff format --check .
```

## Cases

### UAT-401: Database initialization

Initialize a database in a missing temporary parent directory.

**Expected:** Parent and schema are created on demand; importing modules alone
creates nothing.

**Actual:** A nested temporary parent and complete campaign table were created
only when engine initialization was explicitly invoked.

**Status:** `done`

### UAT-402: URL-first repeat

Insert a campaign, then observe the same canonical URL with changed title,
evidence, and scrape timestamp.

**Expected:** One row remains, first seen is preserved, and latest fields plus
last seen/scraped time are updated.

**Actual:** The canonical URL matched after host/tracking normalization; one row
remained with original first seen and latest title, evidence, and timestamps.

**Status:** `done`

### UAT-403: Fallback repeat and URL upgrade

Repeat a URL-less campaign using whitespace-equivalent title/period values, then
observe it with a canonical URL.

**Expected:** One row remains and its identity upgrades to the URL identity.

**Actual:** Whitespace-equivalent fallback observations remained one row, which
then upgraded to the URL identity without duplication.

**Status:** `done`

### UAT-404: Distinct URL behavior

Insert campaigns with identical title/period but different valid URLs.

**Expected:** Two rows remain because URL identity takes precedence.

**Actual:** Identical title/period observations with two valid URLs produced two
records.

**Status:** `done`

### UAT-405: Atomic batch and no deletion

Persist a batch, then persist only one changed member in a later batch.

**Expected:** The changed member updates, the unobserved row remains, and a
failed transaction never partially commits.

**Actual:** Forced failure on the second batch item rolled back the first.
Later batches did not delete campaigns absent from the observation set.

**Status:** `done`

### UAT-406: Scrape CLI integration

Run `scrape` with a fixture-backed collector and temporary configured database
twice.

**Expected:** First run reports inserts, second reports updates, row count is
stable, and no export is created.

**Actual:** Fixture-backed CLI runs reported one insert then one update against
a temporary database, with a stable row count of one and no export file.

**Status:** `done`

## Final result

`done`

## Summary

All 70 tests and Ruff checks passed on Python 3.12.1. Persistence is atomic,
timezone-safe, conservative about missing evidence, and performs no deletion.
