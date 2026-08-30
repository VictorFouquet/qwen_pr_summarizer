# PR-summarizer research — trial-by-trial progress

Human-readable companion to `research/log.jsonl`. For each trial: the hypothesis (note), the aggregate score, and the **actual summary the agent produced** for each eval PR. Regenerate with `python research/report.py`.

## Scoreboard

Best so far: **0.5273** (trial 4).

| Trial | Composite | Faith | BodySim | Brev | (Cov) | Note |
|------:|----------:|------:|--------:|-----:|------:|------|
| 1 | 0.1344 | 0.167 | 0.702 | 1.000 | 0.000 | BASELINE (three-tool + earned faithfulness, config 3000814c954c): seed prompt. Faithfulness now rewards grounded specifics (needs reading), empty->0. Expect the lazy baseline (opens ~0 files) to score low -> the gradient to reward reading. |
| 2 | 0.2518 | 0.341 | 0.701 | 1.000 | 0.019 | campaign T2: make reading the default. Baseline agent opens ~0 files -> faith ~0. Instruct it to open the diffs of the core source files (skip noise) and never summarize from names alone. Expect files-opened up, faith+bsim up. |
| 3 | 0.1535 | 0.200 | 0.765 | 1.000 | 0.005 | campaign T3: mandatory numbered procedure forcing step 3 (call get_file_diff on EACH main source file before summarizing). Baseline+T2 agent opened ~0 diffs; force actual reading. Watch files-opened in the trace. |
| 4 ⭐ | 0.5273 | 0.726 | 0.732 | 1.000 | 0.043 | campaign T4: reading procedure (T3) + name the concrete elements seen in the diffs. T3 read but stayed vague (faith 0). Now instruct naming real functions/classes/fields/routes -> grounded specifics -> faith up while keeping T3's bsim gain. |


---

## Trial 1 — composite **0.1344** · faith 0.167 · bodysim 0.702 · brev 1.000 · (cov 0.000)

- **Prompt id:** `ee65195c801c` · **config_fp:** `1b472c42d619`
- **Hypothesis / note:** BASELINE (three-tool + earned faithfulness, config 3000814c954c): seed prompt. Faithfulness now rewards grounded specifics (needs reading), empty->0. Expect the lazy baseline (opens ~0 files) to score low -> the gradient to reward reading.

### VictorFouquet/supportops#8 — composite **0.0000** · faith 0.000 · bodysim 0.586 · brev 1.000 · (cov 0.000) (0/21 files, 50 words)

> **Purpose:** Introduce a ticketing system with comment functionality to supportops.  
> **Changes:** Added DTOs, services, controllers, and tests for ticket creation, status updates, and comments. Updated documentation to reflect new features.  
> **Context:** Part of a phased implementation plan (Phase 5) to enhance support operations with ticket lifecycle management and authorization rules.

<details><summary>Agent budget · 1 tool calls over 1 steps · 0/21 files opened</summary>

- step 0 · `list_pr_files` → 1.9k chars

</details>

### VictorFouquet/supportops#10 — composite **0.4033** · faith 0.500 · bodysim 0.807 · brev 1.000 · (cov 0.000) (0/40 files, 70 words)

> **Purpose:** Introduce a notification system and queue service to support asynchronous notifications and ticket management.  
> **Changes:** Added new packages (`notifications`, `queue`) with core functionality, updated API modules and services to integrate with these systems, and expanded test coverage. Modified documentation to explain architecture and implementation plans.  
> **Context:** The PR introduces asynchronous notification handling, ticket comment tracking, and a queue system, supported by new test files, configuration files, and architectural documentation.

<details><summary>Agent budget · 1 tool calls over 1 steps · 0/40 files opened</summary>

- step 0 · `list_pr_files` → 3.5k chars

</details>

### VictorFouquet/supportops#11 — composite **0.0000** · faith 0.000 · bodysim 0.713 · brev 1.000 · (cov 0.000) (0/70 files, 96 words)

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


---

## Trial 2 — composite **0.2518** · faith 0.341 · bodysim 0.701 · brev 1.000 · (cov 0.019)

- **Prompt id:** `a9aeac259260` · **config_fp:** `1b472c42d619`
- **Hypothesis / note:** campaign T2: make reading the default. Baseline agent opens ~0 files -> faith ~0. Instruct it to open the diffs of the core source files (skip noise) and never summarize from names alone. Expect files-opened up, faith+bsim up.

### VictorFouquet/supportops#8 — composite **0.2698** · faith 0.394 · bodysim 0.685 · brev 1.000 · (cov 0.000) (0/21 files, 78 words)

> **Purpose:** Introduce ticket management and comment features in the API, including DTOs, services, controllers, and documentation.  
> **Changes:** Added 18 new files under `apps/api/src/tickets` for ticket lifecycle, status transitions, and comment handling, along with test files and architecture documentation. Key components include DTOs for ticket operations, services for business logic, controllers for endpoints, and updated ADRs.  
> **Context:** Part of phase 5 of the project plan, enhancing supportops with ticketing system capabilities. Documentation updates clarify authorization rules and system architecture.

