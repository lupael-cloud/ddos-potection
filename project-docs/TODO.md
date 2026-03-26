# TODO — DDoS Protection Platform

> **AI agents:** Read [`AI_INSTRUCTIONS.md`](AI_INSTRUCTIONS.md) before making any changes to this repository.

This file tracks concrete, actionable work items. Each item references the relevant
source file(s) and the phase in [`ROADMAP.md`](ROADMAP.md) it belongs to.

Legend: `[ ]` open · `[x]` done · `[~]` in-progress · `[!]` blocked

---

## 🔴 Critical — Must fix before next production release

- [ ] **[Security] Sanitise `subprocess` calls in `mitigation_service.py`**
  - File: `backend/services/mitigation_service.py`
  - Risk: rule conditions that contain shell metacharacters could achieve command injection
  - Fix: validate IP/CIDR inputs with `ipaddress` module before passing to iptables/nftables; use argument list (not shell=True)

- [ ] **[Security] PCAP download path traversal**
  - File: `backend/routers/capture_router.py` — `GET /api/v1/capture/download/{file}`
  - Risk: a crafted filename (e.g., `../../etc/passwd`) could read arbitrary files
  - Fix: resolve the requested path and assert it is inside the configured PCAP directory

- [ ] **[Infra] Add Alembic for database migrations**
  - Without migrations, schema changes require manual SQL or full DB recreation
  - Steps: `pip install alembic`, `alembic init`, create initial migration from current models, add to CI

- [ ] **[Health] Add `/health/live` and `/health/ready` endpoints**
  - File: `backend/main.py`
  - Required by Kubernetes liveness/readiness probes
  - `live` → always 200 if process is alive; `ready` → 200 only if DB + Redis reachable

---

## 🟠 High Priority

- [ ] **[Detection] NTP amplification detection**
  - File: `backend/services/anomaly_detector.py`
  - Add: high UDP/123 response rate (>amplification threshold) triggers `ntp_amplification` alert

- [ ] **[Detection] Memcached amplification detection**
  - File: `backend/services/anomaly_detector.py`
  - Add: UDP/11211 responses >1400 bytes triggers `memcached_amplification` alert

- [ ] **[Detection] SSDP amplification detection**
  - File: `backend/services/anomaly_detector.py`
  - Add: UDP/1900 large responses triggers `ssdp_amplification` alert

- [ ] **[Detection] TCP RST flood and TCP ACK flood**
  - File: `backend/services/anomaly_detector.py`
  - Add: high RST/ACK ratio per source, and pure ACK floods without prior SYN

- [ ] **[GeoIP] Replace placeholder coordinates in attack map**
  - File: `backend/routers/attack_map_router.py`
  - Current implementation returns hardcoded/random coordinates
  - Fix: integrate MaxMind GeoLite2 (`geoip2` Python library, free DB download on startup)

- [ ] **[Scale] Wire Kafka for flow pipeline**
  - `aiokafka` is already in `requirements.txt` but not used
  - Files: `backend/services/traffic_collector.py`, new `backend/services/kafka_consumer.py`
  - Provide `KAFKA_ENABLED=false` env flag to keep Redis Streams fallback

- [ ] **[Config] Refactor `config.py` into sub-models**
  - File: `backend/config.py`
  - 111 flat env variables; group into: `DatabaseSettings`, `RedisSettings`, `DetectionSettings`, `NotificationSettings`, `BGPSettings`, `CaptureSettings`

- [ ] **[Mitigation] Implement mitigation lifecycle state machine**
  - Files: `backend/services/mitigation_service.py`, `backend/routers/mitigation_router.py`
  - States: `Detected → Mitigating → Verifying → Resolved` (+ `Escalating`)
  - Add post-mitigation traffic verification and cooldown-based de-mitigation

- [ ] **[Detector] Make anomaly detector event-driven**
  - File: `backend/services/anomaly_detector.py`
  - Currently polls Redis with `asyncio.sleep(10)` — replace with event-driven consumer

- [ ] **[Alerts] Add Slack and Microsoft Teams notification channels**
  - File: `backend/services/notification_service.py`
  - Add alongside existing Email, Twilio SMS, Telegram

