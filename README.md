# skills-mcp

Expose Claude Skills via an MCP server.

skills-mcp is a read-only bridge that discovers skills across registries, validates each `SKILL.md`, and serves the metadata through both an MCP server and a CLI.  
You can list the skills you have, check for missing frontmatter, scaffold a new skill directory, or hand the metadata to an MCP-compatible agent—without touching upstream sources.

## Quickstart
- `uv pip install -e .` — install the package in editable mode.
- `uv run pytest` — execute the test suite.
- `uv run python -m skills_mcp.server` — launch the (stub) MCP server to verify registry discovery.
- `uv run skills-cli --help` — explore the CLI once the package is installed.

## Requirements
- Python 3.13 (or newer) — suggested Homebrew interpreter at `/opt/homebrew/bin/python3.13`.
- [uv](https://github.com/astral-sh/uv) for dependency management and execution.
- Read access to any referenced registries (e.g., `anthropic-skills/` or local `skills/` directories).

## Running the MCP Server
The MCP entrypoint is still a stub while transport wiring is built, but you can confirm configuration with:

```bash
uv run python -m skills_mcp.server
```

The command lists all discovered registries and available tools (`skills.search`, `skills.detail`, `skills.registry_info`, `skills.changes_since`). When the stdio transport is implemented, this module will host the Codex MCP loop without further changes.

## CLI Usage
`skills-cli` reuses the shared registry cache and parser logic. Sample workflows:

```bash
# Show configured registries and skill counts
uv run skills-cli status

# List up to 20 skills tagged with "demo" from the local registry
uv run skills-cli list --registry local --tag demo --limit 20

# Validate every configured skill and surface warnings
uv run skills-cli validate

# Scaffold a new skill into the first writable registry using the built-in template
uv run skills-cli scaffold my-new-skill

# Export a skill as JSON for inspection
uv run skills-cli export local my-new-skill --format json

# Compare two skills side-by-side
uv run skills-cli diff local my-new-skill anthropic template-skill
```

Templates live under `src/skills_mcp/templates/` — `scaffold` enforces writable registry checks before copying the `basic_skill` scaffold into the target directory.

## Validation & Warnings
The parser enforces YAML frontmatter delimiters, required `name`/`description` fields, and mapping-shaped metadata. Missing fields or malformed YAML result in warnings that show up in:
- `uv run skills-cli validate`
- `skills_mcp.registry.SkillRegistry.warning_report()`
- MCP tool responses (once the server is wired up)

Use the CLI to troubleshoot issues locally before publishing new skills.

## Change Detection & Caching
`SkillRegistry` keeps an in-memory cache keyed by registry and directory slug. It refreshes entries only when the on-disk `SKILL.md` mtime changes, so `list`, `export`, and MCP tools respond quickly on subsequent calls. Editing or removing files triggers a new parse on the next `refresh()`; `scaffold` calls refresh automatically after creating a new skill.

### Cache TTL
- `SKILLS_MCP_CACHE_TTL=<seconds>` — optional environment variable that forces a refresh after the given number of seconds. Set to `0` to always rescan, or leave unset to reuse the cache indefinitely.

## Logging
- `SKILLS_MCP_LOG_LEVEL=DEBUG` (or INFO/WARNING/ERROR) controls package logging. The CLI and MCP server configure Python's logging once per run.

## Troubleshooting
- **`uv` sandbox errors:** retry the failing command with elevated permissions when prompted; the CLI may need to read cached sdists under `~/.cache/uv/`.
- **Missing registries:** set `SKILLS_MCP_HOME` or edit `~/.config/skills-mcp/skills_mcp.toml` to declare additional registry paths.
- **Template issues:** ensure `src/skills_mcp/templates/basic_skill/SKILL.md` exists; `scaffold` aborts if it cannot find the template.
- **Validation failures:** run `uv run skills-cli validate -- path/to/skill_dir` to inspect a specific skill in isolation.
