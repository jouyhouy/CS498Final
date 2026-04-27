# CS498 Final Project — Top-Level Design

## 1. Purpose

This document defines the **top-level product and system design** for a course-scale web application inspired by MongoDB Atlas' **Data Explorer** experience.

The goal is to build a usable, demo-ready platform that:
- helps users inspect and manage dataset-like content,
- provides clear navigation across data views,
- supports incremental backend integration (frontend-first development).

---

## 2. Product Scope (MVP)

### In Scope
- Single workspace with one active data cluster (course-project scale).
- Data Explorer-style UI:
  - left navigation for clusters/databases/collections,
  - top tabs for documents and data operations,
  - central pane for query/result exploration.
- Basic query/filter and pagination for documents.
- Schema summary view (field frequencies/types).
- Index list and validation rule display (read-first, write-later).

### Out of Scope (for now)
- Multi-tenant org billing and advanced RBAC.
- Production-grade sharding orchestration.
- Full backup/restore workflows.
- Complex pipeline builder UX parity with Atlas.

---

## 3. Design Principles

1. **Course-friendly simplicity**: prioritize demo reliability over distributed-system complexity.
2. **Frontend-first architecture**: UI works with mock adapters before backend is ready.
3. **Contract-driven integration**: stable API/data contracts reduce rework.
4. **Readability and learnability**: information hierarchy should be obvious in one glance.

---

## 4. Information Architecture (Data Explorer Inspired)

## 4.1 Left Pane: Resource Tree

Hierarchy:
- **Clusters**
  - Databases
    - Collections

Core interactions:
- Expand/collapse tree nodes.
- Select a collection to load explorer context.
- Search clusters/collections.

Expected state:
- One default cluster for MVP (`Cluster0`-like naming is fine).

## 4.2 Top Tabs (Collection Context)

Within a selected collection, provide tabs:
1. **Documents** — browse/filter raw records.
2. **Aggregations** — prebuilt/basic pipelines (MVP can start read-only).
3. **Schema** — inferred fields, types, and cardinality hints.
4. **Indexes** — existing index list and metadata.
5. **Validation** — JSON schema/rules shown in a readable form.

## 4.3 Main Workspace

- Query input bar (e.g., JSON-like filter).
- Data table/cards with paging.
- Context alerts/tips (e.g., schema or performance hints).
- Empty-state guidance when no data is loaded.

---

## 5. User Roles & Core Flows

## 5.1 Roles (MVP)

- **Viewer**: inspect data, run filters, read schema/indexes.
- **Editor (optional stretch)**: insert/update/delete records with guardrails.

## 5.2 Primary Flows

1. Open app → select cluster/database/collection.
2. Browse documents with filters and sort.
3. Switch to Schema tab → inspect field structure.
4. Switch to Indexes/Validation tabs → understand constraints.

---

## 6. Functional Requirements

## 6.1 Explorer Navigation
- Render hierarchical tree for cluster resources.
- Persist current selection in URL or app state.

## 6.2 Documents Tab
- Query by JSON filter (or key-value builder).
- Sort by one or more fields.
- Pagination with total count display.

## 6.3 Schema Tab
- Infer schema from sampled documents.
- Show per-field type distribution and occurrence ratio.

## 6.4 Indexes Tab
- Display index names, keys, uniqueness, and sparse/TTL flags.

## 6.5 Validation Tab
- Display active validation rules (if present).
- Show fallback message when none exists.

---

## 7. Non-Functional Requirements

- **Performance**: first contentful data render under ~2s for small datasets.
- **Reliability**: graceful loading/error/empty states in every tab.
- **Security**: no secrets in frontend; backend-only DB credentials.
- **Maintainability**: strict separation of UI, API client, and data adapters.

---

## 8. High-Level System Architecture

## 8.1 Frontend

Recommended layers:
- `pages/` or route views
- `components/` UI modules (tree, tabs, tables)
- `services/` API client + adapters
- `mocks/` static mock datasets

