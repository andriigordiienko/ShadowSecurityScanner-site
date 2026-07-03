# Growth playbook — off-page SEO & AI visibility

The on-page work is done (custom domain, canonical/schema fixed, dedicated
`/nessus-alternative/` + `/openvas-alternative/` landing pages, FAQ schema).

Rankings for the **head terms** ("penetration testing tool", "network vulnerability
scanner") are won by domain authority (backlinks) + time — a new domain will not top
them on on-page alone. What *is* winnable now:

- **AI answers** (ChatGPT / Perplexity / Google AI Overviews) — driven by clear,
  structured, citeable content + mentions on Reddit/HN/GitHub. You already have the content.
- **Long-tail / commercial-intent queries** — "free Nessus alternative", "open source
  OpenVAS alternative", "EPSS KEV prioritisation tool", "offline vulnerability scanner".

Work this list **top-down** — items are ordered by ROI.

Canonical facts to paste everywhere (keep consistent — AI models reward consistency):
- Name: **ShadowSecurityScanner**
- Site: **https://shadowsecurityscanner.com/**
- Source: **https://github.com/safetylab/ShadowSecurityScanner**
- One-liner: *Free, open-source network vulnerability scanner & penetration testing tool
  that ranks findings by real-world exploitability (EPSS + CISA KEV). Single desktop app
  for Windows, macOS, Linux. No cloud, no telemetry. MIT-licensed.*

---

## 0. Do these first (30 min, highest ROI) — YOUR ACCOUNTS

- [ ] **Kill the duplicate.** The old GitHub Pages copy is still live at
      `https://andriigordiienko.github.io/ShadowSecurityScanner-site/` and duplicates the
      whole site. In the repo: **Settings → Pages → Source → None** (disable), and delete
      `.github/workflows/pages.yml`. (See §7 for detail.)
- [ ] **Google Search Console** — https://search.google.com/search-console → add property
      `shadowsecurityscanner.com` → verify (the `google-site-verification` meta tag is
      already in every page: `pavvQ_k1NvDGLWqNoWLqDAdIR3prVobNSzERwxsixx0`, so "HTML tag"
      verification should pass immediately) → **Sitemaps → submit** `sitemap.xml` →
      **URL Inspection → Request indexing** for the homepage and both alternative pages.
- [ ] **Bing Webmaster Tools** — https://www.bing.com/webmasters → add site → the
      `msvalidate.01` meta tag (`443E917CAA9649CC2AD1E681049AB99F`) is already present →
      submit `sitemap.xml`. (Bing also feeds DuckDuckGo **and** ChatGPT search.)
- [ ] **GitHub repo About** — set Website = `https://shadowsecurityscanner.com`; add topics:
      `penetration-testing` `vulnerability-scanner` `security-tools` `pentest` `epss`
      `cisa-kev` `cve` `network-security` `infosec` `sarif`.

---

## 1. Directories & listings (high-value, AI-cited backlinks)

Each of these ranks well itself and is frequently cited by AI assistants.

- [ ] **AlternativeTo** — https://alternativeto.net/ — add as alternative to *Nessus*,
      *OpenVAS*, *Nexpose*. (Description below.)
- [ ] **Product Hunt** — launch post (copy below).
- [ ] **SaaSHub**, **Slant.co** ("best free vulnerability scanners"), **StackShare**.
- [ ] **awesome-security**, **awesome-pentest**, **awesome-hacking** GitHub lists — open a
      PR adding one line + link.
- [ ] **Wikidata** entry once notable (feeds Knowledge Graph + AI).

**Directory description (≤ 200 chars):**
> Free, open-source network vulnerability scanner & penetration testing tool.
> Service/OS fingerprinting, EPSS + CISA KEV exploit prioritisation, scan diffing,
> SARIF/PDF reports. Windows/macOS/Linux. No cloud.

**Product Hunt tagline:**
> The open-source vulnerability scanner that ranks findings by what's actually exploited.

**Product Hunt first comment:**
> Hi PH 👋 I rebuilt the classic Shadow Security Scanner as a free, MIT-licensed,
> cross-platform desktop app. Most scanners hand you a flat CVE list sorted by CVSS —
> this one folds in FIRST.org EPSS (30-day exploit probability) and the CISA KEV catalog
> and sorts KEV → EPSS → severity, so you fix what attackers actually use first. One
> binary, fully offline, exports PDF/HTML/SARIF. Feedback very welcome.

---

## 2. Show HN

**Title:** Show HN: ShadowSecurityScanner – open-source vuln scanner that ranks by EPSS/KEV

**URL:** https://shadowsecurityscanner.com/

**Body:**
> I rebuilt the classic Shadow Security Scanner as a free, open-source, cross-platform
> desktop app (Go + React + Wails). It does port scanning, service/OS fingerprinting and
> thousands of network + web checks — but the part I care about most is prioritisation:
> every finding carries its FIRST.org EPSS exploit probability and a CISA KEV flag, sorted
> KEV → EPSS → severity, so you fix what attackers actually exploit first instead of
> chasing CVSS 9.8s nobody uses.
>
> Single binary, runs entirely offline (no cloud, no telemetry), exports PDF/HTML/SARIF/
> XML/CSV. MIT-licensed. Source: https://github.com/safetylab/ShadowSecurityScanner
>
> Feedback welcome — especially on the detection corpus and false-positive handling.

*Tip: post Tue–Thu ~09:00 ET. Reply to every comment in the first 2 hours.*

---

## 3. Reddit (r/netsec, r/cybersecurity, r/blueteam, r/homelab)

Read each subreddit's self-promotion rules first; lead with value, not a pitch.

**Title:** I built a free open-source vuln scanner that prioritises findings by EPSS + CISA KEV

**Body:**
> Frustrated that most scanners dump a flat CVE list sorted by CVSS, I built an
> open-source desktop scanner that folds in FIRST.org EPSS (30-day exploit probability)
> and the CISA KEV catalog so triage reflects real-world exploitation. Single binary,
> Windows/macOS/Linux, fully offline, MIT. Scan diffing + SARIF export too.
> Would love feedback from people doing regular internal scans / pentests.
> Site: https://shadowsecurityscanner.com/ — Source: https://github.com/safetylab/ShadowSecurityScanner

---

## 4. Answer engines & Q&A (direct AI-visibility signal)

- [ ] Answer relevant questions on **Stack Exchange (Security)**, **Quora**, **Reddit**
      threads asking "free Nessus alternative?" / "open source vulnerability scanner?" —
      give a genuinely useful answer, mention the tool where it fits, link once.
- [ ] Periodically ask ChatGPT / Gemini / Perplexity *"free open-source vulnerability
      scanner"* and *"Nessus alternative"* and track whether the tool surfaces. Improvement
      here tracks your mention count on Reddit/HN/GitHub.

---

## 5. Content roadmap (each page targets queries the homepage can't)

Already live: `/compare/`, `/nessus-alternative/`, `/openvas-alternative/`, 3 guides.
Next, in priority order:

- [ ] **"ShadowSecurityScanner tutorial"** — walkthrough with real screenshots/GIFs.
- [ ] **Replace CSS mock-ups with real screenshots** (Google Images traffic + trust + AI).
- [ ] **YouTube demo** (2–3 min). Title + description with target keywords; embed on-site
      with `VideoObject` schema. YouTube is the #2 search engine and heavily cited by AI.
- [ ] **"Nessus Essentials 16-IP limit / free alternatives"** deep-dive.
- [ ] **"EPSS vs CVSS"** standalone deep-dive (expand the existing guide).
- [ ] **"Best free vulnerability scanners 2026"** roundup (include competitors honestly —
      roundups earn links and rank).

---

## 6. Measure

- **GSC** weekly: impressions/clicks per query. Any query ranking page 2 with impressions
  → expand that page. This is your highest-signal feedback loop.
- **Core Web Vitals** at https://pagespeed.web.dev/ after any asset change.
- Track backlinks appearing (e.g. free tier of Ahrefs Webmaster Tools).

---

## 7. Detail: disabling the duplicate GitHub Pages site

The domain now points to your own server (Apache on 5.78.116.238), so the github.io copy
serves the same content on a second URL = duplicate content that splits ranking signals.
Two ways to resolve — **A is recommended**:

**A. Disable Pages (cleanest):**
1. Repo → **Settings → Pages → Build and deployment → Source → None**.
2. Delete `.github/workflows/pages.yml` (so it can't redeploy).
3. Optional: in GSC, use *Removals* to speed the old URLs out of the index.

**B. Keep Pages but consolidate signals:** push the committed canonical fix (already done
in the repo — all pages now declare `canonical` → shadowsecurityscanner.com). Once Pages
redeploys, github.io will tell Google the custom domain is authoritative. Only use this if
you have a reason to keep the github.io URL alive. You cannot point a `CNAME` at the custom
domain because DNS for it already resolves to your Apache server.

---

## 8. Reality check on the two head terms

"penetration testing tool" and "network vulnerability scanner" are dominated by Tenable,
Qualys, Rapid7, Intruder — domains with huge backlink profiles and 10–15+ yrs of history.
Expect: **long-tail + AI answers first (weeks–months), head terms only after sustained
authority (many months+ of backlinks/content)**. The fastest measurable wins are §0 + §1
+ §2/§3. Do those and re-check GSC in 2–4 weeks.
