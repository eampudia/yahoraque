"""The AI's instructions, kept in prompts/*.md so anyone can read and reuse them.

Each file starts with an HTML comment that explains it, followed by sections
("## Title"). {PLACEHOLDERS} are filled in by the code that uses the prompt.
"""

import re
from pathlib import Path

PROMPTS_DIR = Path(__file__).parent / "prompts"
LEADING_COMMENT = re.compile(r"\A\s*<!--.*?-->\s*", re.DOTALL)
SECTION_TITLE = re.compile(r"^## (.+)$", re.MULTILINE)


def load(name):
    """The sections of prompts/<name>.md: {title: text}."""
    text = LEADING_COMMENT.sub("", (PROMPTS_DIR / f"{name}.md").read_text(encoding="utf-8"))
    parts = SECTION_TITLE.split(text)
    # parts = [text before the first title, title, text, title, text, ...]
    return {title.strip(): body.strip() for title, body in zip(parts[1::2], parts[2::2])}


def fill(template, **values):
    """Replace each {KEY} with its value. Other braces (JavaScript, CSS) stay as they are."""
    for key, value in values.items():
        template = template.replace(f"{{{key}}}", str(value))
    return template
