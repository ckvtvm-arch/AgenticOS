# AgenticOS

Design and architect a next‑generation operating system specifically optimized for Agentic AI systems. This OS treats AI agents as first‑class citizens, enabling seamless multi‑agent orchestration, secure resource management, and native AI‑to‑system integration. The OS rethinks computing paradigms for an AI‑native world.

## Repository layout

- `agentic-ai-os-dashboard/` — Vite + React dashboard for local development and demos
- More components will be added here as the OS architecture takes shape

## Quick start: Dashboard

Prerequisites:
- Node.js 18+ (LTS recommended)
- npm 10+

Steps:
1) Change into the dashboard:
   - `cd agentic-ai-os-dashboard`
2) Install dependencies:
   - `npm ci` (preferred) or `npm install`
3) Configure environment:
   - Create a file named `.env.local` in the same directory and set:
     - `GEMINI_API_KEY=your_key_here`
4) Run the dev server:
   - `npm run dev`

The app will print a local URL to open in your browser.

## Common issues

- EBADPLATFORM (inotify) on macOS:
  - Symptom: `Unsupported platform for inotify@...: wanted {"os":"linux"} (current: {"os":"darwin"})`
  - Cause: Installing a Linux‑only package (e.g., `inotify`) on macOS or running `npm install` in the wrong directory.
  - Fix:
    - Ensure you are inside `agentic-ai-os-dashboard/` before running `npm install`.
    - If the error persists, remove `node_modules` and `package-lock.json`, then reinstall: `rm -rf node_modules package-lock.json && npm ci`.
    - This project does not require `inotify` on macOS; Vite uses cross‑platform file watching.

- No package.json at repository root:
  - Run `npm install` only inside `agentic-ai-os-dashboard/`.

## Contributing

- Open issues or PRs as the architecture and modules are introduced.
- Please avoid committing secrets; use `.env.local` for local configuration.

## License

This project is licensed under the terms in `LICENSE`.
