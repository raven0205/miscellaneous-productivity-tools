# AI E-commerce Marketing Autopilot — Implementation Plan

* **Version:** 1.0  
* **Status:** Approved Baseline  
* **Target:** MVP Release  

---

## Overview

This document outlines the step-by-step implementation plan for building the **AI E-commerce Marketing Autopilot**. Execution must strictly follow the defined phases to maintain system integrity, high test coverage ($\ge 90\%$ for critical logic), and verified guardrail enforcement.

---

## Execution Phases

### Phase 1: Foundation & Project Setup
**Goal:** Establish repository structure, database connection, linting/formatting pipelines, and initial FastAPI + React skeletons.

- [ ] **Task 1.1:** Initialize monorepo or standard directory structure (`/backend`, `/frontend`).
- [ ] **Task 1.2:** Configure Python backend (`FastAPI`, `SQLAlchemy`/`SQLModel`, `Alembic`, `pytest`, `HTTPX`, `pydantic`).
- [ ] **Task 1.3:** Configure React frontend (`Vite`, `React`, `TypeScript`, `TailwindCSS`, `Vitest`).
- [ ] **Task 1.4:** Set up PostgreSQL database container and initial migration baseline.
- [ ] **Task 1.5:** Configure code quality tools (Ruff/Black/mypy for Python, ESLint/Prettier/tsc for TS).

---

### Phase 2: Core Data Models & Synthetic Data Engine
**Goal:** Define schemas, implement migration scripts, and construct a deterministic synthetic data generator.

- [ ] **Task 2.1:** Define database models:
  - `User`, `Role`
  - `Customer`, `Cart`, `CartItem`
  - `Campaign`, `CampaignExecution`
  - `DeliveryAttempt`, `ConversionEvent`
  - `Incident`, `ResponderAction`, `AuditLog`, `SystemSettings`
- [ ] **Task 2.2:** Generate and execute initial Alembic migration.
- [ ] **Task 2.3:** Implement synthetic data generator (`FR-02`):
  - Seed 100 synthetic customers and carts.
  - Include exact distributions for consent/no-consent, abandoned/purchased, treatment/control, frequency capped, and failure scenarios.
  - Implement deterministic seeding command (`python -m app.cli seed-db`).

---

### Phase 3: Authentication, RBAC & System Settings
**Goal:** Secure the backend, establish user management, and provide validated configuration settings.

- [ ] **Task 3.1:** Implement password hashing (Argon2 / bcrypt) and JWT/session authentication (`FR-01`).
- [ ] **Task 3.2:** Implement backend RBAC middleware and dependency injection (`Administrator` vs. `Operator`).
- [ ] **Task 3.3:** Implement Audit Logging service to record security and configuration events (`NFR-02`).
- [ ] **Task 3.4:** Build Settings management service with validation (`FR-16`):
  - Abandonment threshold (default: 1 hour).
  - Polling interval (default: 60s).
  - Customer frequency cap (default: 1 send / 24 hrs).
  - Max discount cap (default: 5%).

---

### Phase 4: Core Guardrails & Safety Engine
**Goal:** Build deterministic, non-bypassable backend safety rules.

- [ ] **Task 4.1:** Implement Abandonment Eligibility Evaluator (`FR-03`).
- [ ] **Task 4.2:** Implement Marketing Consent Verification module (`FR-04`).
- [ ] **Task 4.3:** Implement Idempotency & Duplicate-Send Prevention service (`FR-05`):
  - Database unique constraints on `(cart_id, campaign_id)`.
  - Transactional pre-send idempotency checks.
- [ ] **Task 4.4:** Implement Atomic Customer Frequency Cap checks (`FR-06`).
- [ ] **Task 4.5:** Implement Discount Restriction validator (`FR-07`).
- [ ] **Task 4.6:** Write integration tests covering all guardrail boundaries ($\ge 90\%$ coverage).

---

### Phase 5: Delivery Simulation & Polling Worker
**Goal:** Construct the background job processor and delivery simulation layer.

- [ ] **Task 5.1:** Implement Replaceable Delivery Provider interface (`FR-10`):
  - Simulated backend supporting success, transient, and permanent failure rates.
  - Configurable bounded retries.
