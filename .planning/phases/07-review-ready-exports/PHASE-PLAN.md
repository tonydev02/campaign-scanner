# Phase Plan: 07 Review-Ready Exports

## Status

`done`

## Purpose

Make stored campaigns easier to review with an LLM without weakening the full
evidence record or adding financial scoring.

## Scope

- Persist a `detail_scrape_status` explaining whether detail evidence was
  extracted, skipped, unsupported, not attempted, or failed.
- Derive conservative facts from visible card/title text:
  - maximum reward points
  - reward type
  - new application requirement
  - lottery and guaranteed-reward signals
  - financial-product and gambling/prediction signals
- Add `compact` and `full` JSON export profiles.
- Omit null fields from compact campaigns.
- Replace full raw evidence in compact output with a bounded preview and text
  length metadata.
- Keep full export behavior available for debugging and deep review.
- Keep date filters, deterministic ordering, UTF-8 output, and atomic writes.
- Migrate existing SQLite databases forward without deleting campaign data.

## Out of scope

- New public campaign sources.
- LLM calls or final financial judgment.
- Automatic campaign entry or spending actions.
- Persisted arbitrary detail-page section maps.
- Changes to private-page access.

## Tasks

- [x] Approve the export-quality priority and phase boundary.
- [x] Add schema, ORM, migration, and upsert support for new facts.
- [x] Add title/card rule extraction with conservative tests.
- [x] Track detail scrape outcomes through collection and persistence.
- [x] Add compact/full serializers and CLI profile selection.
- [x] Run automated tests and Ruff.
- [x] Record UAT results and repository state.

## Definition of done

- Existing databases gain the new columns without losing rows.
- A scrape records a meaningful detail status for every campaign.
- Explicit title/card phrases populate only supported conservative facts.
- Compact JSON omits nulls and bounds raw evidence.
- Full JSON retains the canonical campaign shape and full raw evidence.
- Export filtering and ordering behave identically across profiles.
- Automated tests and lint pass.