- [ ] **[Observability] Add SLA tracking**
  - Record TTD (time-to-detect) and TTM (time-to-mitigate) for every incident
  - New model: `SLARecord`; new router: `backend/routers/sla_router.py`

---

## 🟡 Medium Priority

- [ ] **[Frontend] TypeScript migration for API service layer**
  - File: `frontend/src/services/api.js` → `api.ts`
  - Start with service layer to catch API contract mismatches at build time

- [ ] **[Infra] Redis Sentinel in docker-compose.yml**
  - Replace single Redis container with Sentinel configuration for HA

- [ ] **[Scale] SO_REUSEPORT for collector workers**
  - File: `backend/services/traffic_collector.py`
  - Spread UDP receive across N CPU cores using `SO_REUSEPORT`

- [ ] **[Threat intel] Threat intelligence feed ingestion**
  - New file: `backend/services/threat_intel.py`
  - Sources: Spamhaus DROP/EDROP, Emerging Threats, CINS Army, Feodo Tracker
  - Refresh hourly via Celery beat; store in Redis SET for O(1) lookup

- [ ] **[Auth] Webhook system with HMAC-SHA256 signatures**
  - New files: `backend/services/webhook_service.py`, `backend/routers/webhook_router.py`
  - Register URLs for alert/mitigation events; exponential-backoff retry on failure

- [ ] **[RBAC] Customer self-service portal**
  - Add `customer` role to RBAC (read-only, scoped to their IP prefixes)
  - New frontend pages: MyProtection, MyAlerts, MyReports, MySettings

- [ ] **[Compliance] Audit logging middleware**
  - New files: `backend/models/models.py` (AuditLog model), `backend/middleware/audit_middleware.py`
  - Auto-log all POST/PUT/DELETE API calls: who, what, old value, new value, IP

- [ ] **[HA] Horizontal Pod Autoscaler for Kubernetes**
  - File: `kubernetes/`
  - Add HPA for collector and API deployments based on CPU and custom flow-rate metric

---

## 🟢 Low Priority / Nice to Have

- [ ] **[Frontend] Dark mode / theming**
- [ ] **[API] GraphQL endpoint** alongside REST
- [ ] **[Reporting] Two-Factor Authentication (TOTP)**
- [ ] **[Mobile] React Native companion app**
- [ ] **[Integration] Netbox IPAM sync** (`backend/services/netbox_sync.py`)
- [ ] **[Integration] SNMP trap sender** for Zabbix/Nagios
- [ ] **[Analytics] Attack campaign tracking** across ISP tenants
- [ ] **[Analytics] Traffic forecasting** (ARIMA/Prophet) for capacity planning
- [ ] **[DevOps] Helm chart** for Kubernetes deployment
- [ ] **[DevOps] HashiCorp Vault** integration for secrets management

---

## ✅ Completed

- [x] FastAPI backend, PostgreSQL, Redis, JWT auth
- [x] React 18 dashboard with Chart.js
- [x] NetFlow v5/v9, sFlow v5, IPFIX collection
- [x] SYN / UDP / ICMP / DNS-amp / entropy detection
- [x] iptables, nftables, MikroTik API, BGP RTBH, FlowSpec mitigation
- [x] Multi-tenant ISP accounts with RBAC
- [x] Stripe, PayPal, bKash billing
- [x] 33 Prometheus metrics + 3 Grafana dashboards
- [x] Email, Twilio SMS, Telegram notifications
- [x] AF_PACKET packet capture; AF_XDP with fallback
- [x] VLAN untagging (802.1Q, 802.1ad, QinQ)
- [x] Per-subnet hostgroups with longest-prefix-match
- [x] WebSocket live attack map
- [x] PDF/CSV/TXT report generation
- [x] Docker Compose + Kubernetes YAML
- [x] 9 pytest test modules (~100+ tests)
- [x] Prometheus / Grafana monitoring stack
- [x] FastAPI security patch (CVE - python-multipart ≤0.0.6)

---

*Last updated: 2026-03-25*
