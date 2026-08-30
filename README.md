---
name: internly
description: Template — automated YC founder outreach. Finds pre-seed/seed startups, drafts personalized emails, sends via Gmail.
updated: 2026-08-28
---

# internly

Automated founder outreach tool. Finds YC-backed startups (pre-seed/seed/post-seed), generates personalized one-paragraph emails using a free AI model, and sends them through your Gmail via MCP.

## Quick Start

### 1. Clone the template

```bash
git clone https://github.com/justrishith/internly.git
cd internly
```

### 2. Run interactive setup

```bash
python internly.py init
```

This walks you through setting up:
- Your name, project URL, GitHub, pitch
- Zen API key (free, from opencode.ai/auth)
- Gmail OAuth credentials (see [setup guide](GOOGLE_CLOUD_SETUP.md))

### 3. Test it

```bash
pip install -r requirements.txt
python internly.py stats
```

### 4. Run your first outreach

```bash
python internly.py daily-run --limit 5
```

## Commands

| Command | What it does |
|---------|--------------|
| `init` | Interactive setup — creates .env file |
| `daily-run` | Full pipeline: fetch → find → draft → send |
| `draft` | Draft emails without sending |
| `send` | Send already-drafted emails |
| `stats` | View sending statistics |
| `list` | List founders in database |

## How it works

1. **Fetches YC companies** from the free yc-oss/api (6000+ companies)
2. **Finds founder emails** via web scraping
3. **Generates observations** by scraping their homepage and calling a free AI model
4. **Rotates 3 templates** — each is one personalized paragraph
5. **Sends via Gmail API** — through your Google account, no third-party service
6. **Logs everything** to SQLite

## The 3 Templates

Templates rotate A → B → C. Each uses your info from `.env`:

- **Template A**: "I built something similar" angle
- **Template B**: "Congrats on the batch" angle
- **Template C**: "I already looked at your product" angle

Edit `templates.py` to customize the wording.

## Automation (GitHub Actions)

The tool runs daily at 8 AM UTC via GitHub Actions.

1. Fork or clone this repo
2. Add these secrets in Settings → Secrets → Actions:
   - `ZEN_API_KEY`
   - `GOOGLE_GMAIL_CLIENT_ID`
   - `GOOGLE_GMAIL_CLIENT_SECRET`
   - `GOOGLE_REFRESH_TOKEN`
   - `YOUR_NAME`
   - `YOUR_LINK`
   - `YOUR_GITHUB`
   - `YOUR_PITCH`
3. The workflow runs automatically

## Config

All settings are in `.env` (created by `init`). See `.env.example` for all options:

| Setting | What it controls |
|---------|-----------------|
| `YOUR_NAME` | Your name in emails |
| `YOUR_LINK` | Your main project URL |
| `YOUR_GITHUB` | Your GitHub profile |
| `YOUR_PITCH` | 1-2 sentence elevator pitch |
| `ZEN_API_KEY` | For AI-generated observations |
| `DAILY_LIMIT` | Max emails per day (default: 25) |
| `YC_BATCHES` | Which YC batches to target |
| `YC_STAGES` | Which stages (Early, Growth) |

## Database

All data is in `internly.db` (SQLite). Inspect directly:

```bash
sqlite3 internly.db
.tables
SELECT * FROM founders;
SELECT * FROM emails;
```

## Files

| File | Purpose |
|------|---------|
| `internly.py` | Main CLI entry point |
| `yc_fetcher.py` | Fetches YC companies from free API |
| `email_finder.py` | Finds founder emails via scraping |
| `templates.py` | 3 one-paragraph email templates |
| `observer.py` | Scrapes homepage + generates observation |
| `sender.py` | Gmail API sender via OAuth |
| `tracker.py` | SQLite database operations |
| `config.py` | Configuration from environment |
| `GOOGLE_CLOUD_SETUP.md` | Step-by-step Google Cloud tutorial |
| `.github/workflows/daily-outreach.yml` | GitHub Actions schedule |

## License

MIT — use it, fork it, modify it.
