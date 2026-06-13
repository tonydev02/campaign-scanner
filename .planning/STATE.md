# Project State: V Point Campaign Scanner

## Current status

- Active phase: `01-project-bootstrap`
- Phase status: `not_started`
- Overall status: `not_started`
- Last updated: 2026-06-14

## Current repository state

The repository currently contains `AGENTS.md`, the planning system, and phase
templates. Application code, package metadata, tests, and runtime data
directories have not been created yet.

## Active phase objective

Establish a safe, testable Python 3.11+ project foundation with package
metadata, a CLI shell, configuration defaults, logging, repository directories,
and protections against committing credentials or private financial data.

## Roadmap

| Phase | Name | Status |
|---:|---|---|
| 01 | Project bootstrap | `not_started` |
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
  Playwright for browser automation, and SQLAlchemy or SQLModel for SQLite.
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

- Created the ten-phase MVP roadmap.
- Fully specified the Phase 01 implementation and UAT requirements.
- Added provisional planning documents for Phases 02 through 10.

## Next action

Implement and verify `01-project-bootstrap` according to its phase plan and UAT
document. Before implementation starts, change the active phase status to
`in_progress`.
