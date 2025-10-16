# Gestão Legal - Architecture Documentation

**Last Updated**: 2025-10-15
**Architecture**: Monorepo with SPA Frontend + Flask API Backend

---

## 🏗️ Project Overview

Gestão Legal is a legal case management system for UFMG's Law Faculty. It's a full-stack application with a SPA frontend, REST API backend, and containerized deployment.

### Quick Stats
- **Type**: Legal case management SaaS
- **Architecture**: SPA + REST API
- **Deployment**: Docker + nginx
- **Team**: UFMG Law Faculty extension project

---

## 📁 Repository Structure

```
/home/andre/Projetos/gestaolegal/gestaolegal/
├── frontend/                    # SvelteKit SPA (Port 5001)
│   ├── src/
│   │   ├── routes/             # SvelteKit pages (SPA mode)
│   │   ├── lib/
│   │   │   ├── api-client.ts   # HTTP client with auth
│   │   │   ├── components/     # Reusable UI components
│   │   │   ├── forms/          # Form schemas (Zod)
│   │   │   └── types/          # TypeScript types
│   │   └── hooks.server.ts     # Build-time only hooks
│   ├── build/                  # Production static files
│   ├── nginx.conf              # nginx SPA configuration
│   ├── Dockerfile              # Multi-stage: Node build + nginx serve
│   ├── package.json
│   └── svelte.config.js        # adapter-static config
│
├── gestaolegal/                # Flask Backend (Port 5000)
│   ├── controllers/            # API route handlers
│   ├── services/               # Business logic
│   ├── repositories/           # Data access layer
│   ├── models/                 # Pydantic models
│   ├── database/               # SQLAlchemy tables
│   ├── utils/                  # Utilities (JWT, decorators)
│   ├── static/                 # File uploads
│   └── __init__.py             # App factory
│
├── migrations/                 # Alembic database migrations
├── tests/                      # Backend tests (pytest)
├── docker-compose.yml          # Local development setup
├── Dockerfile                  # Backend container
├── pyproject.toml              # Python dependencies (UV)
├── Makefile                    # Dev shortcuts
├── ARCHITECTURE.md             # This file
└── SPA_MIGRATION_SUMMARY.md    # Migration notes

External (separate repos):
└── ../devops/                  # Ansible deployment configs
```

---

## 🎯 Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        User Browser                          │
└────────────────┬────────────────────────────────────────────┘
                 │
                 │ HTTPS
                 ↓
