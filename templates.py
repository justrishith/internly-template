"""
3 auto-approved email templates for founder outreach.
Each template is one paragraph, designed to feel personal and direct.
All personal info comes from environment variables.
"""

TEMPLATES = {
    "A": {
        "name": "built_similar",
        "subject": "Building something adjacent to {company}",
        "body": (
            "Hey {founder_name}, I came across {company} on the YC directory and spent "
            "a few minutes clicking through what you've built — {observation} I'm {your_name}, "
            "a developer who ships real products. {your_pitch} I'm looking for a small remote "
            "project or internship where I can actually contribute — not just shadow. I can "
            "commit 5-8 hours a week during the school year and way more over summer. If "
            "there's a bug, a feature, or even just documentation that needs hands, I'd love "
            "to take a crack at it this week. Worth a 10-minute email exchange?"
        ),
    },
    "B": {
        "name": "batch_congrats",
        "subject": "Congrats on {batch}",
        "body": (
            "Hi {founder_name}, congrats on getting {company} into {batch} — that's "
            "a milestone most people never reach. I'm {your_name}, a student who builds "
            "real products, not tutorial clones. {your_pitch} I'm looking for a founder "
            "who'll let me contribute to something real — a feature, a bug fix, integration "
            "work, whatever has the highest leverage right now. I'm remote, reliable, and I "
            "show up every week without being chased. If you've got 10 minutes this week, "
            "I'd love to hear what's on your plate."
        ),
    },
    "C": {
        "name": "product_observation",
        "subject": "Observation about {company}",
        "body": (
            "Hey {founder_name}, I spent 20 minutes going through {company} and "
            "{observation} I'm {your_name}, a builder with live products — {your_pitch} "
            "I'm looking for a small engineering project or internship where I can contribute "
            "remotely. I'm not looking for a paycheck first — I want experience building "
            "something that real users touch. If there's a chunk of work you've been putting "
            "off because nobody's available, I'll take it on this week. Can I send you a PR "
            "or a draft?"
        ),
    },
}

TEMPLATE_ORDER = ["A", "B", "C"]

def get_template(index: int) -> dict:
    """Get template by rotation index (0, 1, 2, 0, 1, 2, ...)."""
    key = TEMPLATE_ORDER[index % len(TEMPLATE_ORDER)]
    return TEMPLATES[key]

def fill_template(template: dict, **kwargs) -> dict:
    """Fill template with variables. Returns {subject, body}."""
    return {
        "subject": template["subject"].format(**kwargs),
        "body": template["body"].format(**kwargs),
    }
