# Phase UAT: 02 Campaign Schema and Normalization

## Status

`done`

## Objective

Verify schema validation, Japanese date parsing, normalization, campaign status,
and both deduplication identity strategies without live website access.

## Environment

| Item | Value |
|---|---|
| Python | 3.11+ |
| Network/browser | Not used |
| Database | Not used |
| Test date | 2026-06-14 |
| Tester | Codex |

## Automated verification

```bash
uv run --extra dev pytest
uv run --extra dev ruff check .
uv run --extra dev ruff format --check .
```

## Cases

### UAT-201: Campaign schema

Validate a complete Japanese campaign and a sparse campaign, then reject an
invalid source type or naive scrape timestamp.

**Expected:** Supported records serialize to JSON-compatible values with nulls
preserved; invalid enum values and timezone-naive timestamps fail clearly.

**Actual:** Complete and sparse records validated and serialized. Invalid source
types, blank required text, and timezone-naive timestamps were rejected.

**Status:** `done`

### UAT-202: Date parsing

Exercise every documented date format, invalid dates, unsupported partial text,
and a year-crossing range with an explicit reference date.

**Expected:** Supported dates parse exactly; uncertain or invalid dates are
null; no date is invented.

**Actual:** All documented styles and a year-crossing range parsed exactly.
Unsupported, partial, year-ambiguous, and invalid calendar dates stayed null.

**Status:** `done`

### UAT-203: Japanese text normalization

Normalize leading/trailing whitespace, full-width spaces, tabs, and repeated
spaces in Japanese text.

**Expected:** Whitespace is normalized while Japanese characters are unchanged.

**Actual:** Full-width spaces, tabs, line breaks, and repeated spaces normalized
without changing Japanese characters.

**Status:** `done`

### UAT-204: URL-first identity

Compare absolute and relative variants containing fragments, tracking
parameters, query ordering, host case, and trailing slashes.

**Expected:** Equivalent URLs produce one stable `url:` identity.

**Actual:** Relative and absolute variants canonicalized to one URL after
fragment/tracking removal, query sorting, host casing, and slash normalization.

**Status:** `done`

### UAT-205: Title-period fallback identity

Build identities for URL-less campaigns whose title and period differ only in
whitespace.

**Expected:** Equivalent title/period pairs produce one stable fallback key;
missing title is rejected.

**Actual:** Whitespace-equivalent title/period pairs produced one fallback key;
a blank title without a valid URL raised a validation error.

**Status:** `done`

### UAT-206: Status calculation

Calculate status before, near, and after an explicit end date and without an end
date.

**Expected:** Results are `active`, `ending_soon`, `expired`, and `unknown` at
the documented boundaries.

**Actual:** Unknown, expired, inclusive seven-day ending-soon, and active
boundaries matched the contract.

**Status:** `done`

## Final result

`done`

## Summary

All 46 tests passed on Python 3.12.1. Ruff lint and formatting checks passed.
No network, browser, database, or file export activity occurred.
