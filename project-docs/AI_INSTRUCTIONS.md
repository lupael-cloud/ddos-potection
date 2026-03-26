# AI Agent Instructions — DDoS Protection Platform

This file is the **mandatory starting point** for every AI coding agent (GitHub Copilot,
Claude, GPT-4o/Codex, Gemini, Cursor, Aider, or any other AI tool) working in this repository.

> **You MUST read and follow the instructions in this file and the linked documents before
> writing or modifying any code, tests, documentation, or configuration in this repository.**

---

## 1. Mandatory Reading Order

Before touching any file in the repository, read the following in order:

1. **[`OVERVIEW.md`](OVERVIEW.md)** — Understand what this project is, its architecture,
   technology stack, service ports, and repository layout.
2. **[`REPORT.md`](REPORT.md)** — Understand the current implementation status: what is done,
   what is partial, what is planned, and what known issues exist.
3. **[`TODO.md`](TODO.md)** — Check the open task list before making changes. If your task is
   already listed, follow the notes there. If it is not listed, add it when done.
4. **[`ROADMAP.md`](ROADMAP.md)** — Understand where the project is going. Do not implement
   features in ways that conflict with the planned architecture.
5. **The relevant technical doc** for the area you are changing (see Section 3 below).

---

## 2. Core Development Rules

### 2.1 Do No Harm
- **Never remove or break existing tests.** Run `cd backend && pytest` before and after changes.
- **Never change the public API contract** (endpoint paths, request/response schemas) without
  updating both the frontend (`frontend/src/services/api.js`) and the relevant doc in this folder.
- **Never commit secrets, credentials, or API keys.** Use `.env` and `.env.example`.
- **Never introduce new `shell=True` subprocess calls** or string-interpolated shell commands.
  Use argument lists with validated inputs (`ipaddress.ip_address()` for IPs).

### 2.2 Style & Conventions
- **Python (backend):** PEP 8, type hints on all function signatures, docstrings for public
  functions and classes. Use `async def` for I/O-bound functions.
- **JavaScript (frontend):** ES6+, functional React components with hooks, no class components.
  Follow Airbnb style guide.
