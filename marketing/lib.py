"""Shared helpers for the marketing automation (stdlib only).

Everything here runs both on a GitHub-hosted runner (Python 3.12) and on a
developer Mac (Python 3.9), so no third-party packages and no 3.10+ syntax.
"""
from __future__ import annotations

import datetime as dt
import gzip
import html
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent  # the site root
MKT = ROOT / "marketing"
DATA = MKT / "data"
SITE = "https://shadowsecurityscanner.com"
PUBLIC_REPO = "safetylab/ShadowSecurityScanner"
UA = "ShadowSecurityScanner-marketing/1.0 (+https://shadowsecurityscanner.com/)"

CONFIG = json.loads((MKT / "config.json").read_text())


# ── logging ─────────────────────────────────────────────────────────────────

def log(msg: str) -> None:
    print(msg, file=sys.stderr, flush=True)


def warn(msg: str) -> None:
    # Rendered as an annotation on the Actions run page.
    prefix = "::warning::" if os.environ.get("GITHUB_ACTIONS") else "warning: "
    log(prefix + msg)


def dry_run() -> bool:
    return os.environ.get("DRY_RUN", "").lower() in ("1", "true", "yes")


# ── HTTP ────────────────────────────────────────────────────────────────────

class HTTPError(Exception):
    def __init__(self, status: int, url: str, body: str):
        super().__init__(f"HTTP {status} {url}: {body[:300]}")
        self.status = status
        self.body = body


def http(method: str, url: str, *, headers: dict | None = None, data: bytes | None = None,
         json_body=None, form: dict | None = None, timeout: int = 60):
    """Returns (status, body bytes, response headers). Raises HTTPError on >= 400."""
    hdrs = {"User-Agent": UA}
    if json_body is not None:
        data = json.dumps(json_body).encode()
        hdrs["Content-Type"] = "application/json"
    elif form is not None:
        data = urllib.parse.urlencode(form).encode()
        hdrs["Content-Type"] = "application/x-www-form-urlencoded"
    hdrs.update(headers or {})
    req = urllib.request.Request(url, data=data, method=method, headers=hdrs)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            body = r.read()
            if r.headers.get("Content-Encoding") == "gzip":  # Stack Exchange always gzips
                body = gzip.decompress(body)
            return r.status, body, dict(r.headers)
    except urllib.error.HTTPError as e:
        raise HTTPError(e.code, url, e.read().decode("utf-8", "replace")) from None


def get_json(url: str, headers: dict | None = None):
    return json.loads(http("GET", url, headers=headers)[1])


def github(path: str, token_env: str = "GITHUB_TOKEN", method: str = "GET", body=None):
    """Calls the GitHub REST API; anonymous when the token env var is unset."""
    headers = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
    token = os.environ.get(token_env) or os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    url = path if path.startswith("http") else f"https://api.github.com/{path.lstrip('/')}"
    status, raw, _ = http(method, url, headers=headers, json_body=body)
    return json.loads(raw) if raw else None


# ── state ───────────────────────────────────────────────────────────────────

def load_json(path: Path, default):
    try:
        return json.loads(path.read_text())
    except FileNotFoundError:
        return default


def save_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False, sort_keys=True) + "\n")


STATE_PATH = DATA / "state.json"


def load_state() -> dict:
    return load_json(STATE_PATH, {})


def save_state(state: dict) -> None:
    save_json(STATE_PATH, state)


def write_if_changed(path: Path, text: str) -> bool:
    """Writes only real changes so scheduled runs don't churn commits."""
    if path.exists() and path.read_text() == text:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    log(f"updated {path.relative_to(ROOT)}")
    return True


# ── time ────────────────────────────────────────────────────────────────────

def now() -> dt.datetime:
    # NOW=2026-10-12T13:00:00 pins the clock for tests and dry runs.
    fixed = os.environ.get("NOW")
    if fixed:
        return dt.datetime.fromisoformat(fixed).replace(tzinfo=dt.timezone.utc)
    return dt.datetime.now(dt.timezone.utc)


def today() -> dt.date:
    return now().date()


def parse_ts(s: str) -> dt.datetime:
    return dt.datetime.fromisoformat(s.replace("Z", "+00:00"))


# ── outbox ──────────────────────────────────────────────────────────────────

OUTBOX = DATA / "outbox"


