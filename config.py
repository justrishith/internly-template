import os
from pathlib import Path
from dataclasses import dataclass, field

BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / "internly.db"

@dataclass
class Config:
    # Zen API (for generating observations)
    zen_api_key: str = field(default_factory=lambda: os.getenv("ZEN_API_KEY", ""))
    zen_model: str = "mimo-v2.5-free"
    zen_url: str = "https://opencode.ai/zen/v1/chat/completions"

    # Gmail (for sending)
    gmail_client_id: str = field(default_factory=lambda: os.getenv("GOOGLE_GMAIL_CLIENT_ID", ""))
    gmail_client_secret: str = field(default_factory=lambda: os.getenv("GOOGLE_GMAIL_CLIENT_SECRET", ""))
    gmail_refresh_token: str = field(default_factory=lambda: os.getenv("GOOGLE_REFRESH_TOKEN", ""))

    # Sending config
    daily_limit: int = field(default_factory=lambda: int(os.getenv("DAILY_LIMIT", "25")))
    send_delay: float = field(default_factory=lambda: float(os.getenv("SEND_DELAY", "2.0")))

    # Your info — all from env, no hardcoded values
    your_name: str = field(default_factory=lambda: os.getenv("YOUR_NAME", ""))
    your_link: str = field(default_factory=lambda: os.getenv("YOUR_LINK", ""))
    your_github: str = field(default_factory=lambda: os.getenv("YOUR_GITHUB", ""))
    your_portfolio: str = field(default_factory=lambda: os.getenv("YOUR_PORTFOLIO", ""))
    your_pitch: str = field(default_factory=lambda: os.getenv("YOUR_PITCH", ""))

    # YC filtering
    yc_batches: list = field(default_factory=lambda: os.getenv(
        "YC_BATCHES", "Summer 2024,Winter 2025,Summer 2025,Winter 2026"
    ).split(","))
    yc_stages: list = field(default_factory=lambda: os.getenv(
        "YC_STAGES", "Early,Growth"
    ).split(","))

def load_config() -> Config:
    return Config()
