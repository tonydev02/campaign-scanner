# Phase UAT: 04 SQLite Persistence and Deduplication

## Status

`not_started`

## UAT objective

Verify SQLite persistence and that repeated observations update campaigns
without creating duplicates or losing first-seen evidence.

## Planned scenarios

- Insert a new campaign.
- Repeat by canonical URL.
- Repeat without URL using normalized title and period.
- Verify timestamp preservation, changed fields, and no automatic deletion.

## Actual result

TODO. Expand this document before Phase 04 implementation.
