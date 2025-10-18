# Repository Guidelines

## Project Structure & Module Organization
- Source artifacts live at the repository root for now; the MCP server package will reside under `src/skills_mcp/` with CLI code in `src/skills_mcp/cli/` and templates in `src/skills_mcp/templates/`.
- Planning and research docs (`PRD.md`, `TSD.md`, `ROADMAP.md`, `research_summary.md`, `initial_intake.md`) stay at the root.
- Tests belong in `tests/`, mirroring package modules (e.g., `tests/test_registry.py`).
- The `anthropic-skills/` directory provides upstream reference skills and should be treated as read-only input.

## Build, Test, and Development Commands
- `uv run pytest` — run the test suite.
- `uv run python -m skills_mcp.server` — launch the MCP server via stdio for manual validation.
- `uv run skills-cli --help` — inspect CLI entry points once packaged.
- `uv pip install -e .` — install the project in editable mode for local development.

## Coding Style & Naming Conventions
- Python 3.13 with 4-space indentation; use `snake_case` for functions and variables, `PascalCase` for classes, `UPPER_SNAKE_CASE` for constants.
- Omit Python type annotations; rely on clear naming and short Google-style docstrings for complex functions.
- Prefer expressive helper functions over inline lambdas; keep modules focused to avoid sprawling files.
- Formatting and linting: adopt `ruff` (or `flake8` + `black` equivalents) once tooling is added; run via `uv run ruff check .` if configured.

## Testing Guidelines
- Use `pytest` with descriptive test names (`test_parses_valid_skill`). Arrange tests to cover registry parsing, cache behavior, MCP responses, and CLI commands.
- Organize fixtures under `tests/fixtures/` (e.g., sample `SKILL.md` files).
- Aim for coverage of critical paths (parsing, resource serialization, CLI actions). Add regression tests for reported bugs.

## Commit & Pull Request Guidelines
- Commit messages use imperative verbs (`Add`, `Update`, `Refactor`) without prefixes (e.g., `Add registry parser`). Combine related scopes with commas or semicolons.
- Keep commits focused; avoid formatting-only commits unless necessary.
- Pull requests should summarize the change, link related issues, list affected files or routes, and include verification steps (tests run, manual validation).
- Provide screenshots or logs when changes affect user-facing CLI output or MCP responses.
