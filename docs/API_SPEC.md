# CreativeFlow REST API Specification (v1)

Base URL: `/api/v1`

All protected endpoints accept either:
- Cookie-based session authentication (`sessionid`)
- Header-based user context (`X-User-Id: <id>` or `Authorization: Bearer <id>`)

---

## 1. Authentication (`/api/v1/auth/`)

- `POST /auth/register/`: Register a new freelancer or client user.
- `POST /auth/login/`: Authenticate and start session.
- `POST /auth/logout/`: Terminate session.
- `GET /auth/me/`: Retrieve current authenticated profile.
- `PATCH /auth/me/`: Update profile details (hourly rate, title, bio, avatar).
- `GET /auth/demo-users/`: List seeded demo accounts for instant switching:
  - **Elena Rostova** (Principal Creative Director, id: 1)
  - **Marcus Vance** (Client - Lumina Health Labs, id: 2)
  - **Sophia Chen** (Senior 3D & Motion Designer, id: 3)

---

## 2. Client Management (`/api/v1/clients/`)

- `GET /clients/?search=<query>&archived=<bool>`: List clients with search and filter.
- `POST /clients/`: Create client profile.
- `GET /clients/<id>/`: Retrieve client details with project and billing statistics.
- `PATCH /clients/<id>/`: Update client contact or notes.
- `DELETE /clients/<id>/`: Soft-delete/archive client without compromising historical invoices.

---

## 3. Project Workspace (`/api/v1/projects/`)

- `GET /projects/?status=<status>&client=<client_id>&search=<query>`: List filtered projects.
- `POST /projects/`: Create project with brief, budget, deadlines, and revision allowances.
- `GET /projects/<id>/`: Retrieve full project workspace with deliverables.
- `PATCH /projects/<id>/`: Update status, dates, priority, or brief.

---

## 4. Deliverables & Versions (`/api/v1/deliverables/`)

- `GET /deliverables/?project=<project_id>`: List deliverables.
- `POST /deliverables/`: Create a project deliverable specification.
- `GET /deliverables/<id>/`: Retrieve deliverable and its full version history.
- `POST /deliverables/versions/`: Advance version counter (e.g. v1 -> v2) and reset deliverable status to `in_review`.

---

## 5. Tasks & Kanban Board (`/api/v1/tasks/`)

- `GET /tasks/?project=<project_id>&status=<status>&priority=<priority>`: List tasks.
- `POST /tasks/`: Create a task.
- `GET /tasks/<id>/`: Retrieve task details with comments.
- `PATCH /tasks/<id>/`: Update status (auto-records `completed_at` timestamp if marked `done`).
- `DELETE /tasks/<id>/`: Delete task.
- `POST /tasks/<id>/comments/`: Append activity comments to task.

---

## 6. Revision Scope Tracking (`/api/v1/revisions/`)

- `GET /revisions/?project=<project_id>&status=<status>`: List revision requests.
- `POST /revisions/`: Submit client change request (validates and enforces project revision allowance).
- `PATCH /revisions/<id>/`: Resolve revision or reject with explanation.

---

## 7. Client Approvals (`/api/v1/approvals/`)

- `GET /approvals/?project=<project_id>&version=<version_id>`: List recorded sign-offs.
- `POST /approvals/`: Persist immutable approval decision (`approved` or `changes_requested`) with client signature and feedback. Automatically updates deliverable version status.

---

## 8. Invoices & Payments (`/api/v1/invoices/`)

- `GET /invoices/?client=<client_id>&status=<status>`: List invoices with computed balance dues.
- `POST /invoices/`: Issue new invoice with dynamic line items. Server calculates subtotals, taxes, and totals.
- `GET /invoices/<id>/`: Retrieve invoice breakdown.
- `GET /invoices/<id>/pdf/`: Stream crisp ReportLab PDF invoice download.
- `POST /invoices/<id>/payments/`: Record partial or full payment. Deducts balance due and updates status to `partially_paid` or `paid`.

---

## 9. In-App Notifications & Activity (`/api/v1/notifications/`)

- `GET /notifications/`: List user's notifications.
- `PATCH /notifications/<id>/read/`: Mark notification as read.
- `POST /notifications/mark-all-read/`: Mark all user notifications as read.
- `GET /notifications/activity/`: Recent studio activity feed.

---

## 10. Financial & Sprint Reports (`/api/v1/reports/`)

- `GET /reports/dashboard/`: Computes aggregated metrics:
  - `active_projects`
  - `projects_in_review`
  - `task_completion_rate`
  - `total_invoiced`
  - `total_paid_revenue` (actual cash collected)
  - `outstanding_balance`
  - `monthly_revenue` breakdown
  - `status_distribution`

