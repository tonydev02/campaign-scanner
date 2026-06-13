# Phase Plan: <PHASE_NAME>

## Status

`not_started`

Allowed status values:

- `not_started`
- `in_progress`
- `blocked`
- `ready_for_uat`
- `uat_failed`
- `done`

## Phase summary

Describe this phase in 2–5 sentences.

Example:

> This phase implements public V Point campaign list scraping. The scraper opens the public campaign page, extracts visible campaign cards, normalizes basic fields, and stores raw extracted data for later export.

## Background

Why this phase exists.

Include links, screenshots, prior decisions, or context if useful.

## Goals

- [ ] Goal 1
- [ ] Goal 2
- [ ] Goal 3

## Non-goals

Things that should not be implemented in this phase.

- Do not implement automatic campaign entry.
- Do not implement private Vpass login.
- Do not implement final financial recommendation logic.
- Do not overbuild UI unless explicitly required.

## Scope

### In scope

- Feature 1
- Feature 2
- Feature 3

### Out of scope

- Feature A
- Feature B
- Feature C

## Requirements

### Functional requirements

| ID | Requirement | Priority | Status |
|---|---|---:|---|
| FR-001 | Describe requirement | Must | not_started |
| FR-002 | Describe requirement | Should | not_started |
| FR-003 | Describe requirement | Could | not_started |

### Non-functional requirements

| ID | Requirement | Priority | Status |
|---|---|---:|---|
| NFR-001 | Must preserve Japanese text as UTF-8 | Must | not_started |
| NFR-002 | Must not store passwords or session cookies in git | Must | not_started |
| NFR-003 | Must handle parser failure without losing raw text | Must | not_started |

## Technical design

### Expected files to create or modify

```text
src/
  vpoint_scanner/
    ...
tests/
  ...