# Backend package entrypoint

This file is the entrypoint for all work inside the backend package.

## Scope
- This guidance applies only to the current package.
- Do not use frontend instructions, frontend plans, or frontend architectural assumptions.
- Do not read sibling package guidance unless the user explicitly asks for cross-package work.

## Required startup behavior
Before doing any analysis, planning, coding, refactoring, debugging, or data-layer changes:

1. Read `agent/AGENTS.md` first.
2. Treat `agent/AGENTS.md` as the primary source of truth for this package.
3. If the user specified a plan file under `agent/docs/`, read that exact file and follow it.
4. If no plan file was specified, do not choose one automatically unless the user explicitly asks you to.
5. Keep all changes scoped to the backend package unless the task explicitly requires coordination with another package.

## Plan execution rules
- Plans live under `agent/docs/`.
- Execute only the plan file explicitly selected by the user.
- Do not merge multiple plans unless the user asks for that.
- Do not silently reorder plan steps.
- If the selected plan conflicts with the current codebase, stop and report the mismatch clearly before continuing.
- If part of the plan is already completed in code, report that and continue from the next valid step.

## Implementation rules
- Prefer minimal, localized changes.
- Reuse existing backend patterns, naming, modules, services, and infrastructure conventions.
- Do not introduce new architecture, frameworks, persistence patterns, or contracts unless the plan or user explicitly requests it.
- Preserve existing API and system behavior unless the task requires a change.
- When changing business logic, check related services, schemas, validators, background jobs, and tests before adding new abstractions.

## Validation
Before marking work complete:
- Run the relevant backend checks if available.
- Verify the implemented changes match the selected plan.
- Summarize what was completed and what remains, if anything.
- Call out any migration, deployment, config, or compatibility impact.

## Response behavior
At the start of work, explicitly state:
- that you are operating in the backend package,
- that you read `agent/AGENTS.md`,
- and which plan file you are executing, if one was provided.