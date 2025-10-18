# skills-mcp Initial Intake

**Project Name**  
skills-mcp

**Problem Statement:**  
Claude’s new Skills system lets models load curated instructions, scripts, and assets on demand to execute specialized workflows, but Codex currently has no first-class way to surface, manage, or author these skills. Developers working inside Codex need a repeatable path to browse reference skills (like those in `anthropic-skills`), compose new ones, and keep them synchronized without manually copying folders or juggling YAML metadata. Without tighter integration, Codex users miss out on the consistency, speed, and organizational knowledge capture that Skills provide, especially when MCP servers are already the main bridge to external tools and data.

**Proposed Solution (High-Level):**  
Build an MCP server that exposes a Skills management interface to Codex. The server should let users list and inspect available skills, scaffold new skills from templates, sync skills between local workspaces and remote catalogs, and optionally execute auxiliary scripts bundled with skills. It should lean on the existing `anthropic-skills` repository for canonical structures (e.g., `SKILL.md` with YAML frontmatter) and make it easy to combine procedural instructions from Skills with MCP-provided tool access, reflecting best practices from the Claude documentation.

**Target Audience:**  
Developers and prompt engineers using Codex CLI who want to extend Claude with reusable workflows, particularly teams experimenting with Claude’s Skills preview and organizations standardizing internal processes.

**Key Constraints and Preferences:**  
- Prefer Python for the MCP server implementation and package management via `uv`.  
- Must align with the Model Context Protocol so Codex can load the server alongside other MCP integrations without manual configuration hacks.  
- Should operate offline against locally cloned skill catalogs (e.g., `anthropic-skills`) but allow optional remote sync when credentials are available.  
- Need safeguards to respect read-only skill assets (e.g., upstream examples) while clearly separating user-authored skills.  
- Provide ergonomic commands or prompts inside Codex so users don’t have to remember raw MCP messages.

**Unknowns & Open Questions:**  
- How should Skills map onto MCP resources and tools? (e.g., expose each skill as a resource, offer tooling to create/update `SKILL.md`, or provide higher-level commands?)  
- What metadata or validation is required before Codex (or Claude Code) will accept a custom skill bundle?  
- Can this be a locally installed cli tool?