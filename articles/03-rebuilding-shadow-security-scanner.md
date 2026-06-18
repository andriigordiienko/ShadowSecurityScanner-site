---
title: "Rebuilding a 2000s Vulnerability Scanner as a Modern Open-Source Tool"
published: false
description: "The original Shadow Security Scanner was a fast, Windows-native vuln scanner in the early 2000s. I rebuilt it from scratch in Go and React — here's what changed and what carried over."
tags: opensource, security, go, react
---

In the early 2000s, **Shadow Security Scanner (SSS)** from Safety-Lab was one of the
faster vulnerability scanners around. It had a reputation for actually *auditing*
services — proxies, LDAP, mail — rather than just checking whether a port was open, and
it shipped a catalog of 5,000+ audits with a daily-updated base. It was also very much a
product of its era: Windows-native, ActiveX-extensible, proprietary.

I wanted that capability in something that fits how we work today — cross-platform,
open-source, scriptable, and aware of *real-world exploitability*. So I rebuilt it from
scratch as **[ShadowSecurityScanner](https://andriigordiienko.github.io/ShadowSecurityScanner-site/)**.
Here's what that involved.

## The stack

- **Go** for the scanning engine — fast, statically compiled, great concurrency for
  network I/O, and a single binary with **no CGO**.
- **React** for the UI, wrapped with **[Wails](https://wails.io/)** so it runs as a
  native desktop window (WebView2 on Windows, WebKitGTK on Linux) instead of yet another
  Electron app.
- **SQLite** for local storage — the whole thing is self-contained, with no database
  server and no cloud.

The result is one file you download and run. No installer, no agents, no telemetry — scan
data never leaves your machine.

## What carried over from the original

The thing worth preserving was the **breadth of checks**. The legacy audit corpus was
re-derived into a modern catalog of 6,000+ entries, and the protocol coverage that gave
SSS its name lives on: HTTP/TLS, SSH, FTP, SMTP/POP3/IMAP, DNS, SMB/NetBIOS, NFS, LDAP,
SNMP and more — each with version-aware checks rather than a simple port knock.

One small piece of nostalgia that survived: unauthenticated **Windows version detection
via the SMB2 NTLM challenge**.

## What's new

The biggest change is **prioritisation**. A 2000s scanner handed you a flat list. A 2026
scanner shouldn't. Every finding now carries:

- its **EPSS** score (FIRST.org's 30-day exploit probability), and
- a **CISA KEV** flag if it's known to be actively exploited,

sorted KEV → EPSS → severity so you fix what attackers actually use first. The catalog
refreshes daily from a signed feed (CISA KEV, Nuclei templates, curated advisories) and
is enriched with CVSS/CWE from NVD.

Other modern niceties: **scan diffing** (what's new, regressed or resolved between scans)
and exports to **PDF, HTML, SARIF, XML and CSV** — SARIF specifically so results drop
into GitHub code scanning and CI.

## Lessons from the rewrite

- **Single-binary distribution is underrated.** "Download and run" removes an enormous
  amount of friction versus deploying a server stack.
- **Prioritisation > more checks.** Adding the 6,001st check helps less than telling a
  user which 5 of their existing findings to fix today.
- **Offline-first is a feature.** For a security tool especially, "your data stays here"
  is a selling point, not a limitation.

It's free and MIT-licensed — [the source is on GitHub](https://github.com/safetylab/ShadowSecurityScanner)
and the [site has the downloads and docs](https://andriigordiienko.github.io/ShadowSecurityScanner-site/).
Feedback on detection coverage and false positives is very welcome.
