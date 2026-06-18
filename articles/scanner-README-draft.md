<!--
  DRAFT README for the public repo  github.com/safetylab/ShadowSecurityScanner
  Copy everything BELOW this comment into that repo's README.md (replace or merge).
  Adjust build/usage commands if they differ from your actual scripts.
-->

# ShadowSecurityScanner

![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)
![Platforms](https://img.shields.io/badge/platforms-Windows%20%7C%20macOS%20%7C%20Linux-blue)
![GitHub release](https://img.shields.io/github/v/release/safetylab/ShadowSecurityScanner)
![GitHub stars](https://img.shields.io/github/stars/safetylab/ShadowSecurityScanner?style=social)

**ShadowSecurityScanner** is a free, open-source **penetration testing tool** and
**network vulnerability scanner**. It performs port scanning, service & OS fingerprinting,
and thousands of catalogued network and web checks, then ranks every finding by real-world
exploit probability — **EPSS** (FIRST.org) + **CISA KEV** — not just raw CVSS. A single
self-contained desktop app for **Windows, macOS and Linux**. No cloud, no agents, no telemetry.

- 🌐 **Website & docs:** https://andriigordiienko.github.io/ShadowSecurityScanner-site/
- 📊 **vs Nessus & OpenVAS:** https://andriigordiienko.github.io/ShadowSecurityScanner-site/compare/
- 📘 **Guides:** https://andriigordiienko.github.io/ShadowSecurityScanner-site/guides/
- ⬇️ **Download:** https://github.com/safetylab/ShadowSecurityScanner/releases/latest

---

## Why ShadowSecurityScanner?

Most scanners hand you a flat list of CVEs sorted by CVSS. ShadowSecurityScanner ranks
findings by how likely they are to actually be exploited:

- **Exploit-aware prioritisation** — every finding carries its **EPSS** score and a
  **CISA KEV** "known-exploited" flag, sorted KEV → EPSS → severity.
- **Service & OS fingerprinting** — across HTTP, TLS, SSH, FTP, SMTP, POP3, IMAP, DNS,
  SMB/NetBIOS, NFS, LDAP, SNMP and more — including unauthenticated Windows version
  detection via the SMB2 NTLM challenge.
- **Active web probes** — thousands of CGI / web-app checks (legacy SSS corpus + Nuclei
  templates), de-duplicated by path with soft-404 calibration to limit false positives.
- **Scan diffing** — see what's new, regressed or resolved between scans.
- **Live audit catalog** — 6,000+ CVEs and checks, refreshed daily from a signed feed
  (CISA KEV, Nuclei, curated advisories), enriched with CVSS/CWE (NVD) and EPSS.
- **Reporting** — export to PDF, HTML, SARIF (GitHub code scanning), XML and CSV.
- **Private by design** — single binary, all data stays on your machine, no telemetry.

## Download

Grab the latest build for your platform from the
[**Releases page**](https://github.com/safetylab/ShadowSecurityScanner/releases/latest):

| Platform | File |
|---|---|
| Windows (x64) | `ShadowSecurityScanner-windows-amd64.exe` |
| Windows (ARM64) | `ShadowSecurityScanner-windows-arm64.exe` |
| macOS (Apple Silicon) | `ShadowSecurityScanner-macos-arm64.dmg` |
| Linux (x64) | `ShadowSecurityScanner-linux-amd64` |
| Linux (ARM64) | `ShadowSecurityScanner-linux-arm64` |

No installer required. On Linux: `chmod +x` and run. On macOS: first launch, right-click → Open.

## Built with

Go · React · [Wails](https://wails.io/) · SQLite (no CGO) — compiles to a single
native desktop binary.

## Build from source

```bash
git clone https://github.com/safetylab/ShadowSecurityScanner.git
cd ShadowSecurityScanner
# Example — adjust to your actual build script:
scripts/build-desktop.sh windows amd64
```

## Legal & ethical use

ShadowSecurityScanner is for **authorized security testing only** — scan systems you own
or are explicitly permitted to assess. Denial-of-service tests are intentionally excluded.

## License

Released under the [MIT License](LICENSE).

## Heritage

A clean-room successor to the early-2000s Safety-Lab *Shadow Security Scanner* — the same
mission (broad, fast service auditing), rebuilt from scratch as a modern, cross-platform,
open-source tool with exploit-aware prioritisation.
