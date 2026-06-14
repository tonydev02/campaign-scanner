# Project State: V Point Campaign Scanner

## Current status

- Active phase: `07-review-ready-exports`
- Phase status: `done`
- Overall status: `in_progress`
- Last updated: 2026-06-14

## Current repository state

Phases 01 through 06 provide the project foundation, canonical domain, gentle
public list/detail collection, conservative fact extraction, optional public
screenshots, atomic SQLite upsert, UTF-8 JSON export, and current-date summary.

## Active phase objective

Make JSON exports concise and explainable for LLM review while preserving full
campaign evidence and conservative scanner behavior.

## Roadmap

| Phase | Name | Status |
|---:|---|---|
| 01 | Project bootstrap | `done` |
| 02 | Campaign schema and normalization | `done` |
| 03 | V Point public list scraping | `done` |
| 04 | SQLite persistence and deduplication | `done` |
| 05 | JSON export and summary | `done` |
| 06 | Detail page extraction and screenshots | `done` |
| 07 | Review-ready exports | `done` |
| 07A | Additional public sources | `not_started` |
| 08 | LLM fact extraction | `not_started` |
| 09 | Conservative campaign labeling | `not_started` |
| 10 | Private Vpass reading | `not_started` |

## Decisions

- Reprioritize Phase 07 from additional sources to review-ready export quality;
  additional public sources move to a later separately approved phase.
- Provide explicit compact and full JSON profiles; compact output omits nulls
  and bounds raw evidence while full output preserves canonical evidence.
- Apply additive campaign-column migrations when opening an existing database
  so export and summary work immediately after an upgrade.
- Keep detail-section map persistence outside Phase 07.
- Phase 06 automatically traverses only HTTPS `cpn.tsite.jp/detail/...` pages;
  third-party and hash-routed destinations are preserved but never opened.
- Detail evidence combines labeled card/detail text and stores a SHA-256 hash;
  no OCR is attempted for image-only terms.
- Use a 1.5-second delay between sequential same-origin detail requests.
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

- Completed Phase 07 and its six UAT scenarios with 98 passing tests.
- Added compact/full export profiles, bounded evidence previews, detail outcome
  metadata, conservative visible-text facts, and additive SQLite migrations.
- Verified both profiles against the existing 51-campaign database; compact
  output was 63,289 bytes versus 107,772 bytes for full output.
- Re-scoped Phase 07 around detail outcome tracking, conservative title facts,
  and compact/full JSON exports based on review of the successful MVP output.
- Completed Phase 06 and its six UAT cases with 86 passing tests.
- Approved live UAT persisted 51 cards, enriched 4 same-origin details, skipped
  47 destinations, failed 0, and saved 4 public screenshots under `/tmp`.
- Added conservative visible-text fact extraction, combined evidence hashes,
  one-page delayed detail traversal, blocked-stop behavior, and screenshot paths.
- Inspected a same-origin public detail page and expanded Phase 06 eligibility,
  extraction, evidence, delay, screenshot, failure, and UAT contracts.
- Completed Phase 05 and its six UAT cases with 77 passing tests.
- Added deterministic current-date export filters, atomic UTF-8 JSON writing,
  read-only database validation, and CLI summary counts.
- Expanded Phase 05 current-date filters, JSON envelope, atomic write, summary,
  CLI error, and UAT contracts and started implementation.
- Completed Phase 04 and its six UAT cases with 70 passing tests.
- Added full SQLAlchemy schema mapping, timezone-safe SQLite timestamps, atomic
  bulk upsert, URL/fallback identity upgrade, and scrape CLI persistence.
- Expanded Phase 04 schema mapping, identity upgrade, transaction, CLI, and UAT
  contracts and started implementation.
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

Choose whether to add another approved public source or proceed to optional LLM
fact extraction.
