# Phase UAT: 07 Review-Ready Exports

## Status

`done`

## UAT objective

Verify that daily review exports are concise and explain missing detail facts,
while the full evidence export and existing persistence behavior remain intact.

## Acceptance scenarios

1. Existing database migration
   - Initialize a database created with the Phase 06 schema.
   - Expected: new columns are added and existing campaigns remain readable.

2. Detail outcome tracking
   - Process extracted, external, unsupported, and failed detail destinations.
   - Expected: each campaign records the corresponding allowed status.

3. Conservative title facts
   - Parse explicit Japanese reward, application, financial, and gambling terms.
   - Expected: supported facts are populated without inventing missing values.

4. Compact export
   - Export campaigns containing null fields and long raw evidence.
   - Expected: nulls are omitted, raw text is previewed, and evidence length and
     detail availability metadata are present.

5. Full export
   - Export the same campaigns using the full profile.
   - Expected: canonical fields and complete raw evidence remain available.

6. CLI profiles and filters
   - Run compact and full exports with current-date filters.
   - Expected: profile-specific output files are written atomically with the
     same selected campaigns and deterministic order.

## Actual result

Passed on 2026-06-14.

- 98 automated tests passed.
- Ruff lint and formatting checks passed.
- A Phase 06-shaped SQLite fixture migrated without losing its row.
- The existing local database migrated and exported 51 campaigns successfully.
- Compact export measured 63,289 bytes versus 107,772 bytes for full output.
- Existing evidence produced reward amounts, lottery/gambling flags, and
  `extracted`, `external_skipped`, and `unsupported` detail statuses.
- No network requests, campaign entry, spending action, or private-page access
  occurred during UAT.
