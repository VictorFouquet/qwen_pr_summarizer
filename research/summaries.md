# PR-summarizer research — trial-by-trial progress

Human-readable companion to `research/log.jsonl`. For each trial: the hypothesis (note), the aggregate score, and the **actual summary the agent produced** for each eval PR. Regenerate with `python research/report.py`.

## Scoreboard

Best so far: **0.6811** (trial 2).

| Trial | Composite | Faith | BodySim | Brev | (Cov) | Note |
|------:|----------:|------:|--------:|-----:|------:|------|
| 1 | 0.6305 | 0.933 | 0.741 | 0.667 | 0.138 | BASELINE (body-similarity objective, config 4f79b185cee7): seed prompt, scored by embedding similarity to the real PR body. Fresh log; not comparable to the archived coverage-era trials. |
| 2 ⭐ | 0.6811 | 0.970 | 0.764 | 0.667 | 0.138 | bodysim T2: faithfulness fix. #10 & #8 lose faith to prose-slash false paths (BullMQ/Redis, ticket/comment). Positive-only 'slash = real paths only' clause. Coverage no longer scores, so no downside this time. Expect faith->~1.0, bsim held. |


---

## Trial 1 — composite **0.6305** · faith 0.933 · bodysim 0.741 · brev 0.667 · (cov 0.138)

- **Prompt id:** `2feebcd93b97` · **config_fp:** `a89bd8ec1635`
- **Hypothesis / note:** BASELINE (body-similarity objective, config 4f79b185cee7): seed prompt, scored by embedding similarity to the real PR body. Fresh log; not comparable to the archived coverage-era trials.

### VictorFouquet/supportops#8 — composite **0.6336** · faith 0.909 · bodysim 0.697 · brev 1.000 · (cov 0.000) (0/21 files, 136 words)

> **Purpose:**  
> Implement a ticket management system with CRUD operations, status transitions, and comment handling, following architectural decisions documented in ADRs 0011 and 0012.
> 
> **Changes:**  
> - Added `TicketDto`, `CreateTicketDto`, `ListTicketsDto`, and `UpdateTicketDto` for ticket data modeling.  
> - Implemented `TicketsService` for ticket creation, retrieval, updates, assignment, and status transitions with validation.  
> - Created `TicketCommentsService` for managing ticket comments, including creation and listing.  
> - Added controllers for REST endpoints (`/tickets` and `/tickets/:id/comments`).  
> - Wrote unit and integration tests for all services and endpoints.  
> - Updated architectural documentation to reflect the new ticket/comment feature.  
> 
> **Context:**  
> The feature enforces organization isolation, validates user permissions, and governs ticket status transitions (e.g., OPEN → RESOLVED → CLOSED). Comments are attributed to agents or customers, with internal flags for private notes. All changes align with ADRs 0011 (ticket lifecycle) and 0012 (authorization and comments).

<details><summary>Unsupported claims (hallucinations)</summary>

- `[path] ticket/comment`

</details>

### VictorFouquet/supportops#10 — composite **0.8889** · faith 0.889 · bodysim 1.000 · brev 1.000 · (cov 0.000) (0/40 files, 120 words)

> **Purpose:**  
> Implement asynchronous ticket notifications using a background queue and worker to decouple notification delivery from request processing, ensuring reliability and scalability.
> 
> **Changes:**  
> - **New packages:** `@supportops/queue` (BullMQ/Redis plumbing) and `@supportops/notifications` (notification domain, transport, and delivery logic).  
> - **Worker:** `workers/notification-worker` processes queued notifications via a console transport (logs messages).  
> - **API Integration:** `apps/api` now emits `TICKET_ASSIGNED` and `TICKET_COMMENTED` notifications using `NotificationService`, enqueuing via `@supportops/queue`.  
> - **Documentation:** Added ADRs (0013, 0014) and updated architecture to reflect the new notification system.  
> 
> **Context:**  
> Notifications are persisted to the database with `PENDING` status and enqueued for delivery. A background worker handles delivery via a pluggable transport (e.g., email), with best-effort enqueueing to avoid request failures. Team-only assignments and unassigned tickets do not trigger notifications.

<details><summary>Unsupported claims (hallucinations)</summary>

- `[path] BullMQ/Redis`

</details>

### VictorFouquet/supportops#11 — composite **0.3689** · faith 1.000 · bodysim 0.527 · brev 0.000 · (cov 0.414) (29/70 files, 665 words)

