# AI Agent Instructions — DDoS Protection Platform

> This file is read automatically by AI coding agents (OpenAI Codex, Claude, GPT-4o, etc.)
> that support `AGENTS.md` at the repository root.

**You MUST read and follow [`project-docs/AI_INSTRUCTIONS.md`](project-docs/AI_INSTRUCTIONS.md)
before making any change to this repository.**

## Mandatory Reading Order

1. [`project-docs/AI_INSTRUCTIONS.md`](project-docs/AI_INSTRUCTIONS.md) — rules, constraints, style
2. [`project-docs/OVERVIEW.md`](project-docs/OVERVIEW.md) — architecture & tech stack
3. [`project-docs/REPORT.md`](project-docs/REPORT.md) — current implementation status & known issues
4. [`project-docs/TODO.md`](project-docs/TODO.md) — open tasks (check before starting work)
5. [`project-docs/ROADMAP.md`](project-docs/ROADMAP.md) — planned features & architecture direction

## Quick Rules

- All new documentation goes in `project-docs/` — never create `.md` files at the repo root.
- Run `cd backend && pytest -v` before and after any backend change.
- Never use `shell=True` in subprocess calls; validate IPs with the `ipaddress` module.
- Every API endpoint must require JWT auth except `/api/v1/auth/token` and `/register`.
- Every DB query for ISP-specific data must filter by `isp_id`.
- Update `project-docs/CHANGELOG.md` and `project-docs/TODO.md` with every change.

## Documentation Index

All documentation: [`project-docs/INDEX.md`](project-docs/INDEX.md)
