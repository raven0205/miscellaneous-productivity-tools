# AI E-commerce Marketing Autopilot — Product Specification

**Version:** 1.0  
**Status:** Approved baseline for MVP implementation  
**Project type:** AI-assisted e-commerce marketing automation  
**Primary use case:** Abandoned-cart recovery  
**Target environment:** Local development followed by cloud staging  
**Data policy:** Synthetic data only for the MVP

---

## 1. Product Overview

### 1.1 Problem Statement

E-commerce stores lose potential revenue when customers add products to their carts but leave without completing a purchase.

Manually identifying abandoned carts, preparing personalized reminders, monitoring campaign performance, and investigating delivery failures can be time-consuming.

The AI E-commerce Marketing Autopilot aims to automate this workflow through coordinated marketing agents, deterministic safety rules, performance monitoring, and a separate operational Responder Agent.

### 1.2 Product Goal

Build an end-to-end application that can:

1. Identify eligible abandoned carts.
2. Validate customer consent and marketing policies.
3. Generate an appropriate recovery message.
4. Simulate email delivery.
5. Measure attributed purchases and estimated incremental performance.
6. Detect campaign and operational incidents.
7. Execute predefined low-risk recovery actions.
8. Escalate high-risk or unresolved incidents to a human.
9. Display campaign performance and operational activity through a dashboard.

The MVP must demonstrate that the workflow works reliably using synthetic data. It must not claim to demonstrate actual business uplift.

### 1.3 Success Criteria

The MVP is successful when:

- The complete abandoned-cart workflow works locally and in staging.
- All three marketing agents complete their defined responsibilities.
- The Responder Agent follows its authorization boundaries.
- Marketing consent, frequency caps, discount limits, and duplicate-send prevention are enforced.
- All four frontend pages work.
- Authentication, role permissions, audit logs, and alerts function correctly.
- Required automated tests pass.
- Critical business logic achieves at least 90% test coverage.
- CI blocks merging and deployment when required checks fail.
- Staging deployment is verified and rollback is demonstrated.
- All synthetic outcomes are clearly labelled.

---

## 2. Users and Permissions

The application has two user roles.

### 2.1 Administrator

Administrators can:

- Log in and access all four pages.
- View campaign and performance metrics.
- Inspect campaign executions and delivery outcomes.
- Investigate incidents.
- View audit history.
- Manage campaigns within the system's safety rules.
- Change high-risk settings.
- Create, disable, and manage operator accounts.

Administrators cannot bypass mandatory consent, frequency-cap, discount-cap, or duplicate-send protections.

### 2.2 Operator

Operators can:

- Log in.
- View the dashboard.
- View campaign details.
- Investigate incidents.
- View audit history.
- Execute explicitly permitted campaign or incident actions.

Operators cannot:

- Manage users.
- Change high-risk configuration.
- Override mandatory safety rules.
- Execute responder actions outside their permissions.

### 2.3 Authorization Requirements

- All protected backend endpoints require authentication.
- Role permissions must be checked by the backend.
- Frontend visibility controls are not a substitute for backend authorization.
- Unauthorized actions must be rejected and appropriately logged.
- Sensitive credentials must never appear in application logs.

---

## 3. MVP Functional Requirements

### FR-01: Authentication

**Description:** Users must authenticate before accessing protected application functionality.

Requirements:

- Support email/password login.
- Store passwords using secure password hashing.
- Provide protected routes and endpoints.
- Enforce administrator and operator permissions.
- Use appropriately secured, expiring sessions or tokens.
- Reject invalid credentials and unauthorized requests.
- Provide a logout mechanism.

**Acceptance criteria:**

- Valid users can log in.
- Invalid credentials are rejected.
- Unauthenticated users cannot access protected API endpoints.
- Operators cannot perform administrator-only actions.
- Authentication and authorization tests pass.

### FR-02: Synthetic Data Management

**Description:** The application must provide reproducible demo data for local development and testing.

Requirements:

