# Phase Plan: 06 Detail Page Extraction and Screenshots

## Status

`not_started`

## Purpose

Enrich public campaigns from detail pages and optionally preserve screenshots
without interacting with entry or application controls.

## Provisional scope

- Rate-limited one-page-at-a-time detail traversal only when needed.
- Raw detail text, evidence hash, structured terms, and public screenshots.
- Graceful failure with card-level data retained.
- No private screenshots, CAPTCHA bypass, or application actions.

## Before implementation

Inspect current detail pages and expand extraction, evidence, delay, storage,
failure, and UAT requirements before making code changes.
