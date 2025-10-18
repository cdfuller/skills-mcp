"""Tests for SkillResourceAdapter."""

import textwrap

from skills_mcp.registry import SkillRegistry
from skills_mcp.resources import SkillResourceAdapter


def write_skill(skill_dir, contents):
    """Write SKILL.md with provided contents."""
    skill_dir.mkdir(parents=True, exist_ok=True)
    (skill_dir / "SKILL.md").write_text(textwrap.dedent(contents), encoding="utf-8")


def create_registry(tmp_path, registry_id, skills):
    """Create a registry directory with provided skill definitions."""
    registry_path = tmp_path / registry_id
    registry_path.mkdir()
    for slug, contents in skills:
        write_skill(registry_path / slug, contents)
    return registry_path


def build_adapter(tmp_path):
    """Construct a registry and adapter for testing."""
    primary = create_registry(
        tmp_path,
        "primary",
        [
            (
                "first",
                """\
                ---
                name: First Skill
                description: Primary registry entry.
                tags:
                  - alpha
                ---
                Body A.
                """,
            ),
            (
                "second",
                """\
                ---
                name: Second Skill
                description: Additional entry.
                tags:
                  - beta
                ---
                Body B.
                """,
            ),
        ],
    )

    secondary = create_registry(
        tmp_path,
        "secondary",
        [
            (
                "third",
                """\
                ---
                name: Third Skill
                description: Different registry.
                tags:
                  - alpha
                  - gamma
                ---
                Body C.
                """,
            ),
        ],
    )

    registry = SkillRegistry(
        [
            {"id": "primary", "path": primary, "writable": False, "tags": ["ref"]},
            {"id": "secondary", "path": secondary, "writable": True, "tags": ["local"]},
        ]
    )
    adapter = SkillResourceAdapter(registry)
    return registry, adapter


def test_list_resources_returns_sorted_results(tmp_path):
    _, adapter = build_adapter(tmp_path)

    page = adapter.list_resources()

    ids = [item["id"] for item in page["items"]]
    assert ids == [
        "skill://primary/first",
        "skill://primary/second",
        "skill://secondary/third",
    ]
    assert page["total"] == 3


def test_list_resources_supports_pagination(tmp_path):
    _, adapter = build_adapter(tmp_path)

    page_one = adapter.list_resources(limit=2)
    assert len(page_one["items"]) == 2
    assert page_one["next_cursor"] == "2"

    page_two = adapter.list_resources(cursor=page_one["next_cursor"], limit=2)
    assert len(page_two["items"]) == 1
    assert page_two["next_cursor"] is None


def test_list_resources_filters_by_registry_and_tags(tmp_path):
    _, adapter = build_adapter(tmp_path)

    filtered = adapter.list_resources(registry_ids=["secondary"], tags={"alpha"})
    assert [item["slug"] for item in filtered["items"]] == ["third"]


def test_get_resource_returns_metadata_and_content(tmp_path):
    _, adapter = build_adapter(tmp_path)

    data = adapter.get_resource("skill://primary/first")

    assert data["resource"]["display_name"] == "First Skill"
    assert data["resource"]["registry_id"] == "primary"
    assert data["content"]["body"].strip() == "Body A."


def test_parse_resource_id_handles_invalid_inputs():
    adapter = SkillResourceAdapter(SkillRegistry([]))

    assert adapter.parse_resource_id("skill://abc/def") == ("abc", "def")
    assert adapter.parse_resource_id("skill://missing") is None
    assert adapter.parse_resource_id("other://wrong") is None
