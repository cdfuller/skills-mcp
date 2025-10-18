# Domain Research Summary — skills-mcp

## Claude Skills (Support Article)
- Skills are folders bundling instructions, scripts, and resources that Claude loads dynamically (“progressive disclosure”) only when relevant to a task, avoiding context-window overload.
- Feature availability: currently a preview for Claude Pro/Max/Team/Enterprise with code execution enabled, beta in Claude Code, and available to API users when the code-execution tool is active.
- Two categories:
  - *Anthropic Skills*: maintained by Anthropic (e.g., document editors) and auto-invoked.
  - *Custom Skills*: user-authored workflows, typically domain-specific; examples include branded content creation, templated comms, meeting-note structures, task generation, data analysis, and personal automations.
- Key benefits emphasized: improved task performance via specialized instructions, institutional knowledge capture, and low-friction customization (Markdown instructions with optional scripts).
- Skills complement (but differ from) related features:
  - vs Projects: projects preload static background info; skills activate on demand across contexts.
  - vs MCP: MCP links Claude to external tools/data; skills teach Claude how to use those tools effectively. They are intended to be combined.
  - vs Custom Instructions: custom instructions apply globally; skills are task-specific.

## `anthropic-skills` Repository
- Provides canonical examples of skill directory layout (`SKILL.md` with YAML frontmatter and Markdown instructions) across creative, technical, and enterprise use cases.
- Includes meta-skills (e.g., `skill-creator`, `template-skill`) that define minimal scaffolding, useful for generating new skills programmatically.
- Contains an `mcp-builder` skill with deep guidance on building MCP servers:
  - Highlights agent-centric tool design (workflow-oriented tools, concise outputs, actionable errors).
  - Recommends evaluation-driven development and references to MCP protocol docs and SDK guides.
  - Details planning steps (tool selection, IO design, error handling) which inform our server feature set.
- Illustrates precedent for including scripts/utilities alongside `SKILL.md`, reinforcing need to respect executable assets when syncing skills.

## Implications for skills-mcp MCP Server
- Must ingest, validate, and present `SKILL.md` metadata and instructions cleanly so Codex users can browse and reason about available workflows.
- Need mechanisms for creating new skills using templates while enforcing required YAML fields (`name`, `description`) and optional metadata from examples.
- Because skills and MCP are complementary, the server should bridge procedural knowledge (skills) with tool invocation—e.g., surfaces describing how a skill expects associated tools or scripts to be run.
- Progressive disclosure suggests UX affordances for filtering/loading only relevant skill details (summaries vs full instructions) to conserve context/token budgets.
- Preview/beta status implies varying user environments (Claude Code, API, Codex CLI); server should work offline with local copies but be ready to integrate with remote catalogs once available.
- Security considerations: executing bundled scripts may pose risks; need sandboxing or explicit opt-in if execution support is included.
