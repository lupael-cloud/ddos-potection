# Roadmap — DDoS Protection Platform for ISPs

> **AI agents:** Read [`AI_INSTRUCTIONS.md`](AI_INSTRUCTIONS.md) before making any changes to this repository.

This document tracks planned features, enhancements, and architectural improvements. Items are
organised by release phase and priority level.

Legend: 🔴 Critical · 🟠 High · 🟡 Medium · 🟢 Low · ✅ Done · 🚧 In-progress · 📋 Planned

---

## ✅ Released — v1.0.x (Current)

### Core Platform
- ✅ FastAPI backend with PostgreSQL, Redis, JWT auth
- ✅ React 18 dashboard (traffic, alerts, rules, reports, settings)
- ✅ NetFlow v5/v9, sFlow v5, IPFIX collection
- ✅ Threshold-based detection: SYN, UDP, ICMP, DNS-amp, entropy
- ✅ Mitigation: iptables/nftables, MikroTik API, BGP RTBH, FlowSpec
- ✅ Multi-tenant ISP accounts with RBAC
- ✅ Subscription management & billing (Stripe, PayPal, bKash)
- ✅ Prometheus metrics (33 metrics) + Grafana dashboards (3)
- ✅ Multi-channel alerts: Email, Twilio SMS, Telegram
- ✅ Packet capture: PCAP, AF_PACKET, AF_XDP (with fallback)
- ✅ VLAN untagging: 802.1Q, 802.1ad, QinQ
- ✅ Per-subnet threshold management (hostgroups, longest-prefix-match)
- ✅ Live attack map with WebSocket streaming
- ✅ Report generation: PDF / CSV / TXT
- ✅ Docker Compose + Kubernetes deployment manifests
- ✅ 9 pytest test modules (~100+ tests)

---

## Phase 1 — Foundation & Scale (Q2 2026)

### 1.1 High-Throughput Pipeline 🔴
- 📋 **Kafka integration** — wire `aiokafka` (already in `requirements.txt`) to replace Redis Streams as primary flow bus; Redis becomes fast-window cache
- 📋 **SO_REUSEPORT collector workers** — multi-process UDP receive across CPU cores
- 📋 **Complete AF_XDP path** — implement real XDP eBPF filter (`xdp_ddos_filter.c`) via `libbpf`; target ≥10 Mpps on 10GbE NIC
- 📋 **TimescaleDB** — add as PostgreSQL extension for `TrafficLog` time-series efficiency; implement hot (7d) / warm (90d) / cold (1y) data tiers

### 1.2 High Availability 🔴
- 📋 **`/health/live` and `/health/ready` endpoints** — Kubernetes liveness/readiness probes
- 📋 **Redis Sentinel** — replace single Redis with Sentinel in `docker-compose.yml`
- 📋 **Stateless API** — externalise all session state to Redis; enable horizontal scaling
- 📋 **Multi-collector deployment** — N collector containers behind UDP load balancer (HAProxy)
- 📋 **PostgreSQL read replicas** — route SELECT queries to replica for reporting workloads

### 1.3 Database Migrations 🟠
- 📋 **Alembic setup** — add migration framework; current schema is created ad-hoc via `Base.metadata.create_all`
- 📋 **Expand/contract pattern** — all schema changes backward compatible

---

## Phase 2 — Advanced Detection (Q3 2026)

### 2.1 Machine Learning Baseline 🔴
- 📋 **Baseline learner service** — rolling 4-week per-prefix statistics (mean ± N×σ adaptive thresholds); store in `baseline_stats` table
- 📋 **Isolation Forest anomaly detector** (`scikit-learn`) — feature vector: `[pps, bps, fps, syn_ratio, udp_ratio, icmp_ratio, entropy_src, entropy_dst_port]`; retrain every 24h
- 📋 **Shadow mode** — new detectors alert but do not trigger mitigation until validated
- 📋 **LSTM attack predictor** — predict attack start 60–120s before threshold breach (v2)