- Seed approximately 100 synthetic customers and carts.
- Include customers with and without marketing consent.
- Include abandoned, purchased, and not-yet-eligible carts.
- Include previously processed carts.
- Include customers who have reached their frequency cap.
- Include discount eligibility cases.
- Include treatment and control assignments.
- Include successful and failed delivery scenarios.
- Include incidents and duplicate-send attempts.

**Acceptance criteria:**

- The dataset can be seeded reproducibly.
- Test scenarios do not depend on unpredictable random outcomes.
- Seed data does not contain real customer information.
- Resetting the demo environment produces a known initial state.

### FR-03: Abandoned-Cart Detection

**Description:** The Campaign Agent must identify carts eligible for recovery.

Requirements:

- Default abandonment threshold: one hour.
- Allow administrators to configure the threshold.
- Use a separate database-backed polling worker.
- Default polling interval: 60 seconds, configurable.
- Persist job status and processing attempts.
- Safely claim work when multiple workers run.
- Skip carts that are no longer eligible.
- Record eligibility decisions and rejection reasons.

**Acceptance criteria:**

- A cart below the abandonment threshold is not processed.
- A cart past the threshold can be processed when otherwise eligible.
- A cart that has already been purchased is not sent a recovery message.
- An already-processed cart is not processed into a second recovery send.
- Worker failures and processing attempts are recorded.
- Tests cover threshold boundaries and concurrent processing.

### FR-04: Consent Enforcement

**Description:** Only customers with valid marketing email consent may receive recovery messages.

Requirements:

- Marketing consent is mandatory.
- Recheck consent immediately before delivery.
- Suppress customers without consent.
- Record the suppression reason.
- Prevent agents and responder actions from bypassing consent.

**Acceptance criteria:**

- A customer without consent never receives a recovery message.
- A customer whose consent is withdrawn before delivery is suppressed.
- Suppressed messages do not reach the delivery provider.
- The rejection is recorded for investigation and auditing.

### FR-05: Duplicate-Send Prevention

**Description:** Each cart can receive at most one recovery message.

Requirements:

- Generate and enforce appropriate idempotency keys.
- Persist campaign execution and delivery state.
- Use database constraints and transactional checks where appropriate.
- Recheck previous sends immediately before delivery.
- Record duplicate-send attempts.
- Enforce protection when multiple jobs process concurrently.

**Acceptance criteria:**

- Reprocessing the same cart does not create a second recovery send.
- Concurrent workers cannot successfully send twice for the same cart.
- A retry after a successful send does not produce another send.
- Duplicate attempts are recorded and can trigger an incident.

### FR-06: Customer Frequency Cap

**Description:** Prevent excessive marketing messages to the same customer.

Requirements:

- Default maximum: one marketing message per customer per rolling 24-hour period.
- Allow administrators to configure the cap.
- Enforce the cap atomically in the backend.
- Recheck the cap immediately before delivery.
- Record rejected attempts.

**Acceptance criteria:**

- A customer who has already reached the cap is suppressed.
- A customer becomes eligible again when the configured rolling window permits it.
- Concurrent jobs cannot bypass the cap.
- Operators cannot change the cap.

### FR-07: Discount Restrictions

**Description:** Personalization may recommend an incentive only within approved limits.

Requirements:

- Default maximum discount: 5%.
- Allow administrators to configure the maximum.
- Validate offer eligibility and minimum order value where applicable.
- Enforce discount restrictions in the backend.
- Simulate discounts without issuing real coupons or modifying real prices.

**Acceptance criteria:**

- Valid offers within the configured limit can be used in simulated messages.
- Offers above the limit are rejected.
- Ineligible customers do not receive simulated offers.
- LLM output cannot override discount restrictions.

### FR-08: Campaign Agent

**Description:** Coordinate abandoned-cart recovery.

Requirements:

- Identify candidate carts.
- Request eligibility validation.
- Coordinate message personalization.
- Submit approved messages to the delivery provider.
- Record campaign execution status.
- Record guardrail rejections and processing failures.

