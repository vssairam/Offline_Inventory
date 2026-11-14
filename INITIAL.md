# INITIAL.md - Inventory Management Product Definition

> Add products, manage stock, get low-stock alerts, and view sales reports.

---

## PRODUCT

### Name
Inventory Management

### Description
A web app for small retailers to keep their product catalog, track stock levels, get alerted (in-app and by email) when items run low, and record sales that automatically deduct stock, with sales reports for insight.

### Target User
Small retailers and shop owners.

### Type
- [x] SaaS (Software as a Service)

---

## TECH STACK

### Backend
- [x] FastAPI + Python

### Frontend
- [x] React + Vite + TypeScript

### Database
- [x] PostgreSQL

### Authentication
- [x] Email/Password only (JWT access + refresh tokens)

### UI Framework
- [x] Tailwind + shadcn/ui

### Payments
- [x] None

---

## MODULES

### Module 1: Authentication (Required)

**Description:** User authentication and authorization

**Models:**
- User: id, email, hashed_password, full_name, is_active, is_verified, is_admin, created_at
- RefreshToken: id, user_id, token, expires_at, revoked

**API Endpoints:**
- POST /api/v1/auth/register - Create new account
- POST /api/v1/auth/login - Login with email/password
- POST /api/v1/auth/refresh - Refresh access token
- POST /api/v1/auth/logout - Revoke refresh token
- GET /api/v1/auth/me - Get current user profile
- PUT /api/v1/auth/me - Update profile

**Frontend Pages:**
- /login - Login page
- /register - Registration page
- /forgot-password - Forgot password page
- /profile - User profile page (protected)

---

### Module 2: Products

**Description:** Product catalog with categories, pricing, images and reorder levels.

**Models:**
- Category: id, user_id, name, created_at
- Product: id, user_id, category_id, name, sku (unique per user), price, cost, quantity (current stock), reorder_level, image_url, is_active, created_at, updated_at

**API Endpoints:**
- GET /api/v1/products - List/search products (query, category, low_stock filter, pagination)
- POST /api/v1/products - Create product
- GET /api/v1/products/{id} - Get product
- PUT /api/v1/products/{id} - Update product
- DELETE /api/v1/products/{id} - Delete product
- POST /api/v1/products/{id}/image - Upload product image
- GET/POST/PUT/DELETE /api/v1/categories - Manage categories

**Frontend Pages:**
- /products - Product list with search and filters
- /products/new - Create product form
- /products/:id/edit - Edit product form

---

### Module 3: Stock

**Description:** View current stock levels per product. Stock changes automatically when sales are recorded.

**Models:** Uses `Product.quantity` and `Product.reorder_level` (no separate movement-history model in MVP).

**API Endpoints:**
- GET /api/v1/stock - Stock levels for all products (supports low-stock filter)

**Frontend Pages:**
- /stock - Stock page showing current quantity vs. reorder level, low items highlighted

---

### Module 4: Alerts

**Description:** Low-stock alerts shown in the app and sent by email when a product's quantity falls to or below its reorder level.

**Models:**
- Alert: id, user_id, product_id, type (low_stock), message, is_read, email_sent, created_at

**API Endpoints:**
- GET /api/v1/alerts - List alerts
- PUT /api/v1/alerts/{id}/read - Mark alert as read

**Behavior:**
- Alert created (once per crossing) when a sale reduces quantity to <= reorder_level
- Email notification sent to the shop owner for each new low-stock alert
- Alerts surfaced in the app (dashboard widget / notification badge); no dedicated alerts page in MVP

---

### Module 5: Sales and Reports

**Description:** Record sales (which deduct stock) and view/export sales reports.

**Models:**
- Sale: id, user_id, total_amount, sold_at, created_at
- SaleItem: id, sale_id, product_id, quantity, unit_price, unit_cost

**API Endpoints:**
- GET /api/v1/sales - List sales (date range, pagination)
- POST /api/v1/sales - Record a sale (validates and deducts stock atomically)
- GET /api/v1/sales/{id} - Get sale details
- GET /api/v1/reports/sales - Sales report (totals, revenue, profit, top products by date range)
- GET /api/v1/reports/sales/export - Export report as CSV

**Frontend Pages:**
- /sales - Sales list
- /sales/new - Record sale form
- /reports - Sales report with date range and export

---

### Module 6: Dashboard

**Description:** Overview and statistics (analytics dashboard)

**Frontend Pages:**
- /dashboard - Widgets: total products, low-stock items, recent alerts, sales trend chart
- /settings - User settings and preferences

---

### Module 7: Admin Panel

**Description:** Admin-only management interface

**API Endpoints:**
- GET /api/v1/admin/users - List all users
- PUT /api/v1/admin/users/{id} - Update user status
- GET /api/v1/admin/stats - Platform statistics

**Frontend Pages:**
- /admin - Admin dashboard (protected, admin only)
- /admin/users - User management

---

## MVP SCOPE

### Must Have (MVP)
- [x] User registration and login
- [x] Add and edit products
- [x] Record sales (deducting stock)
- [x] Basic sales report

### Nice to Have (Post-MVP)
- [ ] Product deletion, search and category filters polish
- [ ] Low-stock alerts (in-app and email)
- [ ] Stock page and stock movement history / manual stock adjustments
- [ ] Report CSV export
- [ ] Product image uploads
- [ ] Analytics dashboard
- [ ] Admin panel

---

## ACCEPTANCE CRITERIA

### Authentication
- [ ] User can register with email/password
- [ ] User can login with email/password
- [ ] JWT tokens work correctly with refresh
- [ ] Protected routes redirect to login

### Products
- [ ] User can create, edit, delete and search products
- [ ] SKU is unique per user
- [ ] Users only see their own products

### Stock
- [ ] Stock page shows quantity and reorder level for each product
- [ ] Low-stock products are visually highlighted

### Alerts
- [ ] Alert is created when quantity drops to or below reorder level
- [ ] Email is sent for new low-stock alerts
- [ ] User can mark alerts as read

### Sales and Reports
- [ ] Recording a sale deducts stock atomically
- [ ] Sale is rejected if stock is insufficient
- [ ] Sales report shows totals, revenue and profit for a date range
- [ ] Report can be exported as CSV

### Quality
- [ ] All API endpoints documented in OpenAPI
- [ ] Backend test coverage 80%+
- [ ] Frontend TypeScript strict mode passes
- [ ] Docker builds and runs successfully

---

## SPECIAL REQUIREMENTS

### Security
- [x] Rate limiting on auth endpoints
- [x] Input validation on all endpoints
- [x] SQL injection prevention
- [x] XSS prevention
- [x] File upload validation (type and size) for product images

### Integrations
- [x] Email service for notifications (low-stock alerts)
- [ ] Payments (not needed)
- [x] File upload service (product images)

---

## AGENTS

> These 6 agents will build your product in parallel:

| Agent | Role | Works On |
|-------|------|----------|
| DATABASE-AGENT | Creates all models and migrations | All database models |
| BACKEND-AGENT | Builds API endpoints and services | All modules' backends |
| FRONTEND-AGENT | Creates UI pages and components | All modules' frontends |
| DEVOPS-AGENT | Sets up Docker, CI/CD, environments | Infrastructure |
| TEST-AGENT | Writes unit and integration tests | All code |
| REVIEW-AGENT | Security and code quality audit | All code |

---

# READY?

```bash
/generate-prp INITIAL.md
```

Then:

```bash
/execute-prp PRPs/inventory-management-prp.md
```
