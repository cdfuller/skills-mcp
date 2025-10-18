# Technical Specification Document — skills-mcp

## Architecture Overview
- **Language & Tooling:** Python 3.13, packaged with `uv`. Project structured as a Python package (`skills_mcp`) with both MCP server entrypoints and CLI commands.
- **Core Components:**
  1. **Registry Manager:** Discovers, normalizes, and caches Skill directories from configured sources.
  2. **Skill Parser:** Reads `SKILL.md`, extracts YAML frontmatter and Markdown body, validates required fields, and computes derived metadata (hash, summary snippet).
  3. **Resource Adapter:** Maps parsed Skills to MCP resources and handles resource pagination, filtering, and detail retrieval.
  4. **Tool Handler:** Implements read-only MCP tools (search, detail retrieval, registry info) with deterministic outputs.
  5. **CLI Wrapper:** Reuses the Registry Manager and Skill Parser for local commands (list, validate, scaffold, export).
  6. **Caching Layer:** Maintains in-memory cache keyed by registry path + file mtime/hash, with optional on-disk cache for large catalogs.
  7. **Remote Importer:** Fetches Skills from remote Git repositories or direct URLs, verifies structure, and stages them into the CLI configuration directory.
  8. **Configuration Loader:** Reads `skills_mcp.toml` (or environment variables) to define registry paths, cache preferences, CLI defaults.

```
┌────────────────┐     ┌────────────────┐     ┌────────────────┐
│ Registry Paths │──▶──│ Registry       │──▶──│ Skill Parser   │
│ (filesystem)   │     │ Manager        │     │ (YAML+Markdown)│
└────────────────┘     └────────────────┘     └────────────────┘
                                            │    ▲
                                            ▼    │
                                         ┌────────────────┐
                                         │ Skill Metadata │
                                         └────────────────┘
                                            ▲    │
                    ┌─────────────────┬─────┘    └─────┬─────────────────┐
                    │                 │                │                 │
            ┌─────────────┐  ┌─────────────┐   ┌─────────────┐  ┌──────────────┐
            │ MCP Resources│  │ MCP Tools   │   │ CLI Commands│  │ Cache Manager │
            └─────────────┘  └─────────────┘   └─────────────┘  └──────────────┘
```

## Module Structure (Proposed)
- `skills_mcp/__init__.py`
- `skills_mcp/config.py`
- `skills_mcp/registry.py`
- `skills_mcp/parser.py`
- `skills_mcp/cache.py`
- `skills_mcp/resources.py`
- `skills_mcp/tools.py`
- `skills_mcp/server.py` (MCP entrypoint, stdio)
- `skills_mcp/cli/__init__.py`
- `skills_mcp/cli/commands.py`
- `skills_mcp/cli/main.py`
- `skills_mcp/templates/` (skill template assets)
- `tests/` (unit + integration tests)

## Data Models
```python
class RegistryConfig(TypedDict):
    id: str                 # e.g., "anthropic-examples"
    path: Path              # Source directory (read-only)
    writable: bool          # False for upstream catalogs, True for user workspace
    tags: list[str]         # Optional categorical tags for grouping

class SkillMetadata(TypedDict):
    registry_id: str
    slug: str               # Directory name
    name: str               # From frontmatter
    description: str        # From frontmatter
    frontmatter: dict
    markdown: str
    excerpt: str            # First N sentences
    sha256: str             # Hash of file contents
    last_modified: datetime
    path: Path
    warnings: list[str]     # Validation issues
```

## MCP Resource Design
- **Resource Namespace:** `skill://{registry_id}/{slug}`
  - Resource metadata fields:
    - `display_name`
    - `description`
    - `registry` (ID, label)
    - `excerpt`
    - `tags` (from frontmatter or directory naming)
    - `hash`, `last_modified`
    - `warnings` (if any)
- **Resource Payload (`content`):** JSON object with keys `frontmatter` and `body`.
- **Pagination:** Resource listing implements cursor-based pagination (e.g., `page_size` default 20 with `next_cursor`).

## MCP Tools (Read-Only)
| Tool | Description | Input Schema | Output Schema |
|------|-------------|--------------|---------------|
| `skills.search` | Query skills by keyword, registry, tags | `{ query: str?, registry_ids: list[str]?, tags: list[str]?, limit: int? }` | `{ results: list[SkillSummary], exhausted: bool }` |
| `skills.detail` | Retrieve full metadata + content for a skill | `{ registry_id: str, slug: str }` | `{ metadata: SkillMetadata, content: { frontmatter, body } }` |
| `skills.registry_info` | List configured registries and statuses | `{}` | `{ registries: list[{ id, path, count, writable }] }` |
| `skills.changes_since` | Return skills modified after timestamp/hash | `{ registry_id?: str, since?: iso8601, hashes?: list[str] }` | `{ updated: list[SkillSummary], removed: list[SkillSummary] }` |