> # Web Application Implementation for SupportOps
> 
> ## Overview
> 
> This implementation creates a Next.js web application for the SupportOps platform, featuring:
> 
> 1. **Authentication system** with secure session management
> 2. **Ticket management interface** with filtering and comment capabilities
> 3. **Secure architecture** with server-side API calls
> 4. **Comprehensive testing** with unit tests and type safety
> 
> ## Implementation Details
> 
> ### 1. HTTP Client and Session Management
> 
> **Files:**
> - `http.ts`: Handles API requests with authentication
> - `session.ts`: Manages session cookies
> - `api.ts`: Wraps API endpoints with type safety
> 
> **Key Features:**
> - Secure HTTP client with automatic authentication token handling
> - Cookie-based session management with httpOnly cookies
> - Type-safe API calls with proper error handling
> 
> ```typescript
> // http.ts
> export class ApiError extends Error {
>   readonly status: number;
>   constructor(status: number, body: unknown) {
>     super(`API request failed with status ${status}`);
>     this.name = 'ApiError';
>     this.status = status;
>     this.body = body;
>   }
> }
> 
> export async function request<T>(path: string, opts: RequestOptions = {}) {
>   // Implementation details
> }
> ```
> 
> ### 2. Authentication System
> 
> **Files:**
> - `login/page.tsx`: Login page
> - `login-form.tsx`: Login form component
> - `api/session/route.ts`: Session API route
> 
> **Key Features:**
> - Secure login with token-based authentication
> - Session management with cookie-based authentication
> - Route protection with middleware
> 
> ```typescript
> // middleware.ts
> export function middleware(req: NextRequest) {
>   // Implementation details
> }
> ```
> 
> ### 3. Ticket Management Interface
> 
> **Files:**
> - `tickets/page.tsx`: Ticket list page
> - `tickets/[id]/page.tsx`: Ticket detail page
> - `ticket-filters.tsx`: Ticket filters component
> - `comment-thread.tsx`: Comment thread component
> 
> **Key Features:**
> - Filterable ticket list with status/priority filters
> - Detailed ticket view with comment thread
> - Status and assignment controls
> - Commenting functionality
> 
> ```typescript
> // ticket-filters.tsx
> export function TicketFilters({ current }: { current: { status?: string; priority?: string } }) {
>   // Implementation details
> }
> ```
> 
> ### 4. UI Components
> 
> **Files:**
> - `button.tsx`: Custom button component
> - `field.tsx`: Form field component
> - `app-header.tsx`: Application header
> - `badge.tsx`: Status/priority badges
> 
> **Key Features:**
> - Consistent UI components with proper styling
> - Status/priority visualization with color-coded badges
> - Responsive layout for different screen sizes
> 
> ```typescript
> // badge.tsx
> export function Badge({ tone, value }: { tone: 'status' | 'priority'; value: string }) {
>   // Implementation details
> }
> ```
> 
> ### 5. Data Management
> 
> **Files:**
> - `lookups.ts`: Name lookup utilities
> - `format.ts`: Date formatting utilities
> 
> **Key Features:**
> - Efficient data lookup with name indexing
> - Consistent date formatting across the application
> 
> ```typescript
> // lookups.ts
> export function nameIndex(items: { id: string; name: string }[]): Map<string, string> {
>   // Implementation details
> }
> ```
> 
> ## Testing Strategy
> 
> ### Unit Tests
> 
> **Files:**
> - `http.spec.ts`: Tests for HTTP client
> - `api.spec.ts`: Tests for API wrappers
> - `login-form.spec.tsx`: Tests for login form
> - `comment-thread.spec.tsx`: Tests for comment thread
> 
> **Key Features:**
> - Comprehensive test coverage for all components
> - Mocking of dependencies for isolated testing
> - Type safety verification with TypeScript
> 
> ### Integration Tests
> 
> **Files:**
> - `ticket-list.test.tsx`: Tests for ticket list functionality
> - `ticket-detail.test.tsx`: Tests for ticket detail view
> 
> **Key Features:**
> - End-to-end testing of user workflows
> - Verification of state transitions and UI updates
> - Validation of API interactions
> 
> ## Security Considerations
> 
> 1. **Secure Session Management:**
>    - HTTP-only cookies for session tokens
>    - Secure cookie attributes (SameSite, Secure)
>    - No client-side storage of sensitive data
> 
> 2. **API Security:**
>    - Server-side API calls only
>    - No direct browser-to-API requests
>    - Proper error handling and validation
> 
> 3. **Input Validation:**
>    - All user inputs are validated and sanitized
>    - Proper handling of edge cases and invalid data
> 
> ## Documentation
> 
> ### Architecture Documentation
> 
> **File:** `docs/architecture.md`
> 
> **Key Points:**
> - Next.js App Router architecture
> - Server-side API integration
> - Session management architecture
> - Component structure and responsibilities
> 
> ### Development Guide
> 
> **File:** `README.md`
> 
> **Key Points:**
> - How to run the web application
> - Required environment variables
> - Development and testing instructions
> - Deployment considerations
> 
> ## Conclusion
> 
> This implementation provides a secure, type-safe, and well-tested web application for the SupportOps platform. The architecture follows best practices for Next.js applications, with proper separation of concerns and secure session management. The comprehensive testing strategy ensures that all components work as expected, and the documentation provides clear guidance for developers and maintainers.


