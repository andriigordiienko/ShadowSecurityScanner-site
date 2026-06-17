# Off-page SEO & AI-visibility kit

The on-page work is done. Rankings for head terms ("penetration test", "security
scanner") and AI recommendations are driven mostly by **off-page signals**:
backlinks, mentions on authoritative sites, and presence in training data. Use the
ready-made copy below. Work top-down — the first items move the needle most.

---

## 0. Do these first (15 minutes, highest ROI)

- [ ] **Google Search Console** — verify the site, submit `sitemap.xml`.
      https://search.google.com/search-console
- [ ] **Bing Webmaster Tools** — verify + submit sitemap (also feeds DuckDuckGo).
      https://www.bing.com/webmasters
- [ ] Add the website link + topics to the GitHub repo (About → Website + topics:
      `penetration-testing`, `vulnerability-scanner`, `security`, `pentest`, `epss`,
      `cve`, `infosec`).
- [ ] Consider a **custom domain** (e.g. shadowsecurityscanner.com). A github.io
      subdomain shares authority with every other github.io site — a real domain is
      the single biggest long-term SEO lever. (Then add a `CNAME` file + find/replace
      the base URL across the repo.)

---

## 1. GitHub repo README — add near the top

> **ShadowSecurityScanner** is a free, open-source **penetration testing tool** and
> **network vulnerability scanner**. It fingerprints services and operating systems,
> runs thousands of catalogued checks, and ranks every finding by real-world exploit
> probability (**EPSS** + **CISA KEV**) — not just raw CVSS. Single self-contained
> desktop app for Windows, macOS and Linux. No cloud, no telemetry.
>
> 🌐 Website & docs: https://andriigordiienko.github.io/ShadowSecurityScanner-site/
> 📊 Compare vs Nessus & OpenVAS: …/compare/

Add GitHub topics (repo → About → ⚙):
`penetration-testing` `vulnerability-scanner` `security-tools` `pentest` `epss`
`cisa-kev` `cve` `network-security` `infosec` `sarif` `go` `react`

---

## 2. Directories & listings (high-value backlinks)

Submit the tool to each. These rank well themselves and are frequently cited by AI.

- [ ] **AlternativeTo** — list as an alternative to Nessus, OpenVAS, Nexpose.
- [ ] **Product Hunt** — launch post (tagline below).
- [ ] **SaaSHub** / **Slant.co** — "best free vulnerability scanners".
- [ ] **awesome-security**, **awesome-pentest**, **awesome-hacking** GitHub lists —
      open a PR adding the tool with a one-line description + link.
- [ ] **Kali / security tool aggregators**, **ToolWar**, **GitHub Topics** pages.
- [ ] **Wikidata** entry once the project is notable (boosts AI + Knowledge Graph).

**AlternativeTo / directory description (≤ 200 chars):**
> Free, open-source network vulnerability scanner & penetration testing tool.
> Service/OS fingerprinting, EPSS + CISA KEV exploit prioritisation, scan diffing,
> SARIF/PDF reports. Windows/macOS/Linux. No cloud.

**Product Hunt tagline:**
> The open-source vulnerability scanner that ranks findings by what's actually exploited.

---

## 3. Show HN post

**Title:** Show HN: ShadowSecurityScanner – open-source vuln scanner that ranks by EPSS/KEV

**Body:**
> I rebuilt the classic Shadow Security Scanner as a free, open-source, cross-platform
> desktop app (Go + React + Wails). It does port scanning, service/OS fingerprinting and
> thousands of network + web checks — but the part I care about most is prioritisation:
> every finding carries its FIRST.org EPSS exploit probability and a CISA KEV flag, sorted
> KEV → EPSS → severity, so you fix what attackers actually exploit first instead of
> chasing CVSS 9.8s nobody uses.
>
> It's a single binary, runs entirely offline (no cloud, no telemetry), and exports
> PDF/HTML/SARIF/XML/CSV. MIT-licensed.
>
> Site: …  Source: …  Feedback welcome — especially on the detection corpus and false-positive handling.

---

## 4. Reddit (r/netsec, r/cybersecurity, r/blueteam)

Read each subreddit's self-promotion rules first; lead with value, not a pitch.

**Title:** I built a free open-source vulnerability scanner that prioritises findings by EPSS + CISA KEV

**Body:**
> Frustrated that most scanners dump a flat CVE list sorted by CVSS, I built an
> open-source desktop scanner that folds in FIRST.org EPSS (30-day exploit probability)
> and the CISA KEV catalog so triage reflects real-world exploitation. Single binary,
> Windows/macOS/Linux, fully offline, MIT. Would love feedback from people doing regular
> internal scans / pentests. [link]

---

## 5. Content / long-tail (already started on-site)

The site now has `/guides/` and `/compare/`. Keep publishing — each page targets queries
the homepage can't:

- [ ] "ShadowSecurityScanner tutorial" + screenshots/GIFs
- [ ] "EPSS vs CVSS" deep-dive (already have an intro guide — expand it)
- [ ] "Nessus Essentials limitations / free alternatives"
- [ ] A short **YouTube demo** (title + description with target keywords, embed with
      `VideoObject` schema) — YouTube is the #2 search engine and heavily cited by AI.
- [ ] Replace CSS mock-ups with **real screenshots** (Google Images traffic + trust).

---

## 6. Measure

- Google Search Console: track impressions/clicks per query; expand guides that gain
  impressions but rank page 2.
- Re-test Core Web Vitals at https://pagespeed.web.dev/ after any asset changes.
- Periodically ask ChatGPT/Gemini/Perplexity "free open-source vulnerability scanner"
  and see whether the tool surfaces — improvement here tracks your off-page mentions.