**Acceptance criteria:**

- Eligible carts progress through the expected workflow.
- Ineligible carts are skipped with a recorded reason.
- Campaign status reflects the actual processing outcome.
- Duplicate processing does not create duplicate sends.

### FR-09: Personalization Agent

**Description:** Create an appropriate recovery message using deterministic templates and optional LLM assistance.

Requirements:

- Provide deterministic templates as the default.
- Optionally use an LLM to draft messages.
- Validate generated output before delivery.
- Reject malformed or policy-violating output.
- Fall back to deterministic messages when credentials are missing or the LLM fails.
- Avoid unnecessary disclosure of customer information to external services.

**Acceptance criteria:**

- The workflow succeeds without LLM credentials.
- Valid LLM output is still subject to backend validation.
- Missing credentials, timeouts, invalid output, and provider failures trigger fallback behavior.
- The agent cannot override consent, frequency caps, or discount limits.
- No unvalidated LLM output is sent.

### FR-10: Simulated Email Delivery

**Description:** Provide a replaceable delivery-provider interface with simulation enabled by default.

Requirements:

- Simulate successful delivery.
- Simulate transient and permanent failures.
- Record each delivery attempt.
- Support bounded retries for transient failures.
- Prevent duplicate sends during retries.
- Keep real email delivery disabled by default.

**Acceptance criteria:**

- Successful delivery is recorded.
- Transient failures can be retried within configured limits.
- Exhausted retries create an appropriate failure state or incident.
- Permanent failures do not trigger endless retries.
- No real email is sent during standard development or automated tests.

### FR-11: Performance Agent

**Description:** Calculate campaign performance and experiment outcomes.

Requirements:

- Calculate delivery success and failure rates.
- Calculate attributed purchases and revenue.
- Calculate treatment and control conversion rates.
- Use a 24-hour attribution window.
- Calculate estimated incremental performance.
- Report sample sizes and measurement limitations.
- Label synthetic outcomes as simulated.

**Acceptance criteria:**

- Metrics match the underlying synthetic events.
- Purchases are attributed only according to the defined attribution rules.
- Attributed purchases and estimated incremental uplift are shown separately.
- Treatment and control sample sizes are displayed.
- All charts and reports clearly identify simulated results.

### FR-12: Responder Agent

**Description:** Detect operational incidents and perform bounded recovery actions.

Requirements:

- Consume alerts and supporting evidence.
- Use deterministic incident rules and an explicit action allowlist.
- Automatically retry eligible transient failures within limits.
- Check worker health.
- Pause a failing campaign when an explicit rule authorizes it.
- Require human approval to resume campaigns paused for serious incidents.
- Require approval for high-risk or ambiguous remediation.
- Verify outcomes before resolving incidents.
- Escalate unresolved incidents.
- Record proposed and executed actions.

**Acceptance criteria:**

- Permitted low-risk actions can run automatically.
- High-risk actions require approval.
- Unauthorized actions are rejected.
- A failed recovery is escalated.
- An incident is not marked resolved before recovery is verified.
- The responder cannot bypass consent, duplicate-send prevention, frequency caps, or discount restrictions.
- Every action has an auditable record.

---

## 4. Dashboard and Frontend Requirements

The application must provide four pages.

### FR-13: Overview Dashboard

Display:

- Recovery rate.
- Attributed revenue.
- Estimated incremental uplift.
- Delivery success rate.
- Treatment versus control conversion.
- Active campaigns.
- Open incidents.
- Recent activity.

Charts:

- Recovery trends.
- Delivery outcomes.
- Treatment versus control conversion.

Requirements:

- Metrics must be calculated by the backend.
- The dashboard must display sample sizes where relevant.
- Simulated results must be clearly labelled.
- Related campaign and incident records should be accessible from the dashboard.

**Acceptance criteria:** All displayed metrics match backend calculations and synthetic records.

### FR-14: Campaigns Page

Display:

