# Phase Plan: 05 JSON Export and Summary

## Status

`not_started`

## Purpose

Export stored campaigns as clean UTF-8 JSON and provide a concise database
summary through the CLI.

## Provisional scope

- Full active export and ending-within-days filtering.
- Export envelope and campaign shape defined by `AGENTS.md`.
- Atomic output writing and human-readable summary counts.
- No LLM judgment or spending recommendation.

## Before implementation

Expand filter semantics, output ordering, error behavior, tests, and UAT before
making code changes.
