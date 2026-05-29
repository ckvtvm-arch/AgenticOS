# Contributing to AgenticOS

Thank you for your interest in AgenticOS! This document provides guidelines for contributing, from setting up a development environment to submitting a pull request.

---

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Environment](#development-environment)
- [Project Structure](#project-structure)
- [Coding Standards](#coding-standards)
- [Pull Request Process](#pull-request-process)
- [Where to Start](#where-to-start)

---

## Code of Conduct

This project is committed to providing a welcoming and inclusive experience. Be respectful, constructive, and collaborative. Harassment or discriminatory behavior will not be tolerated.

---

## Getting Started

1. **Fork the repository** on GitHub.
2. **Clone your fork:**
   ```bash
   git clone https://github.com/<your-username>/AgenticOS.git
   cd AgenticOS
   ```
3. **Set up the dashboard** (see [Quick Start](./README.md#quick-start--dashboard-local-dev)).
4. **Read the docs:**
   - [`ARCHITECTURE.md`](./ARCHITECTURE.md) — system design overview
   - [`ROADMAP.md`](./ROADMAP.md) — current priorities and milestones

---

## Development Environment

### Dashboard (React + Vite)

```bash
cd agentic-ai-os-dashboard
npm ci
cp .env.example .env.local   # add your API keys
npm run dev                   # starts on http://localhost:3000
```

### Backend (Python + FastAPI) — TBD

```bash
# Once Phase 1 backend scaffold is created:
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Linting & Formatting

| Language | Tool | Command |
|----------|------|---------|
| TypeScript / React | ESLint + Prettier | `npm run lint` (dashboard) |
| Python | Ruff | `ruff check .` (backend) |

---

## Project Structure

```
AgenticOS/
├── agentic-ai-os-dashboard/   # React + Vite frontend
│   ├── App.tsx                # Main app component
│   ├── types.ts               # Shared type definitions
│   ├── components/            # UI components
│   │   ├── AgentList.tsx
│   │   ├── ArchitectureView.tsx
│   │   ├── Card.tsx
│   │   ├── Header.tsx
│   │   ├── ResourceMonitor.tsx
│   │   ├── SystemStatus.tsx
│   │   └── icons/             # SVG icon components
│   └── vite.config.ts
├── backend/                   # Python FastAPI server (planned)
├── adk/                       # Agent Development Kit (planned)
├── ARCHITECTURE.md
├── ROADMAP.md
├── CONTRIBUTING.md
└── README.md
```

---

## Coding Standards

### General

- **Use meaningful names** — variables, functions, and classes should be self-documenting.
- **Keep functions small** — aim for single responsibility, < 30 lines where practical.
- **Write tests** — new features should include tests; bug fixes should include a regression test.
- **Document public APIs** — use JSDoc (TypeScript) or docstrings (Python).

### TypeScript / React

- Use TypeScript `strict` mode. Avoid `any` — prefer `unknown` if type is uncertain.
- Components: prefer functional components with hooks; avoid class components.
- Styles: use Tailwind utility classes; avoid CSS modules or styled-components unless necessary.
- Exports: use named exports for components, default exports for pages.

### Python (for future backend)

- Follow [PEP 8](https://peps.python.org/pep-0008/) with a 100-character line limit.
- Use type hints for all function signatures.
- Use `async`/`await` for I/O-bound operations (FastAPI pattern).
- Use Pydantic for data validation and serialization.

### Git Commits

- Use [Conventional Commits](https://www.conventionalcommits.org/):
  - `feat:` — new feature
  - `fix:` — bug fix
  - `docs:` — documentation only
  - `refactor:` — code change that neither fixes a bug nor adds a feature
  - `chore:` — maintenance, dependencies, CI
- Example: `feat: add agent lifecycle API endpoints`
- Keep commits small and focused.

---

## Pull Request Process

1. **Create an issue** describing the change, or comment on an existing issue to claim it.
2. **Create a branch** from `main`:
   ```bash
   git checkout -b feat/my-feature
   ```
3. **Make your changes.** Write tests and update docs as needed.
4. **Run linting and tests:**
   ```bash
   cd agentic-ai-os-dashboard
   npm run lint
   npm run test       # if available
   ```
5. **Commit** with a conventional commit message.
6. **Push** and open a pull request against `main`.
7. **Fill in the PR template** — include what changed, why, and how to test.
8. **Request a review** from a maintainer.
9. **Address feedback** — make additional commits or amend as requested.
10. **Merge** once approved and CI passes.

### PR Checklist

- [ ] Code follows coding standards
- [ ] Tests pass (or no tests exist for this area yet)
- [ ] Documentation updated (if applicable)
- [ ] No new warnings or console errors
- [ ] Manual testing done (if applicable)

---

## Where to Start

Not sure what to work on? Here are good entry points:

| Skill | Suggested Area | Phase |
|-------|---------------|-------|
| TypeScript / React | Dashboard components, integration with backend API | 1 |
| Python / FastAPI | Backend server, WebSocket, database models | 1 |
| Python / async | Agent runtime, process management, scheduler | 2 |
| Python / SDK design | Agent Development Kit (ADK) | 3 |
| ONNX / ML | Inference engine, model serving | 4 |
| Security / containers | Sandboxing, capability model | 5 |
| Docs / examples | Documentation, tutorials, example agents | Any |

Check the [`ROADMAP.md`](./ROADMAP.md) for current milestones and open issues for available tasks.

---

## Questions?

Open a [GitHub Discussion](https://github.com/ckvtvm-arch/AgenticOS/discussions) or comment on a relevant issue.

Happy building! 🚀