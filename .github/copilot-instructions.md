# GitHub Copilot Instructions — DDoS Protection Platform

You are working on an enterprise-grade, open-source DDoS protection platform for Internet Service
Providers (ISPs). Before suggesting or generating any code, you MUST follow the instructions in
`project-docs/AI_INSTRUCTIONS.md`.

## Read These First

- `project-docs/AI_INSTRUCTIONS.md` — mandatory rules for all AI agents
- `project-docs/OVERVIEW.md` — architecture, tech stack, service ports
- `project-docs/REPORT.md` — current implementation status and known issues
- `project-docs/TODO.md` — open tasks (check before adding code)
- `project-docs/ROADMAP.md` — planned features and architecture direction
- `project-docs/INDEX.md` — full documentation index

## Technology Stack

- **Backend:** Python 3.11, FastAPI, SQLAlchemy 2.0, Pydantic 2.5, Redis 7, PostgreSQL 15
- **Frontend:** React 18, Chart.js 4, Axios, React Router 6
- **Network:** Scapy, Netmiko, NAPALM, ExaBGP/FRR/BIRD
- **Infra:** Docker Compose, Kubernetes, Prometheus, Grafana

## Critical Rules

1. **All documentation** goes in `project-docs/` — never create `.md` files at the repo root.
2. **Run tests** before and after backend changes: `cd backend && pytest -v`
3. **Never use `shell=True`** in subprocess calls. Validate all IP/CIDR inputs with `ipaddress`.
4. **All API endpoints** except `/api/v1/auth/token` and `/api/v1/auth/register` must require JWT.
5. **All ISP-specific DB queries** must include a `WHERE isp_id = :isp_id` filter.
6. **Never commit secrets**. Use `.env.example` as a template; real secrets go in `.env` only.
7. **Path traversal:** When serving files, validate path is inside the allowed base directory.
8. **Update `project-docs/CHANGELOG.md`** and **`project-docs/TODO.md`** with every change.

## File Structure

```
project-docs/   ← ALL documentation lives here
backend/        ← FastAPI Python backend
frontend/       ← React 18 dashboard
docker/         ← Docker, Prometheus, Grafana configs
kubernetes/     ← Kubernetes manifests
scripts/        ← Router integration scripts
```

## Security-Sensitive Files (Handle With Extra Care)

- `backend/services/mitigation_service.py` — executes firewall/BGP commands
- `backend/routers/capture_router.py` — serves PCAP files from filesystem
- `backend/routers/payment_router.py` — Stripe/PayPal webhook verification
- `backend/utils/permissions.py` — RBAC enforcement
