"""Tests for skills_mcp.parser."""

import textwrap

from skills_mcp.parser import parse_skill_dir


def write_skill(tmp_path, slug, contents):
    """Create a temporary skill directory with provided SKILL.md contents."""
    skill_dir = tmp_path / slug
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text(textwrap.dedent(contents), encoding="utf-8")
    return skill_dir


def test_parse_skill_dir_returns_metadata_for_valid_skill(tmp_path):
    skill_dir = write_skill(
        tmp_path,
        "demo-skill",
        """\
        ---
        name: Sample Skill
        description: Demonstrates parsing happy path.
        tags:
          - demo
        ---
        First paragraph describing the skill.

        Second paragraph with additional details.
        """,
    )

    metadata = parse_skill_dir(skill_dir)

    assert metadata["name"] == "Sample Skill"
    assert metadata["description"] == "Demonstrates parsing happy path."
    assert metadata["frontmatter"]["tags"] == ["demo"]
    assert metadata["body"].startswith("First paragraph describing the skill.")
    assert metadata["excerpt"] == "First paragraph describing the skill."
    assert metadata["warnings"] == []
    assert len(metadata["sha256"]) == 64


def test_parse_skill_dir_missing_frontmatter_delimiter_warns(tmp_path):
    skill_dir = write_skill(
        tmp_path,
        "missing-frontmatter",
        """\
        # Heading

        Body without any YAML frontmatter.
        """,
    )

    metadata = parse_skill_dir(skill_dir)

    assert "Missing YAML frontmatter delimiter." in metadata["warnings"]
    assert metadata["name"] == ""
    assert metadata["description"] == ""


def test_parse_skill_dir_invalid_yaml_frontmatter_warns(tmp_path):
    skill_dir = write_skill(
        tmp_path,
        "invalid-frontmatter",
        """\
        ---
        name: Broken Example
        description: "Unterminated string
        ---
        Body content that should still be parsed.
        """,
    )

    metadata = parse_skill_dir(skill_dir)

    assert any(
        warning.startswith("Failed to parse frontmatter")
        for warning in metadata["warnings"]
    )
    assert "Missing 'name' in frontmatter." in metadata["warnings"]
    assert "Missing 'description' in frontmatter." in metadata["warnings"]
    assert metadata["body"].startswith("Body content that should still be parsed.")


def test_parse_skill_dir_requires_mapping_frontmatter(tmp_path):
    skill_dir = write_skill(
        tmp_path,
        "list-frontmatter",
        """\
        ---
        - name: Nested
          description: Example wrapped in list.
        ---
        Body remains accessible even if metadata fails.
        """,
    )

    metadata = parse_skill_dir(skill_dir)

    assert "Frontmatter must be a mapping." in metadata["warnings"]
    assert "Missing 'name' in frontmatter." in metadata["warnings"]
    assert "Missing 'description' in frontmatter." in metadata["warnings"]
    assert metadata["name"] == ""
    assert metadata["description"] == ""
