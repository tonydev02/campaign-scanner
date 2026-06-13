# Project State: V Point Campaign Scanner

## Current status

- Active phase: `04-sqlite-persistence-and-deduplication`
- Phase status: `not_started`
- Overall status: `in_progress`
- Last updated: 2026-06-14

## Current repository state

Phases 01 through 03 provide the project foundation, canonical campaign domain,
fixture-backed card parser, and a gentle one-page Playwright collector for the
approved public V Point all-campaigns list. Persistence and campaign export
remain unimplemented.

## Active phase objective

Persist normalized campaigns in local SQLite with deterministic URL-first and
title-period fallback upserts.

## Roadmap

| Phase | Name | Status |
|---:|---|---|
| 01 | Project bootstrap | `done` |
| 02 | Campaign schema and normalization | `done` |
| 03 | V Point public list scraping | `done` |
| 04 | SQLite persistence and deduplication | `not_started` |
| 05 | JSON export and summary | `not_started` |
| 06 | Detail page extraction and screenshots | `not_started` |
| 07 | Additional public sources | `not_started` |
| 08 | LLM fact extraction | `not_started` |
| 09 | Conservative campaign labeling | `not_started` |
| 10 | Private Vpass reading | `not_started` |

## Decisions

- Use `https://cpn.tsite.jp/list/all` as the approved V Point public list source.
- Parse its rendered card DOM and optionally enrich from embedded public
  `__NEXT_DATA__`; do not call hidden APIs.
- Preserve semantic SPA fragments such as `#/detail2/<campaign-id>` during URL
  canonicalization because the approved source uses them as campaign routes.
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

- Completed Phase 03 and its six UAT cases with 62 passing tests.
- Approved live UAT collected 51 cards from `https://cpn.tsite.jp/list/all`
  using one Playwright page and created no database or export.
- Added fixture-backed DOM and metadata parsing, safe source errors, CLI list
  collection, and semantic hash-route canonicalization.
- Confirmed the Phase 03 approved source and current server-rendered structure:
  `/list/all` exposed 51 cards in one page on 2026-06-14.
- Expanded Phase 03 parsing, browser safety, failure, CLI, and UAT contracts.
- Completed Phase 02 and its six UAT cases with 46 passing tests.
- Added the canonical campaign schema, conservative Japanese date parsing,
  canonical URL and fallback identities, and date-based status calculation.
- Expanded Phase 02 schema, normalization, date, identity, and UAT contracts and
  started implementation.
- Completed Phase 01 project bootstrap and all six UAT cases.
- Added package metadata, a uv lockfile, CLI placeholders, safe configuration,
  logging, data directory placeholders, security ignore rules, and README setup.
- Added 14 bootstrap tests; pytest and Ruff checks pass on Python 3.12.1.
- Created the ten-phase MVP roadmap.
- Fully specified the Phase 01 implementation and UAT requirements.
- Added provisional planning documents for Phases 02 through 10.

## Next action

Expand Phase 04 persistence and deduplication planning/UAT, then implement it.
