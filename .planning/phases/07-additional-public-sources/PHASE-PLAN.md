# Phase Plan: 07 Additional Public Sources

## Status

`not_started`

## Purpose

Add supported SMBC and other approved public campaign listings through the
existing source interface.

## Provisional scope

- `smbc_public` adapter and any explicitly approved public source.
- Shared normalized output, source-specific fixtures, and cross-source identity.
- Scrape-all orchestration with one browser context and one page at a time.
- No private Vpass pages.

## Before implementation

Confirm approved source URLs and terms, then expand adapters, orchestration,
deduplication, failure isolation, tests, and UAT before making code changes.