### 2.2 Expanded Attack Signatures 🟠
- 📋 NTP amplification detection (UDP/123, amplification ratio >10x)
- 📋 SSDP amplification (UDP/1900 large responses)
- 📋 Memcached amplification (UDP/11211 >1400-byte responses)
- 📋 TCP RST / TCP ACK flood
- 📋 HTTP flood / Slowloris (Layer 7, from PCAP stream)
- 📋 DNS water-torture (NXDOMAIN rate threshold)
- 📋 BGP hijack indicator alerting
- 📋 IP spoofing detection (uRPF-style check against registered prefixes)

### 2.3 Threat Intelligence 🟠
- 📋 **Feed ingestion service** — Spamhaus DROP/EDROP, Emerging Threats, CINS Army, Feodo Tracker; refresh hourly via Celery beat
- 📋 **GeoIP** — MaxMind GeoLite2 integration (real coordinates in attack map, geo-blocking rules)
- 📋 **RPKI/ROA validation** — flag traffic from RPKI-invalid prefixes
- 📋 **Threat score** (0–100) on every alert: bad-actor feed hit +40, RPKI invalid +20, geo-blocked region +20, ML confidence +20

### 2.4 Cloud & Tunnel Flow Support 🟡
- 📋 GRE decapsulation for flow analysis
- 📋 AWS VPC Flow Logs ingestion
- 📋 Google Cloud Flow Logs ingestion
- 📋 Encrypted flow support (TLS-wrapped NetFlow)

---

## Phase 3 — Advanced Mitigation (Q3–Q4 2026)

### 3.1 Scrubbing Centre Integration 🔴
- 📋 **Diversion module** — BGP /32 advertisement with scrubbing-centre next-hop; GRE tunnel management for clean return traffic
- 📋 **Multi-centre support** — anycast closest-centre selection, capacity management
- 📋 **Third-party APIs** — Lumen DDoS Hyper, Cloudflare Magic Transit, NSFOCUS ADS

### 3.2 Multi-Vendor Router ACL Push 🟠
- 📋 **Cisco IOS/IOS-XR driver** — ACL push via Netmiko
- 📋 **Juniper JunOS driver** — firewall filter via NAPALM
- 📋 **Nokia SROS driver** — CPM filter
- 📋 **Arista EOS driver** — ACL via eAPI
- 📋 **Router inventory model** — `Router(vendor, ip, credentials, role: border/scrubbing/access)`

### 3.3 Mitigation Lifecycle 🟠
- 📋 **State machine**: `Detected → Mitigating → Verifying → Resolved / Escalating`
- 📋 **Post-mitigation verification** — confirm traffic dropped below threshold for 60s; escalate if not
- 📋 **Cooldown de-mitigation** — hold for configurable period after traffic normalises; gradual removal
- 📋 **Intelligent selection** — map attack type → optimal mitigation action
- 📋 **Auto-escalation matrix** — if mitigation N ineffective after T min, apply N+1

### 3.4 SLA Tracking 🟠
- 📋 TTD (time-to-detect) and TTM (time-to-mitigate) recording per incident
- 📋 Tier-based SLA targets: Standard (TTD <5m, TTM <15m) / Pro (TTD <2m, TTM <5m) / Enterprise (TTD <30s, TTM <2m)
- 📋 Monthly SLA compliance reports with breach credit calculation

---

## Phase 4 — ISP Operations (Q4 2026)

### 4.1 NOC Integration 🟠
- 📋 **Webhook system** — register URLs for alert/mitigation events; HMAC-SHA256 signatures; exponential-backoff retry
- 📋 **PagerDuty native** — Events API v2
- 📋 **Slack / Microsoft Teams** — rich message cards
- 📋 **ServiceNow / JIRA / Zendesk** — incident ticket creation

### 4.2 Customer Self-Service Portal 🟠
- 📋 `customer` RBAC role — read-only, scoped to their IP prefixes
- 📋 Frontend pages: MyProtection, MyAlerts, MyReports, MySettings
- 📋 Customer notification preference management (whitelist IPs, choose alert channels)

### 4.3 Whitelabel & Multi-Brand 🟡
- 📋 Per-ISP branding fields: logo, primary colour, company name, portal domain
- 📋 CSS variable injection from API at login
- 📋 Branded email templates
- 📋 Custom domain (CNAME) support

---

## Phase 5 — Security & Compliance (Q1 2027)

