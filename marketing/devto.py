"""Publishes the next drafted article from articles/ to dev.to on a cadence.

Articles are numbered Markdown files with dev.to front matter
(articles/01-….md). Every `devto_every_days` days, on a Tuesday–Thursday,
the lowest-numbered unpublished one goes live with a footer linking back to
the site, and an announcement is queued for the social channels.

Secret: DEVTO_API_KEY (dev.to → Settings → Extensions → DEV Community API Keys).
"""
from __future__ import annotations

import os
import re

from lib import (CONFIG, PUBLIC_REPO, ROOT, SITE, dry_run, enqueue_post, http, json, load_state,
                 log, now, parse_ts, save_state)

FOOTER = (f"\n\n---\n\n*ShadowSecurityScanner is a free, open-source (MIT) network vulnerability scanner "
          f"for Windows, macOS and Linux that ranks findings by EPSS and CISA KEV. "
          f"[Website]({SITE}/) · [GitHub](https://github.com/{PUBLIC_REPO}) · "
          f"[Weekly KEV digest]({SITE}/kev/)*\n")


def front_matter(md: str) -> dict:
    m = re.match(r"^---\n(.*?)\n---\n", md, re.S)
    if not m:
        return {}
    return {k.strip(): v.strip().strip('"') for k, v in
            (line.split(":", 1) for line in m.group(1).splitlines() if ":" in line)}


def main(force: bool = False) -> bool:
    if not os.environ.get("DEVTO_API_KEY"):
        log("DEVTO_API_KEY not set — skipping dev.to")
        return False
    state = load_state()
    done = state.setdefault("devto", {})
    if not force:
        if now().weekday() not in (1, 2, 3):
            return False
        last = max((parse_ts(d["at"]) for d in done.values()), default=None)
        if last and (now() - last).days < CONFIG["devto_every_days"]:
            return False
    queue = [p for p in sorted((ROOT / "articles").glob("[0-9]*.md")) if p.name not in done]
    if not queue:
        log("dev.to: no unpublished articles left — draft a new one in articles/")
        return False
    path = queue[0]
    md = path.read_text()
    meta = front_matter(md)
    md = re.sub(r"^published:\s*false\s*$", "published: true", md, count=1, flags=re.M) + FOOTER
    if dry_run():
        log(f"[dry-run] would publish {path.name}: {meta.get('title')}")
        return False
    _, raw, _ = http("POST", "https://dev.to/api/articles", headers={"api-key": os.environ["DEVTO_API_KEY"]},
                     json_body={"article": {"body_markdown": md}})
    url = json.loads(raw)["url"]
    done[path.name] = {"at": now().isoformat(timespec="seconds"), "url": url}
    save_state(state)
    log(f"dev.to: published {path.name} → {url}")
    title = meta.get("title", path.stem)
    short = f"New article: {title}"
    if len(short) > 230:
        short = short[:229] + "…"
    enqueue_post(f"devto-{path.stem}", url=url, title=title, description=meta.get("description", ""),
                 short=short, long=f"{title}\n\n{meta.get('description', '')}")
    return False  # nothing on the site itself changed


if __name__ == "__main__":
    import sys
    main(force="--force" in sys.argv)
