# Documentation Index — DDoS Protection Platform

> **AI agents:** Read [`AI_INSTRUCTIONS.md`](AI_INSTRUCTIONS.md) **first**, before anything else.

All project documentation lives in this `project-docs/` folder. This index is the master
table of contents.

---

## 🤖 AI Agent Instructions (Start Here)

| File | Description |
|---|---|
| [`AI_INSTRUCTIONS.md`](AI_INSTRUCTIONS.md) | **Mandatory reading for every AI agent.** Rules, constraints, style guide, and what to read for each area of the codebase. |

---

## 📊 Project Status & Planning

| File | Description |
|---|---|
| [`OVERVIEW.md`](OVERVIEW.md) | High-level project description, architecture diagram, tech stack, service ports, repository layout |
| [`REPORT.md`](REPORT.md) | Current implementation status per component, known issues, risk register, codebase metrics |
| [`ROADMAP.md`](ROADMAP.md) | Feature roadmap by phase (Q2 2026 – Q2 2027), prioritised backlog, KPI targets |
| [`TODO.md`](TODO.md) | Concrete actionable work items with file references, priority levels, and completion status |
| [`CHANGELOG.md`](CHANGELOG.md) | Version history following Keep-a-Changelog / Semantic Versioning |

---

## 🚀 Getting Started

| File | Description |
|---|---|
| [`QUICKSTART.md`](QUICKSTART.md) | Get the platform running in under 10 minutes with Docker Compose |
| [`DEPLOYMENT.md`](DEPLOYMENT.md) | Production deployment guide (SSL, firewall, backups, scaling) |
| [`DEVELOPMENT.md`](DEVELOPMENT.md) | Local development environment setup, coding standards, test workflow |
| [`CONTRIBUTING.md`](CONTRIBUTING.md) | How to contribute: PR workflow, commit message format, review process |

---

## 🔧 Feature & Integration Guides

| File | Description |
|---|---|
| [`TRAFFIC_COLLECTION.md`](TRAFFIC_COLLECTION.md) | NetFlow v5/v9, sFlow v5, IPFIX — collector setup and router configuration |
| [`PACKET_CAPTURE.md`](PACKET_CAPTURE.md) | PCAP, AF_PACKET, AF_XDP, VLAN untagging — capture modes and configuration |
| [`BGP-RTBH.md`](BGP-RTBH.md) | BGP blackholing (RTBH) via ExaBGP, FRR, and BIRD |
| [`FLOWSPEC.md`](FLOWSPEC.md) | FlowSpec (RFC 5575) announcements for advanced mitigation |
| [`CUSTOM-RULES.md`](CUSTOM-RULES.md) | Rule engine: IP block, rate limit, protocol filter, geo-block |
| [`MONITORING.md`](MONITORING.md) | Prometheus metrics (33 total), Grafana dashboards (3), alert channels |
| [`MULTI_ISP_SETUP.md`](MULTI_ISP_SETUP.md) | Multi-tenant ISP configuration, onboarding, subscription management |
| [`MULTI_ISP_FEATURES.md`](MULTI_ISP_FEATURES.md) | Multi-ISP feature description: RBAC, isolation, billing, branding |

---

## 🔒 Security

| File | Description |
|---|---|
| [`SECURITY.md`](SECURITY.md) | Security features, hardening recommendations, compliance (GDPR, PCI DSS, ISO 27001), incident response |
| [`SECURITY_SUMMARY.md`](SECURITY_SUMMARY.md) | CodeQL analysis results, accepted false positives, security mitigations in place |

---

## 📈 Implementation Summaries

| File | Description |
|---|---|
| [`IMPLEMENTATION_SUMMARY.md`](IMPLEMENTATION_SUMMARY.md) | Summary of monitoring & alerting system implementation (Prometheus, Grafana, notifications, attack map) |
| [`PACKET_CAPTURE_IMPLEMENTATION.md`](PACKET_CAPTURE_IMPLEMENTATION.md) | Summary of packet capture and per-subnet threshold management implementation |
| [`MULTI_ISP_IMPLEMENTATION_SUMMARY.md`](MULTI_ISP_IMPLEMENTATION_SUMMARY.md) | Summary of multi-ISP and multi-tenant feature implementation |
| [`IMPLEMENTATION_DETAILS_Q2_2026.md`](IMPLEMENTATION_DETAILS_Q2_2026.md) | Detailed implementation guide for Q2 2026 advanced features: ML, GeoIP, ClickHouse, Helm, 2FA, Slack |

---

## 🏆 Comparison & Analysis

| File | Description |
|---|---|
| [`COMPARISON_FASTNETMON.md`](COMPARISON_FASTNETMON.md) | Feature-by-feature comparison with FastNetMon Advanced Edition, migration guide, use-case recommendations |

---

## 🖼️ Screenshots

| File | Description |
|---|---|
| [`screenshots/dashboard.png`](screenshots/dashboard.png) | Main dashboard |
| [`screenshots/traffic-monitor.png`](screenshots/traffic-monitor.png) | Traffic monitoring view |
| [`screenshots/alerts.png`](screenshots/alerts.png) | Alert management |
| [`screenshots/rules.png`](screenshots/rules.png) | Rule management |
| [`screenshots/BGP-UI-LAYOUT.md`](screenshots/BGP-UI-LAYOUT.md) | BGP UI layout description |

---

## Document Count Summary

| Category | Count |
|---|---|
| AI / Planning docs | 5 (AI_INSTRUCTIONS, OVERVIEW, REPORT, ROADMAP, TODO) |
| Getting started | 4 (QUICKSTART, DEPLOYMENT, DEVELOPMENT, CONTRIBUTING) |
| Feature guides | 8 |
| Security | 2 |
| Implementation summaries | 4 |
| Comparison | 1 |
| Changelog | 1 |
| **Total** | **25** |

---

*Last updated: 2026-03-25*
