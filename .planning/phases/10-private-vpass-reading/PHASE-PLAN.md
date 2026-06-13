# Phase Plan: 10 Private Vpass Reading

## Status

`not_started`

## Purpose

Read minimum necessary campaign information from Vpass pages only after the user
manually authenticates in a local browser profile.

## Provisional scope

- Manual-login workflow with explicit user control.
- Read-only campaign extraction after authentication.
- Minimum private data retention and private artifact isolation.
- Stop on CAPTCHA, 2FA, blocking, or uncertain access conditions.

## Before implementation

Perform a dedicated security and compliance review. Expand session handling,
redaction, storage, deletion, access limits, failure behavior, tests, and UAT
before making code changes.
