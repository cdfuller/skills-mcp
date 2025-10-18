# The Reusable Project Planning Process

This process guides the development of a project from an initial idea to a complete plan, documented in three distinct Markdown artifacts: The **PRD** (What/Why), the **TSD** (How), and the **Roadmap** (Milestones/Sequence).

## 0\. Initial Intake (The Project Brief)

To begin a new project, the user should provide the initial information using the following template:

```markdown
**Project Name**
[The chosen name, or a concept you'd like to brainstorm]

skills-mcp

**Problem Statement:**
[Describe the problem you are trying to solve, the pain points, and the context. Why is this needed?]

Recently anthropic released skills (see https://support.claude.com/en/articles/12512176-what-are-skills). I want to build an MCP server to integrate the skills into codex

**Proposed Solution (High-Level):**
[Describe your initial vision for the application or system. What should it do?]

MCP server for loading/managing/creating skills.

**Target Audience:**
[Who will be using this application?]

Developers

**Key Constraints and Preferences:**
[List any critical technical constraints (e.g., "must be client-side", "must work offline"), preferred technologies (e.g., "prefer Python", "avoid frameworks"), budgetary constraints (e.g., "must use free services"), or design inspirations.]

I prefer python, but will consider other langauges if it's easier to deploy

**Unknowns & Open Questions:**
[List gaps in information, unresolved decisions, or outstanding questions that need clarification before planning can proceed.]

* I don't know what the MCP interface should look like. Resources vs tool cools vs ?

```

## 1\. Phase 1: Discovery, Research, and PRD Definition (The "What")

This phase focuses on understanding the domain and defining the product scope.

1.  **Project Naming:**
      * Determine or refine the project’s name as the first step.
      * Naming helps define the identity and context of the project before proceeding with deeper research.
      * **Action:** Confirm or brainstorm a project name with the user to establish a clear reference point.
      * **Name Brainstorming Guidance:**
        * Explore names through multiple lenses: Literal, Metaphoric, Conceptual, Technical, and Symbolic.
        * Balance clarity, emotion, and distinctiveness when brainstorming.
        * Evaluate finalists for clarity, tone, distinctiveness, and practicality (domain/handle availability).
        * Test top names in real contexts (spoken, written, visual) before finalizing.
        * Share 10 names for each category. 4 out of 10 should use alliteration.
2.  **Domain Research Strategy:**
      * Analyze the intake brief to identify specialized domain knowledge required (e.g., complex calculations, industry standards, competitive landscape).
      * The LLM proposes specific areas requiring deeper research.
      * **Action:** The LLM asks the user whether the LLM should conduct this research and present findings, or if the user will provide the necessary domain expertise.
3.  **Execute Domain Research:**
      * Based on the strategy, the research is conducted.
      * *Output:* A brief summary of key domain insights, terminology, and potential functional edge cases relevant to the project.
4.  **Clarification Round 1 (Product Focus):**
      * Ask a numbered list of questions informed by the domain research, and format each question as:

        ```markdown
        1. Topic/Question
            - Option A (Recommended, if applicable): ...
            - Option B: ...
            - Option C: ...
            - ...
            - Option X: Explain the options
        ```

      * Ensure Option A clearly signals the recommended path when one exists (omit the "Recommended" tag if unsure), add additional options in alphabetical order as needed, and always include Option X as the final choice so the user can request deeper explanation before deciding.
5.  **Artifact Generation 1:** Generate the **Product Requirements Document (PRD)** in Markdown format.
      * Add a clearly labeled, one-sentence summary (≤ 80 characters) that can double as the GitHub description for the project.

## 2\. Phase 2: Technical Analysis and TSD Definition (The "How")

This phase focuses on translating the product vision into a technical blueprint.

1.  **Technical Research and Analysis:**
      * Review the PRD and domain insights. Identify technical challenges.
      * **Action:** Conduct research focused on specific technical implementations, algorithms, available libraries, APIs, and architectural patterns suitable for the requirements and constraints.
      * Analyze the trade-offs (performance, cost, complexity, maintainability) between different approaches.
2.  **Clarification Round 2 (Technical Focus):**
      * Ask a numbered list of technology-focused questions using the same Option-based structure above, where Option A (Recommended) reflects the preferred implementation when there is a clear favorite (omit the tag if unsure) and Option X remains available for explanation.
      * Present the trade-offs identified during the technical research inline with the options before asking for the user's decision (e.g., "Approach A is faster but increases app size; Approach B is smaller but slower. Do you prefer A?").
3.  **Artifact Generation 2:** Generate the **Technical Specification Document (TSD)** in Markdown format, including detailed Input/Output examples and technical edge cases.

## 3\. Phase 3: Roadmap and Execution Planning (The "Sequence")

This phase breaks the work into manageable steps.

1.  **Milestone Definition:** Analyze the PRD and TSD and break the project down into sequential, logical steps that deliver incremental value, without assigning calendar dates or durations.
      * Reserve one of the earliest execution tasks for creating a project-appropriate `.gitignore`.
2.  **Artifact Generation 3:** Generate the **Implementation Roadmap** in Markdown format, documenting the ordered milestones and key deliverables with no time-based commitments.
3.  **Handoff:** Confirm all artifacts (PRD, TSD, Roadmap) with the user and ask which Milestone they would like to begin implementing.
      * During execution, explicitly call out when each milestone is completed before moving to the next.