---

## Trial 2 — composite **0.6811** · faith 0.970 · bodysim 0.764 · brev 0.667 · (cov 0.138)

- **Prompt id:** `b49db9e16ff8` · **config_fp:** `a89bd8ec1635`
- **Hypothesis / note:** bodysim T2: faithfulness fix. #10 & #8 lose faith to prose-slash false paths (BullMQ/Redis, ticket/comment). Positive-only 'slash = real paths only' clause. Coverage no longer scores, so no downside this time. Expect faith->~1.0, bsim held.

### VictorFouquet/supportops#8 — composite **0.7654** · faith 1.000 · bodysim 0.765 · brev 1.000 · (cov 0.000) (0/21 files, 133 words)

> **Purpose:**  
> Implement a tickets module for managing support tickets, including CRUD operations, status transitions, assignment, and threaded comments with authorship tracking.
> 
> **Changes:**  
> - Added `tickets` module with:  
>   - DTOs for ticket creation, updates, listing, and comments.  
>   - `TicketsService` for ticket management (create, read, update, assign, status transitions).  
>   - `TicketCommentsService` for comment handling (create, list).  
>   - Controller endpoints for `/tickets` and nested `/comments`.  
>   - ADRs (0011, 0012) defining ticket lifecycle rules and authorization models.  
>   - Tests for all service and controller logic.  
>   - Updated architecture documentation to reflect the new module.
> 
> **Context:**  
> The module enforces organization isolation, validates assignments, and governs ticket status transitions (e.g., OPEN → PENDING → RESOLVED → CLOSED). Comments are attributed to agents or customers, with internal flags for private notes. All operations are scoped to the authenticated user's organization.

### VictorFouquet/supportops#10 — composite **0.9091** · faith 0.909 · bodysim 1.000 · brev 1.000 · (cov 0.000) (0/40 files, 134 words)

> **Purpose:**  
> Implement asynchronous notifications for ticket assignments and comments using a queue system (BullMQ/Redis) to decouple notification delivery from request processing.
> 
> **Changes:**  
> - **New packages:** `@supportops/notifications` (handles notification rendering, transport, and delivery) and `@supportops/queue` (BullMQ/Redis plumbing).  
> - **Worker:** `workers/notification-worker` processes queued notifications via a console transport (logs messages).  
> - **API Integration:** `apps/api` now emits `TICKET_ASSIGNED` and `TICKET_COMMENTED` notifications asynchronously, using `NotificationService` to record and enqueue events.  
> - **Documentation:** Added ADRs (0013, 0014) and updated architecture docs to describe the notification system and its components.  
> 
> **Context:**  
> Notifications are persisted to the database (`PENDING` status) and enqueued for delivery via Redis. A background worker processes these jobs, rendering messages and updating their status (`SENT`/`FAILED`). Enqueue is best-effort, so Redis outages do not block ticket actions. Tests ensure notifications are recorded and delivered correctly without Redis dependencies.

<details><summary>Unsupported claims (hallucinations)</summary>

- `[path] BullMQ/Redis`

</details>

### VictorFouquet/supportops#11 — composite **0.3689** · faith 1.000 · bodysim 0.527 · brev 0.000 · (cov 0.414) (29/70 files, 665 words)

