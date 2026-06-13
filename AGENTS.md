# AGENTS.md

## Project: V Point Campaign Scanner

This project collects V Point / SMBC / Vpass campaign information from campaign listing pages, stores the campaigns in a local database, and exports a clean JSON file that can be reviewed by the user or passed to an LLM for final judgment.

The current MVP goal is simple:

1. Extract all visible campaigns from supported campaign list pages.
2. Normalize campaign data into a database.
3. Export campaign data to JSON.
4. Do **not** automatically enter campaigns.
5. Do **not** encourage extra spending.

The project should help the user answer:

> “Which campaigns are eligible and worth considering based on my normal spending?”

---

## Core principles

### 1. Extraction first, judgment later

For the MVP, prioritize accurate campaign extraction over complicated scoring.

The scraper should capture:

- campaign title
- campaign URL
- image URL if available
- source site
- visible period text
- start date
- end date
- tags or category if available
- whether it appears to require entry
- short description
- raw text snapshot
- scrape timestamp

Final decision-making can happen later using exported JSON.

### 2. Do not automate risky actions

The system must not:

- automatically enter campaigns
- automatically click application/entry buttons
- automatically spend money
- apply for credit cards
- store banking passwords
- bypass CAPTCHA, 2FA, or access controls
- scrape private pages aggressively

If a page requires login, prefer manual login through a local browser profile and only read campaign information after the user has logged in.

### 3. Protect personal finance discipline

Campaigns are treated as optional bonuses, not investment strategy.

The application should avoid language or logic that encourages extra spending. A campaign is useful only if it matches spending the user already planned to do.

Default policy:

```yaml
extra_spending_allowed: 0
auto_entry_allowed: false
new_credit_card_application_allowed: false
```

### 4. Preserve evidence

Campaign conditions change often. Store enough raw data to allow later verification.

For each campaign, store:

- source URL
- scrape timestamp
- raw extracted text
- screenshot path if available
- structured fields parsed from raw text

---

## Suggested tech stack

Use Python unless there is a strong reason not to.

Recommended stack:

- Python 3.11+
- Playwright for browser-based scraping
- BeautifulSoup or selectolax for HTML parsing
- SQLite for local storage
- SQLModel or SQLAlchemy for ORM
- Pydantic for schema validation
- pytest for tests
- ruff for linting/formatting
- typer or argparse for CLI commands

Optional later:

- FastAPI for a small local API
- Streamlit for a simple dashboard
- Gmail parser for campaign emails
- LLM extraction layer for detailed campaign terms

---

## Repository structure

Recommended structure:

```text
vpoint-campaign-scanner/
  AGENTS.md
  README.md
  pyproject.toml
  .env.example
  data/
    raw/
    screenshots/
    exports/
    vpoint_campaigns.sqlite3
  src/
    vpoint_scanner/
      __init__.py
      config.py
      cli.py
      db.py
      models.py
      schemas.py
      export.py
      normalize.py
      sources/
        __init__.py
        base.py
        vpoint_public.py
        smbc_public.py
        vpass_private.py
      parsers/
        __init__.py
        campaign_card.py
        campaign_detail.py
      llm/
        __init__.py
        extract_terms.py
        prompts.py
  tests/
    fixtures/
    test_campaign_card_parser.py
    test_normalize.py
    test_export.py
```

---

## Data model

Use this as the base campaign schema.

```python
from datetime import datetime, date
from typing import Optional, Literal
from pydantic import BaseModel, HttpUrl


class Campaign(BaseModel):
    id: Optional[int] = None

    source: str
    source_type: Literal[
        "vpoint_public",
        "smbc_public",
        "vpass_private",
        "email",
        "manual"
    ]

    title: str
    campaign_url: Optional[str] = None
    image_url: Optional[str] = None

    visible_period_text: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None

    description: Optional[str] = None
    category: Optional[str] = None

    requires_entry: Optional[bool] = None
    entry_text: Optional[str] = None

    reward_text: Optional[str] = None
    max_reward_points: Optional[int] = None
    reward_type: Optional[Literal[
        "guaranteed",
        "lottery",
        "multiplier",
        "coupon",
        "unknown"
    ]] = None

    target_payment_text: Optional[str] = None
    target_store_text: Optional[str] = None
    minimum_spend_text: Optional[str] = None
    exclusions_text: Optional[str] = None

    raw_text: Optional[str] = None
    raw_html_hash: Optional[str] = None
    screenshot_path: Optional[str] = None

    first_seen_at: Optional[datetime] = None
    last_seen_at: Optional[datetime] = None
    scraped_at: datetime

    status: Literal[
        "active",
        "ending_soon",
        "expired",
        "unknown"
    ] = "unknown"
```

For SQLite, a simpler SQL table is acceptable as long as exported JSON follows this shape.

---

## JSON export format

The export should be easy to paste into ChatGPT.

