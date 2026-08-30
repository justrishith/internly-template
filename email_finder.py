"""
Email finder using OpenLeads for founder contact discovery.
Falls back to web scraping if OpenLeads isn't available.
"""

import re
import requests
from typing import Optional

def find_email_openleads(name: str, company_url: str) -> Optional[str]:
    """Try to find email using OpenLeads (local, no API key)."""
    try:
        import openleads
        ol = openleads.OpenLeads()
        results = ol.find_email(name=name, domain=company_url)
        if results and len(results) > 0:
            return results[0].get("email")
    except ImportError:
        pass  # OpenLeads not installed, fall back
    except Exception:
        pass

    return None

def find_email_scrape(company_url: str) -> list[str]:
    """Scrape company website for email addresses."""
    emails = []
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'

    # Only check main page and /contact — fast
    for path in ["", "/contact"]:
        try:
            url = company_url.rstrip("/") + path
            resp = requests.get(url, headers=headers, timeout=5)
            found = re.findall(email_pattern, resp.text)
            for e in found:
                if not e.endswith(('.png', '.jpg', '.gif', '.css', '.js')):
                    emails.append(e)
        except Exception:
            continue

    # Deduplicate while preserving order
    seen = set()
    unique = []
    for e in emails:
        if e.lower() not in seen:
            seen.add(e.lower())
            unique.append(e)

    return unique

def find_founder_email(founder_name: str, company_url: str) -> Optional[str]:
    """
    Find a founder's email. Tries multiple strategies:
    1. OpenLeads (if installed)
    2. Web scraping for any email on the site
    3. Returns None if nothing found
    """
    # Strategy 1: OpenLeads
    email = find_email_openleads(founder_name, company_url)
    if email:
        return email

    # Strategy 2: Scrape website
    emails = find_email_scrape(company_url)
    if emails:
        # Try to match by founder name parts
        name_parts = founder_name.lower().split()
        for e in emails:
            local = e.split("@")[0].lower()
            # Check if any name part matches the email local part
            if any(part in local for part in name_parts if len(part) > 2):
                return e

        # If no name match, return the first one (usually info@ or hello@)
        # Skip generic addresses
        generic = ["info", "hello", "contact", "support", "admin", "noreply"]
        for e in emails:
            local = e.split("@")[0].lower()
            if not any(g in local for g in generic):
                return e

        # Return first non-generic or first overall
        return emails[0]

    return None
