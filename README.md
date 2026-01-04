# 🛡️ Homelab Security Architecture: Automated SSH Defense

![Architecture Diagram](homelab-security-architecture.png)

## 🏗️ Design Overview
This repository documents the security architecture designed to protect my Homelab infrastructure against brute-force attacks. The goal is to create a closed-loop system that not only blocks threats but visualizes them in real-time.

### 🔄 The Architecture Logic
1.  **Detection**: `sshd` logs authentication failures.
2.  **Reaction**: Fail2Ban (configured with custom jails) triggers immediate temporary bans.
3.  **Ingestion**: A Python service parses logs to extract IP addresses.
4.  **Intelligence**: IPs are enriched with GeoLocation data (GeoLite2).
5.  **Persistence**: Attack data is stored in a relational database (SQLite).
6.  **Visualization**: A dashboard renders the threat map.

---

## 🚀 Project Status & Roadmap
**Current Phase: Active Development / Implementation**

I am currently implementing this architecture in my production environment.

- [x] **Phase 1: Hardening** (Completed)
    - SSH Configuration & Key-based Auth.
    - Fail2Ban Jail configuration & Regex filtering.
- [x] **Phase 2: Log Parsing** (Completed)
    - Python script for real-time log ingestion.
- [ ] **Phase 3: Data Persistence** (In Progress)
    - SQLite Schema design.
    - Script integration for database writes.
- [ ] **Phase 4: Visualization** (Planned)
    - Frontend dashboard for the threat map.

## 🛠️ Tech Stack
* **Core**: Python 3, Bash
* **Security**: Fail2Ban, IPTables
* **Infrastructure**: Docker, Ubuntu Server

---

### ⚠️ Note for Reviewers
*> This repository currently hosts the design documentation. The source code will be pushed once the Persistence layer (Phase 3) passes internal testing in the Homelab.*
