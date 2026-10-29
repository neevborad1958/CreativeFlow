# CreativeFlow — Deployment & Local Operations Guide

This guide details running CreativeFlow locally or deploying it in a production containerized environment.

---

## 1. Local Development (Instant Setup)

### Prerequisites
- Python 3.12+ (or 3.14)
- Node.js 20+

### Step 1: Backend Setup
```bash
# In the repository root:
# 1. Activate the Python virtual environment
.venv\Scripts\activate      # Windows
# or: source .venv/bin/activate  # macOS / Linux

# 2. Navigate to backend directory
cd backend

# 3. Apply database migrations
python manage.py migrate

# 4. Populate with rich creative studio demo data
python manage.py seed_demo_data

# 5. Start the Django development server
python manage.py runserver 127.0.0.1:8000
```
Backend API will be live at `http://127.0.0.1:8000/api/v1/`.

### Step 2: Frontend Setup
```bash
# In a separate terminal:
cd frontend

# Start the Vite development server with proxying
npm run dev
```
Open `http://localhost:5173` in your browser.

---

## 2. Running Automated Tests

### Backend Unit & Integration Tests:
```bash
cd backend
python manage.py test apps.projects.tests
```

### Frontend Typecheck & Build:
```bash
cd frontend
npm run build
```

---

## 3. Seeded Demo Accounts

You can test all 3 roles seamlessly with the role switcher in the UI or by logging in:

| Role | Username | Password | Identity |
|---|---|---|---|
| **Freelancer / Studio Lead** | `elena` | `creative123` | Elena Rostova (Principal Creative Director) |
| **Client** | `marcus` | `client123` | Marcus Vance (VP Brand, Lumina Health Labs) |
| **Team Member** | `sophia` | `team123` | Sophia Chen (Senior 3D & Motion Designer) |

---

## 4. Docker Compose Deployment (PostgreSQL + Redis + Django + React)

```bash
# Spin up complete stack with PostgreSQL database:
docker-compose up --build
```
- Frontend: `http://localhost:5173`
- Backend API: `http://localhost:8000`
- PostgreSQL: `localhost:5432`

