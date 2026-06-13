# Phase Plan: 01 Project Bootstrap

## Status

`not_started`

Allowed status values:

- `not_started`
- `in_progress`
- `blocked`
- `ready_for_uat`
- `uat_failed`
- `done`

## Phase summary

This phase creates the Python project foundation used by every later phase. It
establishes package metadata, a typed configuration layer, logging, a Typer CLI
shell, safe repository directories, development tooling, and tests for the
foundation. The CLI commands are placeholders only; no campaign collection,
storage, or export behavior is implemented yet.

## Background

The repository currently has planning documents but no application code.
Bootstrapping is isolated from feature development so later phases can rely on
one stable package layout, command surface, dependency set, and security policy.

## Goals

- [ ] Create an installable Python 3.11+ package using a `src` layout.
- [ ] Provide a working CLI with `scrape`, `export`, and `summary` placeholders.
- [ ] Establish safe configuration, logging, data directories, and ignore rules.
- [ ] Configure pytest and Ruff and add focused bootstrap tests.
- [ ] Document local setup and the current non-functional command behavior.

## Non-goals

- Do not scrape live or fixture campaign pages.
- Do not create a SQLite schema or persist campaigns.
- Do not generate JSON campaign exports.
- Do not implement browser login, cookie storage, or private Vpass access.
- Do not implement LLM extraction, campaign scoring, or recommendations.
- Do not automate campaign entry, applications, purchases, or spending.

## Scope

### In scope

- `pyproject.toml` with project metadata, Python version, runtime dependencies,
  development dependencies, package discovery, pytest, and Ruff configuration.
- `src/vpoint_scanner` package with `__init__.py`, `__main__.py`, `cli.py`,
  `config.py`, and a small logging setup.
- Typer command group and placeholder `scrape`, `export`, and `summary`
  commands whose help exposes the future options from `AGENTS.md`.
- Safe defaults for local data paths and policy flags.
- Creation of public runtime directories with tracked placeholders where useful.
- `.gitignore`, `.env.example`, README setup instructions, and bootstrap tests.

### Out of scope

- Parser, source adapter, ORM model, database, export, screenshot, LLM, scoring,
  and private-page modules.
- Playwright browser installation or any live network request.
- Selecting target campaign URLs or page selectors.
- Producing real campaign records or user recommendations.

## Requirements

### Functional requirements

| ID | Requirement | Priority | Status |
|---|---|---:|---|
| FR-001 | `python -m vpoint_scanner --help` displays CLI help without a traceback | Must | `not_started` |
| FR-002 | CLI help lists `scrape`, `export`, and `summary` commands | Must | `not_started` |
| FR-003 | Placeholder commands exit successfully and clearly state that their feature belongs to a later phase | Must | `not_started` |
| FR-004 | `scrape` help accepts `--source` and `--screenshots` | Must | `not_started` |
| FR-005 | `export` help accepts `--format`, `--output`, and `--ending-within-days` | Must | `not_started` |
| FR-006 | Configuration exposes project data paths and the three safe policy defaults | Must | `not_started` |
| FR-007 | Application logging can be initialized without duplicate handlers or import-time side effects | Should | `not_started` |

### Non-functional requirements

| ID | Requirement | Priority | Status |
|---|---|---:|---|
| NFR-001 | Support Python 3.11 or newer and use UTF-8 throughout | Must | `not_started` |
| NFR-002 | Runtime stack declares Typer, Pydantic, Playwright, and one SQLAlchemy-based ORM | Must | `not_started` |
| NFR-003 | Development stack declares pytest and Ruff | Must | `not_started` |
| NFR-004 | Ignore `.env`, SQLite files, private raw data/screenshots, browser profiles, cookies, and sessions | Must | `not_started` |
| NFR-005 | Configuration defaults set extra spending to zero and disable automatic entry and new-card applications | Must | `not_started` |
| NFR-006 | No command stores credentials or performs network/browser activity in this phase | Must | `not_started` |

## Technical design

### Package and tooling

- Use a standard `pyproject.toml` build configuration and `src` package layout.
- Use Typer for command declaration and `python -m vpoint_scanner` as the
  canonical invocation.
- Use Pydantic Settings or a small Pydantic-backed settings model. Environment
  variables may override paths, but policy defaults must remain conservative.
- Choose either SQLModel or SQLAlchemy in `pyproject.toml`; do not declare both
  unless SQLModel requires SQLAlchemy transitively.
- Declare Playwright now for the agreed stack, but do not launch a browser.

### CLI contract

- The root command displays help when called without a subcommand.
- `scrape` exposes `--source` and `--screenshots`.
- `export` exposes `--format`, `--output`, and `--ending-within-days`.
- `summary` has no required options.
- Placeholder execution prints a neutral “not implemented in this phase”
  message and exits with code 0. It must not imply that campaigns were processed.

### Configuration and paths

- Define defaults under repository-local `data/raw`, `data/screenshots`,
  `data/exports`, and `data/vpoint_campaigns.sqlite3`.
- Define policy defaults equivalent to:
  `extra_spending_allowed=0`, `auto_entry_allowed=false`, and
  `new_credit_card_application_allowed=false`.
- Do not create or require a real `.env`; provide `.env.example` without secrets.
- Track empty public data directories only through neutral placeholder files.
  Private data directories and generated exports remain ignored.

### Expected files

```text
README.md
pyproject.toml
.env.example
.gitignore
src/vpoint_scanner/
  __init__.py
  __main__.py
  cli.py
  config.py
  logging.py
tests/
  test_cli.py
  test_config.py
  test_security.py
data/
  raw/
  screenshots/
  exports/
```

## Implementation tasks

- [ ] Add package metadata, dependencies, test settings, and Ruff settings.
- [ ] Add package initialization and module entry point.
- [ ] Implement the Typer command shell and placeholder command options.
- [ ] Implement typed paths, safety policy defaults, and logging setup.
- [ ] Add safe data directory placeholders and `.env.example`.
- [ ] Add comprehensive ignore rules for generated and sensitive artifacts.
- [ ] Write README setup, invocation, and safety-boundary documentation.
- [ ] Add tests for imports, CLI behavior, configuration, and ignored paths.
- [ ] Run Ruff checks and pytest.
- [ ] Synchronize this plan, Phase UAT, and `.planning/STATE.md`.

## Error handling

- Invalid CLI option values produce Typer validation errors and nonzero exits.
- Configuration errors identify the invalid field without printing secrets.
- Placeholder commands never report false success such as campaign counts or
  created export paths.

## Definition of done

- The package installs in a Python 3.11+ environment.
- Root and subcommand help run successfully.
- Placeholder commands expose the agreed command surface without side effects.
- Safety policy defaults and data paths are covered by tests.
- Sensitive paths and file patterns are covered by `.gitignore` tests.
- Ruff and pytest pass.
- Phase 01 UAT is completed and recorded before the phase is marked `done`.