def enqueue_post(post_id: str, *, url: str, title: str, short: str, long: str,
                 tags: list | None = None, description: str = "") -> bool:
    """Queues an announcement for post.py. Idempotent per post_id.

    short: ≤ 230 chars, no URL (X / Bluesky). long: ≤ 1200 chars, no URL
    (Mastodon / LinkedIn). The URL and hashtags are appended per channel.
    """
    sent = DATA / "sent" / f"{post_id}.json"
    path = OUTBOX / f"{post_id}.json"
    if path.exists() or sent.exists():
        return False
    if len(short) > 230:
        raise ValueError(f"{post_id}: short text is {len(short)} chars (max 230)")
    save_json(path, {
        "id": post_id, "created": now().isoformat(timespec="seconds"),
        "url": url, "title": title, "description": description or short,
        "short": short, "long": long, "tags": tags or CONFIG["hashtags"],
        "done": {}, "attempts": 0,
    })
    log(f"queued post {post_id}")
    return True


# ── HTML pages ──────────────────────────────────────────────────────────────

esc = html.escape


def page(*, path: str, title: str, description: str, body: str, breadcrumbs: list,
         jsonld: list, og_type: str = "article", header_link: tuple = ("Guides", "guides/")) -> str:
    """Renders a page in the site's layout. path is like "kev/2026-w41/"."""
    depth = path.strip("/").count("/") + 1 if path.strip("/") else 0
    up = "../" * depth
    url = f"{SITE}/{path}"
    crumbs = [("Home", "")] + breadcrumbs
    crumb_html = "<span>/</span>".join(
        esc(name) if i == len(crumbs) - 1 else f'<a href="{up}{p}">{esc(name)}</a>'
        for i, (name, p) in enumerate(crumbs))
    graph = jsonld + [{
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": name, "item": f"{SITE}/{p}"}
            for i, (name, p) in enumerate(crumbs)],
    }]
    ld = json.dumps({"@context": "https://schema.org", "@graph": graph}, indent=2, ensure_ascii=False)
    hl_label, hl_path = header_link
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <meta name="google-site-verification" content="pavvQ_k1NvDGLWqNoWLqDAdIR3prVobNSzERwxsixx0" />
  <meta name="msvalidate.01" content="443E917CAA9649CC2AD1E681049AB99F" />
  <title>{esc(title)}</title>
  <meta name="description" content="{esc(description)}" />
  <meta name="author" content="AndriiGordiienko" />
  <meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1" />
  <meta name="theme-color" content="#0a0e16" />
  <link rel="canonical" href="{url}" />
  <meta property="og:type" content="{og_type}" />
  <meta property="og:title" content="{esc(title)}" />
  <meta property="og:description" content="{esc(description)}" />
  <meta property="og:url" content="{url}" />
  <meta property="og:image" content="{SITE}/assets/og-image.png" />
  <meta name="twitter:card" content="summary_large_image" />
  <link rel="icon" href="{up}assets/logo.svg" type="image/svg+xml" />
  <link rel="stylesheet" href="{up}styles.css" />
  <script type="application/ld+json">
{ld}
  </script>
</head>
<body>
  <header class="site-header">
    <a class="brand" href="{up}" aria-label="ShadowSecurityScanner home">
      <img src="{up}assets/logo.svg" alt="" width="34" height="34" />
      <span>Shadow<strong>Security</strong>Scanner</span>
    </a>
    <div class="header-cta">
      <a class="btn btn-ghost" href="{up}{hl_path}">{esc(hl_label)}</a>
      <a class="btn btn-primary" href="{up}#download">Download</a>
    </div>
  </header>

  <nav class="breadcrumbs" aria-label="Breadcrumb">{crumb_html}</nav>

{body}

  <footer class="site-footer">
    <div class="foot-brand"><img src="{up}assets/logo.svg" alt="" width="28" height="28" /><span>ShadowSecurityScanner</span></div>
    <nav class="foot-nav">
      <a href="{up}">Home</a>
      <a href="{up}guides/">Guides</a>
      <a href="{up}kev/">KEV digest</a>
      <a href="{up}changelog/">Changelog</a>
      <a href="https://github.com/{PUBLIC_REPO}" target="_blank" rel="noreferrer">GitHub</a>
    </nav>
    <div class="foot-meta"><span>© {today().year} AndriiGordiienko · MIT License</span></div>
  </footer>
