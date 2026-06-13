# V Point Campaign Scanner

V Point Campaign Scanner is a local tool for collecting campaign information
and reviewing it without encouraging extra spending. The project is currently
in Phase 01: the package, configuration, logging, and CLI shell are available,
but scraping, database storage, and JSON export are not implemented yet.

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
uv run python -m vpoint_scanner --help
```

With a standard virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
python -m vpoint_scanner --help
```

## CLI

The current commands expose the planned interface and return an honest
placeholder message without network, browser, database, or export side effects:

```bash
python -m vpoint_scanner scrape --source vpoint_public
python -m vpoint_scanner scrape --screenshots
python -m vpoint_scanner export --format json --output data/exports/campaigns.json
python -m vpoint_scanner export --ending-within-days 7
python -m vpoint_scanner summary
```

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

Tests in Phase 01 use no browser and make no network requests.
