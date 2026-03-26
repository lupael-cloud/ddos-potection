# Project Overview — DDoS Protection Platform for ISPs

> **AI agents:** Read [`AI_INSTRUCTIONS.md`](AI_INSTRUCTIONS.md) before making any changes to this repository.

## What This Project Is

The **DDoS Protection Platform** is an open-source, enterprise-grade, multi-tenant SaaS application
purpose-built for Internet Service Providers (ISPs). It provides automated detection, real-time
alerting, and multi-layer mitigation of DDoS attacks across an ISP's entire customer base without
requiring any per-incident operator intervention.

It is a direct, zero-licensing-cost alternative to commercial products such as FastNetMon Advanced,
Arbor Sightline, or Radware DefensePro.

---

## Core Architecture

```
Routers / Network Edge
  │  NetFlow v5/v9 · sFlow v5 · IPFIX (UDP)
  ▼
Traffic Collector Cluster ──► Redis Streams ──► Anomaly Detector
  │                                                    │
  │  AF_PACKET / AF_XDP (inline capture)               │ Alerts
  ▼                                                    ▼
Packet Capture Service                     Mitigation Orchestrator
                                                    │
                              ┌─────────────────────┼────────────────────┐
                              ▼                     ▼                    ▼
                         iptables /           BGP RTBH /           MikroTik
                         nftables             FlowSpec              RouterOS API
                              │
                              ▼
                    Backend API (FastAPI)
                              │
               ┌──────────────┼───────────────┐
               ▼              ▼               ▼
          React Dashboard  Prometheus      Notification
          (ISP operators)   + Grafana      (Email/SMS/
                                            Telegram)
```

---

## Technology Stack

| Layer | Technology |
|---|---|
| **Backend API** | Python 3.11, FastAPI 0.109, Uvicorn |
| **Database** | PostgreSQL 15 (ORM: SQLAlchemy 2.0, Pydantic 2.5) |
| **Cache / Streams** | Redis 7 |
| **Frontend** | React 18, Chart.js 4, Recharts, Axios |
| **Auth** | JWT (python-jose), bcrypt |
| **Network** | Scapy 2.7, Paramiko, Netmiko 4.3, NAPALM |
| **Monitoring** | Prometheus, Grafana |
| **Async Tasks** | Celery 5.3, aiokafka (Kafka-ready) |
| **Payments** | Stripe, PayPal, bKash |
| **Alerting** | Email (SMTP), Twilio SMS, Telegram Bot |
| **Deployment** | Docker Compose, Kubernetes |

---

## Key Capabilities

### Traffic Collection
- **NetFlow v5 / v9** — Cisco, MikroTik, many others
- **sFlow v5** — Juniper, Arista, generic switches
- **IPFIX** — RFC 5101/5102 compliant
- **AF_PACKET** (Linux raw sockets) — high-performance
- **AF_XDP** — eXpress Data Path (≥10 Gbps, with AF_PACKET fallback)
- **VLAN untagging** — 802.1Q, 802.1ad, QinQ

### Attack Detection
| Vector | Method | Threshold Config |
|---|---|---|
| SYN Flood | Packet rate / destination | `SYN_FLOOD_THRESHOLD` |
| UDP Flood | Volume / 60-second window | `UDP_FLOOD_THRESHOLD` |
| ICMP Flood | ppm per destination | `ICMP_FLOOD_THRESHOLD` |
| DNS Amplification | Large UDP/53 responses | `DNS_AMPLIFICATION_THRESHOLD` |
| Distributed (botnet) | Shannon entropy of source IPs | `ENTROPY_THRESHOLD` |
| Per-subnet | Longest-prefix-match hostgroups | Per-hostgroup |

### Mitigation
- **iptables / nftables** — Linux firewall rules
- **MikroTik RouterOS API** — Direct router control
- **BGP RTBH** — RFC 5635 blackholing via ExaBGP / FRR / BIRD
- **FlowSpec** — RFC 5575 announcements
- **Custom rule engine** — IP block, rate-limit, protocol filter, geo-block

### Multi-tenancy & Billing
- ISP accounts with isolated data, RBAC (admin / operator / viewer)
- Subscription tiers: Basic ($29.99), Professional ($99.99), Enterprise ($299.99)
- Payment: Stripe, PayPal, bKash; invoice generation
- Monthly / weekly / incident reports (PDF / CSV / TXT)

---

## Service Ports

| Service | Port | Protocol |
|---|---|---|
| Frontend Dashboard | 3000 | TCP (HTTP) |
| Backend API | 8000 | TCP (HTTP) |
| NetFlow Collector | 2055 | UDP |
| sFlow Collector | 6343 | UDP |
| IPFIX Collector | 4739 | UDP |
| PostgreSQL | 5432 | TCP |
| Redis | 6379 | TCP |
| Prometheus | 9090 | TCP |
| Grafana | 3001 | TCP |

---

## Repository Layout

```
ddos-potection/
├── README.md               ← Start here
├── LICENSE
├── .env.example            ← Environment variable template
├── docker-compose.yml      ← One-command deployment
├── project-docs/           ← ALL documentation (this folder)
│   ├── INDEX.md            ← Documentation index
│   ├── OVERVIEW.md         ← This file
│   ├── ROADMAP.md          ← Feature roadmap
│   ├── TODO.md             ← Open tasks
│   ├── REPORT.md           ← Project status report
│   ├── AI_INSTRUCTIONS.md  ← AI agent instructions
│   ├── QUICKSTART.md
│   ├── DEPLOYMENT.md
│   ├── DEVELOPMENT.md
│   ├── ...                 ← All other docs
│   └── screenshots/
├── backend/                ← FastAPI Python backend
├── frontend/               ← React web dashboard
├── docker/                 ← Docker configs, Prometheus, Grafana
├── kubernetes/             ← Kubernetes manifests
└── scripts/                ← Router integration scripts
```

---

## Quick Start (30 seconds)

```bash
git clone https://github.com/lupael/ddos-potection.git
cd ddos-potection
cp .env.example backend/.env   # edit as needed
docker-compose up -d
# Dashboard → http://localhost:3000
# API docs  → http://localhost:8000/docs
# Grafana   → http://localhost:3001 (admin/admin)
```

Full instructions: [`QUICKSTART.md`](QUICKSTART.md)

---

## License

MIT — see [`../LICENSE`](../LICENSE)

---

*Last updated: 2026-03-25*
