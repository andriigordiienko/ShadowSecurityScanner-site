<!--
  DRAFT README for the PUBLIC downloads repo  github.com/safetylab/shadowsecurityscanner
  This repo only hosts release binaries — the source is maintained privately, so there is
  NO "build from source" section. Copy everything BELOW this comment into the repo README.md.
-->

# ShadowSecurityScanner

![Platforms](https://img.shields.io/badge/platforms-Windows%20%7C%20macOS%20%7C%20Linux-blue)
![Downloads](https://img.shields.io/github/downloads/safetylab/shadowsecurityscanner/total)
![Latest release](https://img.shields.io/github/v/release/safetylab/shadowsecurityscanner)
![Stars](https://img.shields.io/github/stars/safetylab/shadowsecurityscanner?style=social)

**ShadowSecurityScanner** is a free **penetration testing tool** and **network vulnerability
scanner**. It performs port scanning, service & OS fingerprinting, and thousands of catalogued
network and web checks, then ranks every finding by real-world exploit probability —
**EPSS** (FIRST.org) + **CISA KEV** — not just raw CVSS. A single self-contained desktop app
for **Windows, macOS and Linux**. No cloud, no agents, no telemetry.

> This repository hosts the **release binaries**. Builds are published here by CI.

- 🌐 **Website & docs:** https://andriigordiienko.github.io/ShadowSecurityScanner-site/
- 📊 **vs Nessus & OpenVAS:** https://andriigordiienko.github.io/ShadowSecurityScanner-site/compare/
- 📘 **Guides:** https://andriigordiienko.github.io/ShadowSecurityScanner-site/guides/

---

## Download

Get the latest build for your platform from the
[**Releases page**](https://github.com/safetylab/shadowsecurityscanner/releases/latest):

| Platform | File |
|---|---|
| Windows (x64) | `ShadowSecurityScanner-windows-amd64.exe` |
| Windows (ARM64) | `ShadowSecurityScanner-windows-arm64.exe` |
| macOS (Apple Silicon) | `ShadowSecurityScanner-macos-arm64.dmg` |
| Linux (x64) | `ShadowSecurityScanner-linux-amd64` |
| Linux (ARM64) | `ShadowSecurityScanner-linux-arm64` |

No installer required.
- **Windows:** runs in its own window via WebView2 (preinstalled on Win 11 & current Win 10).
- **macOS:** open the `.dmg`, drag to Applications; first launch right-click → Open.
- **Linux:** needs `libwebkit2gtk-4.1` & `libgtk-3`; `chmod +x` then run.

## What it does

- **Exploit-aware prioritisation** — every finding carries its **EPSS** score and a
  **CISA KEV** "known-exploited" flag, sorted KEV → EPSS → severity.
- **Service & OS fingerprinting** — HTTP, TLS, SSH, FTP, SMTP, POP3, IMAP, DNS, SMB/NetBIOS,
  NFS, LDAP, SNMP and more, including unauthenticated Windows version detection via the
  SMB2 NTLM challenge.
- **Active web probes** — thousands of CGI / web-app checks with soft-404 calibration to
  limit false positives.
- **Scan diffing** — what's new, regressed or resolved between scans.
- **Live audit catalog** — 6,000+ CVEs and checks, refreshed daily (CISA KEV, Nuclei,
  curated advisories), enriched with CVSS/CWE (NVD) and EPSS.
- **Reporting** — PDF, HTML, SARIF (GitHub code scanning), XML and CSV.

## Built with

Go · React · [Wails](https://wails.io/) · SQLite (no CGO) — a single native desktop binary.

## Legal & ethical use

For **authorized security testing only** — scan systems you own or are explicitly permitted
to assess. Denial-of-service tests are intentionally excluded.

## Source & license

Source is maintained privately; release binaries are published in this repository.
See the [website](https://andriigordiienko.github.io/ShadowSecurityScanner-site/) for details.