All tool implementations reference the Registry Manager cache and never mutate filesystem state.

## CLI Commands
- `skills-cli list [--registry] [--tag] [--json]`
- `skills-cli validate [PATH]`
- `skills-cli scaffold NAME --template template-skill --dest DEST`
- `skills-cli export NAME --format json|markdown --out file`
- `skills-cli diff --registry upstream --against local`
- `skills-cli import --repo https://github.com/org/repo --path path/to/skill` (supports sparse checkout or archive download; stores result in CLI config directory)

CLI commands reuse the same parsing/validation logic; scaffold command writes to writable registries only (typically user workspace).

## Configuration
- Default configuration file `skills_mcp.toml`:
  ```toml
  [registries.anthropic]
  path = "./anthropic-skills"
  writable = false

  [registries.local]
  path = "./skills"
  writable = true
  ```
- Environment overrides: `SKILLS_MCP_REGISTRIES` (JSON/TOML path list), `SKILLS_MCP_CACHE_TTL`, etc.
- CLI flag `--config` to load alternative files.

## Parsing & Validation Rules
- Required frontmatter keys: `name` (string), `description` (string).
- Optional recognized keys: `license`, `tags`, `version`, `dependencies`.
- Validate Markdown body is non-empty; warn if missing sections (e.g., `# Examples`).
- Accept YAML anchors but return resolved dict; on parse failure, attach warning and skip from MCP resources unless `--include-broken` flag is set (for CLI inspection).

## Caching Strategy
- In-memory cache keyed by `(registry_id, slug, sha256)` storing `SkillMetadata`.
- Periodic refresh triggered when:
  - MCP server starts.
  - Tool request includes `force_refresh`.
  - File system watchers (optional) signal change (fallback to mtime scan).
- On large catalogs, maintain persistent JSON index under `~/.cache/skills-mcp/{registry_id}.json`.

## Error Handling
- All MCP tool responses include `warnings` array when issues exist (e.g., malformed YAML).
- Common error codes:
  - `SKILL_NOT_FOUND`
  - `REGISTRY_NOT_CONFIGURED`
  - `INVALID_INPUT` (schema validation errors)
  - `UNSUPPORTED_OPERATION` (attempted write)
- Errors formatted as conversational text plus structured fields to guide Codex.

## Security Considerations
- Server performs read-only filesystem operations; confirm `Path.is_relative_to` to prevent directory traversal outside configured registries.
- CLI scaffold command checks `writable` flag; refuses to write into read-only registries.
- No dynamic execution of scripts or code embedded in Skills; treat them as opaque assets.
- Remote imports should verify repository sources (allowlist or explicit user confirmation) and sanitize extracted paths before copying into the configuration directory.

## Edge Cases & Handling
- **Duplicate Skill Names:** Use directory slug for resource IDs; include name collision warning.
- **Missing Frontmatter:** Skip from resources (unless CLI `--include-broken`), return validation error.
- **Large Skills (>100KB):** Truncate `excerpt`; allow full body retrieval with confirmation flag.
- **Binary Assets:** Expose via metadata but do not inline; tool can list asset filenames.
- **Registry Unavailable:** Mark registry status as `offline` and continue serving others.

## Testing Strategy
- **Unit Tests:** Registry discovery, YAML parsing, hash computation, filtering logic.
- **Integration Tests:** MCP stdio sessions verifying resource listings, tool responses using fixtures.
- **CLI Tests:** Snapshot tests for command outputs, scaffold/validate flows in temp directories.
- **Performance Tests:** Benchmark listing vs caches on synthetic catalogs (configurable number of Skills).
- **Static Analysis:** `ruff`/`flake8` for linting (if adopted), `pytest` as test runner.

## Deployment & Distribution
- Package with `pyproject.toml` managed by `uv`.
- Provide `skills_mcp.server:main` entrypoint for MCP stdio.
- Provide `skills-cli` console script for CLI usage.
- Document instructions to register MCP server within Codex configuration.

## Monitoring & Observability
- Optional logging via `structlog` or standard logging with structured fields (registry_id, slug, action, latency).
- Support `--verbose` flag in CLI and `SKILLS_MCP_LOG_LEVEL` env var for MCP server.

## Future Extensions (Not in initial scope)
- Remote registry sync via HTTP.
- Tag taxonomy service.
- Authenticated registry access.
- UI dashboards leveraging the same registry API.
