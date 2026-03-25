# Claude AI Instructions — DDoS Protection Platform

> This file is read automatically by Claude (Anthropic) when working in this repository.

**You MUST read and follow [`project-docs/AI_INSTRUCTIONS.md`](project-docs/AI_INSTRUCTIONS.md)
before making any change to this repository.**

## Mandatory Reading Order

1. [`project-docs/AI_INSTRUCTIONS.md`](project-docs/AI_INSTRUCTIONS.md) — **start here**
2. [`project-docs/OVERVIEW.md`](project-docs/OVERVIEW.md) — architecture & tech stack
3. [`project-docs/REPORT.md`](project-docs/REPORT.md) — current status & known issues
4. [`project-docs/TODO.md`](project-docs/TODO.md) — open tasks
5. [`project-docs/ROADMAP.md`](project-docs/ROADMAP.md) — planned features

## Quick Summary

This is an enterprise-grade, open-source DDoS protection platform for ISPs.
Stack: FastAPI + PostgreSQL + Redis + React 18 + Prometheus/Grafana.
Multi-tenant: every DB query must filter by `isp_id`.
Security-sensitive files: `mitigation_service.py` (subprocess), `capture_router.py` (file serving).

## All Documentation

[`project-docs/INDEX.md`](project-docs/INDEX.md)
