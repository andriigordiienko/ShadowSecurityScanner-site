"""Keeps the site in step with the public releases and announces new ones.

- index.html JSON-LD softwareVersion  → latest release
- llms.txt "Latest release" line      → latest release + date
- /changelog/                         → every release with its notes
- sitemap.xml                         → lastmod for / and /changelog/
- outbox                              → one announcement per new release
"""
from __future__ import annotations

import re

from lib import (PUBLIC_REPO, ROOT, SITE, CONFIG, cta, enqueue_post, esc, github, load_state,
                 log, md_to_html, now, page, parse_ts, save_state, sitemap_upsert,
                 write_if_changed)

PLACEHOLDER = re.compile(r"^\s*Automated build of ", re.I)


def releases() -> list:
    rels = github(f"repos/{PUBLIC_REPO}/releases?per_page=100")
    rels = [r for r in rels if not r["draft"] and not r["prerelease"]
            and re.match(r"^v\d", r["tag_name"]) and r.get("published_at")]
    return sorted(rels, key=lambda r: r["published_at"], reverse=True)


def highlights(body: str, limit: int = 3) -> list:
    """First bullets of the "New" section (fall back to any bullets)."""
    new = re.search(r"###\s*New\s*\n(.*?)(?:\n###|\n---|\Z)", body or "", re.S)
    src = new.group(1) if new else (body or "")
    bullets = [re.sub(r"\s*\(`[^`]*`\)\s*$", "", b).strip()
               for b in re.findall(r"^[-*]\s+(.+)$", src, re.M)]
    return bullets[:limit]


def update_index(version: str) -> bool:
    p = ROOT / "index.html"
    s = p.read_text()
    s2 = re.sub(r'("softwareVersion":\s*")[^"]*(")', rf"\g<1>{version}\g<2>", s)
    return write_if_changed(p, s2)


def update_llms(version: str, date: str) -> bool:
    p = ROOT / "llms.txt"
    s = p.read_text()
    line = f"- **Latest release:** {version} ({date}) — changelog: {SITE}/changelog/"
    if re.search(r"^- \*\*Latest release:\*\*.*$", s, re.M):
        s2 = re.sub(r"^- \*\*Latest release:\*\*.*$", line, s, flags=re.M)
    else:
        # Right after the License line in "Key facts".
        s2 = re.sub(r"^(- \*\*License:\*\*.*)$", rf"\1\n{line}", s, count=1, flags=re.M)
    return write_if_changed(p, s2)


def render_changelog(rels: list) -> str:
    up = "../"
    sections = []
    for r in rels:
        date = r["published_at"][:10]
        tag = r["tag_name"]
        body = r.get("body") or ""
        if PLACEHOLDER.match(body) or not body.strip():
            notes = "<p>Build release — bug fixes, catalog and dependency updates.</p>"
        else:
            # Drop the download footer and the file/checksum sections: the
            # release page has them, and the changelog has its own CTA.
            body = re.split(r"\n---\s*\n", body)[0]
            body = re.sub(r"(?ms)^#{1,3}\s*(Download|Verifying[^\n]*|Checksums?[^\n]*)\s*\n.*?(?=^#{1,3}\s|\Z)", "", body)
            notes = md_to_html(body, h_offset=1)
        sections.append(f"""    <section id="{esc(tag)}">
      <h2>{esc(tag)} <span class="meta">· {date}</span></h2>
{notes}
      <p><a href="{esc(r['html_url'])}" rel="noreferrer">Release page &amp; downloads →</a></p>
    </section>""")
    latest = rels[0]
    body = f"""  <article class="article">
    <div class="article-head">
      <span class="eyebrow">Changelog</span>
      <h1>ShadowSecurityScanner changelog</h1>
      <p class="meta">Latest: {esc(latest['tag_name'])} · {latest['published_at'][:10]} · {len(rels)} releases</p>
    </div>
    <p>Every release of the free, open-source vulnerability scanner — new checks, fixes and
    performance work. Builds for Windows, macOS and Linux are attached to each release on
    <a href="https://github.com/{PUBLIC_REPO}/releases" rel="noreferrer">GitHub</a>.</p>
{chr(10).join(sections)}
{cta(up, "Get the latest build", "Free and open-source. Windows, macOS and Linux.")}
  </article>"""
    return page(
        path="changelog/",
        title="Changelog — ShadowSecurityScanner releases",
        description=f"Release history of ShadowSecurityScanner, the free open-source vulnerability "
                    f"scanner. Latest: {latest['tag_name']} ({latest['published_at'][:10]}).",
        body=body,
        breadcrumbs=[("Changelog", "changelog/")],
        og_type="website",
        jsonld=[{
            "@type": "SoftwareApplication",
            "name": "ShadowSecurityScanner",
            "applicationCategory": "SecurityApplication",
            "operatingSystem": "Windows, macOS, Linux",
            "softwareVersion": latest["tag_name"].lstrip("v"),
            "datePublished": latest["published_at"][:10],
            "releaseNotes": f"{SITE}/changelog/",
            "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"},
            "url": SITE + "/",
        }],
    )


def announce(state: dict, latest: dict) -> None:
    tag = latest["tag_name"]
    if state.get("announced_release") == tag:
        return
    age = (now() - parse_ts(latest["published_at"])).days
    if age > CONFIG["release_announce_max_age_days"]:
        log(f"{tag} is {age} days old — marking announced without posting")
        state["announced_release"] = tag
        return
    hl = highlights(latest.get("body") or "")
    hl_short = "; ".join(hl[:2])
    short = f"ShadowSecurityScanner {tag} is out — free, open-source vuln scanner with EPSS + CISA KEV prioritisation."
    if hl_short and len(short) + len(hl_short) + 6 <= 230:
        short += f"\n\nNew: {hl_short}"
    long = (f"ShadowSecurityScanner {tag} is out.\n\n"
            + ("What's new:\n" + "\n".join(f"• {h}" for h in hl) + "\n\n" if hl else "")
            + "Free, open-source network vulnerability scanner that ranks findings by real-world "
              "exploitability (FIRST.org EPSS + CISA KEV). Single desktop app for Windows, macOS "
              "and Linux — no cloud, no telemetry, MIT-licensed.\n\n"
            + f"Full changelog: {SITE}/changelog/#{tag}")
    enqueue_post(f"release-{tag}", url=latest["html_url"], title=f"ShadowSecurityScanner {tag}",
                 description=CONFIG["one_liner"], short=short, long=long)
    state["announced_release"] = tag


def main() -> bool:
    rels = releases()
    if not rels:
        log("no releases found")
        return False
    latest = rels[0]
    version, date = latest["tag_name"].lstrip("v"), latest["published_at"][:10]
    changed = False
    changed |= update_index(version)
    changed |= update_llms(version, date)
    changed |= write_if_changed(ROOT / "changelog" / "index.html", render_changelog(rels))
    if changed:
        sitemap_upsert([("", date, "weekly", "1.0"), ("changelog/", date, "weekly", "0.6")])
    state = load_state()
    announce(state, latest)
    save_state(state)
    log(f"release sync: latest {latest['tag_name']} ({date}), site changed: {changed}")
    return changed


if __name__ == "__main__":
    main()
