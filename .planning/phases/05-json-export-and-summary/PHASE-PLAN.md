# Phase Plan: 05 JSON Export and Summary

## Status

`done`

## Purpose

Export stored campaigns as clean UTF-8 JSON suitable for manual/ChatGPT review
and provide an accurate, concise database summary through the CLI.

## Goals

- [x] Export a stable JSON envelope and canonical campaign records.
- [x] Support default active and explicit ending-within-days filters.
- [x] Write output atomically without corrupting an existing export.
- [x] Summarize total, source, and date-status counts.
- [x] Fail clearly when the database does not exist or is uninitialized.

## Filter semantics

- Default export includes campaigns whose explicit end date is today or later,
  plus campaigns with unknown end dates; only explicitly expired rows are
  excluded.
- `--ending-within-days N` includes campaigns with an explicit end date from
  today through today + N days, inclusive. Unknown and expired rows are omitted.
- Status is recalculated at export/summary time from the current date so stored
  scrape-time status cannot become stale.
- Output order is end date ascending, null end dates last, then title and ID.

## Requirements

| ID | Requirement | Status |
|---|---|---|
| FR-501 | JSON envelope contains timezone-aware `exported_at`, `source_count`, `campaign_count`, and `campaigns` | `done` |
| FR-502 | Campaign objects follow the canonical schema with JSON dates/datetimes and explicit nulls | `done` |
| FR-503 | UTF-8 output preserves Japanese text with `ensure_ascii=false` | `done` |
| FR-504 | Default export excludes only explicitly expired campaigns | `done` |
| FR-505 | Ending-window filter is inclusive and requires an explicit non-expired end date | `done` |
| FR-506 | Output is deterministically ordered and atomically replaces the target | `done` |
| FR-507 | Default output path is `data/exports/campaigns.json`; explicit output is supported | `done` |
| FR-508 | Summary reports total, source count, active, ending soon, expired, and unknown | `done` |
| FR-509 | Missing/uninitialized database and write failures return clean nonzero CLI errors | `done` |
| FR-510 | Export and summary perform no scraping, LLM judgment, or recommendation | `done` |

## Technical design

- Add `export.py` with filter, ordering, envelope construction, and atomic JSON
  writing. Inject `today` and `exported_at` in tests.
- Use a temporary file in the destination directory, flush/fsync it, and replace
  the target with `os.replace`; remove the temporary file after failure.
- Add read-only database opening and summary helpers to `db.py`.
- `source_count` counts distinct stored source URLs.
- Summary recalculates statuses with the standard seven-day ending-soon window.
- CLI `export` supports JSON only and uses configured default paths.

## Tasks

- [x] Implement read-only database validation and summary calculation.
- [x] Implement filtering, ordering, envelope serialization, and atomic writing.
- [x] Replace export and summary placeholders with real commands.
- [x] Add export shape, Japanese, null, filter, ordering, and error tests.
- [x] Add CLI UAT with a temporary seeded database.
- [x] Run pytest/Ruff and synchronize planning.

## Definition of done

- Default and ending-window exports produce valid UTF-8 JSON at expected paths.
- Envelope counts and campaign contents are accurate and deterministic.
- Existing output cannot be partially overwritten by a failed write.
- Summary counts reflect the current date.
- Missing databases fail without creating new empty databases or exports.
- Tests, Ruff, UAT, and planning synchronization pass.