- **Commit messages:** Conventional Commits format — `type(scope): subject`
  - Types: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`, `security`
- **File placement:** Backend code in `backend/`, frontend in `frontend/`, all documentation
  in `project-docs/`, deployment files in `docker/` or `kubernetes/`.

### 2.3 Testing Requirements
- Every new service function must have at least one unit test in `backend/tests/`.
- Every new API endpoint must have at least one integration test.
- Test files follow the pattern `test_<module>.py`.
- Use `pytest-mock` for mocking; `pytest-asyncio` for async tests.

### 2.4 Documentation Requirements
- Update `project-docs/CHANGELOG.md` for every user-visible change.
- Update `project-docs/TODO.md`: mark items complete `[x]` when done, add new items when
  discovered.
- If you add a new major feature or subsystem, create a dedicated doc page in `project-docs/`
  and add it to `project-docs/INDEX.md`.

---

## 3. Technical Reference by Area

| You are changing... | Read first... |
|---|---|
| Traffic collection (NetFlow/sFlow/IPFIX) | [`TRAFFIC_COLLECTION.md`](TRAFFIC_COLLECTION.md) |
| Packet capture (PCAP / AF_PACKET / AF_XDP) | [`PACKET_CAPTURE.md`](PACKET_CAPTURE.md) |
| BGP blackholing / RTBH | [`BGP-RTBH.md`](BGP-RTBH.md) |
| FlowSpec announcements | [`FLOWSPEC.md`](FLOWSPEC.md) |
| Mitigation rules engine | [`CUSTOM-RULES.md`](CUSTOM-RULES.md) |
| Monitoring / Prometheus / Grafana | [`MONITORING.md`](MONITORING.md) |
| Multi-ISP / multi-tenant features | [`MULTI_ISP_SETUP.md`](MULTI_ISP_SETUP.md) · [`MULTI_ISP_FEATURES.md`](MULTI_ISP_FEATURES.md) |
| Production deployment | [`DEPLOYMENT.md`](DEPLOYMENT.md) |
| Local development setup | [`DEVELOPMENT.md`](DEVELOPMENT.md) |
| Security hardening | [`SECURITY.md`](SECURITY.md) · [`SECURITY_SUMMARY.md`](SECURITY_SUMMARY.md) |
| Q2 2026 advanced features (ML, GeoIP, ClickHouse, Helm, 2FA, Slack) | [`IMPLEMENTATION_DETAILS_Q2_2026.md`](IMPLEMENTATION_DETAILS_Q2_2026.md) |
| Comparison with FastNetMon Advanced | [`COMPARISON_FASTNETMON.md`](COMPARISON_FASTNETMON.md) |

---

## 4. Architecture Constraints

- **Data path:** Routers → UDP collectors → Redis Streams → Anomaly Detector → Alerts.
  Do not bypass Redis for detector communication.
- **Auth:** All API endpoints (except `/api/v1/auth/token` and `/api/v1/auth/register`)
  **must** require a valid JWT token via `Depends(get_current_user)`.
- **Multi-tenancy:** Every database query that returns ISP-specific data **must** filter by
  `isp_id`. Never return data from one ISP to another.
- **Mitigation commands:** Always validate IP/CIDR inputs with Python's `ipaddress` module
  before passing to firewall tools. See [TODO.md — Critical #1](TODO.md).
- **File serving:** When serving user-accessible files (PCAP downloads), always resolve the
  absolute path and assert it starts with the configured base directory. See [TODO.md — Critical #2](TODO.md).

---

## 5. What NOT to Do

- ❌ Do not add new top-level Python packages without first checking them with
  `pip-audit` or the GitHub advisory DB.
- ❌ Do not add new dependencies to `requirements.txt` without adding them to `CHANGELOG.md`.
- ❌ Do not change database model column types or names without an Alembic migration
  (once Alembic is set up; until then, document the manual SQL required).
- ❌ Do not create markdown files at the repository root for notes, plans, or summaries.
  All documentation goes in `project-docs/`.
- ❌ Do not hardcode thresholds, credentials, or configuration in source code.
  Use `config.py` and environment variables.
- ❌ Do not create temporary scripts, helper files, or workarounds outside `/tmp`.
  If a throwaway script is needed, put it in `/tmp` and never commit it.
- ❌ Do not silently swallow exceptions. Log them with the standard `logging` module.

---

## 6. Sensitive Files — Handle With Care

| File | Why sensitive |
|---|---|
| `backend/.env` | All secrets. Never commit. See `.env.example`. |
| `backend/services/mitigation_service.py` | Executes firewall/BGP commands. Validate all inputs. |
| `backend/routers/capture_router.py` | Serves files from filesystem. Prevent path traversal. |
| `backend/routers/payment_router.py` | Stripe/PayPal webhooks. Verify signatures before trusting. |
| `backend/utils/permissions.py` | RBAC enforcement. Do not weaken role checks. |

---

## 7. Quick Environment Reference

```bash
# Start all services
docker-compose up -d

# Run backend tests
cd backend && pytest -v

# Run frontend tests
cd frontend && npm test

# Check API docs
open http://localhost:8000/docs

# Check metrics
curl http://localhost:8000/metrics

# Grafana
open http://localhost:3001  # admin/admin
```

---

## 8. Getting Help

- **Documentation index:** [`INDEX.md`](INDEX.md)
- **Project overview:** [`OVERVIEW.md`](OVERVIEW.md)
- **Open issues:** <https://github.com/lupael/ddos-potection/issues>
- **API docs (live):** <http://localhost:8000/docs>

---

*This file is authoritative. If you find a conflict between this file and another source,
follow this file and open an issue to resolve the discrepancy.*

*Last updated: 2026-03-25*
