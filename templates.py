"""
5 email templates for founder outreach.
Written in Rishith's natural voice — direct, short, no fluff.

Each template uses variables:
  {founder_name}  — first name of the founder
  {company}       — company name
  {batch}         — YC batch (Summer 2024, etc.)
  {observation}   — AI-generated observation about their product
  {your_name}     — your name from .env
  {your_link}     — your project URL from .env
  {your_pitch}    — your elevator pitch from .env

Edit these to match your voice. The AI observation ({observation}) makes
each email feel personal without you writing each one from scratch.
"""

TEMPLATES = {
    "A": {
        "name": "built_similar",
        "subject": "{company}",
        "body": (
            "Hi {founder_name},\n"
            "\n"
            "Came across {company} on YC. {observation}\n"
            "\n"
            "I'm {your_name}. {your_pitch} Looking for a small remote "
            "project or internship where I can ship code. 5-8 hours a "
            "week during school, more in summer.\n"
            "\n"
            "If you've got something that needs hands, I can take a "
            "crack at it this week.\n"
            "\n"
            "Thanks,\n"
            "{your_name}"
        ),
    },
    "B": {
        "name": "batch_congrats",
        "subject": "Congrats on {batch}",
        "body": (
            "Hi {founder_name},\n"
            "\n"
            "Congrats on getting {company} into {batch}.\n"
            "\n"
            "I'm {your_name}. {your_pitch} I'm looking for a founder "
            "who'll let me contribute to something real. Feature, bug "
            "fix, docs, whatever's highest leverage.\n"
            "\n"
            "Got 10 minutes this week?\n"
            "\n"
            "Thanks,\n"
            "{your_name}"
        ),
    },
    "C": {
        "name": "product_observation",
        "subject": "{company}",
        "body": (
            "Hey {founder_name},\n"
            "\n"
            "Spent a few minutes on {company}. {observation}\n"
            "\n"
            "I'm {your_name}. {your_pitch} Looking for a small project "
            "or internship where I can contribute remotely. Not after "
            "the paycheck, I want to build stuff users actually touch.\n"
            "\n"
            "If there's something you've been putting off, throw it "
            "at me.\n"
            "\n"
            "Thanks,\n"
            "{your_name}"
        ),
    },
    "D": {
        "name": "short_direct",
        "subject": "Quick question",
        "body": (
            "Hi {founder_name},\n"
            "\n"
            "I'm {your_name}. {your_pitch}\n"
            "\n"
            "I'm looking for a small engineering project or internship. "
            "Remote, 5-8 hours a week. I ship fast and I don't need "
            "hand-holding.\n"
            "\n"
            "Anything you need help with?\n"
            "\n"
            "Thanks,\n"
            "{your_name}"
        ),
    },
    "E": {
        "name": "specific_contribution",
        "subject": "{company}",
        "body": (
            "Hey {founder_name},\n"
            "\n"
            "I was looking at {company} and noticed {observation}\n"
            "\n"
            "I'm {your_name}. {your_pitch} I can probably knock that "
            "out this week if you're open to it.\n"
            "\n"
            "Worth a quick exchange?\n"
            "\n"
            "Thanks,\n"
            "{your_name}"
        ),
    },
}

TEMPLATE_ORDER = ["A", "B", "C", "D", "E"]


def get_template(index: int) -> dict:
    """Get template by rotation (0, 1, 2, 3, 4, 0, 1, ...)."""
    key = TEMPLATE_ORDER[index % len(TEMPLATE_ORDER)]
    return TEMPLATES[key]


def fill_template(template: dict, **kwargs) -> dict:
    """Fill template with variables. Returns {subject, body}."""
    return {
        "subject": template["subject"].format(**kwargs),
        "body": template["body"].format(**kwargs),
    }
