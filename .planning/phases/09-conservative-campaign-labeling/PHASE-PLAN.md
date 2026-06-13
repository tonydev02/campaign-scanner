# Phase Plan: 09 Conservative Campaign Labeling

## Status

`not_started`

## Purpose

Add transparent preliminary labels that favor manual review and protect the
user’s existing spending and savings plan.

## Provisional scope

- Allowed labels from `AGENTS.md` and deterministic evidence-based rules.
- Default incomplete information to `manual_check` or `unknown`.
- Ignore debt, revolving payment, cash advance, new-card, and extra-spend cases.
- Never describe lotteries as profitable without explicit expected-value data.

## Before implementation

Define evidence requirements and precedence for every label, then expand tests,
explanations, export changes, and UAT before making code changes.