Pattern:
- `ExplorerService` interface
  - `MockExplorerService` (frontend-first)
  - `ApiExplorerService` (backend integration)

## 8.2 Backend

Responsibilities:
- API endpoints for explorer resources.
- Query sanitization and pagination guardrails.
- Schema/index metadata aggregation.

## 8.3 Database

- Single MongoDB cluster for MVP.
- One database and a few collections for demo workflows.
- Minimal index strategy based on query patterns.

---

## 9. API Contract (Draft)

Base: `/api`

- `GET /clusters`
  - Returns available clusters.
- `GET /clusters/:cluster/databases`
  - Returns databases in cluster.
- `GET /clusters/:cluster/databases/:db/collections`
  - Returns collections.
- `GET /collections/:id/documents?filter=&sort=&page=&limit=`
  - Returns paginated documents.
- `GET /collections/:id/schema`
  - Returns inferred schema summary.
- `GET /collections/:id/indexes`
  - Returns index metadata.
- `GET /collections/:id/validation`
  - Returns validation rules/status.

Response envelope (recommended):
```json
{
  "data": {},
  "meta": {
    "requestId": "...",
    "page": 1,
    "limit": 20,
    "total": 100
  },
  "error": null
}
```

---

## 10. Data Model (Logical)

Core entities:
- `Cluster`
  - `id`, `name`, `provider`, `region`
- `Database`
  - `id`, `clusterId`, `name`
- `Collection`
  - `id`, `databaseId`, `name`, `documentCount`
- `Document`
  - free-form JSON payload + metadata (`_id`, timestamps)
- `SchemaFieldSummary`
  - `fieldPath`, `types[]`, `presenceRatio`
- `IndexInfo`
  - `name`, `keys`, `unique`, `ttl`, `sparse`
- `ValidationRule`
  - `type`, `rawRule`, `lastUpdated`

---

## 11. UX Notes (Atlas-Inspired, Not Clone)

- Keep left tree compact and searchable.
- Use strong tab labels and persistent context breadcrumb.
- Show actionable empty states ("Analyze schema", "No indexes found").
- Prioritize visual hierarchy over visual complexity.

---

## 12. Delivery Plan

## Phase 1 — Frontend Skeleton (Mock Data)
- Implement explorer layout and tab shell.
- Hook all views to `MockExplorerService`.
- Add loading/error/empty states.

## Phase 2 — Backend API (Single Cluster)
- Implement endpoints for tree + documents + metadata.
- Add request validation and response envelope.

## Phase 3 — Integration
- Swap service binding from mock to API.
- Verify all tabs with real MongoDB data.

## Phase 4 — Hardening (Optional)
- Add auth guard.
- Add basic telemetry/logging.
- Improve query UX and index hints.

---

## 13. Risks and Mitigations

- **Risk:** Backend delayed.
  - **Mitigation:** Keep frontend contract stable via mock adapter.
- **Risk:** Query performance on large collection.
  - **Mitigation:** enforce pagination + add targeted indexes.
- **Risk:** Schema inconsistency in NoSQL docs.
  - **Mitigation:** sample-based schema summary with confidence hints.

---

## 14. Success Criteria (MVP)

Project is successful when:
1. User can navigate cluster → database → collection.
2. Documents tab supports filtering + pagination.
3. Schema/Indexes/Validation tabs display meaningful metadata.
4. Frontend works first with mock, then with real backend by config switch.
5. Demo is stable and understandable for graders in under 5 minutes.

---

## 15. Next Action Checklist

- [ ] Confirm frontend framework and folder conventions.
- [ ] Implement `ExplorerService` interface.
- [ ] Create mock payloads for one realistic collection.
- [ ] Build tree + tabs + documents table.
- [ ] Define backend endpoint signatures in code.
- [ ] Connect to GCP-hosted MongoDB and test end-to-end.