<details><summary>Agent budget · 1 tool calls over 1 steps · 0/21 files opened</summary>

- step 0 · `list_pr_files` → 1.9k chars

</details>

### VictorFouquet/supportops#10 — composite **0.4071** · faith 0.500 · bodysim 0.814 · brev 1.000 · (cov 0.000) (0/40 files, 89 words)

> **Purpose:** Introduce an asynchronous notification system and queue infrastructure for the application's ticketing functionality.  
> **Changes:**  
> - Added a `notifications` package with services, transports, and rendering logic for handling notifications.  
> - Created a `queue` package to manage message queuing, including index files and configurations.  
> - Integrated notification capabilities into the `tickets` module, adding services for comment and ticket management.  
> - Added test files and documentation to explain the architecture and implementation plan.  
> **Context:** Part of a phased implementation (Phase 6) to enhance the system with background processing and notification triggers.

<details><summary>Agent budget · 1 tool calls over 1 steps · 0/40 files opened</summary>

- step 0 · `list_pr_files` → 3.5k chars

</details>

### VictorFouquet/supportops#11 — composite **0.0786** · faith 0.130 · bodysim 0.603 · brev 1.000 · (cov 0.057) (4/70 files, 86 words)

> **Purpose:** Initialize a new Next.js web application for the supportops project, including frontend tools and testing infrastructure.  
> 
> **Changes:**  
> - Added a complete Next.js project structure with TypeScript, React 19, ESLint, Vitest, and TailwindCSS.  
> - Included configuration files for linting, testing, and build processes.  
> - Introduced API routes and UI components for ticket management (e.g., `tickets/[id]/page.tsx`).  
> 
> **Context:**  
> The PR establishes the foundation for a web client, likely part of a larger system for handling support tickets, with documentation updates and dependency upgrades to align with modern tooling.

<details><summary>Agent budget · 2 tool calls over 2 steps · 1/70 files opened</summary>

- step 0 · `list_pr_files` → 6.0k chars
- step 1 · `get_file_diff` `apps/web/package.json` → 1.0k chars

</details>


---

## Trial 3 — composite **0.1535** · faith 0.200 · bodysim 0.765 · brev 1.000 · (cov 0.005)

- **Prompt id:** `7d7d41e94272` · **config_fp:** `1b472c42d619`
- **Hypothesis / note:** campaign T3: mandatory numbered procedure forcing step 3 (call get_file_diff on EACH main source file before summarizing). Baseline+T2 agent opened ~0 diffs; force actual reading. Watch files-opened in the trace.

### VictorFouquet/supportops#8 — composite **0.0000** · faith 0.000 · bodysim 0.704 · brev 1.000 · (cov 0.000) (0/21 files, 74 words)

> **Purpose:** Implement a ticket management system with status transitions and CRUD operations.  
> **Changes:** Added a service layer for handling ticket creation, updates, assignments, and status changes, including validation for legal status transitions (e.g., OPEN → RESOLVED). DTOs for request payloads and response structures were introduced.  
> **Context:** The implementation integrates with a Prisma database, includes error handling for missing entities, and supports pagination for listing tickets. Documentation updates clarify the ticket lifecycle and authorization rules.

<details><summary>Agent budget · 2 tool calls over 2 steps · 1/21 files opened</summary>

- step 0 · `list_pr_files` → 1.9k chars
- step 1 · `get_file_diff` `apps/api/src/tickets/tickets.service.ts` → 5.0k chars

</details>

### VictorFouquet/supportops#10 — composite **0.4604** · faith 0.600 · bodysim 0.767 · brev 1.000 · (cov 0.000) (0/40 files, 91 words)

> **Purpose:** Implement notification triggers for ticket assignments to notify assignees when tickets are assigned or reassigned.  
> **Changes:**  
> - Integrated `NotificationService` into `TicketsService` to send notifications via `ticketAssigned` when assignments change.  
> - Added logic to notify assignees upon ticket assignment or reassignment.  
> - Introduced new files and modules for the notification system (e.g., `NotificationService`, transports, and tests).  
> 
> **Context:**  
> The changes align with architecture documents (ADR) and a phase plan for notifications, adding asynchronous notification capabilities and a queue system. The PR expands the notification infrastructure to support real-time updates for ticket assignments.

<details><summary>Agent budget · 2 tool calls over 2 steps · 1/40 files opened</summary>

- step 0 · `list_pr_files` → 3.5k chars
- step 1 · `get_file_diff` `apps/api/src/tickets/tickets.service.ts` → 2.1k chars

</details>

### VictorFouquet/supportops#11 — composite **0.0000** · faith 0.000 · bodysim 0.823 · brev 1.000 · (cov 0.014) (1/70 files, 106 words)

