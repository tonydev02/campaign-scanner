# Phase UAT: 06 Detail Page Extraction and Screenshots

## Status

`done`

## Objective

Verify safe same-origin detail enrichment, evidence preservation, optional
public screenshots, delays, and card retention on failure.

## Environment

| Item | Value |
|---|---|
| List URL | `https://cpn.tsite.jp/list/all` |
| Eligible detail scope | `https://cpn.tsite.jp/detail/...` |
| Browser | Playwright Chromium, one context/page |
| Live storage | Temporary database and screenshot directory |
| Test date | 2026-06-14 |
| Tester | Codex |

## Automated verification

```bash
uv run --extra dev pytest
uv run --extra dev ruff check .
uv run --extra dev ruff format --check .
```

## Cases

### UAT-601: Detail fixture extraction

Enrich a card from a saved same-origin detail fixture.

**Expected:** Card evidence remains, detail evidence and SHA-256 are added, and
only explicit entry/reward/payment/spend/exclusion facts are populated.

**Actual:** Fixture enrichment retained labeled card evidence, added visible
detail text and SHA-256, and extracted only explicit entry/reward/payment/spend
and exclusion facts. A coupon value regression was confirmed not to become
minimum spend.

**Status:** `done`

### UAT-602: Eligibility and no-click traversal

Provide same-origin, external, hash-route, missing, and invalid URLs to a fake
page that records actions.

**Expected:** Only same-origin `/detail/` URLs are navigated; actions contain no
click, fill, submit, or entry interaction.

**Actual:** Eligibility accepted only HTTPS same-origin detail paths. Fake-page
actions contained only navigation, selector waits, content, and screenshots.

**Status:** `done`

### UAT-603: Delay and one-page behavior

Enrich multiple eligible campaigns with injected sleep recording.

**Expected:** One page is reused; delay occurs only between requests and remains
within the configured 1–3 second policy.

**Actual:** One fake page was reused for two eligible details, with exactly one
1.5-second delay between requests and none before the first.

**Status:** `done`

### UAT-604: Failure and blocked handling

Fail one detail normally, then simulate HTTP 429.

**Expected:** Normal failure retains the card and continues. Blocking retains
all cards and stops further detail navigation with a reported failure count.

**Actual:** HTTP 500 retained its card and continued; HTTP 429 retained all
remaining cards and stopped further detail navigation with correct failures.

**Status:** `done`

### UAT-605: Optional public screenshots

Run fake and approved live enrichment with screenshots disabled/enabled.

**Expected:** No file/call when disabled; enabled same-origin details save
sanitized full-page screenshots under the configured public directory.

**Actual:** Disabled mode made no screenshot call. Enabled fake/live modes saved
sanitized full-page public PNGs; one live image was visually checked as public
campaign content without account data.

**Status:** `done`

### UAT-606: Approved live end-to-end scrape

Run one scrape with `--screenshots`, temporary database, and temporary
screenshots against the approved list.

**Expected:** 51 list cards are preserved; eligible same-origin details are
enriched sequentially, public screenshots are saved, external URLs are skipped,
and export/entry/application actions do not occur.

**Actual:** One approved run collected/persisted 51 cards, enriched 4 eligible
same-origin details, skipped 47 destinations, failed 0, and saved 4 screenshots
under `/tmp`. SQLite confirmed 51 rows, 4 hashes, and 4 screenshot paths.

**Status:** `done`

## Final result

`done`

## Summary

All 86 tests and Ruff checks passed on Python 3.12.1. The approved live run used
one context/page, polite delays, temporary storage, no clicks, and no private or
third-party traversal.
