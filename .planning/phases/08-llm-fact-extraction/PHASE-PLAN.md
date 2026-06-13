# Phase Plan: 08 LLM Fact Extraction

## Status

`not_started`

## Purpose

Optionally extract structured campaign facts from preserved text while keeping
the scraper deterministic and financial judgment outside the extraction layer.

## Provisional scope

- Typed extraction request/response and prompt contract.
- Entry, reward, target payment/store, spend threshold, and exclusion facts.
- Confidence, notes, validation, and safe fallback to unknown.
- No recommendations, autonomous actions, or unsupported assumptions.

## Before implementation

Select the provider and model policy explicitly, then expand privacy, retries,
cost controls, prompt versioning, fixtures, and UAT before making code changes.
