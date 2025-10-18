"""Integration-style tests for CLI commands."""

import os
import textwrap

import pytest

from skills_mcp.cli.main import main


def create_local_skill(tmp_home, slug, content):
    """Write a SKILL.md inside the local registry."""
    skills_dir = tmp_home / "skills"
    skill_dir = skills_dir / slug
    skill_dir.mkdir(parents=True, exist_ok=True)
    (skill_dir / "SKILL.md").write_text(textwrap.dedent(content), encoding="utf-8")
    return skill_dir


@pytest.fixture()
def tmp_cli_home(tmp_path, monkeypatch):
    """Ensure CLI config and registries live in a temporary directory."""
    home = tmp_path / "cli-home"
    monkeypatch.setenv("SKILLS_MCP_HOME", str(home))
    return home


def test_list_command_outputs_table(tmp_cli_home, capsys):
    create_local_skill(
        tmp_cli_home,
        "demo-skill",
        """\
        ---
        name: Demo Skill
        description: Listed skill.
        tags:
          - sample
        ---
        Body.
        """,
    )

    main(["list"])
    output = capsys.readouterr().out

    assert "demo-skill" in output
    assert "Demo Skill" in output


def test_validate_command_reports_warnings(tmp_cli_home, capsys):
    create_local_skill(
        tmp_cli_home,
        "broken-skill",
        """\
        ---
        name: ""
        ---
        Body.
        """,
    )

    with pytest.raises(SystemExit) as excinfo:
        main(["validate"])
    output = capsys.readouterr().out

    assert excinfo.value.code == 1
    assert "broken-skill" in output
    assert "Missing 'name' in frontmatter." in output


def test_scaffold_command_creates_new_skill(tmp_cli_home, capsys):
    main(["scaffold", "new-skill"])
    output = capsys.readouterr().out

    created_file = tmp_cli_home / "skills" / "new-skill" / "SKILL.md"
    assert created_file.exists()
    assert "Created skill scaffold" in output
    content = created_file.read_text(encoding="utf-8")
    assert "New Skill" in content


def test_export_command_outputs_markdown(tmp_cli_home, capsys):
    create_local_skill(
        tmp_cli_home,
        "demo-skill",
        """\
        ---
        name: Demo Skill
        description: Listed skill.
        ---
        Body.
        """,
    )

    main(["export", "local", "demo-skill"])
    output = capsys.readouterr().out

    assert "Body." in output


def test_diff_command_shows_changes(tmp_cli_home, capsys):
    create_local_skill(
        tmp_cli_home,
        "original",
        """\
        ---
        name: Original
        description: First version.
        ---
        Body v1.
        """,
    )
    create_local_skill(
        tmp_cli_home,
        "updated",
        """\
        ---
        name: Updated
        description: Second version.
        ---
        Body v2.
        """,
    )

    main(["diff", "local", "original", "local", "updated"])
    output = capsys.readouterr().out

    assert "--- local/original" in output
    assert "+++ local/updated" in output
    assert "-Body v1." in output
    assert "+Body v2." in output
