# V Point Campaign Scanner

V Point Campaign Scanner is a local tool for collecting campaign information
and reviewing it without encouraging extra spending. It currently collects all
visible cards from the public V Point campaign list and upserts them into local
SQLite. It exports clean UTF-8 JSON and reports current database counts.

## Requirements

- Python 3.11 or newer
- [uv](https://docs.astral.sh/uv/) (recommended) or another Python package
  installer

No account login, credentials, or `.env` file is needed. Chromium is required
only for the public scrape command.

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
Playwright and upserts the collected cards into
`data/vpoint_campaigns.sqlite3`. It sequentially enriches only same-origin
`cpn.tsite.jp/detail/...` pages and never clicks entry controls or opens
third-party campaign links:

```bash
python -m vpoint_scanner scrape --source vpoint_public
python -m vpoint_scanner scrape --screenshots
```

Export a compact daily-review file, retain full evidence for deep review, use an
inclusive ending window, or inspect current counts:

```bash
python -m vpoint_scanner export
python -m vpoint_scanner export --profile full
python -m vpoint_scanner export --profile compact --output data/exports/review.json
python -m vpoint_scanner export --ending-within-days 7
python -m vpoint_scanner summary
```

Compact output omits null fields and includes at most 800 characters of raw
evidence per campaign. Full output preserves the complete canonical record.

Screenshots are optional and limited to enriched public detail pages under
`data/screenshots/public/`. They may contain campaign marketing content but must
never be used for private account pages.

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
