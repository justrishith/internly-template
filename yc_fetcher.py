"""
Fetches YC-backed companies from the free yc-oss/api.
No API key needed. Filters by batch and stage.
"""

import json
import requests
from typing import Optional
from config import load_config

YC_API_BASE = "https://yc-oss.github.io/api/companies"

def fetch_all_companies() -> list[dict]:
    """Fetch all YC companies from the public API."""
    url = f"{YC_API_BASE}/all.json"
    try:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"Error fetching YC companies: {e}")
        return []

def filter_companies(
    companies: list[dict],
    batches: Optional[list[str]] = None,
    stages: Optional[list[str]] = None,
    status: str = "Active",
) -> list[dict]:
    """Filter companies by batch, stage, and status."""
    config = load_config()
    batches = batches or config.yc_batches
    stages = stages or config.yc_stages

    filtered = []
    for c in companies:
        # Status filter
        if c.get("status", "").lower() != status.lower():
            continue

        # Batch filter
        company_batch = c.get("batch", "")
        if company_batch not in batches:
            continue

        # Stage filter
        company_stage = c.get("stage", "")
        if company_stage and company_stage not in stages:
            continue

        filtered.append({
            "id": c.get("id"),
            "name": c.get("name", ""),
            "slug": c.get("slug", ""),
            "website": c.get("website", ""),
            "description": c.get("one_liner", "") or c.get("long_description", ""),
            "batch": company_batch,
            "stage": company_stage,
            "industries": c.get("industries", []),
            "tags": c.get("tags", []),
            "team_size": c.get("team_size", 0),
            "is_hiring": c.get("isHiring", False),
            "yc_url": c.get("url", ""),
        })

    return filtered

def get_founder_info(slug: str) -> dict:
    """
    Try to get founder info from the YC company page.
    Returns {name, role, linkedin} or empty dict.
    """
    url = f"https://www.ycombinator.com/companies/{slug}"
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        resp = requests.get(url, headers=headers, timeout=10)

        import re
        import html

        # The page has HTML-encoded JSON with founder data
        # Look for "founders":[{...}] pattern
        decoded = html.unescape(resp.text)

        # Find founder names in the decoded content
        founders = []
        linkedins = []

        # Pattern for full_name in founder objects
        name_matches = re.findall(r'"full_name"\s*:\s*"([^"]+)"', decoded)
        founders = [n for n in name_matches if n and len(n) > 2]

        # Pattern for LinkedIn URLs
        linkedin_matches = re.findall(r'https?://linkedin\.com/in/[a-zA-Z0-9_-]+', decoded)
        linkedins = linkedin_matches

        if founders:
            return {
                "name": founders[0],
                "all_founders": founders[:3],
                "linkedin": linkedins[0] if linkedins else "",
            }
    except Exception:
        pass

    return {}

def fetch_and_filter(batch_limit: int = 50) -> list[dict]:
    """Main entry: fetch YC companies, filter, return ready-to-use list."""
    print("Fetching YC companies...")
    all_companies = fetch_all_companies()
    print(f"Total YC companies: {len(all_companies)}")

    filtered = filter_companies(all_companies)
    print(f"After filtering (batches S24-W25, pre-seed/seed): {len(filtered)}")

    # Limit to batch size
    return filtered[:batch_limit]