> # Web Application Implementation for SupportOps
> 
> ## Overview
> 
> This implementation creates a Next.js web application for the SupportOps platform, featuring:
> 
> 1. **Authentication system** with secure session management
> 2. **Ticket management interface** with filtering and comment capabilities
> 3. **Secure architecture** with server-side API calls
> 4. **Comprehensive testing** with unit tests and type safety
> 
> ## Implementation Details
> 
> ### 1. HTTP Client and Session Management
> 
> **Files:**
> - `http.ts`: Handles API requests with authentication
> - `session.ts`: Manages session cookies
> - `api.ts`: Wraps API endpoints with type safety
> 
> **Key Features:**
> - Secure HTTP client with automatic authentication token handling
> - Cookie-based session management with httpOnly cookies
> - Type-safe API calls with proper error handling
> 
> ```typescript
> // http.ts
> export class ApiError extends Error {
>   readonly status: number;
>   constructor(status: number, body: unknown) {
>     super(`API request failed with status ${status}`);
>     this.name = 'ApiError';
>     this.status = status;
>     this.body = body;
>   }
> }
> 
> export async function request<T>(path: string, opts: RequestOptions = {}) {
>   // Implementation details
> }
> ```
> 
> ### 2. Authentication System
> 
> **Files:**
> - `login/page.tsx`: Login page
> - `login-form.tsx`: Login form component
> - `api/session/route.ts`: Session API route
> 
> **Key Features:**
> - Secure login with token-based authentication
> - Session management with cookie-based authentication
> - Route protection with middleware
> 
> ```typescript
> // middleware.ts
> export function middleware(req: NextRequest) {
>   // Implementation details
> }
> ```
> 
> ### 3. Ticket Management Interface
> 
> **Files:**
> - `tickets/page.tsx`: Ticket list page
> - `tickets/[id]/page.tsx`: Ticket detail page
> - `ticket-filters.tsx`: Ticket filters component
> - `comment-thread.tsx`: Comment thread component
> 
> **Key Features:**
> - Filterable ticket list with status/priority filters
> - Detailed ticket view with comment thread
> - Status and assignment controls
> - Commenting functionality
> 
> ```typescript
> // ticket-filters.tsx
> export function TicketFilters({ current }: { current: { status?: string; priority?: string } }) {
>   // Implementation details
> }
> ```
> 
> ### 4. UI Components
> 
> **Files:**
> - `button.tsx`: Custom button component
> - `field.tsx`: Form field component
> - `app-header.tsx`: Application header
> - `badge.tsx`: Status/priority badges
> 
> **Key Features:**
> - Consistent UI components with proper styling
> - Status/priority visualization with color-coded badges
> - Responsive layout for different screen sizes
> 
> ```typescript
> // badge.tsx
> export function Badge({ tone, value }: { tone: 'status' | 'priority'; value: string }) {
>   // Implementation details
> }
> ```
> 
> ### 5. Data Management
> 
> **Files:**
> - `lookups.ts`: Name lookup utilities
> - `format.ts`: Date formatting utilities
> 
> **Key Features:**
> - Efficient data lookup with name indexing
> - Consistent date formatting across the application
> 
> ```typescript
> // lookups.ts
> export function nameIndex(items: { id: string; name: string }[]): Map<string, string> {
>   // Implementation details
> }
> ```
> 
> ## Testing Strategy
> 
> ### Unit Tests
> 
> **Files:**
> - `http.spec.ts`: Tests for HTTP client
> - `api.spec.ts`: Tests for API wrappers
> - `login-form.spec.tsx`: Tests for login form
> - `comment-thread.spec.tsx`: Tests for comment thread
> 
> **Key Features:**
> - Comprehensive test coverage for all components
> - Mocking of dependencies for isolated testing
> - Type safety verification with TypeScript
> 
> ### Integration Tests
> 
> **Files:**
> - `ticket-list.test.tsx`: Tests for ticket list functionality
> - `ticket-detail.test.tsx`: Tests for ticket detail view
> 
> **Key Features:**
> - End-to-end testing of user workflows
> - Verification of state transitions and UI updates
> - Validation of API interactions
> 
> ## Security Considerations
> 
> 1. **Secure Session Management:**
>    - HTTP-only cookies for session tokens
>    - Secure cookie attributes (SameSite, Secure)
>    - No client-side storage of sensitive data
> 
> 2. **API Security:**
>    - Server-side API calls only
>    - No direct browser-to-API requests
>    - Proper error handling and validation
> 
> 3. **Input Validation:**
>    - All user inputs are validated and sanitized
>    - Proper handling of edge cases and invalid data
> 
> ## Documentation
> 
> ### Architecture Documentation
> 
> **File:** `docs/architecture.md`
> 
> **Key Points:**
> - Next.js App Router architecture
> - Server-side API integration
> - Session management architecture
> - Component structure and responsibilities
> 
> ### Development Guide
> 
> **File:** `README.md`
> 
> **Key Points:**
> - How to run the web application
> - Required environment variables
> - Development and testing instructions
> - Deployment considerations
> 
> ## Conclusion
> 
> This implementation provides a secure, type-safe, and well-tested web application for the SupportOps platform. The architecture follows best practices for Next.js applications, with proper separation of concerns and secure session management. The comprehensive testing strategy ensures that all components work as expected, and the documentation provides clear guidance for developers and maintainers.

