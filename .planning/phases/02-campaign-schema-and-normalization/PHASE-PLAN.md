# Phase Plan: 02 Campaign Schema and Normalization

## Status

`done`

## Purpose

Define the canonical campaign schema and deterministic normalization functions
used by scraping, persistence, and export without performing network or database
work.

## Goals

- [x] Model complete and sparse campaign observations with Pydantic.
- [x] Preserve Japanese source text while normalizing identity whitespace.
- [x] Parse supported Japanese period formats without inventing uncertain dates.
- [x] Canonicalize campaign URLs and produce URL-first deduplication identities.
- [x] Calculate campaign status from explicit end dates.

## Non-goals

- No live page access, HTML parsing, SQLite, JSON files, or CLI behavior.
- No inferred campaign conditions, financial judgment, or recommendation labels.
- No dates inferred when the text is ambiguous or invalid.

## Requirements

| ID | Requirement | Status |
|---|---|---|
| FR-201 | Campaign schema contains every base field defined by `AGENTS.md` | `done` |
| FR-202 | Required fields are source, source type, title, and timezone-aware scrape timestamp | `done` |
| FR-203 | Normalization trims whitespace, converts full-width spaces, and collapses repeated whitespace while preserving Japanese text | `done` |
| FR-204 | URL canonicalization resolves relative URLs with an optional base, lowercases scheme/host, removes fragments and common tracking parameters, sorts query parameters, and normalizes trailing slashes | `done` |
| FR-205 | Parse `MM/DD〜MM/DD`, fully-year-qualified slash dates, Japanese month/day ranges, and `YYYY年M月D日まで` | `done` |
| FR-206 | A missing year may use an explicit reference date; a year-crossing range may advance the end year only when the end month/day precedes the start | `done` |
| FR-207 | Invalid, partial, or unsupported periods retain original text and return null dates | `done` |
| FR-208 | Identity uses canonical URL first, otherwise normalized title plus normalized visible period text | `done` |
| FR-209 | Status is expired after end date, ending soon within a configurable inclusive window, active otherwise, and unknown without an end date | `done` |

## Technical design

- Add `schemas.py` with string enums and a Pydantic `Campaign` model.
- Add `normalize.py` with pure functions and a small parsed-period value object.
- Require timezone-aware `scraped_at`, `first_seen_at`, and `last_seen_at` values.
- Keep raw strings intact in the campaign model; normalization is applied only
  when building canonical URLs and identities.
- Return a stable identity string prefixed with `url:` or `title_period:`.
- Use `urllib.parse` rather than string manipulation for URL handling.
- Date parsing uses anchored regular expressions and `datetime.date`
  construction; any invalid construction returns null dates.

## Implementation tasks

- [x] Add campaign schema, enums, validation, and serialization tests.
- [x] Add text and URL normalization with identity helpers.
- [x] Add conservative Japanese date parsing and status calculation.
- [x] Cover supported, invalid, uncertain, UTF-8, and year-boundary cases.
- [x] Run pytest and Ruff.
- [x] Complete UAT and synchronize planning state.

## Definition of done

- Complete and sparse campaigns validate and serialize predictably.
- All four required date styles are covered by tests.
- Uncertain dates remain null and raw period text is preserved.
- Both identity strategies are deterministic and tested.
- Status calculation is deterministic for an injected reference date.
- All tests and Ruff checks pass, UAT is recorded, and planning is synchronized.
