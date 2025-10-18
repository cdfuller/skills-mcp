"""Tests for read-only tool helpers."""

import os
import textwrap

from skills_mcp.registry import SkillRegistry
from skills_mcp.resources import SkillResourceAdapter
from skills_mcp.tools import (
    changes_since,
    get_skill_detail,
    registry_info,
    search_skills,
)


def write_skill(skill_dir, contents):
    """Write SKILL.md with provided contents."""
    skill_dir.mkdir(parents=True, exist_ok=True)
    (skill_dir / "SKILL.md").write_text(textwrap.dedent(contents), encoding="utf-8")


def build_adapter(tmp_path):
    """Create a registry and adapter for tool tests."""
    registry_path = tmp_path / "catalog"
    registry_path.mkdir()

    write_skill(
        registry_path / "alpha",
        """\
        ---
        name: Alpha Skill
        description: Demonstrates search.
        tags:
          - greetings
        ---
        Hello body.
        """,
    )
    write_skill(
        registry_path / "beta",
        """\
        ---
        name: Beta Skill
        description: Includes advanced workflows.
        tags:
          - workflows
        ---
        Detailed body.
        """,
    )

    registry = SkillRegistry(
        [{"id": "catalog", "path": registry_path, "writable": False, "tags": []}]
    )
    adapter = SkillResourceAdapter(registry)
    return registry, adapter


def test_search_skills_filters_by_query_and_tags(tmp_path):
    _, adapter = build_adapter(tmp_path)

    result = search_skills(adapter, query="advanced", tags=["workflows"])
    assert result["results"][0]["slug"] == "beta"
    assert result["exhausted"] is True


def test_get_skill_detail_returns_full_content(tmp_path):
    _, adapter = build_adapter(tmp_path)

    detail = get_skill_detail(adapter, "catalog", "alpha")
    assert detail["metadata"]["display_name"] == "Alpha Skill"
    assert "Hello body." in detail["content"]["body"]


def test_registry_info_returns_summary(tmp_path):
    registry, adapter = build_adapter(tmp_path)

    info = registry_info(adapter)
    assert info["registries"] == registry.summary()


def test_changes_since_detects_updates(tmp_path):
    registry, adapter = build_adapter(tmp_path)

    # Record initial state
    initial_alpha = adapter.registry.find_skill("catalog", "alpha")["metadata"]["sha256"]
    initial_beta = adapter.registry.find_skill("catalog", "beta")["metadata"]["sha256"]

    alpha_path = tmp_path / "catalog" / "alpha" / "SKILL.md"
    alpha_path.write_text(
        textwrap.dedent(
            """\
            ---
            name: Alpha Skill
            description: Updated copy.
            tags:
              - greetings
            ---
            Updated body.
            """
        ),
        encoding="utf-8",
    )

    current = alpha_path.stat().st_mtime
    os.utime(alpha_path, (current + 5, current + 5))

    adapter.registry.refresh()

    changes = changes_since(
        adapter,
        registry_id="catalog",
        hashes=[initial_alpha, initial_beta],
    )
    assert len(changes["updated"]) == 1
    assert changes["updated"][0]["slug"] == "alpha"