</body>
</html>
"""


def cta(up: str, heading: str, text: str) -> str:
    return f"""    <div class="cta-band">
      <h2 style="margin-top:0">{esc(heading)}</h2>
      <p>{esc(text)}</p>
      <a class="btn btn-primary btn-lg" href="{up}#download">Download ShadowSecurityScanner</a>
    </div>"""


_INLINE = [
    (re.compile(r"`([^`]+)`"), r"<code>\1</code>"),
    (re.compile(r"\*\*([^*]+)\*\*"), r"<strong>\1</strong>"),
    (re.compile(r"\[([^\]]+)\]\((https?://[^)\s]+)\)"), r'<a href="\2" rel="noreferrer">\1</a>'),
    (re.compile(r"(?<![\"'>])(https?://[^\s<)]+[^\s<).,])"), r'<a href="\1" rel="noreferrer">\1</a>'),
]


def md_inline(text: str) -> str:
    out = esc(text, quote=False)
    for rx, repl in _INLINE:
        out = rx.sub(repl, out)
    return out


def md_to_html(md: str, h_offset: int = 0) -> str:
    """Tiny Markdown subset used by release notes: headings, bullets, rules,
    paragraphs, fenced code, pipe tables, `code`, **bold**, [links](…) and
    bare URLs."""
    out, para, items, table, code = [], [], [], [], None

    def cells(row: str) -> list:
        return [c.strip() for c in row.strip().strip("|").split("|")]

    def flush():
        if para:
            out.append(f"<p>{md_inline(' '.join(para))}</p>")
            para.clear()
        if items:
            out.append("<ul>\n" + "\n".join(f"  <li>{md_inline(i)}</li>" for i in items) + "\n</ul>")
            items.clear()
        if table:
            head, rows = cells(table[0]), [cells(r) for r in table[1:]
                                            if not re.match(r"^\|?[\s:|-]+\|?$", r.strip())]
            out.append('<div class="table-wrap" style="margin:0 0 20px"><table class="cmp">\n<thead><tr>'
                       + "".join(f'<th scope="col">{md_inline(c)}</th>' for c in head) + "</tr></thead>\n<tbody>\n"
                       + "\n".join("<tr>" + "".join(f"<td>{md_inline(c)}</td>" for c in r) + "</tr>" for r in rows)
                       + "\n</tbody></table></div>")
            table.clear()

    for line in md.replace("\r\n", "\n").split("\n"):
        s = line.strip()
        if code is not None:
            if s.startswith("```"):
                out.append("<pre><code>" + esc("\n".join(code), quote=False) + "</code></pre>")
                code = None
            else:
                code.append(line)
            continue
        m = re.match(r"^(#{1,6})\s+(.*)$", s)
        if s.startswith("```"):
            flush()
            code = []
        elif s.startswith("|"):
            if para or items:
                flush()
            table.append(s)
        elif not s:
            flush()
        elif m:
            flush()
            lvl = min(6, len(m.group(1)) + h_offset)
            out.append(f"<h{lvl}>{md_inline(m.group(2))}</h{lvl}>")
        elif re.match(r"^(-{3,}|\*{3,})$", s):
            flush()
        elif re.match(r"^[-*+]\s+", s):
            if para or table:
                flush()
            items.append(re.sub(r"^[-*+]\s+", "", s))
        else:
            if items or table:
                flush()
            para.append(s)
    flush()
    return "\n".join(out)


# ── sitemap / llms.txt ──────────────────────────────────────────────────────

def sitemap_upsert(entries: list) -> bool:
    """entries: (path, lastmod 'YYYY-MM-DD', changefreq, priority). Updates the
    <lastmod> of existing URLs or inserts new <url> blocks before </urlset>."""
    p = ROOT / "sitemap.xml"
    xml = p.read_text()
    for path, lastmod, freq, prio in entries:
        loc = f"<loc>{SITE}/{path}</loc>"
        block_rx = re.compile(r"(<url>\s*" + re.escape(loc) + r"\s*<lastmod>)([^<]*)(</lastmod>)")
        if loc in xml:
            xml = block_rx.sub(lambda m: m.group(1) + lastmod + m.group(3), xml, count=1)
        else:
            block = (f"  <url>\n    {loc}\n    <lastmod>{lastmod}</lastmod>\n"
                     f"    <changefreq>{freq}</changefreq>\n    <priority>{prio}</priority>\n  </url>\n")
            xml = xml.replace("</urlset>", block + "</urlset>")
    return write_if_changed(p, xml)


def gh_output(**kv) -> None:
    out = os.environ.get("GITHUB_OUTPUT")
    if out:
        with open(out, "a") as f:
            for k, v in kv.items():
                f.write(f"{k}={v}\n")
