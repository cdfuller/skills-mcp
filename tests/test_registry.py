"""Tests for skills_mcp.registry."""

import os
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


def test_refresh_reuses_cached_records_when_unmodified(tmp_path):
    registry_path = create_registry(
        tmp_path,
        "catalog",
        [
            (
                "epsilon",
                """\
                ---
                name: Epsilon Skill
                description: Cached skill.
                ---
                Body.
                """,
            ),
        ],
    )

    registry = SkillRegistry(
        [{"id": "catalog", "path": registry_path, "writable": False, "tags": []}]
    )

    initial = registry.find_skill("catalog", "epsilon")
    registry.refresh()
    cached = registry.find_skill("catalog", "epsilon")

    assert cached is initial


def test_refresh_detects_modified_skill(tmp_path):
    registry_path = create_registry(
        tmp_path,
        "catalog",
        [
            (
                "zeta",
                """\
                ---
                name: Zeta Skill
                description: Original description.
                ---
                Body v1.
                """,
            ),
        ],
    )

    registry = SkillRegistry(
        [{"id": "catalog", "path": registry_path, "writable": False, "tags": []}]
    )

    original = registry.find_skill("catalog", "zeta")
    skill_file = registry_path / "zeta" / "SKILL.md"
    skill_file.write_text(
        textwrap.dedent(
            """\
            ---
            name: Zeta Skill
            description: Updated description.
            ---
            Body v2.
            """
        ),
        encoding="utf-8",
    )
    current_mtime = skill_file.stat().st_mtime
    os.utime(skill_file, (current_mtime + 5, current_mtime + 5))

    registry.refresh()
    updated = registry.find_skill("catalog", "zeta")

    assert updated is not original
    assert (
        updated["metadata"]["sha256"] != original["metadata"]["sha256"]
    ), "Digest should change when file content changes."
    assert updated["metadata"]["description"] == "Updated description."


def test_refresh_removes_deleted_skill(tmp_path):
    registry_path = create_registry(
        tmp_path,
        "catalog",
        [
            (
                "theta",
                """\
                ---
                name: Theta Skill
                description: To be deleted.
                ---
                Body.
                """,
            ),
        ],
    )

    registry = SkillRegistry(
        [{"id": "catalog", "path": registry_path, "writable": False, "tags": []}]
    )

    assert registry.find_skill("catalog", "theta") is not None

    for path in (registry_path / "theta").glob("**/*"):
        if path.is_file():
            path.unlink()
    (registry_path / "theta").rmdir()

    registry.refresh()
    assert registry.find_skill("catalog", "theta") is None
    assert registry.summary() == [
        {"id": "catalog", "path": str(registry_path), "writable": False, "count": 0}
    ]


def test_warning_report_includes_skills_with_warnings(tmp_path):
    registry_path = create_registry(
        tmp_path,
        "catalog",
        [
            (
                "iota",
                """\
                ---
                description: Missing name.
                ---
                Body.
                """,
            ),
            (
                "kappa",
                """\
                ---
                name: Kappa Skill
                description: Complete entry.
                ---
                Body.
                """,
            ),
        ],
    )

    registry = SkillRegistry(
        [{"id": "catalog", "path": registry_path, "writable": False, "tags": []}]
    )

    reports = registry.warning_report()

    assert len(reports) == 1
    report = reports[0]
    assert report["slug"] == "iota"
    assert report["registry_id"] == "catalog"
    assert "Missing 'name' in frontmatter." in report["warnings"]


def test_cache_ttl_forces_refresh(tmp_path):
    registry_path = create_registry(
        tmp_path,
        "catalog",
        [
            (
                "omega",
                """\
                ---
                name: Omega Skill
                description: Initial description.
                ---
                Body v1.
                """,
            ),
        ],
    )

    registry = SkillRegistry(
        [{"id": "catalog", "path": registry_path, "writable": False, "tags": []}],
        cache_ttl=0,
    )

    first = registry.list_skills()[0]

    skill_file = registry_path / "omega" / "SKILL.md"
    skill_file.write_text(
        textwrap.dedent(
            """\
            ---
            name: Omega Skill
            description: Updated description.
            ---
            Body v2.
            """
        ),
        encoding="utf-8",
    )
    current = skill_file.stat().st_mtime
    os.utime(skill_file, (current + 5, current + 5))

    updated = registry.list_skills()[0]

    assert updated is not first
    assert updated["metadata"]["description"] == "Updated description."