Example:

```json
{
  "exported_at": "2026-06-14T06:00:00+09:00",
  "source_count": 2,
  "campaign_count": 10,
  "campaigns": [
    {
      "source": "vpoint_public",
      "title": "はずれなし！毎日あたるくじ",
      "campaign_url": "https://...",
      "visible_period_text": "05/01〜06/30",
      "start_date": "2026-05-01",
      "end_date": "2026-06-30",
      "description": "はずれなし！毎日あたるくじ",
      "requires_entry": null,
      "reward_text": "最大10000pt",
      "reward_type": "lottery",
      "raw_text": "..."
    }
  ]
}
```

---

## CLI commands

Implement these commands:

```bash
# Scrape all configured public sources
python -m vpoint_scanner scrape

# Scrape one source
python -m vpoint_scanner scrape --source vpoint_public

# Save screenshots during scrape
python -m vpoint_scanner scrape --screenshots

# Export all active campaigns to JSON
python -m vpoint_scanner export --format json --output data/exports/campaigns.json

# Export campaigns ending soon
python -m vpoint_scanner export --ending-within-days 7 --output data/exports/ending_soon.json

# Show database summary
python -m vpoint_scanner summary
```

---

## Scraping behavior

### Public campaign list pages

For public pages like campaign list grids:

1. Open the page with Playwright.
2. Wait until campaign cards are visible.
3. Extract all campaign cards.
4. For each card, extract:
   - title
   - period
   - image URL
   - detail URL
   - card text
5. Visit detail pages only if needed.
6. Store the raw card text and raw detail text.

### Pagination and tabs

If the page has tabs such as:

- おすすめ
- すべて
- 新着
- まもなく終了

Prefer scraping `すべて` to avoid duplicates and missing campaigns.

If scraping multiple tabs, deduplicate by canonical URL first, then by normalized title + period.

### Date parsing

Campaign dates may appear as:

- `05/01〜06/30`
- `2026/04/22〜2026/06/30`
- `6月1日〜6月30日`
- `2026年6月30日まで`

Rules:

- Use current year as fallback only when the page does not provide a year.
- Store original text in `visible_period_text`.
- If parsing is uncertain, keep `start_date` and `end_date` as `null`.
- Never invent dates.

### Japanese text handling

Keep Japanese text as-is.

Do not translate campaign titles in stored data. Translation or interpretation can happen later in the LLM review step.

Use UTF-8 everywhere.

---

## Deduplication rules

Campaigns should be treated as the same if:

1. Their canonical campaign URL is the same.

If URL is missing, fallback to:

2. normalized title + visible period text.

Normalize by:

- trimming whitespace
- converting full-width spaces to normal spaces
- removing duplicate spaces
- preserving Japanese characters
- not lowercasing Japanese text unnecessarily

---

## Database rules

Use upsert behavior.

When a campaign is seen for the first time:

- set `first_seen_at`
- set `last_seen_at`
- set `scraped_at`

When a known campaign is seen again:

- preserve `first_seen_at`
- update `last_seen_at`
- update changed fields
- keep latest raw text

Do not delete campaigns automatically. Mark them as expired or unseen.

---

## LLM extraction rules

LLM usage is optional for MVP.

When used, LLMs should only extract structured facts from campaign text. They should not make final financial decisions inside the scraper.

Good LLM tasks:

- identify whether entry is required
- identify reward type
- summarize conditions
- extract target stores
- extract target payment methods
- extract exclusions

Bad LLM tasks for the scraper:

- telling the user to spend money
- deciding to apply for cards
- making assumptions not present in the campaign text

Use this output style:

```json
{
  "requires_entry": true,
  "entry_method": "Vpass login",
  "reward_type": "lottery",
  "reward_text": "2人に1人、最大50,000ポイント",
  "target_payment_text": "VポイントPayアプリ",
  "minimum_spend_text": "3,000円ごとに1口",
  "exclusions_text": "取消・返品・売上遅延などは対象外の可能性あり",
  "confidence": 0.82,
  "notes": "Conditions should be manually checked before action."
}
```

---

## Final decision output

The app itself may provide a preliminary label, but it must stay conservative.

Allowed labels:

- `enter_free`
- `use_if_already_spending`
- `manual_check`
- `ignore`
- `expired`
- `unknown`

Default to `manual_check` or `unknown` when information is incomplete.

Suggested rules:

```python
if campaign.end_date and campaign.end_date < today:
    label = "expired"
elif campaign.requires_entry is True and no_extra_spend_required(campaign):
    label = "enter_free"
elif guaranteed_reward(campaign) and planned_spend_matches(campaign):
    label = "use_if_already_spending"
elif requires_new_card_application(campaign):
    label = "ignore"
elif requires_extra_spending(campaign):
    label = "ignore"
else:
    label = "manual_check"
```

