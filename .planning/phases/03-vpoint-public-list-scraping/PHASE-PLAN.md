# Phase Plan: 03 V Point Public List Scraping

## Status

`done`

## Purpose

Collect every card from the approved public V Point campaign list with one
Playwright page, preserve card evidence, and return normalized campaign objects
without persistence or detail-page traversal.

## Approved source and observed structure

- Source: `https://cpn.tsite.jp/list/all`
- Confirmed: 2026-06-14
- The `すべて` route server-rendered 51 `.list-item` cards in one response.
- Card selectors:
  `.list-item__contents__text`, `.list-item__contents__date`,
  `.list-item__img a`, `.list-item__img img`, and `.t-button`.
- Public `#__NEXT_DATA__` contains matching campaign IDs, explicit start/end
  years, entry type, and external URLs.
- No pagination or tab interaction was present.
- `/robots.txt` redirected to the listing rather than serving robot rules.

## Goals

- [x] Parse saved representative HTML fixtures into canonical campaigns.
- [x] Use one Playwright browser context and page for live collection.
- [x] Prefer `/list/all` directly and never click campaign/entry controls.
- [x] Preserve title, URL, image, visible period, raw card text, and timestamps.
- [x] Use embedded public metadata for explicit dates and entry flags.
- [x] Fail clearly on blocked/network/empty-page conditions.

## Non-goals

- No detail-page visits, external campaign navigation, SQLite, or JSON export.
- No login, cookies, private pages, CAPTCHA handling, entry, or application.
- No hidden API calls or repeated per-card requests.
- Screenshots remain deferred to Phase 06.

## Requirements

| ID | Requirement | Status |
|---|---|---|
| FR-301 | Parse every `.list-item` card in document order | `done` |
| FR-302 | Resolve relative detail/image URLs against the listing URL | `done` |
| FR-303 | Preserve visible period and normalized raw card text | `done` |
| FR-304 | Match `__NEXT_DATA__` metadata by campaign ID when available and retain card data when it is absent/malformed | `done` |
| FR-305 | Produce canonical `Campaign` objects with source type `vpoint_public` | `done` |
| FR-306 | Playwright waits for cards, loads one page only, and closes resources | `done` |
| FR-307 | Unsupported source names, navigation errors, blocked responses, and zero-card pages return actionable failures | `done` |
| FR-308 | `scrape --source vpoint_public` prints an honest collection summary without writing a database or export | `done` |
| FR-309 | `--screenshots` reports that screenshot capture begins in Phase 06 rather than silently ignoring the option | `done` |

## Technical design

- Add `parsers/campaign_card.py` using selectolax for deterministic HTML parsing.
- Add `sources/base.py` with source errors and protocol, and
  `sources/vpoint_public.py` with the approved URL and Playwright collector.
- Parse the rendered card DOM first. Parse `__NEXT_DATA__` with `json.loads`;
  metadata enrichment is optional and never replaces card evidence.
- Derive campaign IDs from `/detail/<id>`, `/detail2/<id>`, or image content
  paths. Use explicit metadata dates when valid; otherwise use Phase 02 period
  parsing with the scrape date as fallback.
- Infer `requires_entry` only from explicit metadata entry type `1`; otherwise
  leave it null.
- The CLI performs no persistence and prints count/source/title lines.
- Add selectolax as a runtime dependency.

## Tasks

- [x] Add representative list fixtures, including relative and external links.
- [x] Implement robust card and metadata parsing.
- [x] Implement Playwright source collection and source dispatch.
- [x] Replace the scrape placeholder with the Phase 03 command.
- [x] Test parser completeness, malformed metadata, failures, and no-click flow.
- [x] Run one approved live UAT against `/list/all`.
- [x] Run pytest/Ruff and synchronize planning.

## Definition of done

- Fixture parsing extracts every card and required field.
- Live `scrape --source vpoint_public` reports at least one campaign from the
  approved public all-campaigns route.
- The collector uses one page and makes no detail-page or entry interaction.
- Failures are actionable and card evidence survives optional metadata failure.
- No database or campaign export is created.
- Tests, Ruff, UAT, and planning synchronization pass.
