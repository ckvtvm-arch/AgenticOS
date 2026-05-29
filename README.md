## AgenticOS

AgenticOS is an experimental project that explores operating‑system primitives and tooling optimized for multi‑agent AI systems. It treats AI agents as first‑class citizens, focusing on secure resource management, coordinated orchestration, and native AI-to-system integration.

This repository currently provides a developer dashboard and initial UI components for local development and demos. The project is evolving; expect additional services, CLI tools, and architecture modules to be added over time.

## Documentation

| Document | Description |
|----------|-------------|
| [`ARCHITECTURE.md`](./ARCHITECTURE.md) | System architecture, layers, components, data flow, and tech choices |
| [`ROADMAP.md`](./ROADMAP.md) | Phased development milestones with acceptance criteria |
| [`CONTRIBUTING.md`](./CONTRIBUTING.md) | Developer setup guide, coding standards, and PR workflow |

## Quick project layout

- `agentic-ai-os-dashboard/` — Vite + React dashboard used for local development and demos

## Quick start — dashboard (local dev)

Prerequisites
- Node.js 18+ (LTS recommended)
- npm 10+ (or compatible package manager)

Steps
1. Change into the dashboard directory:
   - `cd agentic-ai-os-dashboard`
2. Install dependencies:
   - `npm ci` (preferred for CI reproducibility) or `npm install`
3. Configure local environment (optional):
   - Create `.env.local` and add any keys the dashboard expects (example):
     - `GEMINI_API_KEY=your_key_here`
4. Start the dev server:
   - `npm run dev`

The dev server will print a local URL. Default Vite port is 5173, but this project is configured for http://localhost:3000 (see `agentic-ai-os-dashboard/vite.config.ts`).

Building for production
- From `agentic-ai-os-dashboard/` run `npm run build`. The production output is placed in `dist/`.

## Troubleshooting

- EBADPLATFORM / inotify on macOS
  - Symptom: Unsupported platform errors mentioning `inotify`.
  - Cause: A Linux‑only dependency was installed or `npm install` was run in the wrong folder.
  - Fix:
    1. Make sure you run `npm ci` or `npm install` from inside `agentic-ai-os-dashboard/`.
    2. If problems persist: `rm -rf node_modules package-lock.json && npm ci`.

- Missing `package.json` at the repository root
  - Only run Node/npm commands inside `agentic-ai-os-dashboard/` — the repository root doesn't contain a JS project.

## Contributing

See [`CONTRIBUTING.md`](./CONTRIBUTING.md) for detailed guidance on:
- Setting up a development environment
- Coding standards (TypeScript, Python)
- Pull request workflow and checklist
- Finding the right area to contribute based on your skills

## Roadmap

See [`ROADMAP.md`](./ROADMAP.md) for the full phased development plan.

**Near-term priorities (Phase 1):**
- FastAPI backend server with REST + WebSocket endpoints
- Wire dashboard to live backend data (replace mock state)
- Docker Compose for local development

## License

This project is licensed under the terms in `LICENSE`.
