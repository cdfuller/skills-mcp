"""Tests for skills_mcp.registry."""

import textwrap

from skills_mcp.registry import SkillRegistry


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


def test_summary_counts_and_paths(tmp_path):
    first_registry = create_registry(
        tmp_path,
        "primary",
        [
            (
                "alpha",
                """\
                ---
                name: Alpha Skill
                description: First skill entry.
                ---
                Alpha body.
                """,
            ),
            (
                "beta",
                """\
                ---
                name: Beta Skill
                description: Second skill entry.
                ---
                Beta body.
                """,
            ),
        ],
    )

    second_registry = create_registry(
        tmp_path,
        "secondary",
        [
            (
                "gamma",
                """\
                ---
                name: Gamma Skill
                description: Third skill entry.
                ---
                Gamma body.
                """,
            ),
        ],
    )

    registry = SkillRegistry(
        [
            {"id": "primary", "path": first_registry, "writable": False, "tags": []},
            {"id": "secondary", "path": second_registry, "writable": True, "tags": []},
        ]
    )

    summary = registry.summary()

    assert summary == [
        {
            "id": "primary",
            "path": str(first_registry),
            "writable": False,
            "count": 2,
        },
        {
            "id": "secondary",
            "path": str(second_registry),
            "writable": True,
            "count": 1,
        },
    ]


def test_list_skills_and_find_skill(tmp_path):
    registry_path = create_registry(
        tmp_path,
        "catalog",
        [
            (
                "delta",
                """\
                ---
                name: Delta Skill
                description: Discoverable skill.
                ---
                Delta body.
                """,
            ),
        ],
    )

    registry = SkillRegistry(
        [{"id": "catalog", "path": registry_path, "writable": True, "tags": ["demo"]}]
    )

    skills = registry.list_skills()

    assert len(skills) == 1
    record = skills[0]
    assert record["registry_id"] == "catalog"
    assert record["slug"] == "delta"
    assert record["metadata"]["name"] == "Delta Skill"
    assert record["writable"] is True
    assert record["tags"] == ["demo"]

    located = registry.find_skill("catalog", "delta")
    assert located["metadata"]["description"] == "Discoverable skill."


def test_registry_skips_directories_without_skill_file(tmp_path):
    registry_path = tmp_path / "empty"
    (registry_path / "incomplete").mkdir(parents=True)
    # Directory exists but no SKILL.md inside.

    registry = SkillRegistry(
        [{"id": "empty", "path": registry_path, "writable": False, "tags": []}]
    )

    assert registry.summary() == [
        {"id": "empty", "path": str(registry_path), "writable": False, "count": 0}
    ]
    assert registry.list_skills() == []
    assert registry.find_skill("empty", "missing") is None