### 5.1 Audit Logging 🔴
- 📋 `AuditLog` model — immutable record of every config/mitigation change
- 📋 FastAPI middleware for automatic mutation logging
- 📋 `GET /api/v1/audit/logs` (admin, paginated)
- 📋 SIEM export: Syslog RFC 5424 and CEF format (Splunk / QRadar / Elastic)

### 5.2 Flow Authentication 🟠
- 📋 NetFlow/IPFIX source IP allow-listing against registered router inventory
- 📋 HMAC-MD5 authentication over flow headers (where router supports)
- 📋 DTLS-wrapped UDP (optional, for environments that support it)

### 5.3 GDPR & Data Governance 🟠
- 📋 Configurable retention policies per ISP (traffic logs, PCAPs, alerts)
- 📋 Right to erasure: `DELETE /api/v1/admin/isp/{id}/purge-data`
- 📋 GDPR subject access request export
- 📋 IP address classification as potential PII

### 5.4 IPAM & NMS Integration 🟡
- 📋 **Netbox sync** — auto-import prefixes/customers; push mitigations as journal entries
- 📋 **SNMP trap sender** — attack-start / attack-end traps to NMS (Zabbix/Nagios)
- 📋 **Zabbix template** — auto-discovery XML

---

## Phase 6 — Analytics & AI (Q2 2027)

### 6.1 Attack Analytics 🟠
- 📋 Cross-customer correlation — coordinated botnet detection across ISP tenants
- 📋 Attack campaign tracking — group related attacks over time
- 📋 Reusable signature library — auto-extract BPF / FlowSpec rules
- 📋 Botnet C2 fingerprinting

### 6.2 Predictive Analytics 🟡
- 📋 Traffic forecasting (ARIMA / Prophet) for capacity planning
- 📋 Daily attack-probability scoring per prefix
- 📋 Pre-emptive mitigation (lighter action when risk score > threshold)
- 📋 Monthly infrastructure capacity projections

### 6.3 Business Intelligence 🟡
- 📋 MRR / churn / subscription growth analytics
- 📋 Attack cost modelling (estimated business impact)
- 📋 ISP ROI calculator
- 📋 Executive KPI dashboard

---

## Phase 7 — Production DevOps (Q2 2027)

- 📋 **Helm chart** — parametrised chart replacing raw Kubernetes YAML
- 📋 **HPA** — Horizontal Pod Autoscaler for collectors and API
- 📋 **Pod Disruption Budget** — zero-downtime rolling updates
- 📋 **Kubernetes Network Policies** — restrict pod-to-pod paths
- 📋 **Secrets management** — HashiCorp Vault / Kubernetes External Secrets
- 📋 **PostgreSQL PITR backups** — WAL streaming to S3/MinIO, 15-min RPO
- 📋 **Disaster recovery runbook** — documented failover automation

---

## Technical Debt (Ongoing)

| Item | Priority | Notes |
|---|---|---|
| `subprocess` in `mitigation_service.py` | 🔴 | Input sanitisation needed to prevent command injection |
| No Alembic migrations | 🔴 | Schema is created ad-hoc; breaking for upgrades |
| `config.py` 111-variable flat file | 🟠 | Refactor into Pydantic sub-models |
| Detector uses `asyncio.sleep` polling | 🟠 | Should be event-driven from Kafka/Redis |
| No TypeScript in frontend | 🟡 | Migrate API service layer first |
| PCAP download path traversal risk | 🟠 | Validate file path against PCAP directory |
| Placeholder GeoIP in attack map | 🟠 | Replace with real MaxMind integration |

---

## Success KPIs

| Metric | Current | Phase 1–3 Target | Phase 4–7 Target |
|---|---|---|---|
| Max flow throughput | ~1 Mpps | ≥5 Mpps | ≥14 Mpps (10GbE line-rate) |
| Detection time (TTD) | ~10 s | <5 s | <2 s |
| Mitigation time (TTM) | Manual | <30 s automated | <10 s automated |
| False positive rate | Unknown | <5% | <1% |
| Attack vectors covered | 5 | 15 | 25+ |
| Vendor support | MikroTik | +Cisco/Juniper | All major vendors |
| HA uptime SLA | N/A | 99.9% | 99.99% |

---

*Last updated: 2026-03-25*