┌─────────────────────────────────────────────────────────────┐
│              nginx (Port 80/443)                             │
│  • Serves static SPA files                                   │
│  • Routes /api/* to backend                                  │
│  • Caches static assets                                      │
└────────────┬───────────────────────┬────────────────────────┘
             │                       │
             │ Static Files          │ API Proxy
             ↓                       ↓
┌────────────────────┐    ┌─────────────────────────────────┐
│  SvelteKit SPA     │    │    Flask Backend (Port 5000)    │
│  (Static Files)    │    │  • REST API endpoints           │
│  • index.html      │    │  • JWT authentication           │
│  • JS bundles      │    │  • Business logic               │
│  • CSS/assets      │    │  • File handling                │
└────────────────────┘    └──────────┬──────────────────────┘
                                     │
                                     │ SQLAlchemy
                                     ↓
                          ┌─────────────────────────┐
                          │   MySQL 8.0.42          │
                          │   (Port 3306)           │
                          └─────────────────────────┘
```

---

## 🔧 Technology Stack

### Frontend (SPA)
| Layer | Technology | Version | Purpose |
|-------|-----------|---------|---------|
| **Framework** | SvelteKit | 2.22+ | SPA framework |
| **Language** | TypeScript | 5+ | Type safety |
| **Build Tool** | Vite | 7+ | Fast builds |
| **UI Library** | shadcn-svelte | Latest | Component library |
| **Styling** | Tailwind CSS | 4+ | Utility-first CSS |
| **Forms** | Superforms + Zod | Latest | Form handling & validation |
| **HTTP Client** | Custom api-client | - | Fetch wrapper with auth |
| **Web Server** | nginx | alpine | Static file serving |
| **Adapter** | adapter-static | Latest | SPA build output |

### Backend (API)
| Layer | Technology | Version | Purpose |
|-------|-----------|---------|---------|
| **Framework** | Flask | 3.1+ | Web framework |
| **Language** | Python | 3.11+ | Backend logic |
| **ORM** | SQLAlchemy | 2.0+ | Database abstraction |
| **Migrations** | Alembic | 1.13+ | Schema versioning |
| **Validation** | Pydantic | Latest | Data validation |
| **Auth** | PyJWT | Latest | JWT tokens |
| **Password** | bcrypt | Latest | Secure hashing |
| **WSGI** | Gunicorn | 20+ | Production server |
| **Database** | MySQL | 8.0.42 | Data persistence |
| **Package Manager** | UV | Latest | Fast dependency resolver |

### Infrastructure
| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Containers** | Docker | Application isolation |
| **Orchestration** | Docker Compose | Local development |
| **Deployment** | Ansible | Production automation |
| **Reverse Proxy** | nginx | Request routing |
| **CI/CD** | GitHub Actions | Automated builds |

---

## 🔐 Authentication Flow

### 1. Login (Client-Side)
```typescript
// frontend/src/routes/login/+page.svelte
async function handleLogin(email, password) {
  const response = await api.post('auth/login', { email, password });
  // Backend sets httpOnly cookie with JWT
  if (response.ok) {
    goto('/'); // Redirect to dashboard
  }
}
```

### 2. Protected Routes
```typescript
// frontend/src/routes/+layout.svelte
onMount(() => {
  const hasAuthToken = document.cookie.includes('auth_token');
  if (!hasAuthToken && !isPublicRoute) {
    goto('/login');
  }
});
```

### 3. API Calls with Auth
```typescript
// frontend/src/lib/api-client.ts
export async function apiFetch(endpoint: string) {
  const token = getCookieValue('auth_token');
  return fetch(`/api/${endpoint}`, {
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    credentials: 'include'
  });
}
```

### 4. Backend Verification
```python
# gestaolegal/utils/api_decorators.py
@authenticated
@authorized('admin', 'colab_proj')
def protected_endpoint():
    current_user = get_user_from_context()
    # ... endpoint logic
```

---

## 📡 API Structure

### Base URL
- **Development**: `http://localhost:5000/api`
- **Production**: `https://domain.com/api` (via nginx proxy)

### Authentication
- **Type**: JWT (JSON Web Token)
- **Storage**: httpOnly cookie (`auth_token`)
- **Expiry**: 12 hours
- **Header**: `Authorization: Bearer <token>`

### User Roles
1. `admin` - System administrator
2. `colab_proj` - Project collaborator
3. `orient` - Legal supervisor
4. `estag_direito` - Law intern
5. `colab_ext` - External collaborator

### Main Endpoints

#### Auth
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout

#### Users
- `GET /api/users` - List users (paginated)
- `POST /api/users` - Create user
- `GET /api/users/:id` - Get user details
- `PUT /api/users/:id` - Update user
- `DELETE /api/users/:id` - Delete user (soft delete)

#### Cases (Casos)
- `GET /api/casos` - List cases (paginated, filtered)
- `POST /api/casos` - Create case
- `GET /api/casos/:id` - Get case details
- `PUT /api/casos/:id` - Update case
- `DELETE /api/casos/:id` - Delete case

#### Service Recipients (Atendidos)
- `GET /api/atendidos` - List recipients
- `POST /api/atendidos` - Create recipient
- `GET /api/atendidos/:id` - Get recipient
- `PUT /api/atendidos/:id` - Update recipient

#### Events (Eventos)
- `GET /api/casos/:casoId/eventos` - List case events
- `POST /api/casos/:casoId/eventos` - Create event
- `PUT /api/eventos/:id` - Update event

#### Legal Guidance (Orientações Jurídicas)
- `GET /api/orientacoes` - List orientations
- `POST /api/orientacoes` - Create orientation
- `GET /api/orientacoes/:id` - Get orientation
- `PUT /api/orientacoes/:id` - Update orientation

#### Search
- `GET /api/search?q=query` - Global search across entities

---

## 🗄️ Database Schema

### Core Tables

**usuarios** (Users)
- User authentication and profile
- Fields: email, password_hash, name, role, cpf, oab, etc.
- Soft delete support

**atendidos** (Service Recipients)
- People seeking legal assistance
- Demographics: name, cpf, rg, birth_date, phone, etc.
- Socioeconomic data: income, education, family_size

**assistidos** (Represented Parties)
- People being represented in cases
- Relationship to atendidos (can be the same person)
- Additional legal representation details

**casos** (Legal Cases)
- Main case tracking entity
- Status, area of law, dates, assignments
- Many-to-many with users (multiple assignees)
- Many-to-many with assistidos (multiple parties)

**processos** (Legal Proceedings)
- Court proceedings linked to cases
- Process number, court info, parties

**eventos** (Case Events/Timeline)
- Timeline of activities on cases
- Event type, description, date, attachments

**orientacao_juridica** (Legal Guidance)
- Legal consultations/orientations
- Linked to atendidos
- Status tracking (pending, completed, etc.)

**arquivos_caso** (Case Files)
- File attachments for cases
- Stored in filesystem, metadata in DB

**enderecos** (Addresses)
- Polymorphic addresses for users, atendidos, etc.

### Relationships
```
usuarios ←→ casos (many-to-many via user_caso)
casos ←→ assistidos (many-to-many via caso_assistido)
atendidos → assistidos (one-to-many, can become assistido)
casos → eventos (one-to-many)
casos → processos (one-to-many)
casos → arquivos_caso (one-to-many)
atendidos → orientacao_juridica (one-to-many)
```

---

## 🚀 Development Workflow

### Initial Setup

```bash
# Clone repository
cd /home/andre/Projetos/gestaolegal/gestaolegal

# Backend setup
cp .env.example .env
# Edit .env with your configuration

# Frontend setup
cd frontend
npm install

# Start services
cd ..
docker-compose up
```

### Daily Development

```bash
# Start backend only
docker-compose up app_gl db_gl

# In another terminal, run frontend dev server
cd frontend
npm run dev
# Access at http://localhost:5173
```

### Backend Changes

```bash
# Create migration
alembic revision --autogenerate -m "description"

# Review and edit migration file
# migrations/versions/<hash>_description.py

# Apply migration
alembic upgrade head

# Run tests
make test
# or
pytest tests/

# Check code
ruff check .
```

### Frontend Changes

```bash
cd frontend

# Type checking
npm run check

# Format code
npm run format

# Build for production
npm run build

# Preview production build
npm run preview
```

### Adding New Features

#### Backend API Endpoint

1. **Define Model** (`gestaolegal/models/your_entity.py`)
```python
from dataclasses import dataclass

@dataclass
class YourEntity:
    id: int
    name: str
    # ... fields
```

2. **Create Database Table** (`gestaolegal/database/tables.py`)
```python
your_entity_table = Table(
    'your_entity',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String(255)),
    # ... columns
)
```

3. **Create Repository** (`gestaolegal/repositories/your_entity_repository.py`)
```python
class YourEntityRepository(Repository):
    def __init__(self, session):
        super().__init__(session, your_entity_table)
```

4. **Create Service** (`gestaolegal/services/your_entity_service.py`)
```python
class YourEntityService:
    def __init__(self, repository):
        self.repository = repository

    def create(self, data):
        # Business logic
        return self.repository.insert(data)
```

5. **Create Controller** (`gestaolegal/controllers/your_entity_controller.py`)
```python
@authenticated
@authorized('admin')
def create_entity():
    data = request.get_json()
    service = YourEntityService(repo)
    result = service.create(data)
    return jsonify(result), 201
```

6. **Register Blueprint** (`gestaolegal/controllers/__init__.py`)
```python
from .your_entity_controller import your_entity_bp
app.register_blueprint(your_entity_bp)
```

#### Frontend Page

1. **Create Zod Schema** (`frontend/src/lib/forms/schemas/your-entity-schema.ts`)
```typescript
import { z } from 'zod';

export const yourEntitySchema = z.object({
  name: z.string().min(1, 'Name required'),
  // ... fields
});

export type YourEntityData = z.infer<typeof yourEntitySchema>;
```

2. **Create Type** (`frontend/src/lib/types/your-entity.ts`)
```typescript
export interface YourEntity {
  id: number;
  name: string;
  // ... fields
}
```

3. **Create Page** (`frontend/src/routes/(dashboard)/your-entities/+page.svelte`)
```svelte
<script lang="ts">
  import { onMount } from 'svelte';
  import { api } from '$lib/api-client';
  import type { YourEntity } from '$lib/types/your-entity';

  let entities = $state<YourEntity[]>([]);
  let loading = $state(true);

  onMount(async () => {
    const response = await api.get('your-entities');
    entities = await response.json();
    loading = false;
  });
</script>

{#if loading}
  <p>Loading...</p>
{:else}
  <ul>
    {#each entities as entity}
      <li>{entity.name}</li>
    {/each}
  </ul>
{/if}
```

4. **Add to Navigation** (`frontend/src/lib/components/app-sidebar.svelte`)

---

## 🐳 Docker & Deployment

### Local Development (docker-compose.yml)

```yaml
services:
  front_gl:         # SvelteKit SPA
    build: ./frontend
    ports: ["5001:80"]
    depends_on: [app_gl]

  app_gl:           # Flask API
    build: .
    ports: ["5000:5000"]
    depends_on: [db_gl]

  db_gl:            # MySQL
    image: mysql:8.0.42
    ports: ["3306:3306"]
    volumes: [mysql_data]

  adminer_gl:       # DB Admin UI
    image: adminer
    ports: ["8080:8080"]
```

### Production Deployment

**Process**:
1. Build Docker images with version tags
2. Push to registry (or build on server)
3. Ansible playbook deploys to servers
4. nginx reverse proxy handles SSL/routing

**Commands**:
```bash
# Build images
docker build -t gestaolegal-api:v1.0.0 .
docker build -t gestaolegal-front:v1.0.0 ./frontend

# Deploy with Ansible (from devops repo)
cd ../devops
ansible-playbook -i inventories/production \
  playbooks/deploy-tenant.yml \
  -e tenant_name=daj \
  -e backend_version=v1.0.0 \
  -e frontend_version=v1.0.0
```

---

## 🧪 Testing

### Backend Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=gestaolegal --cov-report=html

# Run specific test file
pytest tests/api/test_user_api.py

# Run specific test
pytest tests/api/test_user_api.py::test_create_user
```

**Test Structure**:
```
tests/
├── api/                    # API endpoint tests
│   ├── conftest.py        # Fixtures
│   ├── test_auth_api.py
│   ├── test_user_api.py
│   └── test_caso_api.py
└── services/              # Business logic tests
```

### Frontend Testing

Currently manual testing. Can add:
- Vitest for unit tests
- Playwright for E2E tests

---

## 🔄 Database Migrations

### Creating Migrations

```bash
# Auto-generate migration from model changes
alembic revision --autogenerate -m "add user role field"

# Create empty migration (for data migrations)
alembic revision -m "populate default roles"
```

### Reviewing Migrations

**ALWAYS** review auto-generated migrations:
```python
# migrations/versions/xxx_add_user_role.py
def upgrade():
    op.add_column('usuarios', sa.Column('role', sa.String(50)))
    # Review: Is this correct? Any data migration needed?

def downgrade():
    op.drop_column('usuarios', 'role')
    # Review: Can this be safely rolled back?
```

### Applying Migrations

```bash
# Check current version
alembic current

# View migration history
alembic history

# Upgrade to latest
alembic upgrade head

# Upgrade one version
alembic upgrade +1

# Rollback one version
alembic downgrade -1

# Rollback to specific version
alembic downgrade <revision_id>
```

---

## 📝 Code Style & Conventions

### Backend (Python)

```python
# Use type hints
def create_user(name: str, email: str) -> User:
    ...

# Use dataclasses for models
@dataclass
class User:
    id: int
    name: str

# Repository methods
def insert(self, data: dict) -> dict:
def get_by_id(self, id: int) -> dict | None:
def update(self, id: int, data: dict) -> dict:
def delete(self, id: int) -> bool:

# Service methods
def create_entity(self, data: dict) -> Entity:
def get_entity(self, id: int) -> Entity:
def update_entity(self, id: int, data: dict) -> Entity:
def delete_entity(self, id: int) -> bool:
```

### Frontend (TypeScript)

```typescript
// Use TypeScript strictly
interface User {
  id: number;
  name: string;
}

// Component naming: PascalCase
// MyComponent.svelte

// Functions: camelCase
function fetchUsers() { }

// Types/Interfaces: PascalCase
type UserData = { ... }

// Constants: UPPER_SNAKE_CASE
const API_BASE_URL = '/api';
```

---

## 🛠️ Troubleshooting

### Common Issues

**Backend won't start**
```bash
# Check database connection
docker-compose logs db_gl

# Check backend logs
docker-compose logs app_gl

# Verify .env file exists and has all required variables
cat .env

# Check migrations
alembic current
alembic upgrade head
```

**Frontend build fails**
```bash
# Clear cache and reinstall
rm -rf node_modules .svelte-kit
npm install

# Check for TypeScript errors
npm run check

# Try building
npm run build
```

**Can't login**
```bash
# Check backend is running
curl http://localhost:5000/api/health

# Check cookies in browser DevTools
# Should see auth_token cookie after login

# Check backend logs for errors
docker-compose logs app_gl
```

**API calls return 401**
```bash
# Check if auth_token cookie exists
# Check if JWT token is expired (12h expiry)
# Check nginx proxy configuration
# Verify Authorization header is being sent
```

---

## 📚 Additional Resources

### Documentation
- [Flask Docs](https://flask.palletsprojects.com/)
- [SvelteKit Docs](https://kit.svelte.dev/)
- [SQLAlchemy Docs](https://docs.sqlalchemy.org/)
- [Tailwind CSS](https://tailwindcss.com/)
- [Zod Validation](https://zod.dev/)

### Tools
- [Alembic Migrations](https://alembic.sqlalchemy.org/)
- [Pytest Testing](https://docs.pytest.org/)
- [Docker Docs](https://docs.docker.com/)
- [nginx Docs](https://nginx.org/en/docs/)

---

## 🤝 Contributing

### Before Committing
```bash
# Backend
pytest                  # Run tests
ruff check .           # Lint code

# Frontend
npm run check          # Type check
npm run format         # Format code
npm run build          # Ensure builds
```

### Commit Message Format
```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types**: feat, fix, docs, style, refactor, test, chore

**Examples**:
```
feat(api): add user profile endpoint
fix(auth): resolve JWT expiry issue
docs(architecture): update deployment section
```

---

## 🎯 Roadmap & Future Improvements

### Immediate
- [ ] Convert remaining +page.server.ts files to SPA
- [ ] Add E2E tests with Playwright
- [ ] Improve error handling in frontend
- [ ] Add loading states to all forms

### Short-term
- [ ] Add unit tests for services
- [ ] Implement frontend testing (Vitest)
- [ ] Add file upload progress indicators
- [ ] Improve search functionality
- [ ] Add data export features

### Long-term
- [ ] Mobile app (React Native or Flutter)
- [ ] Real-time notifications (WebSockets)
- [ ] Document generation (PDFs)
- [ ] Advanced analytics dashboard
- [ ] Multi-language support

---

## 📞 Support & Contact

- **Organization**: UFMG Law Faculty
- **Project**: Judicial Assistance Division (DAJ)
- **Type**: Open-source legal case management

---

**Last Updated**: 2025-10-15
**Version**: 2.0 (Post-SPA Migration)
**Maintainers**: UFMG Team
