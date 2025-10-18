# Implementation Roadmap — skills-mcp

## Milestone 0: Project Setup
- Initialize Python package structure with `uv` support and baseline `pyproject.toml`.
- Add project-wide `.gitignore` tailored for Python, `uv`, cache, and Codex artifacts.
- Configure continuous testing scaffolding (`pytest`, lint hooks) and create placeholder tests directory.

## Milestone 1: Registry & Parsing Foundations
- Implement configuration loader and registry discovery against local directories.
- Build Skill parser with YAML + Markdown extraction, validation rules, and hashing.
- Create unit tests covering parsing edge cases and invalid frontmatter handling.

## Milestone 2: Caching & Metadata Services
- Implement in-memory cache with change detection (mtime/hash).
- Surface metadata warnings and excerpt generation utilities.
- Add integration tests ensuring cache refresh and deterministic outputs.

## Milestone 3: MCP Resource & Tool Layer
- Implement MCP resource adapter exposing `skill://` namespace with pagination.
- Add read-only tools (`skills.search`, `skills.detail`, `skills.registry_info`, `skills.changes_since`) per TSD schemas.
- Write end-to-end stdio tests verifying Codex-compatible responses.

## Milestone 4: CLI Wrapper & Templates
- Package shared logic for CLI commands (`list`, `validate`, `scaffold`, `export`, `diff`).
- Bundle template assets and enforce writable registry restrictions.
- Add CLI integration tests using temporary directories.

## Milestone 5: Documentation & Developer Experience
- Update root README with installation, configuration, MCP registration, and CLI usage examples.
- Document validation warnings, change detection semantics, and read-only constraints.
- Provide sample Codex prompt snippets and troubleshooting guide.

## Milestone 6: Hardening & Release Prep
- Conduct performance benchmarking on large catalogs; optimize as needed.
- Finalize logging/observability settings and configurable cache options.
- Tag initial release, publish package artifacts, and prepare change log.
