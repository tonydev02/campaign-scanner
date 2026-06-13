# Project State: V Point Campaign Scanner

## Current status

- Active phase: `02-campaign-schema-and-normalization`
- Phase status: `not_started`
- Overall status: `in_progress`
- Last updated: 2026-06-14

## Current repository state

Phase 01 provides an installable Python 3.11+ package, a Typer CLI shell,
Pydantic-backed safe configuration, idempotent logging, protected data
directories, dependency locking, and bootstrap tests. Scraping, persistence,
and campaign export behavior remain intentionally unimplemented.

## Active phase objective

Define the campaign schema and normalization behavior required by later
scraping, persistence, and export phases.

## Roadmap

| Phase | Name | Status |
|---:|---|---|
| 01 | Project bootstrap | `done` |
| 02 | Campaign schema and normalization | `not_started` |
| 03 | V Point public list scraping | `not_started` |
| 04 | SQLite persistence and deduplication | `not_started` |
| 05 | JSON export and summary | `not_started` |
| 06 | Detail page extraction and screenshots | `not_started` |
| 07 | Additional public sources | `not_started` |
| 08 | LLM fact extraction | `not_started` |
| 09 | Conservative campaign labeling | `not_started` |
| 10 | Private Vpass reading | `not_started` |

## Decisions

- Use Python 3.11+ and a `src/vpoint_scanner` package layout.
- Use Typer for the CLI, Pydantic for external schemas and configuration,
  Playwright for browser automation, and SQLAlchemy for SQLite.
- Use uv with a committed lockfile for reproducible local development.
- Use pytest for tests and Ruff for linting and formatting.
- Preserve Japanese source text as UTF-8 and retain raw evidence when parsing
  is incomplete.
- Treat campaign extraction as separate from financial judgment.
- Never automate campaign entry, spending, credit applications, CAPTCHA/2FA
  bypass, or credential collection.
- Default policy remains: no extra spending, no automatic entry, and no new
  credit card applications.
- Keep dashboard, email ingestion, and other optional interfaces outside the
  MVP roadmap.

## Open questions

None.

## Blockers

None.

## Recent changes

- Completed Phase 01 project bootstrap and all six UAT cases.
- Added package metadata, a uv lockfile, CLI placeholders, safe configuration,
  logging, data directory placeholders, security ignore rules, and README setup.
- Added 14 bootstrap tests; pytest and Ruff checks pass on Python 3.12.1.
- Created the ten-phase MVP roadmap.
- Fully specified the Phase 01 implementation and UAT requirements.
- Added provisional planning documents for Phases 02 through 10.

## Next action

Review and begin `02-campaign-schema-and-normalization` according to its phase
plan and UAT document.
