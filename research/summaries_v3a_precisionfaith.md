# PR-summarizer research — trial-by-trial progress

Human-readable companion to `research/log.jsonl`. For each trial: the hypothesis (note), the aggregate score, and the **actual summary the agent produced** for each eval PR. Regenerate with `python research/report.py`.

## Scoreboard

Best so far: **0.7018** (trial 1).

| Trial | Composite | Faith | BodySim | Brev | (Cov) | Note |
|------:|----------:|------:|--------:|-----:|------:|------|
| 1 ⭐ | 0.7018 | 1.000 | 0.702 | 1.000 | 0.000 | BASELINE (three-tool agent, config f343c52c4bee): seed prompt with list_pr_files / get_file_diff / read_file. No hardcoded cap — the agent chooses what to open. Body-similarity metric unchanged. Fresh log; not comparable to archived v1/v2. |


---

## Trial 1 — composite **0.7018** · faith 1.000 · bodysim 0.702 · brev 1.000 · (cov 0.000)

- **Prompt id:** `ee65195c801c` · **config_fp:** `85c0626572ee`
- **Hypothesis / note:** BASELINE (three-tool agent, config f343c52c4bee): seed prompt with list_pr_files / get_file_diff / read_file. No hardcoded cap — the agent chooses what to open. Body-similarity metric unchanged. Fresh log; not comparable to archived v1/v2.

### VictorFouquet/supportops#8 — composite **0.5857** · faith 1.000 · bodysim 0.586 · brev 1.000 · (cov 0.000) (0/21 files, 50 words)

> **Purpose:** Introduce a ticketing system with comment functionality to supportops.  
> **Changes:** Added DTOs, services, controllers, and tests for ticket creation, status updates, and comments. Updated documentation to reflect new features.  
> **Context:** Part of a phased implementation plan (Phase 5) to enhance support operations with ticket lifecycle management and authorization rules.

<details><summary>Agent budget · 1 tool calls over 1 steps · 0/21 files opened</summary>

- step 0 · `list_pr_files` → 1.9k chars

</details>

### VictorFouquet/supportops#10 — composite **0.8067** · faith 1.000 · bodysim 0.807 · brev 1.000 · (cov 0.000) (0/40 files, 70 words)

> **Purpose:** Introduce a notification system and queue service to support asynchronous notifications and ticket management.  
> **Changes:** Added new packages (`notifications`, `queue`) with core functionality, updated API modules and services to integrate with these systems, and expanded test coverage. Modified documentation to explain architecture and implementation plans.  
> **Context:** The PR introduces asynchronous notification handling, ticket comment tracking, and a queue system, supported by new test files, configuration files, and architectural documentation.

<details><summary>Agent budget · 1 tool calls over 1 steps · 0/40 files opened</summary>

- step 0 · `list_pr_files` → 3.5k chars

</details>

### VictorFouquet/supportops#11 — composite **0.7131** · faith 1.000 · bodysim 0.713 · brev 1.000 · (cov 0.000) (0/70 files, 96 words)

> **Purpose:**  
> Set up a new web application for ticket management and session handling using Next.js, React, and TypeScript.
> 
> **Changes:**  
> - Added a complete Next.js project structure with React, TypeScript, ESLint, Vitest, and Tailwind CSS.  
> - Introduced API routes for ticket assignment, comments, and session management.  
> - Created UI components for tickets, authentication, and layout.  
> - Updated documentation to reflect the new architecture and features.  
> 
> **Context:**  
> The PR establishes a foundation for a support operations web client, including session handling via HTTP-only cookies and integration with backend services. Changes align with architectural decisions documented in the ADRs.

<details><summary>Agent budget · 2 tool calls over 2 steps · 1/70 files opened</summary>

- step 0 · `list_pr_files` → 6.0k chars
- step 1 · `get_file_diff` `apps/web/package.json` → 1.0k chars

</details>

