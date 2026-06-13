# V Point Campaign Scanner

V Point Campaign Scanner is a local tool for collecting campaign information
and reviewing it without encouraging extra spending. It currently collects all
visible cards from the public V Point campaign list. Database storage and JSON
export are introduced in later phases.

## Requirements

- Python 3.11 or newer
- [uv](https://docs.astral.sh/uv/) (recommended) or another Python package
  installer

No browser installation, account login, credentials, or `.env` file is needed
for Phase 01.

## Setup

With uv:

```bash
uv sync --extra dev
uv run playwright install chromium
uv run python -m vpoint_scanner --help
```

With a standard virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
playwright install chromium
python -m vpoint_scanner --help
```

## CLI

The `scrape` command opens the approved public all-campaigns page once with
Playwright and prints the collected card count and titles. It does not visit
campaign details, click entry controls, or write a database:

```bash
python -m vpoint_scanner scrape --source vpoint_public
```

The following command surfaces remain placeholders until their planned phases:

```bash
python -m vpoint_scanner export --format json --output data/exports/campaigns.json
python -m vpoint_scanner export --ending-within-days 7
python -m vpoint_scanner summary
```

`scrape --screenshots` explicitly reports that screenshot capture begins in
Phase 06.

## Configuration

Settings use the `VPOINT_` environment-variable prefix. See `.env.example` for
path examples. Defaults point to this repository's `data/` directory.

The safety policy is deliberately fixed:

- Extra spending allowed: `0`
- Automatic campaign entry: disabled
- New credit card applications: disabled

The application must not store credentials, cookies, browser profiles, private
financial exports, or screenshots containing private account information. It
does not automate campaign entry, purchases, credit applications, CAPTCHA, or
2FA.

## Development

```bash
uv run --extra dev pytest
uv run --extra dev ruff check .
uv run --extra dev ruff format --check .
```

Automated tests use saved fixtures and make no network requests. Live scraping
is an explicit CLI action.
