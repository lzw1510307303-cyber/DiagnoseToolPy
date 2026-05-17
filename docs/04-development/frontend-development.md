# Frontend Development Guide

## Overview

DiagnoseToolPy uses React with Vite and TypeScript as the frontend framework. The frontend consumes backend APIs via the FastAPI backend.

## Tech Stack

- **React 18**: UI library
- **Vite 6**: Build tool and dev server
- **TypeScript 5**: Type safety
- **Ant Design 5**: Component library
- **React Router 7**: Client-side routing
- **Axios**: HTTP client

## Getting Started

### Prerequisites

- Node.js 18+ installed
- FastAPI backend running on port 18080

### Installation

```bash
cd frontend
npm install
```

### Development

Start the Vite development server:

```bash
npm run dev
```

The frontend will be available at `http://localhost:3000` (or next available port).

Vite is configured to proxy all `/api` requests to `http://localhost:18080`, so the frontend can call backend APIs without CORS issues.

### Building for Production

```bash
npm run build
```

The production build will be generated in `frontend/dist/`.

### Preview Production Build

```bash
npm run preview
```

## Running Both Frontend and Backend

1. Start the FastAPI backend:
   ```bash
   uv run uvicorn diagnose_tool.main:app --host 0.0.0.0 --port 18080 --reload
   ```

2. Start the Vite frontend (in a separate terminal):
   ```bash
   cd frontend
   npm run dev
   ```

3. Open `http://localhost:3000` in your browser

## Project Structure

```
frontend/
├── index.html           # HTML entry point
├── package.json         # Dependencies and scripts
├── vite.config.ts       # Vite configuration with API proxy
├── tsconfig.json        # TypeScript configuration
└── src/
    ├── main.tsx         # React entry point
    ├── App.tsx          # Router configuration
    ├── api/
    │   ├── client.ts    # Axios instance with interceptors
    │   ├── sourceApi.ts # Directory check/scan API calls
    │   └── caseApi.ts   # Case API calls (placeholder)
    ├── components/
    │   ├── layout/
    │   │   └── AppLayout.tsx  # Sidebar layout
    │   └── common/
    ├── pages/
    │   ├── DashboardPage.tsx
    │   ├── AnalysisTasksPage.tsx
    │   ├── TaskDetailPage.tsx
    │   ├── CasebasePage.tsx
    │   ├── CaseDetailPage.tsx
    │   └── SettingsPage.tsx
    ├── types/
    │   └── api.ts       # TypeScript types for API
    └── styles/
```

## API Proxy

During development, Vite proxies `/api` requests to the FastAPI backend:

```typescript
// vite.config.ts
export default defineConfig({
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:18080',
        changeOrigin: true,
      },
    },
  },
});
```

This means:
- Frontend calls `/api/source/check`
- Vite proxies to `http://localhost:18080/api/source/check`
- CORS issues are avoided since it's same-origin

## Available Scripts

| Script | Description |
|--------|-------------|
| `npm run dev` | Start Vite dev server with HMR |
| `npm run build` | Build for production |
| `npm run preview` | Preview production build |

## Routes

| Path | Component | Purpose |
|------|-----------|---------|
| `/` | DashboardPage | Entry point with navigation cards |
| `/analysis` | AnalysisTasksPage | Directory input and scan |
| `/analysis/:taskId` | TaskDetailPage | Analysis results (placeholder) |
| `/cases` | CasebasePage | Case list (placeholder) |
| `/cases/:caseId` | CaseDetailPage | Case detail (placeholder) |
| `/settings` | SettingsPage | Configuration display |

## Production Deployment

### Option A: Nginx serves React dist and proxies /api

```nginx
server {
    listen 80;
    root /var/www/diagnosetoolpy/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api/ {
        proxy_pass http://localhost:18080/api/;
    }
}
```

### Option B: FastAPI serves React dist as static files

Add static file serving to FastAPI (future enhancement).

## Troubleshooting

### Port already in use

If port 3000 is in use, Vite will automatically use the next available port. Check the terminal output for the actual URL.

### API calls fail with "Network Error"

1. Verify the FastAPI backend is running on port 18080
2. Check that no CORS issues exist (should be handled by proxy)
3. Check browser console for detailed error messages

### Build fails

1. Ensure Node.js 18+ is installed
2. Run `npm install` again to ensure dependencies are installed
3. Check for TypeScript errors: `npx tsc --noEmit`
