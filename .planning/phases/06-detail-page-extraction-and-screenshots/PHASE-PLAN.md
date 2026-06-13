# Phase Plan: 06 Detail Page Extraction and Screenshots

## Status

`done`

## Purpose

Enrich eligible same-origin public campaigns from detail pages and optionally
preserve public screenshots without interacting with entry/application controls.

## Approved scope and observed structure

- Eligible detail URLs: HTTPS host `cpn.tsite.jp`, path prefix `/detail/`.
- External campaign sites and hash-routed lottery/game apps are never traversed.
- Confirmed 2026-06-14 detail structure includes `.contents`, `.info`,
  `.warning-text`, `.info-one__title`, `.info-one__text`, and inert
  `[data-dynbtn]` entry images.
- One inspected public detail returned HTTP 200 and server-rendered evidence.

## Goals

- [x] Visit eligible detail pages sequentially in the existing browser context.
- [x] Wait 1–3 seconds between detail requests.
- [x] Preserve card evidence plus raw detail text and a detail HTML SHA-256 hash.
- [x] Conservatively extract explicit entry, reward, payment, spend, and
  exclusion facts from visible text.
- [x] Save full-page screenshots only when explicitly requested.
- [x] Retain and persist card-level campaigns when detail enrichment fails.

## Non-goals

- No third-party detail scraping, login, private pages, cookies, or profiles.
- No clicks on entry, application, login, payment, or navigation controls.
- No CAPTCHA/2FA handling or access-control bypass.
- No OCR or extraction of conditions that exist only inside images.
- No LLM interpretation, scoring, recommendation, or automated action.

## Requirements

| ID | Requirement | Status |
|---|---|---|
| FR-601 | Eligibility requires HTTPS `cpn.tsite.jp/detail/...`; all other URLs are skipped | `done` |
| FR-602 | Reuse the one Phase 03 context/page and navigate detail URLs one at a time | `done` |
| FR-603 | Apply configured 1–3 second delay between detail requests, not before the first | `done` |
| FR-604 | Parse visible detail content and preserve normalized raw detail text | `done` |
| FR-605 | Store combined labeled card/detail text and SHA-256 of detail HTML | `done` |
| FR-606 | Infer structured fields only from explicit visible text; uncertain values remain null | `done` |
| FR-607 | Screenshot filenames are sanitized/deterministic, stored under public screenshots, and only created with `--screenshots` | `done` |
| FR-608 | Detail navigation never invokes click/fill/submit methods | `done` |
| FR-609 | Individual detail failures retain card data and continue; blocked/rate-limited responses stop further detail requests | `done` |
| FR-610 | Enriched campaigns and screenshot paths are upserted through Phase 04 persistence | `done` |
| FR-611 | CLI reports collected, enriched, skipped, failed, screenshot, inserted, and updated counts | `done` |

## Technical design

- Add `parsers/campaign_detail.py` with a pure `enrich_campaign_from_detail`
  function and explicit section extraction.
- Combine evidence as `[CARD]\n...\n\n[DETAIL]\n...`; never discard card text.
- Extract `requires_entry` from explicit entry wording/control presence;
  `entry_text` and `reward_text` from visible warning/sections; reward type from
  explicit lottery/multiplier/coupon/guaranteed terms; maximum points and
  minimum spend from numeric text; payment/store/exclusions from matching text.
- Add detail eligibility, sequential enrichment, delay injection, safe loading,
  screenshot naming, and blocked-stop behavior to the V Point source adapter.
- Use configured `detail_delay_seconds=1.5` and public screenshot directory.
- Browser interactions are limited to `goto`, `wait_for_selector`, `content`,
  and optional `screenshot`.

## Failure and evidence behavior

- Navigation/parser/screenshot failure logs a warning and leaves the original
  card observation available for persistence.
- HTTP 401/403/429 stops detail traversal immediately and reports remaining
  eligible campaigns as unprocessed.
- Screenshots are never saved for external/private pages.
- Existing non-null detail evidence is not erased by a later failed scrape due
  to Phase 04 conservative merging.

## Tasks

- [x] Add representative detail fixtures and pure parser tests.
- [x] Implement eligibility, sequential traversal, delay, and blocked-stop flow.
- [x] Implement optional public screenshot capture and path persistence.
- [x] Integrate detail enrichment and counts into scrape CLI.
- [x] Test no-click behavior, external skips, failure retention, and screenshots.
- [x] Run one approved live UAT with temporary database/screenshots.
- [x] Run pytest/Ruff and synchronize planning.

## Definition of done

- Eligible fixture/live details enrich card records with raw evidence and hashes.
- External URLs are not visited.
- Detail failures never lose card records or prior stored evidence.
- Requested public screenshots are saved and unrequested screenshots are absent.
- Request delay and no-click behavior are verified.
- Tests, Ruff, live UAT, and planning synchronization pass.
