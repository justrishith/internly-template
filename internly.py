#!/usr/bin/env python3
"""
internly — Automated YC founder outreach tool.
Finds pre-seed/seed startups, generates personalized emails, sends via Gmail MCP.
"""

import sys
import time
import argparse
import json
from datetime import datetime
from pathlib import Path

from config import load_config
from tracker import (
    get_db, add_founder, add_email, mark_sent, mark_contacted,
    get_today_stats, increment_sent, can_send_more,
    get_uncontacted_founders, get_draft_emails, get_stats_summary,
)
from yc_fetcher import fetch_and_filter, get_founder_info
from email_finder import find_founder_email
from observer import get_observation_for_company
from templates import get_template, fill_template


def cmd_daily_run(args, config):
    """Full daily pipeline: fetch -> find emails -> draft -> send."""
    db = get_db()

    print("=" * 60)
    print(f"  internly — Daily Run — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)

    # Step 1: Fetch YC companies
    print("\n[1/6] Fetching YC companies...")
    companies = fetch_and_filter(batch_limit=50)
    print(f"  Found {len(companies)} companies")

    if not companies:
        print("  No companies found. Check your filters.")
        return

    # Step 2: Find founder contacts
    print("\n[2/6] Finding founder contacts...")
    new_founders = 0
    for company in companies:
        # Get founder info from YC page
        founder_info = get_founder_info(company["slug"])

        # Try to find email
        founder_name = founder_info.get("name", "")
        email = find_founder_email(founder_name, company["website"]) if founder_name else None

        if email or founder_name:
            founder_id = add_founder(
                db,
                name=founder_name or f"Founder @ {company['name']}",
                email=email,
                company=company["name"],
                company_url=company["website"],
                batch=company["batch"],
                stage=company["stage"],
                industries=json.dumps(company.get("industries", [])),
                yc_url=company.get("yc_url", ""),
            )
            new_founders += 1

    print(f"  Added {new_founders} founders to database")

    # Step 3: Get uncontacted founders with emails
    print("\n[3/6] Preparing emails...")
    uncontacted = get_uncontacted_founders(db, limit=args.limit or config.daily_limit)
    print(f"  {len(uncontacted)} founders ready for outreach")

    if not uncontacted:
        print("  No new founders to contact. Done.")
        return

    # Step 4: Generate observations and draft emails
    print("\n[4/6] Generating observations and drafting emails...")
    drafted = 0
    for i, founder in enumerate(uncontacted):
        if not can_send_more(db, config.daily_limit):
            print(f"  Daily limit reached ({config.daily_limit})")
            break

        # Get observation from homepage
        company_data = {
            "name": founder["company"],
            "website": founder["company_url"],
        }
        observation = get_observation_for_company(company_data, config.zen_api_key, config)

        # Pick template (rotate A, B, C)
        template = get_template(i)

        # Fill template
        founder_name = founder["name"].split()[0] if founder["name"] else "there"
        email_content = fill_template(
            template,
            founder_name=founder_name,
            company=founder["company"],
            batch=founder.get("batch", "recent batch"),
            observation=observation,
            your_name=config.your_name,
            your_link=config.your_link,
            your_github=config.your_github,
            your_portfolio=config.your_portfolio,
            your_pitch=config.your_pitch,
        )

        # Save to database
        add_email(
            db,
            founder_id=founder["id"],
            template_key=template["name"],
            subject=email_content["subject"],
            body=email_content["body"],
            observation=observation,
        )
        drafted += 1

    print(f"  Drafted {drafted} emails")

    # Step 5: Send emails
    print("\n[5/6] Sending emails...")
    from sender import send_email

    drafts = get_draft_emails(db, limit=config.daily_limit)
    sent = 0

    for draft in drafts:
        if not can_send_more(db, config.daily_limit):
            break

        success = send_email(
            to=draft["founder_email"],
            subject=draft["subject"],
            body=draft["body"],
            config=config,
        )

        if success:
            mark_sent(db, draft["id"])
            mark_contacted(db, draft["founder_id"])
            increment_sent(db)
            sent += 1
            print(f"  ✅ Sent to {draft['founder_email']} ({draft['company']})")
        else:
            print(f"  ❌ Failed: {draft['founder_email']}")

        time.sleep(config.send_delay)

    # Step 6: Summary
    print("\n[6/6] Daily Summary")
    stats = get_today_stats(db)
    summary = get_stats_summary(db)
    print(f"  Emails sent today: {stats['emails_sent']}/{config.daily_limit}")
    print(f"  Total founders in DB: {summary['total_founders']}")
    print(f"  Total contacted: {summary['total_contacted']}")
    print(f"  Total emails sent: {summary['total_sent']}")
    print(f"  Reply rate: {summary['reply_rate']:.1f}%")
    print("=" * 60)


def cmd_stats(args, config):
    """Show outreach statistics."""
    db = get_db()
    stats = get_today_stats(db)
    summary = get_stats_summary(db)

    print("\n📊 internly — Statistics")
    print(f"  Today: {stats['emails_sent']}/{config.daily_limit} emails sent")
    print(f"  Total founders: {summary['total_founders']}")
    print(f"  Contacted: {summary['total_contacted']}")
    print(f"  Emails sent: {summary['total_sent']}")
    print(f"  Replies: {summary['total_replies']}")
    print(f"  Reply rate: {summary['reply_rate']:.1f}%")


def cmd_list(args, config):
    """List founders in database."""
    db = get_db()

    status_filter = args.status or "all"
    if status_filter == "all":
        rows = db.execute("SELECT * FROM founders ORDER BY created_at DESC LIMIT 50").fetchall()
    else:
        rows = db.execute(
            "SELECT * FROM founders WHERE status = ? ORDER BY created_at DESC LIMIT 50",
            (status_filter,)
        ).fetchall()

    print(f"\n👥 Founders ({len(rows)} shown):\n")
    for f in rows:
        icon = {"new": "🆕", "contacted": "📧", "replied": "💬"}.get(f["status"], "❓")
        print(f"  {icon} {f['name']} — {f['company']} ({f['batch']})")
        print(f"     Email: {f['email'] or 'Not found'} | Status: {f['status']}")
        print()


def cmd_draft_only(args, config):
    """Draft emails without sending."""
    db = get_db()

    uncontacted = get_uncontacted_founders(db, limit=args.limit or 10)
    print(f"\n✍️  Drafting emails for {len(uncontacted)} founders...\n")

    for i, founder in enumerate(uncontacted):
        company_data = {"name": founder["company"], "website": founder["company_url"]}
        observation = get_observation_for_company(company_data, config.zen_api_key, config)

        template = get_template(i)
        founder_name = founder["name"].split()[0] if founder["name"] else "there"
        email_content = fill_template(
            template,
            founder_name=founder_name,
            company=founder["company"],
            batch=founder.get("batch", "recent batch"),
            observation=observation,
            your_name=config.your_name,
            your_link=config.your_link,
            your_github=config.your_github,
            your_portfolio=config.your_portfolio,
            your_pitch=config.your_pitch,
        )

        add_email(
            db,
            founder_id=founder["id"],
            template_key=template["name"],
            subject=email_content["subject"],
            body=email_content["body"],
            observation=observation,
        )

        print(f"To: {founder['email'] or 'NO EMAIL'}")
        print(f"Subject: {email_content['subject']}")
        print(f"Body: {email_content['body'][:200]}...")
        print()


def cmd_send_only(args, config):
    """Send already-drafted emails."""
    db = get_db()

    if not can_send_more(db, config.daily_limit):
        print(f"⛔ Daily limit reached ({config.daily_limit})")
        return

    from sender import send_email

    drafts = get_draft_emails(db, limit=config.daily_limit)
    print(f"\n📬 Sending {len(drafts)} drafted emails...\n")

    sent = 0
    for draft in drafts:
        if not can_send_more(db, config.daily_limit):
            break

        success = send_email(
            to=draft["founder_email"],
            subject=draft["subject"],
            body=draft["body"],
            config=config,
        )

        if success:
            mark_sent(db, draft["id"])
            mark_contacted(db, draft["founder_id"])
            increment_sent(db)
            sent += 1
            print(f"  ✅ Sent to {draft['founder_email']}")
        else:
            print(f"  ❌ Failed: {draft['founder_email']}")

        time.sleep(config.send_delay)

    print(f"\nDone. Sent {sent} emails.")


def cmd_init(args, config):
    """Interactive setup — creates .env file with user inputs."""
    print("\n🔧 internly — Interactive Setup\n")
    print("Answer these questions to configure internly.\n")
    print("Press Enter to skip optional fields.\n")

    fields = {
        "YOUR_NAME": ("Your name (for emails)", True),
        "YOUR_LINK": ("Your main project URL (proof you build)", True),
        "YOUR_GITHUB": ("Your GitHub profile URL", True),
        "YOUR_PORTFOLIO": ("Your portfolio URL", False),
        "YOUR_PITCH": ("Your elevator pitch (1-2 sentences)", True),
        "ZEN_API_KEY": ("OpenCode Zen API key (get at opencode.ai/auth)", True),
        "GOOGLE_GMAIL_CLIENT_ID": ("Google Cloud OAuth Client ID", True),
        "GOOGLE_GMAIL_CLIENT_SECRET": ("Google Cloud OAuth Client Secret", True),
        "GOOGLE_REFRESH_TOKEN": ("OAuth refresh token from OAuth Playground", True),
        "DAILY_LIMIT": ("Max emails per day", False),
        "SEND_DELAY": ("Seconds between sends", False),
    }

    env_lines = []
    for key, (prompt, required) in fields.items():
        default = config.__dict__.get(key.lower(), "")
        if default:
            prompt_text = f"{prompt} [{default}]"
        else:
            prompt_text = f"{prompt}" + (" *" if required else "")

        value = input(f"  {prompt_text}: ").strip()
        if not value and default:
            value = default
        if not value and required:
            print(f"    ⚠️  {key} is required. Skipping...")
            continue
        if value:
            env_lines.append(f"{key}={value}")

    # Write .env file
    env_path = Path(__file__).parent / ".env"
    with open(env_path, "w") as f:
        f.write("# internly configuration — generated by `internly.py init`\n")
        f.write("# Edit this file to change settings.\n\n")
        for line in env_lines:
            f.write(line + "\n")

    print(f"\n✅ Created .env with {len(env_lines)} settings")
    print("   Run `python internly.py stats` to verify.\n")


def main():
    parser = argparse.ArgumentParser(
        description="internly — Automated YC founder outreach",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python internly.py init                   # Interactive setup
  python internly.py daily-run              # Full pipeline
  python internly.py daily-run --limit 10   # Send max 10
  python internly.py draft --limit 5        # Draft only
  python internly.py send                   # Send drafts
  python internly.py stats                  # View stats
  python internly.py list                   # List founders
  python internly.py list --status new      # List uncontacted
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # init
    subparsers.add_parser("init", help="Interactive setup — creates .env file")

    # daily-run
    daily = subparsers.add_parser("daily-run", help="Run full daily pipeline")
    daily.add_argument("--limit", type=int, help="Max emails to send")

    # draft
    draft = subparsers.add_parser("draft", help="Draft emails without sending")
    draft.add_argument("--limit", type=int, default=10, help="Number to draft")

    # send
    subparsers.add_parser("send", help="Send drafted emails")

    # stats
    subparsers.add_parser("stats", help="Show statistics")

    # list
    ls = subparsers.add_parser("list", help="List founders")
    ls.add_argument("--status", help="Filter by status (new, contacted, replied)")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    config = load_config()

    commands = {
        "init": cmd_init,
        "daily-run": cmd_daily_run,
        "draft": cmd_draft_only,
        "send": cmd_send_only,
        "stats": cmd_stats,
        "list": cmd_list,
    }

    commands[args.command](args, config)


if __name__ == "__main__":
    main()