> **Purpose:** Implement a web client for a support system using Next.js app router, with API integrations for tickets, users, and authentication.  
> 
> **Changes:**  
> - Added core API client logic (`api.ts`) to handle authentication, user data retrieval, ticket management (listing, fetching, updating, assigning), and comment handling.  
> - Set up Next.js project structure with TypeScript, ESLint, and CSS configuration files.  
> - Introduced documentation for architectural decisions around the web client and session management.  
> 
> **Context:**  
> The PR establishes the frontend foundation for a support operations tool, focusing on API-driven interactions and Next.js app router integration. Session handling uses HTTP-only cookies, and ticket data is managed via defined types and endpoints.

<details><summary>Agent budget · 2 tool calls over 2 steps · 1/70 files opened</summary>

- step 0 · `list_pr_files` → 6.0k chars
- step 1 · `get_file_diff` `apps/web/src/lib/api.ts` → 2.9k chars

</details>


---

## Trial 4 — composite **0.5273** · faith 0.726 · bodysim 0.732 · brev 1.000 · (cov 0.043)

- **Prompt id:** `e38cd153b3d9` · **config_fp:** `1b472c42d619`
- **Hypothesis / note:** campaign T4: reading procedure (T3) + name the concrete elements seen in the diffs. T3 read but stayed vague (faith 0). Now instruct naming real functions/classes/fields/routes -> grounded specifics -> faith up while keeping T3's bsim gain.

### VictorFouquet/supportops#8 — composite **0.4717** · faith 0.600 · bodysim 0.786 · brev 1.000 · (cov 0.000) (0/21 files, 122 words)

> **Purpose:**  
> Implement ticket management and comment features in the supportops API, including status transitions, assignment, and comment handling.
> 
> **Changes:**  
> - Added a `TicketsController` with endpoints for listing tickets, creating/updating tickets, assigning ownership, changing statuses, and managing comments.  
> - Introduced a `TicketsService` with logic for ticket operations, including validation of legal status transitions (e.g., OPEN → RESOLVED) and database interactions via Prisma.  
> - Created DTOs (data transfer objects) for ticket creation, updates, assignments, and comments to structure request/response data.  
> - Added comment-related endpoints in the controller and a `TicketCommentsService` to handle comment creation and listing.  
> 
> **Context:**  
> The changes align with documentation updates in ADRs (Architecture Decision Records) and a phase plan for ticketing features, ensuring consistent status transitions and authorization checks for comments.

<details><summary>Agent budget · 3 tool calls over 3 steps · 2/21 files opened</summary>

- step 0 · `list_pr_files` → 1.9k chars
- step 1 · `get_file_diff` `apps/api/src/tickets/tickets.controller.ts` → 3.0k chars
- step 2 · `get_file_diff` `apps/api/src/tickets/tickets.service.ts` → 5.0k chars

</details>

### VictorFouquet/supportops#10 — composite **0.6446** · faith 0.778 · bodysim 0.829 · brev 1.000 · (cov 0.000) (0/40 files, 85 words)

> **Purpose:**  
> Implement a notification system to alert users when tickets are assigned to them.  
> 
> **Changes:**  
> - Integrated `NotificationService` into `TicketsService` to send notifications via `ticketAssigned` when tickets are assigned or reassigned.  
> - Added logic in `list` and `assign` methods to trigger notifications to recipients when ticket assignees change.  
> - Introduced new packages (`notifications`, `queue`) and a worker (`notification-worker`) to handle asynchronous notification delivery.  
> 
> **Context:**  
> The PR adds infrastructure for notifications, including service implementations, transport mechanisms, and test files, alongside documentation updates for async notification workflows.

<details><summary>Agent budget · 2 tool calls over 2 steps · 1/40 files opened</summary>

- step 0 · `list_pr_files` → 3.5k chars
- step 1 · `get_file_diff` `apps/api/src/tickets/tickets.service.ts` → 2.1k chars

</details>

### VictorFouquet/supportops#11 — composite **0.4657** · faith 0.800 · bodysim 0.582 · brev 1.000 · (cov 0.129) (9/70 files, 126 words)

> **Purpose:**  
> Set up a new web application for a support operations system, including API client libraries and frontend utilities.
> 
> **Changes:**  
> - Added a comprehensive API client library (`api.ts`) with functions for authentication (`login`, `getMe`), ticket management (`listTickets`, `getTicket`, `addComment`, `setStatus`, `assignTicket`), user/customer data retrieval (`listUsers`, `listCustomers`), and HTTP request handling.  
> - Introduced Next.js project structure files (e.g., `next.config.ts`, `tsconfig.json`) and ESLint/PostCSS configurations.  
> - Created utility files for session management (`session.ts`), HTTP requests (`http.ts`), and type definitions (`api-types.ts`).  
> - Added test setup files (e.g., `vitest.config.ts`) and component files for UI elements (e.g., `app-header.tsx`, `ticket-filters.tsx`).  
> 
> **Context:**  
> The PR establishes a frontend foundation for a support tool, enabling features like ticket tracking, user authentication, and data interaction with a backend API. Documentation updates clarify architecture decisions and project scope.

<details><summary>Agent budget · 2 tool calls over 2 steps · 1/70 files opened</summary>

- step 0 · `list_pr_files` → 6.0k chars
- step 1 · `get_file_diff` `apps/web/src/lib/api.ts` → 2.9k chars

</details>

