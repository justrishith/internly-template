# internly

Automated YC founder outreach. Finds pre-seed/seed startups, writes personalized emails, sends them through your Gmail.

**How it works:** Pulls companies from the YC directory, finds founder emails, generates a one-sentence observation about their product using AI, rotates through 5 email templates, and sends via your Gmail account.

## What you need

| Thing | Where to get it | Cost |
|-------|-----------------|------|
| Python 3.10+ | [python.org](https://python.org) | Free |
| Zen API key | [opencode.ai/auth](https://opencode.ai/auth) | Free |
| Gmail OAuth credentials | [Google Cloud Console](https://console.cloud.google.com) | Free |
| Your name, project URL, pitch | You | Free |

## Quick start

```bash
# Clone
git clone https://github.com/YOUR_USERNAME/internly.git
cd internly

# Install
pip install -r requirements.txt

# Set up (walks you through everything)
python internly.py init

# Test
python internly.py stats

# Run
python internly.py daily-run --limit 5
```

## Commands

```
python internly.py init              # Interactive setup
python internly.py daily-run         # Full pipeline: fetch -> find -> draft -> send
python internly.py daily-run --limit 10   # Send max 10 emails
python internly.py draft             # Draft emails without sending
python internly.py send              # Send drafted emails
python internly.py stats             # View sending stats
python internly.py list              # List founders in database
```

## Configuration

All settings live in `.env` (created by `init`). Here's what each one does:

| Setting | What it does | Example |
|---------|--------------|---------|
| `YOUR_NAME` | Your name in emails | `Rishith` |
| `YOUR_LINK` | Your main project URL | `https://linkup.vercel.app` |
| `YOUR_GITHUB` | Your GitHub profile | `https://github.com/justrishith` |
| `YOUR_PITCH` | 1-2 sentence elevator pitch | `I build real products, not tutorials.` |
| `ZEN_API_KEY` | API key for AI observations | `sk-...` |
| `GOOGLE_GMAIL_CLIENT_ID` | OAuth client ID | `778756...` |
| `GOOGLE_GMAIL_CLIENT_SECRET` | OAuth client secret | `GOCSPX-...` |
| `GOOGLE_REFRESH_TOKEN` | OAuth refresh token | `1//04w...` |
| `DAILY_LIMIT` | Max emails per day | `25` |
| `YC_BATCHES` | Which YC batches to target | `Summer 2024,Winter 2025` |
| `YC_STAGES` | Which stages to target | `Early,Growth` |

## Email templates

There are 5 templates that rotate automatically. Each one is short, direct, and uses your info from `.env`:

- **A** — "I built something similar"
- **B** — "Congrats on the batch"
- **C** — "I looked at your product"
- **D** — "Short and direct"
- **E** — "Specific contribution"

The AI generates a one-sentence observation about each company's product, which gets inserted into the templates so each email feels personal.

Edit `templates.py` to change the wording. See `STYLE_GUIDE.md` for writing tips.

## Google Cloud setup

1. Create a project at [console.cloud.google.com](https://console.cloud.google.com)
2. Enable **Gmail API** and **Gmail MCP API**
3. Set up OAuth consent screen (External, add your email as test user)
4. Add scopes: `gmail.readonly`, `gmail.compose`
5. Create OAuth credentials (Web application)
6. Add `https://developers.google.com/oauthplayroom` as redirect URI
7. Get refresh token at [OAuth Playground](https://developers.google.com/oauthplayground)
8. Set environment variables or use `init`

Full walkthrough: [GOOGLE_CLOUD_SETUP.md](GOOGLE_CLOUD_SETUP.md)

## Automate with GitHub Actions

1. Fork this repo
2. Add these secrets in Settings -> Secrets -> Actions:
   - `ZEN_API_KEY`
   - `GOOGLE_GMAIL_CLIENT_ID`
   - `GOOGLE_GMAIL_CLIENT_SECRET`
   - `GOOGLE_REFRESH_TOKEN`
   - `YOUR_NAME`
   - `YOUR_LINK`
   - `YOUR_GITHUB`
   - `YOUR_PITCH`
3. The workflow runs daily at 8 AM UTC

## How the pipeline works

```
1. Fetch YC companies     yc-oss/api (free, no auth)
       |
2. Find founder emails    Web scraping + email patterns
       |
3. Generate observations  Scrape homepage -> AI writes 1 sentence
       |
4. Pick template          Rotates A -> B -> C -> D -> E
       |
5. Send via Gmail         OAuth refresh token -> Gmail API
       |
6. Log to SQLite          Track everything locally
```

## Project structure

```
internly/
  internly.py        # CLI entry point
  config.py          # Reads .env
  templates.py       # 5 email templates (edit these)
  yc_fetcher.py      # Pulls YC companies
  email_finder.py    # Finds founder emails
  observer.py        # Generates product observations
  sender.py          # Gmail API sender
  tracker.py         # SQLite database
  .env.example       # Config template
  .github/workflows/
    daily-outreach.yml   # GitHub Actions schedule
```

## Troubleshooting

| Problem | Fix |
|---------|-----|
| "No founders found" | Check YC batches/stages in .env |
| "Gmail API error 400" | Re-do OAuth Playground step |
| "Token expired" | Re-run OAuth Playground, update refresh token |
| "Rate limit" on observations | Normal, falls back to default text |
| Emails feel generic | Edit templates.py, add more specific pitch |

## License

MIT
