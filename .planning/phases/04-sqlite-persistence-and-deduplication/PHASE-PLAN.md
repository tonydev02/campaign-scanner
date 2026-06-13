# Phase Plan: 04 SQLite Persistence and Deduplication

## Status

`not_started`

## Purpose

Persist normalized campaigns in local SQLite with deterministic upsert and
deduplication behavior.

## Provisional scope

- ORM table and database initialization.
- URL-first and title-plus-period fallback upserts.
- Preserve `first_seen_at`; update changed fields, raw evidence, and timestamps.
- Never automatically delete campaigns.

## Before implementation

Expand schema mapping, transaction/error behavior, migration assumptions, tests,
and UAT before making code changes.
