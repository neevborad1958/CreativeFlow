# CreativeFlow ✦ Full-Stack Creative Freelancer Platform

**CreativeFlow** is a modern, responsive, production-oriented web application designed for freelance graphic designers, UI/UX architects, 3D motion designers, and creative studios to manage clients, projects, tasks, deliverable revisions, client approvals, invoices, and payments in one cohesive workspace.

Built with a **Python & Django** backend rendering clean **HTML5, CSS3, and vanilla JavaScript (ES6+)** with zero external node_modules or client-side npm build pipelines.

---

## 🎨 Visual Identity & Palette

Designed around a warm editorial studio aesthetic:
- **Warm Ivory Canvas**: `#F8F4EC`
- **Clean Paper Surface**: `#FFFDF7`
- **Obsidian Dark**: `#20241E`
- **Forest Green**: `#52664D`
- **Muted Sage**: `#A7B99A`
- **Lime Glow Accent**: `#D7F7A5`
- **Editorial Typography**: *Newsreader Serif* combined with *Plus Jakarta Sans*

---

## 🚀 Key Features

### 1. Signature Sliced-Screen Hero (Landing Page)
- 5 vertical visual slices with CSS 3D perspective transforms (`perspective: 1400px`).
- Smooth mouse parallax tracking in vanilla JavaScript (`backend/static/js/creativeflow.js`).
- Staggered perspective depth showing interconnected creative studio elements: brand system color swatches, Figma wireframe tokens, live milestone progress bar, revision quota meters, and real PDF invoice snippets.
- Interactive HTML5 Canvas 3D studio artifact with dynamic rotational lighting and drag-to-orbit controls.

### 2. Client Management & CRM
- Complete client CRUD with soft-delete archiving to protect historical financial records.
- Track associated projects, contact information, lifetime billings, and recent activity.

### 3. Project & Creative Brief Workspaces
- Multi-tab project workspaces for **Overview & Brief**, **Tasks**, **Deliverables**, **Revisions**, **Approvals**, and **Invoices**.
- Budget, due date, and milestone health tracking.

### 4. Interactive Task Kanban
- Visual Kanban board with native HTML5 drag-and-drop column transitions (**To Do**, **In Progress**, **In Review**, **Done**).
- Real-time persistence to Django database via Python endpoint (`/dashboard/tasks/update-status/`).
- Priority badges (`Urgent`, `High`, `Medium`, `Low`) and sprint filters.

### 5. Deliverable Version Control
- Track incremental versions (v1, v2, v3) for design files, prototypes, and render packages.
- Uploading a new version automatically updates the deliverable state back to *In Review* and advances version numbers without overwriting previous work.

### 6. Revision Allowance Engine (Scope Creep Guard)
- Configurable revision quotas per project (e.g. 2 or 3 rounds).
- Python server-side limit enforcement: when requested revisions reach the quota, the system halts the request and prompts an add-on discussion.

### 7. Client Approval Workflow
- Clients review specific deliverable versions and sign off with recorded timestamps, feedback notes, and verifiable digital signature trails.

### 8. Financial Engine & PDF Invoicing
- Publication-quality PDF generation powered by Python **ReportLab**.
- Strict Decimal precision math for subtotals, tax rates, and discounts.
- Partial payment records that automatically deduce outstanding balances.
- 1-click binary PDF download endpoint (`/api/v1/invoices/<id>/pdf/`).

### 9. Multi-Role Demo Mode
- Instant 1-click role switcher in the UI to experience the platform as:
  1. **Elena Rostova** (Freelancer / Studio Lead)
  2. **Marcus Vance** (Client - Lumina Health Labs)
  3. **Sophia Chen** (Collaborator / 3D Designer)

---

## 🛠️ Technology Stack

- **Backend**: Python 3.12+ (or 3.14), Django 6.1, Django REST Framework, ReportLab, Pillow, SQLite / PostgreSQL.
- **Frontend**: Clean HTML5, CSS3 Custom Properties Design System (`creativeflow.css`), Vanilla ES6+ JavaScript (`creativeflow.js`).
- **No Node/npm requirement**: Eliminates bulky `node_modules` overhead for maximum performance and lightning-fast page delivery.
- **Deployment**: Docker, Docker Compose, PostgreSQL 16.

---

## 🏁 Quickstart Instructions

### 1. Set Up Environment & Run Migrations
```powershell
# Windows PowerShell:
$env:PYTHONPATH="backend"
& ".venv\Scripts\python.exe" "backend\manage.py" migrate
& ".venv\Scripts\python.exe" "backend\manage.py" seed_demo_data
```

### 2. Run Automated Backend & Core Tests
```powershell
$env:PYTHONPATH="backend"
& ".venv\Scripts\python.exe" "backend\manage.py" test apps
& ".venv\Scripts\python.exe" "backend\manage.py" test apps.projects.tests
```

### 3. Start the Web Server
```powershell
$env:PYTHONPATH="backend"
& ".venv\Scripts\python.exe" "backend\manage.py" runserver
```

Open your browser to:
- **Landing Page & 3D Sliced Hero**: `http://127.0.0.1:8000/`
- **Studio Dashboard Overview**: `http://127.0.0.1:8000/dashboard/`
- **Projects & Briefs**: `http://127.0.0.1:8000/dashboard/projects/`
- **Tasks & Kanban Drag-and-Drop**: `http://127.0.0.1:8000/dashboard/tasks/`
- **Deliverables & Version Control**: `http://127.0.0.1:8000/dashboard/deliverables/`
- **Revision Quota Tracker**: `http://127.0.0.1:8000/dashboard/revisions/`
- **Sign-offs & Approvals**: `http://127.0.0.1:8000/dashboard/approvals/`
- **Invoices & ReportLab PDF**: `http://127.0.0.1:8000/dashboard/invoices/`
- **Reports & Studio Analytics**: `http://127.0.0.1:8000/dashboard/reports/`

---

## 📚 Seed Demo Accounts

Switch roles with 1 click in the top navigation or top sidebar:
- **Elena Rostova** (`elena@creativeflow.studio`): Freelancer / Creative Director (Full admin workspace).
- **Marcus Vance** (`marcus@luminahealth.io`): Client stakeholder (Lumina Health Labs, portal view with approvals & revisions).
- **Sophia Chen** (`sophia@creativeflow.studio`): Senior 3D Designer (Collaborator view).
