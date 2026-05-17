## Why

DiagnoseToolPy currently has a minimal HTML fallback page for its Web UI. As the application grows in functionality, a proper frontend framework is needed to improve UI maintainability, developer experience, and visual quality. Adding a React-based frontend shell establishes the foundation for future UI development without implementing full business features.

## What Changes

- Add `frontend/` directory with React + Vite + TypeScript scaffold
- Configure Vite dev server to proxy `/api` requests to FastAPI backend
- Add base application layout with sidebar navigation using Ant Design
- Add route structure for Dashboard, Analysis Tasks, Task Detail, Casebase, Case Detail, and Settings pages
- Add reusable API client wrapper for calling backend APIs
- Add shared TypeScript types for backend API responses
- Add page shells with placeholder states for not-yet-implemented features
- Add directory scan UI integration calling existing `/api/source/check` and `/api/source/scan` endpoints
- Add frontend development documentation
- Update docs to reflect React + Vite + TypeScript as the preferred frontend stack

## Capabilities

### New Capabilities

- `react-frontend-shell`: React-based frontend shell providing UI foundation with routing, API client, and page layouts

### Modified Capabilities

- (none - backend APIs remain unchanged)

## Impact

- New frontend directory: `frontend/` with React application
- Backend: No changes required (existing APIs work as-is)
- New dependencies: React, Vite, TypeScript, Ant Design, React Router, Axios
- Development workflow: `npm run dev` starts Vite with API proxy to FastAPI
- Production deployment: React dist can be served by Nginx or FastAPI static file serving
