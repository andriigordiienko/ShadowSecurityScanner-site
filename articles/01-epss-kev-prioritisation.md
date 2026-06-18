---
title: "Why CVSS Isn't Enough: Prioritising Vulnerabilities with EPSS and CISA KEV"
published: false
description: "Severity tells you how bad a vulnerability is. EPSS and CISA KEV tell you how likely it is to be exploited. Here's how to combine them into a real fix-first order."
tags: security, cybersecurity, devops, opensource
canonical_url:
---

If you've ever run a vulnerability scan, you know the feeling: hundreds of findings,
all sorted by CVSS, and no realistic way to fix them all. So you start at the top with
the 9.8s and work down. The problem? **CVSS measures impact, not likelihood.** A
critical-severity bug that nobody is exploiting can quietly outrank a medium-severity
bug that attackers are actively weaponising right now.

Two freely available data sources fix this: **EPSS** and the **CISA KEV** catalog.

## EPSS — the Exploit Prediction Scoring System

[EPSS](https://www.first.org/epss/), maintained by FIRST.org, is a model that outputs a
score between 0 and 1 estimating the probability a given CVE will be **exploited in the
wild within the next 30 days**. It's recalculated daily from real-world signals.

- EPSS **0.97** → almost certainly going to be attacked soon.
- EPSS **0.02** → very unlikely, even if the CVSS is high.

Because it updates daily, a CVE that looks quiet today can spike the moment a public
exploit drops.

## CISA KEV — Known Exploited Vulnerabilities

The [CISA KEV catalog](https://www.cisa.gov/known-exploited-vulnerabilities-catalog) is
an authoritative list of CVEs **confirmed to be actively exploited**. If something is in
KEV, it isn't theoretical — it's being used by attackers in the real world, and it
belongs at the very top of your queue regardless of its EPSS or CVSS.

## CVSS vs EPSS: two different axes

Think of it as:

- **CVSS = impact** — how bad it is *if* exploited.
- **EPSS = likelihood** — how probable exploitation actually is.

You need both. The strongest fix-first order combines all three signals:

1. **KEV first** — confirmed active exploitation.
2. **then EPSS** — highest exploit probability.
3. **then severity** — CVSS as the tie-breaker.

## A worked example

Say a scan returns four findings. Sorting by CVSS alone puts the two 9.8s on top — but
that's not where the real risk lives:

| Finding | CVSS | EPSS | KEV? | Fix-first rank |
|---|---|---|---|---|
| SMBv1 RCE (MS17-010) | 9.3 | 0.97 | Yes | **1** |
| OpenSSH regreSSHion | 8.1 | 0.92 | Yes | **2** |
| Obscure parser bug | 9.8 | 0.04 | No | 3 |
| Weak TLS ciphers | 5.3 | 0.03 | No | 4 |

The CVSS 9.8 parser bug drops below two lower-severity issues because almost nobody is
exploiting it, while the KEV-flagged SMBv1 and OpenSSH bugs are being actively
weaponised. That re-ordering *is* the point.

## Operationalising it

- Treat **everything in KEV** as "patch now".
- Pick an **EPSS threshold** that matches your capacity — many teams use ≥ 0.1 (a 10%+
  chance in 30 days) as "act soon".
- **Re-pull EPSS regularly** — it's a moving target.
- Don't drop CVSS entirely; use it to break ties between similarly-likely findings.

## Doing it without spreadsheets

Stitching EPSS and KEV onto scanner output by hand gets old fast. I ended up building it
into an open-source scanner — [ShadowSecurityScanner](https://andriigordiienko.github.io/ShadowSecurityScanner-site/) —
which folds EPSS and KEV onto every finding automatically and sorts by that
KEV → EPSS → severity order, including in its SARIF/PDF exports. It's free, MIT-licensed,
and runs as a single desktop app on Windows, macOS and Linux. But the *concept* is
tool-agnostic: however you scan, prioritising by exploitability instead of raw severity
is one of the highest-leverage changes you can make to a remediation workflow.

*Further reading: [What are EPSS and CISA KEV?](https://andriigordiienko.github.io/ShadowSecurityScanner-site/guides/what-is-epss-and-kev/)*