- Campaign status.
- Eligible carts processed.
- Delivery attempts and outcomes.
- Message decisions.
- Guardrail rejections.
- Purchase attribution.
- Related incidents and audit records.

**Acceptance criteria:** Users can inspect campaign outcomes and navigate to related records.

### FR-15: Incidents Page

Display:

- Incident type and status.
- Alert evidence.
- Incident timeline.
- Related campaigns and delivery events.
- Responder decisions and actions.
- Retry history.
- Escalation and resolution details.

**Acceptance criteria:** Users can investigate an incident and inspect its evidence and action history according to their permissions.

### FR-16: Settings and Audit Page

Display:

- Abandonment threshold.
- Polling interval.
- Customer frequency cap.
- Maximum discount.
- Conversion-degradation threshold.
- Minimum treatment-group sample size.
- Searchable audit records.
- Administrator-only user management.

**Acceptance criteria:**

- Administrators can change permitted settings.
- Operators cannot change high-risk settings or manage users.
- Invalid settings are rejected.
- Changes record actor, timestamp, old value, and new value.
- Secret values are never exposed in audit logs.

---

## 5. Alert Requirements

### FR-17: Delivery-Failure Alert

Trigger when both conditions are true:

- More than 20% of delivery attempts fail in a rolling five-minute window.
- At least 10 delivery attempts exist in that window.

Examples:

- 3 failures out of 10 attempts: alert.
- 2 failures out of 10 attempts: no alert.
- 4 failures out of 8 attempts: no alert under this rule because the minimum sample is not met.

**Acceptance criteria:** Tests verify the minimum attempt count, exact threshold boundary, and rolling-window behavior.

### FR-18: Conversion-Degradation Alert

Defaults:

- Relative decline threshold: 20%.
- Minimum treatment-group observations: 50.

Both settings are administrator-configurable.

Requirements:

- Validate changes.
- Audit every configuration change.
- Define and consistently calculate the comparison baseline.
- Do not evaluate the alert until the minimum sample size is met.
- Record baseline, observed conversion, sample size, threshold, and triggering evidence.
- Distinguish relative decline from percentage-point decline.

Example: A baseline conversion rate of 10% declining to 8% represents a 20% relative decline and a 2-percentage-point decline.

**Acceptance criteria:**

- Samples below 50 treatment observations do not trigger this alert.
- Samples meeting the minimum are evaluated against the configured threshold.
- Invalid settings are rejected.
- The baseline and calculation are visible in incident evidence.
- Tests cover threshold boundaries and sample-size boundaries.

The alert is an operational signal, not proof of statistical significance.

### FR-19: Duplicate-Send Alert

Requirements:

- Detect duplicate-send attempts.
- Record supporting evidence.
- Create an incident according to the configured incident policy.
- Preserve the underlying duplicate-send protection even if alert processing fails.

**Acceptance criteria:** Duplicate attempts are blocked, recorded, and observable.

### FR-20: Technical Health Monitoring

Monitor:

- API availability and latency.
- Database errors.
- Worker heartbeat.
- Worker processing lag.
- Job failures and retry counts.

**Acceptance criteria:** Health and failure states can be observed through logs, metrics, and applicable incidents.

---

## 6. Non-Functional Requirements

### NFR-01: Reliability

- Persist worker jobs and execution state in PostgreSQL.
- Support bounded retries.
- Prevent duplicate processing and sending.
- Handle restarts without losing recorded state.
- Fail safely when optional integrations are unavailable.

### NFR-02: Security

- Secure password hashing.
- Protected API endpoints.
- Server-side role enforcement.
- Secure secret management.
- No secrets or passwords in logs.
- Auditing for important security and business actions.

### NFR-03: Maintainability

- Use clear separation between API, business services, agents, responder, database, and integrations.
- Use type hints and validated request/response schemas.
- Use database migrations.
- Keep optional integrations behind interfaces.
- Avoid unnecessary infrastructure.

### NFR-04: Testability

