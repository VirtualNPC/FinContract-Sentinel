# Skills Index - FinContract Sentinel

Source: extracted from the project SKILLS document in the skills folder.

## skill.project-governance
- Goal: deliver in short iterations with controlled change and managed technical debt.
- Use when: planning releases, changing scope, or prioritizing backlog.
- Key practices: 2-3 week iterations; MoSCoW prioritization; written change requests; reserve ~20% capacity for debt.
- Outputs: iteration plan, prioritized backlog, change log, debt register.

## skill.code-quality
- Goal: keep code clean, modular, and easy to maintain.
- Use when: designing modules, reviewing PRs, or refactoring.
- Key practices: SOLID; clear module boundaries; reuse shared utilities; strict linting and formatting; docstrings for public APIs.
- Outputs: clean module structure, style compliance, documented interfaces.

## skill.version-control-collab
- Goal: ensure safe collaboration and traceability.
- Use when: branching, reviewing, and merging.
- Key practices: Git Flow or GitHub Flow; PR reviews; Conventional Commits; main branch always deployable.
- Outputs: reviewed PRs, clean history, release notes.

## skill.config-and-deps
- Goal: externalize configuration and keep dependencies stable.
- Use when: adding new integrations or deploying to new environments.
- Key practices: environment-based config; secrets outside code; lock dependencies; regular update cadence.
- Outputs: config templates, pinned dependency files, update schedule.

## skill.error-and-logging
- Goal: make failures diagnosable and auditable.
- Use when: implementing core workflows and tool calls.
- Key practices: custom exception types; structured logs with timestamps, module, and function; error categories.
- Outputs: consistent error handling, JSON logs, audit trail.

## skill.agent-architecture
- Goal: build a modular, explainable agent.
- Use when: defining system boundaries and workflows.
- Key practices: separate perception, memory, reasoning, tools, and actions; explicit state transitions; explainability first.
- Outputs: architecture diagram, component interfaces, state machine.

## skill.llm-engineering
- Goal: keep LLM outputs reliable and controllable.
- Use when: writing prompts, calling models, or parsing outputs.
- Key practices: structured prompts; prompt versioning; LLM call wrapper with retries and rate limits; output schema validation.
- Outputs: prompt files, LLM client module, validators.

## skill.tool-integration
- Goal: integrate external tools safely and consistently.
- Use when: adding OCR, search, DB, or rule services.
- Key practices: tool abstraction layer; least privilege; input validation; async calls for long tasks.
- Outputs: tool interface contracts, security checks, async execution plan.

## skill.memory-and-retrieval
- Goal: keep context coherent over time.
- Use when: designing storage for conversation and audit data.
- Key practices: short-term vs long-term memory; vector search for unstructured data; pruning and summarization.
- Outputs: memory schema, retention policy, retrieval API.

## skill.data-parsing-ocr
- Goal: extract accurate data from multiple file formats.
- Use when: handling PDF, Word, Excel, or images.
- Key practices: professional OCR for scans; optimized parsers for tables and clauses; normalize to JSON.
- Outputs: parsing pipeline, normalized data schema.

## skill.rule-engine
- Goal: make rules configurable and traceable.
- Use when: implementing audit policies and exceptions.
- Key practices: rules stored outside code; hard vs soft rules; versioning; execution logs; conflict detection; gray release.
- Outputs: rule repository, version history, rule audit logs.

## skill.risk-human-loop
- Goal: balance automation with human review.
- Use when: defining risk levels and approvals.
- Key practices: risk scoring; human review for high risk; feedback loop to improve prompts and rules; full traceability.
- Outputs: risk matrix, review workflow, feedback dataset.

## skill.testing-and-security
- Goal: prove correctness and protect sensitive data.
- Use when: implementing core logic or releasing.
- Key practices: unit and integration tests; LLM output evaluation; security testing for input validation and access control.
- Outputs: test suites, coverage reports, security checklist.

## skill.ops-and-deployment
- Goal: ensure consistent environments and stable operations.
- Use when: deploying or scaling.
- Key practices: Docker and Compose; CI/CD pipeline; environment isolation; monitoring and alerting; incident playbooks.
- Outputs: Dockerfiles, pipeline config, monitoring dashboards.
