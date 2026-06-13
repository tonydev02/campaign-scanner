# Phase UAT: 03 V Point Public List Scraping

## Status

`done`

## Objective

Verify complete fixture-backed card extraction and one gentle approved live
collection without detail navigation, persistence, or private access.

## Environment

| Item | Value |
|---|---|
| Approved URL | `https://cpn.tsite.jp/list/all` |
| Confirmed structure | 2026-06-14 |
| Browser | Playwright Chromium |
| Database/export | Must not be created |
| Test date | 2026-06-14 |
| Tester | Codex |

## Automated verification

```bash
uv run --extra dev pytest
uv run --extra dev ruff check .
uv run --extra dev ruff format --check .
```

## Cases

### UAT-301: Fixture card completeness

Parse the saved list fixture.

**Expected:** Every `.list-item` yields one campaign in document order with
title, URL, image, visible period, and raw text.

**Actual:** Both fixture cards were returned in document order with all required
fields, relative URL resolution, and raw Japanese card text.

**Status:** `done`

### UAT-302: Structured metadata enrichment

Parse cards with valid, missing, and malformed `__NEXT_DATA__`.

**Expected:** Explicit years and entry flags are used when available; card
records are retained when metadata is unavailable.

**Actual:** Valid metadata supplied explicit 2026 dates and the entry flag.
Malformed metadata retained the card and conservatively parsed its visible date.

**Status:** `done`

### UAT-303: Safe browser flow

Run the collector with a fake Playwright page that records actions.

**Expected:** Exactly one listing navigation and card wait occur; no campaign
link, detail control, entry control, or application control is clicked.

**Actual:** The fake page recorded one `goto`, one card wait, and one content
read. No click method or campaign navigation was invoked.

**Status:** `done`

### UAT-304: Failure handling

Exercise navigation failure, blocked HTTP status, unsupported source, and an
empty rendered page.

**Expected:** Each exits nonzero with an actionable message and no traceback or
false campaign count.

**Actual:** Blocked and error statuses, empty pages, malformed cards, source
errors, and unsupported source names produced clean actionable failures.

**Status:** `done`

### UAT-305: Approved live collection

```bash
uv run python -m vpoint_scanner scrape --source vpoint_public
```

**Expected:** The command reads `https://cpn.tsite.jp/list/all`, reports at
least one campaign, and creates no database or export.

**Actual:** Headless Chromium collected all 51 cards rendered by the approved
page on 2026-06-14. No database or export file was created.

**Status:** `done`

### UAT-306: Screenshot boundary

```bash
uv run python -m vpoint_scanner scrape --source vpoint_public --screenshots
```

**Expected:** The command clearly reports that screenshot capture is introduced
in Phase 06; it does not claim a screenshot was saved.

**Actual:** CLI coverage confirmed the Phase 06 boundary message and no false
screenshot claim; the live page was not fetched a second unnecessary time.

**Status:** `done`

## Final result

`done`

## Summary

All 62 tests and Ruff checks passed on Python 3.12.1. The approved live UAT
collected 51 campaigns with one page and no detail or entry interaction.