- Provide deterministic seed data.
- Mock external services in automated tests.
- Test success, failure, boundary, and concurrency scenarios.
- Use a real PostgreSQL test database for critical integration tests.

### NFR-05: Cost Control

- The application must work without LLM credentials.
- Simulated delivery is the default.
- LLM calls are limited to message drafting and incident assistance.
- Apply request timeouts and token limits.
- Verify cloud hosting costs before deployment.
- Avoid paid monitoring dependencies for the MVP.

### NFR-06: Observability

- Use structured logs.
- Expose health and readiness endpoints.
- Track API and worker metrics.
- Persist incidents and responder actions.
- Record important guardrail rejections.

### NFR-07: Performance and Processing

- Use a configurable polling interval, defaulting to 60 seconds.
- Avoid unnecessary database queries and repeated processing.
- Record processing latency and backlog size.
- Do not claim real-time processing; the polling design is periodic.

---

## 7. API and Data Contract Requirements

The backend must expose a documented REST API through FastAPI's OpenAPI schema.

Required API groups:

- Authentication and current-user information.
- Dashboard metrics.
- Campaigns and campaign executions.
- Carts and eligibility decisions.
- Delivery attempts and events.
- Purchase attribution and experiment results.
- Incidents and responder actions.
- Settings and configuration changes.
- User management.
- Audit records.
- Health and readiness.

Requirements:

- Validate all request payloads.
- Return consistent error responses.
- Enforce authorization on protected operations.
- Generate TypeScript types from OpenAPI.
- Verify API schema/type consistency in CI.
- Never rely on frontend validation alone for critical rules.

Exact endpoint paths and schemas should be finalized in the implementation plan or API design before the corresponding feature is coded.

---

## 8. Testing Requirements

### 8.1 Backend

Use pytest and HTTPX for unit and API tests.

Test:

- Eligibility and abandonment thresholds.
- Consent enforcement.
- Frequency caps.
- Discount limits.
- Idempotency.
- Attribution and experiment calculations.
- Alert rules.
- Settings validation.
- Authentication and role enforcement.
- Responder action authorization.
- LLM fallback behavior.
- Simulated delivery retries.

### 8.2 Database Integration

Use PostgreSQL to test:

- Migrations from an empty database.
- Constraints and transactions.
- Concurrent worker execution.
- Duplicate-send prevention.
- Atomic frequency-cap enforcement.
- Persistent job state.
- Incident and audit persistence.

### 8.3 Frontend

Use Vitest and React Testing Library to test:

- All four pages.
- Forms and settings validation.
- Loading and error states.
- Permission-based UI behavior.
- Campaign and incident interactions.
- Simulated-data labels.

### 8.4 End-to-End

Use Playwright for critical browser workflows.

At minimum, test:

1. Administrator login.
2. Dashboard display.
3. Campaign inspection.
4. Abandoned-cart recovery.
5. Simulated delivery.
6. Attribution reporting.
7. Incident generation.
8. Responder action history.
9. Audit history.
10. Operator permission restrictions.

### 8.5 Quality Gate

- All required tests must pass.
- Backend and frontend linting must pass.
- Type checking must pass.
- API schema checks must pass.
- Migration checks must pass.
- Critical business logic must achieve at least 90% test coverage.
- CI failures must block merging and deployment.

---

## 9. CI/CD and Deployment Requirements

### 9.1 Continuous Integration

GitHub Actions must run the required backend, frontend, integration, migration, schema, and quality checks.

The `main` branch must be protected by required checks.

### 9.2 Staging Deployment

After a successful merge:

1. Deploy the frontend.
2. Deploy the backend.
3. Apply migrations explicitly.
4. Start or update the worker.
5. Verify health and readiness.
6. Verify database connectivity.
7. Run critical smoke tests.
8. Record deployment status.

### 9.3 Production Approval

Production deployment requires manual approval.

Real email delivery and real customer data are outside the default MVP configuration.

### 9.4 Rollback

