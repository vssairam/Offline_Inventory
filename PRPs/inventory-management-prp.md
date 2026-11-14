# PRP: Inventory Management

> Implementation blueprint for parallel agent execution

---

## METADATA

| Field | Value |
|-------|-------|
| **Product** | Inventory Management |
| **Type** | SaaS |
| **Version** | 1.0 |
| **Created** | 2026-11-14 |
| **Complexity** | Medium |

---

## PRODUCT OVERVIEW

**Description:** A web app for small retailers to keep a product catalog, track stock levels, get low-stock alerts (in-app and by email), and record sales that automatically deduct stock, with sales reports.

**Value Proposition:** Shop owners avoid stock-outs and over-ordering, and see revenue and profit without spreadsheets.

**MVP Scope:**
- [ ] User registration and login
- [ ] Add and edit products
- [ ] Record sales (deducting stock atomically)
- [ ] Basic sales report

**Post-MVP (built after MVP gate, still in this PRP's phases 2b):** product delete/search polish, stock page, low-stock alerts + email, CSV export, image uploads, analytics dashboard, admin panel.

---

## TECH STACK

| Layer | Technology | Skill Reference |
|-------|------------|-----------------|
| Backend | FastAPI + Python 3.11+ | skills/BACKEND.md |
| Frontend | React + TypeScript + Vite | skills/FRONTEND.md |
| Database | PostgreSQL + SQLAlchemy + Alembic | skills/DATABASE.md |
| Auth | Email/Password, JWT (access + refresh) + bcrypt | skills/BACKEND.md |
| UI | Tailwind CSS + shadcn/ui | skills/FRONTEND.md |
| Testing | pytest + React Testing Library | skills/TESTING.md |
| Deployment | Docker + GitHub Actions | skills/DEPLOYMENT.md |

---

## DATABASE MODELS

### User
- id, email (unique), hashed_password, full_name, is_active, is_verified, is_admin, created_at

### RefreshToken
- id, user_id (FK User), token, expires_at, revoked

### Category
- id, user_id (FK User), name, created_at
- Unique (user_id, name)

### Product
- id, user_id (FK User), category_id (FK Category, nullable), name, sku, price Numeric(10,2), cost Numeric(10,2), quantity (int >= 0), reorder_level (int >= 0), image_url (nullable), is_active, created_at, updated_at
- Unique (user_id, sku); index on (user_id, name)

### Sale
- id, user_id (FK User), total_amount Numeric(12,2), sold_at, created_at

### SaleItem
- id, sale_id (FK Sale), product_id (FK Product), quantity (int > 0), unit_price Numeric(10,2), unit_cost Numeric(10,2)

### Alert
- id, user_id (FK User), product_id (FK Product), type (`low_stock`), message, is_read, email_sent, created_at

Relationships: User 1-N Category/Product/Sale/Alert; Category 1-N Product; Sale 1-N SaleItem; Product 1-N SaleItem/Alert.

---

## MODULES

### Module 1: Authentication
**Agents:** DATABASE-AGENT + BACKEND-AGENT + FRONTEND-AGENT

**Backend Endpoints:**
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/v1/auth/register | Create account |
| POST | /api/v1/auth/login | Get tokens |
| POST | /api/v1/auth/refresh | Refresh access token |
| POST | /api/v1/auth/logout | Revoke refresh token |
| GET | /api/v1/auth/me | Current user |
| PUT | /api/v1/auth/me | Update profile |

**Frontend Pages:**
| Route | Page | Components |
|-------|------|------------|
| /login | LoginPage | LoginForm |
| /register | RegisterPage | RegisterForm |
| /forgot-password | ForgotPasswordPage | ForgotPasswordForm |
| /profile | ProfilePage (protected) | ProfileForm |

---

### Module 2: Products
**Agents:** BACKEND-AGENT + FRONTEND-AGENT

**Backend Endpoints:**
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/v1/products | List/search (q, category_id, low_stock, pagination) |
| POST | /api/v1/products | Create |
| GET | /api/v1/products/{id} | Get one |
| PUT | /api/v1/products/{id} | Update |
| DELETE | /api/v1/products/{id} | Delete |
| POST | /api/v1/products/{id}/image | Upload image (post-MVP) |
| GET/POST | /api/v1/categories | List / create category |
| PUT/DELETE | /api/v1/categories/{id} | Update / delete category |

**Frontend Pages:**
| Route | Page | Components |
|-------|------|------------|
| /products | ProductListPage | ProductTable, SearchBar, CategoryFilter |
| /products/new | ProductCreatePage | ProductForm |
| /products/:id/edit | ProductEditPage | ProductForm, ImageUpload |

---

### Module 3: Stock (post-MVP)
**Agents:** BACKEND-AGENT + FRONTEND-AGENT

**Backend Endpoints:**
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/v1/stock | Stock levels (low_stock filter) |

**Frontend Pages:**
| Route | Page | Components |
|-------|------|------------|
| /stock | StockPage | StockTable (low items highlighted) |

No movement-history model; stock changes only via sales.

---

### Module 4: Alerts (post-MVP)
**Agents:** BACKEND-AGENT + FRONTEND-AGENT

**Backend Endpoints:**
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/v1/alerts | List alerts |
| PUT | /api/v1/alerts/{id}/read | Mark read |

**Behavior:** Sale service creates one alert per threshold crossing (quantity <= reorder_level, no duplicate while still low) and sends email in a background task; email failure never fails the sale.

**Frontend:** Notification badge + dashboard widget (no dedicated page).

---

### Module 5: Sales and Reports
**Agents:** BACKEND-AGENT + FRONTEND-AGENT

**Backend Endpoints:**
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/v1/sales | List (date range, pagination) |
| POST | /api/v1/sales | Record sale; validate + deduct stock in one transaction |
| GET | /api/v1/sales/{id} | Sale details |
| GET | /api/v1/reports/sales | Totals, revenue, profit, top products |
| GET | /api/v1/reports/sales/export | CSV export (post-MVP) |

**Frontend Pages:**
| Route | Page | Components |
|-------|------|------------|
| /sales | SalesListPage | SalesTable |
| /sales/new | SaleCreatePage | SaleForm, ProductPicker |
| /reports | ReportsPage | DateRangePicker, ReportSummary, ExportButton |

---

### Module 6: Dashboard (post-MVP)
**Agents:** FRONTEND-AGENT (+ BACKEND-AGENT for aggregate queries)

**Frontend Pages:**
| Route | Page | Components |
|-------|------|------------|
| /dashboard | DashboardPage | StatCards, SalesTrendChart, LowStockWidget, RecentAlerts |
| /settings | SettingsPage | SettingsForm |

---

### Module 7: Admin Panel (post-MVP)
**Agents:** BACKEND-AGENT + FRONTEND-AGENT

**Backend Endpoints:**
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/v1/admin/users | List users |
| PUT | /api/v1/admin/users/{id} | Update user status |
| GET | /api/v1/admin/stats | Platform stats |

**Frontend Pages:**
| Route | Page | Components |
|-------|------|------------|
| /admin | AdminDashboardPage (admin only) | StatsCards |
| /admin/users | AdminUsersPage (admin only) | UserTable |

---

## PHASE EXECUTION PLAN

**Phase 1: Foundation (4 agents in parallel)**
- DATABASE-AGENT: All 7 models, Alembic migration, database.py
- BACKEND-AGENT: main.py, config.py, project structure, /health, auth dependencies
- FRONTEND-AGENT: Vite + Tailwind + shadcn/ui setup, folder structure, API client, protected-route wrapper
- DEVOPS-AGENT: Dockerfiles, docker-compose (api, web, postgres), CI workflow, .env.example

**Validation Gate 1:** `pip install -r requirements.txt`, `alembic upgrade head`, `npm install`, `docker-compose config`

**Phase 2a: MVP Modules (backend + frontend in parallel per module)**
- Auth: JWT endpoints + Login/Register/Profile pages
- Products: CRUD endpoints + list/form pages
- Sales and Reports: atomic sale endpoint, report endpoint + sales/report pages

**Validation Gate 2a (MVP gate):** ruff, mypy, `npm run lint`, `npm run type-check`, manual flow: register, add product, record sale, view report

**Phase 2b: Post-MVP Modules (parallel)**
- Stock: endpoint + stock page
- Alerts: alert service, email sender, endpoints, badge/widget
- Products extras: image upload, categories UI
- Reports extras: CSV export
- Dashboard: aggregate endpoint + dashboard/settings pages
- Admin: admin endpoints + admin pages

**Validation Gate 2b:** ruff check, mypy, npm lint, npm type-check

**Phase 3: Quality (3 agents in parallel)**
- TEST-AGENT: pytest + RTL tests, 80%+ backend coverage (focus: stock deduction atomicity, insufficient stock, per-user isolation, alert dedupe)
- REVIEW-AGENT: Security audit (auth, upload validation, rate limiting, per-user data isolation), performance review
- RESEARCH-AGENT: Best practices validation

**Final Validation:** Full test suite, docker build, health checks

---

## VALIDATION GATES

| Gate | Commands |
|------|----------|
| 1 | `alembic upgrade head`, `npm install`, `docker-compose config` |
| 2a / 2b | `ruff check backend/`, `mypy backend/app`, `npm run lint`, `npm run type-check` |
| 3 | `pytest --cov --cov-fail-under=80`, `npm test` |
| Final | `docker-compose up -d`, `curl localhost:8000/health` |

---

## ENVIRONMENT VARIABLES

```env
DATABASE_URL=postgresql://user:password@localhost:5432/inventory_management
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USER=your-smtp-user
SMTP_PASSWORD=your-smtp-password
EMAIL_FROM=alerts@example.com
UPLOAD_DIR=./uploads
MAX_UPLOAD_MB=5
VITE_API_URL=http://localhost:8000
```

---

## NEXT STEP

Execute with parallel agents:
/execute-prp PRPs/inventory-management-prp.md
