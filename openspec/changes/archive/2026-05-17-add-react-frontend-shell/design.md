## Context

DiagnoseToolPy currently has a minimal HTML fallback page (`index()` in `main.py`) serving as the Web UI. The backend is FastAPI with existing API routes (`/api/source/*`, `/api/cases/*`). The project needs a proper frontend framework to improve UI maintainability and developer experience as the application grows.

## Goals / Non-Goals

**Goals:**
- Establish React + Vite + TypeScript as the frontend foundation
- Configure Vite dev server to proxy `/api` to FastAPI backend
- Provide clean management-console style UI using Ant Design
- Create page shells with placeholder states for future features
- Integrate with existing backend APIs (directory check/scan)
- Document frontend development workflow

**Non-Goals:**
- Implement complete log analysis UI
- Implement complete case editor UI
- Implement AI diagnosis UI
- Implement authentication
- Replace backend Jinja2/fallback pages (they remain for simple access)
- Modify backend analyzer/casebase/retrieval logic
- Introduce mandatory database

## Decisions

### React + Vite + TypeScript

**Decision**: Use React with Vite as the build tool and TypeScript for type safety.

**Rationale**: Vite provides fast HMR and simple configuration. TypeScript catches type errors early. React has a large ecosystem and good compatibility with Ant Design.

**Alternatives**:
- Next.js: More opinionated, SSR not needed for this SPA
- Svelte: Smaller ecosystem, less Ant Design support

### Ant Design

**Decision**: Use Ant Design component library for UI components.

**Rationale**: Provides professional management-console style components out of the box. Good documentation and TypeScript support.

**Alternatives**:
- Material UI: Different visual style
- Tailwind + custom components: More work for management-console look

### Vite Proxy Configuration

**Decision**: Configure Vite dev server to proxy `/api` to `http://localhost:18080`.

**Rationale**: Backend runs on port 18080 during development. Proxy avoids CORS issues and allows frontend to call `/api/*` as if same origin.

### API Client Structure

**Decision**: Create typed Axios-based API client in `frontend/src/api/client.ts`.

**Rationale**: Centralizes error handling, request/response typing, and base URL configuration. Axios provides good interceptor support.

**Structure**:
```
frontend/src/api/
├── client.ts      # Axios instance with interceptors
├── sourceApi.ts   # Directory check/scan calls
└── caseApi.ts    # Case CRUD calls (placeholder)
```

### Route Structure

**Decision**: Use React Router with the following routes:

| Path | Component | Purpose |
|------|-----------|---------|
| `/` | DashboardPage | Entry point with navigation cards |
| `/analysis` | AnalysisTasksPage | Directory input and scan |
| `/analysis/:taskId` | TaskDetailPage | Analysis results (placeholder) |
| `/cases` | CasebasePage | Case list (placeholder) |
| `/cases/:caseId` | CaseDetailPage | Case detail (placeholder) |
| `/settings` | SettingsPage | Configuration display |

### Production Deployment Options

**Option A: Nginx serves React dist and proxies /api**
```
Nginx:80 -> serves / (React dist)
Nginx:80 -> proxies /api/* -> FastAPI:18080
```

**Option B: FastAPI serves React dist as static files**
```
FastAPI:18080 -> / -> serves React dist
FastAPI:18080 -> /api/* -> API routes
```

**Decision**: Document both options. Option B is simpler for single-container deployment (already in docker-compose).

### Coexistence with Backend Fallback Pages

**Decision**: Backend's `index()` route and fallback pages remain as simple access points.

**Rationale**: They serve as backup when frontend is unavailable. The frontend replaces them for normal use.

### Shared TypeScript Types

**Decision**: Define types in `frontend/src/types/api.ts` matching backend Pydantic models.

**Rationale**: Provides compile-time safety for API calls. Types mirror backend models for SourcePathRequest, scan results, etc.

## Risks / Trade-offs

[Risk] CORS issues in development → [Mitigation] Vite proxy handles /api requests

[Risk] Backend API changes break frontend types → [Mitigation] Keep types minimal, update as needed

[Risk] Frontend build adds deployment complexity → [Mitigation] Document both deployment options clearly

## Migration Plan

1. Create `frontend/` directory with Vite + React + TypeScript
2. Configure proxy in `vite.config.ts`
3. Add Ant Design and React Router dependencies
4. Create AppLayout with sidebar navigation
5. Create page components with placeholder content
6. Integrate with existing `/api/source/check` and `/api/source/scan` endpoints
7. Add frontend development documentation
8. Verify existing backend tests still pass
9. Deploy: either add React dist to existing Docker image or serve via Nginx

## Open Questions

- Should frontend use a state management library? (Defer until actual state complexity warrants it)
- Should we add React Query / SWR for server state? (Defer, Axios + React state is sufficient for shell)
- Should we add frontend unit tests? (Minimal for shell phase, add when business logic added)