Demonstrate rollback to a known-good application version.

Verify API health, frontend availability, database connectivity, worker health, and a critical workflow after rollback.

Handle database rollback separately. Prefer backward-compatible migrations and use a forward fix or documented backup/restore procedure when reversal is unsafe.

---

## 10. Staging Acceptance Checklist

The MVP is accepted only when the following criteria pass.

### Product functionality

- [ ] All four frontend pages work.
- [ ] All three marketing agents complete their responsibilities.
- [ ] The Responder Agent follows its authorization boundaries.
- [ ] The synthetic abandoned-cart workflow completes end to end.
- [ ] Attribution and treatment/control reporting are correct.
- [ ] Related campaign, incident, and audit records are linked.

### Guardrails

- [ ] Consent is enforced immediately before sending.
- [ ] No cart receives more than one recovery message.
- [ ] Frequency caps are enforced atomically.
- [ ] Discount restrictions are enforced by the backend.
- [ ] Administrator/operator permissions are enforced.
- [ ] LLM failure does not break the core workflow.
- [ ] Real email delivery is disabled by default.

### Alerts and operations

- [ ] Delivery-failure alert boundaries are tested.
- [ ] Conversion-degradation threshold and minimum sample size are tested.
- [ ] Duplicate-send attempts are detected and recorded.
- [ ] Worker health is observable.
- [ ] Responder actions are audited.
- [ ] Failed recovery is escalated.
- [ ] Incidents are resolved only after recovery is verified.

### Quality and deployment

- [ ] Backend tests pass.
- [ ] Frontend tests pass.
- [ ] PostgreSQL integration tests pass.
- [ ] Concurrency tests pass.
- [ ] Playwright critical workflows pass.
- [ ] Critical business logic achieves at least 90% coverage.
- [ ] CI blocks merges when required checks fail.
- [ ] Staging health checks pass.
- [ ] Deployment verification passes.
- [ ] Rollback is demonstrated and verified.
- [ ] Synthetic outcomes are clearly labelled.
- [ ] No real emails are sent by default.

---

## 11. Implementation Order

Build incrementally, verifying each stage before expanding the scope.

1. Repository, environment setup, FastAPI, React, and PostgreSQL.
2. Database models, migrations, and deterministic synthetic data.
3. Authentication, roles, audit logs, and settings validation.
4. Eligibility, consent, frequency caps, discount limits, and idempotency.
5. Simulated email delivery.
6. PostgreSQL-backed polling worker.
7. Campaign Agent.
8. Personalization Agent with deterministic fallback.
9. Performance Agent and experiment measurement.
10. Incident rules and Responder Agent.
11. Dashboard, Campaigns, Incidents, and Settings/Audit pages.
12. Backend, frontend, integration, concurrency, and end-to-end tests.
13. CI quality gates and OpenAPI/type consistency checks.
14. Optional LLM integration.
15. Staging deployment, health verification, and demonstrated rollback.

Do not proceed to the next major phase until the previous phase has a working implementation and passing tests.

---

## 12. Definition of Done

A feature is considered complete when:

- Its requirements are implemented.
- Input validation and authorization are enforced.
- Relevant failure cases are handled.
- Important actions and failures are recorded.
- Unit and integration tests cover expected behavior and boundaries.
- Frontend behavior is tested where applicable.
- Documentation is updated.
- Required CI checks pass.

The overall MVP is complete when every staging acceptance criterion passes.

---

## 13. Relationship to Other Project Documents

- **`specs.md`** — Defines product behavior, functional requirements, non-functional requirements, and acceptance criteria.
- **`architecture.md`** — Defines system structure, technology choices, components, data model, security boundaries, and deployment design.
- **`plan.md`** — Defines implementation phases, task dependencies, milestones, and execution order.
- **`README.md`** — Explains the project, prerequisites, local setup, commands, testing, and deployment instructions.

The requirements in this specification must be satisfied by the implementation. If implementation constraints require a change, update the relevant specification and architecture before proceeding.

