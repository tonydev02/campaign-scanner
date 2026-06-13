# Phase Plan: 02 Campaign Schema and Normalization

## Status

`not_started`

## Purpose

Define the canonical campaign schema, Japanese text normalization, conservative
date parsing, status calculation, and deduplication keys used by later phases.

## Provisional scope

- Pydantic campaign and related value types.
- Date parsing for formats required by `AGENTS.md`.
- Canonical URL and title/period fallback identity rules.
- Fixture-based unit tests, including uncertain dates and UTF-8 text.

## Before implementation

Expand requirements, technical design, tasks, definition of done, and UAT
criteria. Update `.planning/STATE.md` before making code changes.
