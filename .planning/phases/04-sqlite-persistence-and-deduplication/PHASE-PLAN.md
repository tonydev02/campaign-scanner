# Phase Plan: 04 SQLite Persistence and Deduplication

## Status

`done`

## Purpose

Persist canonical campaigns in local SQLite with deterministic upsert behavior,
evidence preservation, and no automatic deletion.

## Goals

- [x] Map the complete campaign schema to one SQLAlchemy table.
- [x] Initialize a repository-local SQLite database on demand.
- [x] Deduplicate by canonical URL first and title-period fallback when needed.
- [x] Preserve first-seen time while updating latest fields and evidence.
- [x] Persist Phase 03 scrape results through the CLI.

## Non-goals

- No Alembic migrations, remote database, export, summary, or detail enrichment.
- No deletion of unseen/expired campaigns.
- No automatic campaign entry or financial recommendation behavior.

## Requirements

| ID | Requirement | Status |
|---|---|---|
| FR-401 | SQLAlchemy table stores all canonical campaign fields plus canonical URL, fallback key, and identity key | `done` |
| FR-402 | Database initialization creates parent directories and tables only when invoked | `done` |
| FR-403 | Canonical URL is the primary lookup when an observation has a valid URL | `done` |
| FR-404 | URL-less observations use normalized title-period fallback; a prior URL-less row may be upgraded when a URL appears | `done` |
| FR-405 | Different non-null canonical URLs remain distinct even when title and period match | `done` |
| FR-406 | First insert sets first seen, last seen, and scraped timestamps from the observation | `done` |
| FR-407 | Repeat observations preserve first seen, update last seen/scraped time, changed structured fields, and latest raw evidence | `done` |
| FR-408 | Bulk upsert is atomic and returns inserted/updated counts | `done` |
| FR-409 | Scrape CLI initializes SQLite and persists all collected cards | `done` |
| FR-410 | No campaign is deleted automatically | `done` |

## Technical design

- Add `models.py` with SQLAlchemy 2 declarative `CampaignRecord`.
- Store enums as their string values and use a UTC ISO datetime type decorator
  because SQLite does not preserve timezone information natively.
- Store `canonical_url` as nullable unique, `fallback_key` as indexed, and
  `identity_key` as unique. URL-bearing rows use `url:` identity; URL-less rows
  use `title_period:` identity.
- For a new URL, only upgrade a fallback match whose canonical URL is null.
- For a URL-less observation, reuse a fallback only when it identifies exactly
  one row; otherwise create/retain the explicit fallback identity.
- Add `db.py` for engine creation, table initialization, record/domain mapping,
  single and bulk upsert, and count retrieval for tests.
- `create_all` is the MVP migration policy; schema migrations are deferred.
- The CLI creates the configured database only after collection succeeds.

## Transaction and error behavior

- Bulk upsert uses one `Session.begin()` transaction.
- Any database exception rolls back the whole batch and surfaces a clean CLI
  failure without claiming records were saved.
- Parent directory creation and SQLite initialization errors identify the path.
- Persistence never deletes rows that were not observed.

## Tasks

- [x] Implement ORM mapping and timezone-safe timestamp storage.
- [x] Implement engine/table initialization and domain conversion.
- [x] Implement URL-first/fallback upsert and bulk transaction.
- [x] Integrate persistence into `scrape`.
- [x] Test inserts, repeats, upgrades, distinct URLs, rollback, and no deletion.
- [x] Run CLI integration UAT against a temporary database.
- [x] Run pytest/Ruff and synchronize planning.

## Definition of done

- A scrape result can be persisted to SQLite.
- Repeating the same observations does not increase row count.
- First-seen timestamps survive updates and latest evidence replaces old data.
- URL-first and fallback rules behave deterministically.
- Unseen campaigns remain stored.
- Tests, Ruff, UAT, and planning synchronization pass.