Do not present lottery campaigns as profitable unless the expected value can be calculated from explicit probability and reward data.

---

## Security rules

Never commit:

- `.env`
- cookies
- browser profiles
- session files
- screenshots containing personal account info
- exported data from private pages
- bank/card statements

Add these to `.gitignore`:

```gitignore
.env
data/*.sqlite3
data/raw/private/
data/screenshots/private/
.playwright/
browser-profile/
cookies.json
*.session
```

For private pages, store only the minimum campaign information needed.

---

## Compliance and politeness

Scrape gently.

Default limits:

- one browser context
- one page at a time
- 1–3 seconds delay between detail page requests
- no unnecessary repeated scraping
- no CAPTCHA bypass
- no hidden API abuse

Respect robots.txt and site terms where applicable.

If the site blocks access, stop and report the issue. Do not try to bypass.

---

## Testing requirements

Add tests for:

1. Parsing campaign cards from saved HTML fixtures.
2. Date parsing from Japanese date formats.
3. Deduplication by URL.
4. Deduplication by title + period fallback.
5. JSON export shape.
6. Upsert behavior preserving `first_seen_at`.

Use saved fixtures instead of live website calls in tests.

---

## Definition of done for MVP

The MVP is complete when:

- `python -m vpoint_scanner scrape --source vpoint_public` collects campaign cards from the target page.
- Campaigns are stored in SQLite.
- Running scrape twice does not create duplicates.
- `python -m vpoint_scanner export --format json` creates a clean JSON file.
- The JSON can be pasted into ChatGPT for final review.
- No login credentials are stored.
- No campaign entry is automated.

---

## Development style

Prefer boring, readable code.

Rules:

- keep functions small
- type hint public functions
- use Pydantic schemas for external data
- log important actions
- handle network failures gracefully
- keep raw data when parsing fails
- never silently discard campaigns

When unsure, preserve raw text and mark structured fields as unknown.

---

## User-specific default policy

This project is for a user who wants to optimize V Point campaigns without damaging their investment and savings plan.

Default recommendation behavior:

- Free entry campaign: worth checking
- Normal planned spending campaign: worth checking
- Extra spending required: usually ignore
- Lottery campaign: enter only if free
- New credit card campaign: ignore unless user explicitly decides otherwise
- Anything involving debt, revolving payment, or cash advance: ignore

The project should help the user stay calm and avoid marketing FOMO.

---

## Planning docs synchronization

This project uses `.planning/` as the source of truth for implementation state.

Before making code changes, the coding assistant must read:

- `.planning/STATE.md`
- the current phase `PHASE-PLAN.md`
- the current phase `PHASE-UAT.md`

The assistant must keep code and planning documents synchronized.

### Required workflow

Before coding:

1. Check `.planning/STATE.md` to understand the current phase, latest status, open decisions, and next action.
2. Check the active phase plan to confirm scope.
3. Check the active UAT document to understand acceptance criteria.
4. Do not implement work outside the active phase unless the phase plan is updated first.

During coding:

1. Keep implementation aligned with the active phase plan.
2. If the implementation scope changes, update the phase plan.
3. If acceptance criteria change, update the UAT document.
4. If a decision is made, record it in `.planning/STATE.md`.
5. If a blocker appears, record it in `.planning/STATE.md`.

After coding:

1. Update `.planning/STATE.md` with:
   - what changed
   - what was completed
   - what remains
   - known issues
   - next recommended action
2. Update the active phase plan task list.
3. Update the active phase UAT result if tests were performed.
4. Do not mark a phase as complete unless its UAT acceptance criteria are satisfied.

### Planning file roles

`AGENTS.md`

- Long-term project rules.
- Coding assistant behavior.
- Architecture and safety principles.
- Does not track temporary progress.

`.planning/STATE.md`

- Current project status.
- Current active phase.
- Recent changes.
- Open questions.
- Next action.
- Resume context for the next coding session.

`.planning/phases/<phase-name>/PHASE-PLAN.md`

- Scope of one implementation phase.
- Tasks, requirements, and definition of done.
- Updated when implementation scope changes.

`.planning/phases/<phase-name>/PHASE-UAT.md`

- User acceptance test plan for one phase.
- Manual test cases.
- Expected results.
- Actual results after testing.

### Phase discipline

Use small phases.

A phase should usually produce one clear improvement, for example:

- project bootstrap
- public campaign list scraping
- SQLite persistence
- JSON export
- detail page extraction
- LLM extraction
- scoring rules
- private Vpass reading

Do not combine too many unrelated features in one phase.

### Status labels

Use these labels consistently:

- `not_started`
- `in_progress`
- `blocked`
- `ready_for_uat`
- `uat_failed`
- `done`

### Documentation rule

If code behavior and `.planning/` disagree, treat `.planning/` as stale and update it immediately.

Never leave the repository in a state where the code says one thing and the planning docs say another.