- [ ] **Task 5.2:** Build PostgreSQL-backed Polling Worker (`FR-03`):
  - Row locking (`FOR UPDATE SKIP LOCKED`) for multi-worker concurrency safety.
  - Job heartbeat and execution state tracking.

---

### Phase 6: Marketing Agents Development
**Goal:** Develop the Campaign, Personalization, and Performance Agents.

- [ ] **Task 6.1:** Implement **Campaign Agent** (`FR-08`):
  - Coordinates candidate querying, guardrail validation, message requests, and delivery submissions.
- [ ] **Task 6.2:** Implement **Personalization Agent** (`FR-09`):
  - Deterministic template engine (default).
  - Optional LLM integration with fallback on timeout/missing key/validation error.
- [ ] **Task 6.3:** Implement **Performance Agent** (`FR-11`):
  - Attributed purchase matching (24-hour window).
  - Calculation of delivery success rates, treatment/control conversion, and estimated incremental uplift.

---

### Phase 7: Incident Engine & Responder Agent
**Goal:** Implement automated monitoring alerts and the operational Responder Agent.

- [ ] **Task 7.1:** Implement Alert Detectors:
  - Delivery Failure Alert ($>20\%$ failure in rolling 5m window, min 10 attempts) (`FR-17`).
  - Conversion Degradation Alert ($>20\%$ relative drop, min 50 observations) (`FR-18`).
  - Duplicate-Send Attempt Alert (`FR-19`).
- [ ] **Task 7.2:** Implement **Responder Agent** (`FR-12`):
  - Action allowlist execution (automated transient retry, campaign pause).
  - Incident escalation logic for high-risk/ambiguous events.
  - Outcome verification before incident resolution.

---

### Phase 8: Dashboard & Frontend Interface
**Goal:** Build the four required UI pages in React with TypeScript and OpenAPI type generation.

- [ ] **Task 8.1:** Export OpenAPI spec from backend and generate TS API client types.
- [ ] **Task 8.2:** Build **Overview Dashboard Page** (`FR-13`):
  - Metrics cards, treatment vs. control charts, active campaigns, open incidents.
- [ ] **Task 8.3:** Build **Campaigns Page** (`FR-14`):
  - Execution history, guardrail rejections, attribution tables.
- [ ] **Task 8.4:** Build **Incidents Page** (`FR-15`):
  - Evidence timeline, responder logs, retry and approval actions.
- [ ] **Task 8.5:** Build **Settings & Audit Page** (`FR-16`):
  - Config forms with RBAC visibility and searchable audit logs.
- [ ] **Task 8.6:** Visual verification: Ensure all synthetic/simulated data badges are displayed clearly.

---

### Phase 9: Comprehensive Testing & Quality Gates
**Goal:** Validate system stability through unit, database integration, and end-to-end testing.

- [ ] **Task 9.1:** Execute full `pytest` suite for backend with coverage reporting ($\ge 90\%$ target on core logic).
- [ ] **Task 9.2:** Execute concurrency and race condition tests on worker and frequency caps.
- [ ] **Task 9.3:** Execute frontend component tests (`Vitest`).
- [ ] **Task 9.4:** Construct and run E2E Playwright test suite (`FR-08` through `FR-16` workflows).

---

### Phase 10: CI/CD Pipeline & Staging Verification
**Goal:** Automate checks and deploy to staging environment.

- [ ] **Task 10.1:** Set up GitHub Actions CI workflow (linting, typechecks, schema verification, pytest, Vitest, Playwright).
- [ ] **Task 10.2:** Configure staging deployment pipeline (FastAPI, React build, DB migration execution, worker startup).
- [ ] **Task 10.3:** Execute and document staging health check verification and manual rollback demonstration.

---

## Milestone Checkpoints

| Milestone | Target Completion Criteria |
| :--- | :--- |
| **M1: Core Engine** | DB migrations applied, synthetic data seeded, Guardrails verified by tests. |
| **M2: Agent Pipeline** | Campaign, Personalization, and Delivery simulation running via worker. |
| **M3: Operations** | Alerts triggering, Responder Agent executing allowable actions, incidents persisted. |
| **M4: Full Stack** | Frontend fully integrated with backend, RBAC active across all 4 pages. |
| **M5: Staging Ready** | $\ge 90\%$ test coverage on critical logic, CI passing, rollback demonstrated on staging. |