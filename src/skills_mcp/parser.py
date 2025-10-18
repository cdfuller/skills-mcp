"""Utilities for parsing SKILL.md files."""

from hashlib import sha256
from pathlib import Path
import textwrap

import yaml


FRONTMATTER_DELIMITER = "---"
SKILL_FILENAME = "SKILL.md"


def read_skill_file(skill_path):
    """Return the contents of a SKILL.md file."""
    with skill_path.open("r", encoding="utf-8") as handle:
        return handle.read()


def split_frontmatter(raw_text):
    """Split raw SKILL.md text into frontmatter and body."""
    lines = raw_text.splitlines()
    if not lines:
        return {}, "", ["SKILL.md is empty."]

    if lines[0].strip() != FRONTMATTER_DELIMITER:
        return {}, raw_text, ["Missing YAML frontmatter delimiter."]

    end_index = None
    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == FRONTMATTER_DELIMITER:
            end_index = index
            break

    if end_index is None:
        body_text = "\n".join(lines[1:])
        return {}, body_text, ["Unterminated YAML frontmatter."]

    frontmatter_block = "\n".join(lines[1:end_index])
    body_text = "\n".join(lines[end_index + 1 :])
    warnings = []

    try:
        frontmatter = yaml.safe_load(frontmatter_block) or {}
    except yaml.YAMLError as error:
        warnings.append(f"Failed to parse frontmatter: {error}")
        frontmatter = {}

    return frontmatter, body_text, warnings


def summarize_body(markdown_text, limit=200):
    """Generate a short excerpt from the markdown body."""
    stripped = textwrap.dedent(markdown_text).strip()
    if not stripped:
        return ""

    excerpt = stripped.split("\n\n")[0]
    if len(excerpt) > limit:
        return excerpt[: limit - 3].rstrip() + "..."
    return excerpt


def parse_skill_dir(path):
    """Parse SKILL.md within the provided directory."""
    skill_file = Path(path) / SKILL_FILENAME
    if not skill_file.exists():
        return None

    raw_text = read_skill_file(skill_file)
    frontmatter, body, warnings = split_frontmatter(raw_text)

    if not isinstance(frontmatter, dict):
        warnings.append("Frontmatter must be a mapping.")
        frontmatter = {}

    name = frontmatter.get("name", "")
    description = frontmatter.get("description", "")
    if not name:
        warnings.append("Missing 'name' in frontmatter.")
    if not description:
        warnings.append("Missing 'description' in frontmatter.")

    digest = sha256(raw_text.encode("utf-8")).hexdigest()

    metadata = {
        "name": name,
        "description": description,
        "frontmatter": frontmatter,
        "body": body,
        "excerpt": summarize_body(body),
        "sha256": digest,
        "warnings": warnings,
    }
    return metadata
