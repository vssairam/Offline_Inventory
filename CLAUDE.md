# CLAUDE.md - Inventory Management Project Rules

> Project-specific rules for Claude Code. This file is read automatically.

---

## Project Overview

**Project Name:** Inventory Management
**Description:** Add products, manage stock, low-stock alerts, and sales reports for small retailers.
**Tech Stack:**
- Backend: FastAPI + Python 3.11+
- Frontend: React + Vite + TypeScript
- Database: PostgreSQL + SQLAlchemy (Alembic migrations)
- Auth: Email/Password (JWT access + refresh tokens)
- UI: Tailwind CSS + shadcn/ui

---

## Project Structure

```
inventory-management/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── models/
│   │   │   ├── user.py
│   │   │   ├── category.py
│   │   │   ├── product.py
│   │   │   ├── sale.py          # Sale, SaleItem
│   │   │   └── alert.py
│   │   ├── schemas/
│   │   ├── routers/
│   │   ├── services/
│   │   └── auth/
│   ├── alembic/
│   ├── tests/
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── hooks/
│   │   ├── services/
│   │   ├── context/
│   │   └── types/
│   └── package.json
├── .claude/
│   └── commands/
├── skills/
├── agents/
└── PRPs/
```

---

## Code Standards

### Python (Backend)
```python
# ALWAYS use type hints
def get_product(db: Session, product_id: int, user_id: int) -> Product:
    pass

# ALWAYS add docstrings for public functions
def create_sale(db: Session, user_id: int, data: SaleCreate) -> Sale:
    """
    Record a sale and deduct stock atomically.

    Args:
        db: Database session
        user_id: Owner of the sale
        data: Sale creation data

    Returns:
        Created Sale object
    """
    pass
```

### TypeScript (Frontend)
```typescript
// ALWAYS define interfaces for props and data
interface ProductProps {
  id: number;
  name: string;
  sku: string;
  quantity: number;
  reorderLevel: number;
}

// NO any types allowed
const fetchProduct = async (id: number): Promise<Product> => {
  // ...
};
```

---

## Forbidden Patterns

### Backend
- ❌ Never use `print()` - use `logging` module
- ❌ Never store passwords in plain text
- ❌ Never hardcode secrets - use environment variables
- ❌ Never use `SELECT *` - specify columns
- ❌ Never skip input validation

### Frontend
- ❌ Never use `any` type
- ❌ Never leave console.log in production
- ❌ Never skip error handling in async operations
- ❌ Never use inline styles - use Tailwind classes / shadcn/ui components

---

## Module-Specific Rules

### Products Module
- All products and categories must belong to a user (`user_id` foreign key)
- SKU must be unique per user
- `price`, `cost` use `Numeric(10, 2)`; never floats
- `quantity` can never be negative

### Stock Module
- Stock is stored on `Product.quantity`; low stock means `quantity <= reorder_level`

### Alerts Module
- Create one low-stock alert per threshold crossing (no duplicates while still low)
- Send email asynchronously; email failure must not fail the sale

### Sales Module
- Recording a sale must validate stock and deduct it in a single transaction
- Reject the sale if any item has insufficient stock
- Store `unit_price` and `unit_cost` on `SaleItem` at time of sale

### Admin Module
- Admin endpoints require `is_admin=True`

### File Uploads
- Validate type (jpeg/png/webp) and size (max 5 MB); never trust client filenames

---

## API Conventions

- All endpoints prefixed with `/api/v1/`
- Use plural nouns for resources: `/products`, `/sales`
- Return appropriate HTTP status codes:
  - 200: Success
  - 201: Created
  - 400: Bad Request
  - 401: Unauthorized
  - 404: Not Found
  - 409: Conflict

---

## Authentication

Email/Password only.

### JWT Configuration
- Access token expires: 30 minutes
- Refresh token expires: 7 days
- Algorithm: HS256
- Hash passwords with bcrypt

---

## Environment Variables

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/inventory_management

# Auth
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Email
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USER=your-smtp-user
SMTP_PASSWORD=your-smtp-password
EMAIL_FROM=alerts@example.com

# Uploads
UPLOAD_DIR=./uploads
MAX_UPLOAD_MB=5

# Frontend
VITE_API_URL=http://localhost:8000
```

---

## Development Commands

```bash
# Backend
cd backend
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm run dev

# Docker
docker-compose up -d

# Tests
pytest backend/tests -v
cd frontend && npm test

# Linting
ruff check backend/
cd frontend && npm run lint
```

---

## Commit Message Format

```
feat([module]): add [feature]
fix([module]): fix [bug]
refactor([module]): refactor [component]
test([module]): add tests for [feature]
docs: update [documentation]
```

---

## Skills Reference

| Task | Skill to Read |
|------|---------------|
| Database models | skills/DATABASE.md |
| API + Auth | skills/BACKEND.md |
| React + UI | skills/FRONTEND.md |
| Testing | skills/TESTING.md |
| Deployment | skills/DEPLOYMENT.md |

---

## Agent Coordination

For complex tasks, the ORCHESTRATOR coordinates:
- DATABASE-AGENT → Backend models
- BACKEND-AGENT → API development
- FRONTEND-AGENT → UI components
- TEST-AGENT → Testing
- REVIEW-AGENT → Code review
- DEVOPS-AGENT → Deployment

Read agent definitions in `/agents/` folder.
