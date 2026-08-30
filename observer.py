"""
Scrapes a startup's homepage and generates a one-sentence observation
using OpenCode's free model (mimo-v2.5-free).
"""

import re
import requests
from bs4 import BeautifulSoup

def scrape_homepage(url: str) -> str:
    """Scrape text from a company's homepage."""
    if not url:
        return ""

    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")

        # Remove script, style, nav, footer
        for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
            tag.decompose()

        # Get text from main content areas
        text = ""
        for tag in soup.find_all(["main", "section", "article", "div"]):
            text += tag.get_text(separator=" ", strip=True) + " "

        # Clean up
        text = re.sub(r'\s+', ' ', text).strip()
        return text[:3000]  # Limit to 3000 chars for token efficiency

    except Exception as e:
        print(f"Scrape error for {url}: {e}")
        return ""

def generate_observation(homepage_text: str, company_name: str, api_key: str, config) -> str:
    """Call the free model to generate a one-sentence observation."""
    if not api_key:
        return f"looks like they're building something interesting in the {company_name} space."

    if not homepage_text:
        return f"the product seems solid based on what I can see from {company_name}'s site."

    prompt = f"""Read this startup's homepage text. Write ONE specific sentence about what they do well or what could be improved.

Rules:
- Be factual, not flattering
- No "I'm impressed" or "great work"
- Reference something specific (a feature, a UX choice, a positioning angle)
- One sentence, under 30 words
- If you can't find anything specific, say "the product seems well-structured for its target users"

Homepage text from {company_name}:
{homepage_text[:2000]}

One specific observation:"""

    try:
        import requests as req
        resp = req.post(
            config.zen_url,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": config.zen_model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 80,
                "temperature": 0.7,
            },
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        observation = data["choices"][0]["message"]["content"].strip()

        # Clean up: remove quotes, trailing period issues
        observation = observation.strip('"\'')
        if not observation.endswith("."):
            observation += "."

        return observation

    except Exception as e:
        print(f"Model error: {e}")
        return f"the product seems well-structured for its target users."

def get_observation_for_company(company: dict, api_key: str, config) -> str:
    """Full pipeline: scrape homepage -> generate observation."""
    url = company.get("website", "")
    name = company.get("name", "this company")

    homepage_text = scrape_homepage(url)
    observation = generate_observation(homepage_text, name, api_key, config)

    return observation
