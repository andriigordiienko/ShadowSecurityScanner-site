"""Daily metrics snapshot + weekly report issue.

GitHub keeps repository traffic for 14 days only, so the daily snapshot
archives it into CSV files here to build a long-term history:

  data/metrics.csv   stars, forks, watchers, downloads (total / latest / per OS)
  data/traffic.csv   repo views + clones per day        (needs METRICS_TOKEN)
  data/referrers.json top referrers, one 14-day window per snapshot date
  data/site.csv      site requests / page views / uniques (needs CF_API_TOKEN + CF_ZONE_ID)

METRICS_TOKEN: a PAT with read access to repository administration on
safetylab/ShadowSecurityScanner (the traffic API needs push-level access).
"""
from __future__ import annotations

import csv
import datetime as dt
import io
import os
import re

from lib import (DATA, PUBLIC_REPO, SITE, github, http, json, load_json, load_state, log, now,
                 save_json, today, warn)

METRICS = DATA / "metrics.csv"
TRAFFIC = DATA / "traffic.csv"
SITE_CSV = DATA / "site.csv"
REFERRERS = DATA / "referrers.json"


def read_csv(path) -> list:
    if not path.exists():
        return []
    return list(csv.DictReader(io.StringIO(path.read_text())))


def upsert_csv(path, fields: list, rows: list, key: str = "date") -> None:
    """Merges rows by key (newer wins) and rewrites the file sorted by key."""
    merged = {r[key]: r for r in read_csv(path)}
    for r in rows:
        merged[str(r[key])] = {k: r.get(k, "") for k in fields}
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=fields, lineterminator="\n")
    w.writeheader()
    for k in sorted(merged):
        w.writerow({f: merged[k].get(f, "") for f in fields})
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(buf.getvalue())


def platform(asset: str) -> str:
    a = asset.lower()
    return "windows" if "windows" in a else "macos" if "macos" in a or a.endswith(".dmg") else \
        "linux" if "linux" in a else "other"


def snapshot() -> None:
    repo = github(f"repos/{PUBLIC_REPO}")
    rels = [r for r in github(f"repos/{PUBLIC_REPO}/releases?per_page=100") if not r["draft"]]
    per_os = {"windows": 0, "macos": 0, "linux": 0, "other": 0}
    for r in rels:
        for a in r["assets"]:
            per_os[platform(a["name"])] += a["download_count"]
    versioned = sorted((r for r in rels if r["tag_name"].startswith("v")),
                       key=lambda r: r["published_at"] or "", reverse=True)
    latest = versioned[0] if versioned else {"tag_name": "", "assets": []}
    row = {
        "date": today().isoformat(), "stars": repo["stargazers_count"], "forks": repo["forks_count"],
        "watchers": repo["subscribers_count"], "downloads_total": sum(per_os.values()),
        "latest_tag": latest["tag_name"],
        "latest_downloads": sum(a["download_count"] for a in latest["assets"]),
        "dl_windows": per_os["windows"], "dl_macos": per_os["macos"], "dl_linux": per_os["linux"],
    }
    upsert_csv(METRICS, list(row), [row])
    log(f"metrics: {row}")

    if os.environ.get("METRICS_TOKEN"):
        try:
            views = github(f"repos/{PUBLIC_REPO}/traffic/views", "METRICS_TOKEN")["views"]
            clones = github(f"repos/{PUBLIC_REPO}/traffic/clones", "METRICS_TOKEN")["clones"]
            days = {}
            for v in views:
                days.setdefault(v["timestamp"][:10], {})["views"] = v["count"]
                days[v["timestamp"][:10]]["view_uniques"] = v["uniques"]
            for c in clones:
                days.setdefault(c["timestamp"][:10], {})["clones"] = c["count"]
                days[c["timestamp"][:10]]["clone_uniques"] = c["uniques"]
            # Today's bucket is still filling up; the next run rewrites it.
            upsert_csv(TRAFFIC, ["date", "views", "view_uniques", "clones", "clone_uniques"],
                       [{"date": d, **v} for d, v in days.items()])
            refs = load_json(REFERRERS, {})
            refs[today().isoformat()] = github(f"repos/{PUBLIC_REPO}/traffic/popular/referrers", "METRICS_TOKEN")
            save_json(REFERRERS, dict(sorted(refs.items())[-120:]))
        except Exception as e:
            warn(f"GitHub traffic unavailable (check METRICS_TOKEN): {e}")
    else:
        log("METRICS_TOKEN not set — skipping repo traffic")

    if os.environ.get("CF_API_TOKEN") and os.environ.get("CF_ZONE_ID"):
        try:
            site_snapshot()
        except Exception as e:
            warn(f"Cloudflare analytics unavailable: {e}")


def site_snapshot() -> None:
    since = (today() - dt.timedelta(days=8)).isoformat()
    q = """query($zone: String!, $since: Date!) { viewer { zones(filter: {zoneTag: $zone}) {
      httpRequests1dGroups(limit: 10, filter: {date_geq: $since}, orderBy: [date_ASC]) {
        dimensions { date } sum { requests pageViews } uniq { uniques } } } } }"""
    _, raw, _ = http("POST", "https://api.cloudflare.com/client/v4/graphql",
                     headers={"Authorization": f"Bearer {os.environ['CF_API_TOKEN']}"},
                     json_body={"query": q, "variables": {"zone": os.environ["CF_ZONE_ID"], "since": since}})
    res = json.loads(raw)
    if res.get("errors"):
        raise RuntimeError(res["errors"])
    groups = res["data"]["viewer"]["zones"][0]["httpRequests1dGroups"]
    upsert_csv(SITE_CSV, ["date", "requests", "page_views", "uniques"], [
        {"date": g["dimensions"]["date"], "requests": g["sum"]["requests"],
         "page_views": g["sum"]["pageViews"], "uniques": g["uniq"]["uniques"]} for g in groups])


# ── weekly report ───────────────────────────────────────────────────────────

def _int(v) -> int:
    try:
        return int(v)
    except (TypeError, ValueError):
        return 0


def window_sum(rows: list, field: str, start: dt.date, end: dt.date) -> int:
    return sum(_int(r.get(field)) for r in rows if start.isoformat() <= r["date"] <= end.isoformat())


def report() -> str:
    end = today() - dt.timedelta(days=1)
    start = end - dt.timedelta(days=6)
    prev_end, prev_start = start - dt.timedelta(days=1), start - dt.timedelta(days=7)
    m = read_csv(METRICS)
    cur = m[-1] if m else {}
    base = next((r for r in reversed(m) if r["date"] <= start.isoformat()), m[0] if m else {})

    def delta(field):
        d = _int(cur.get(field)) - _int(base.get(field))
        return f"{_int(cur.get(field))} ({'+' if d >= 0 else ''}{d})"

    lines = [f"## Неделя {start} — {end}", "",
             "| Метрика | Значение (Δ за неделю) |", "|---|---|",
             f"| ⭐ Звёзды | {delta('stars')} |",
             f"| ⬇️ Загрузки, всего | {delta('downloads_total')} |",
             f"| ⬇️ Windows / macOS / Linux | {delta('dl_windows')} / {delta('dl_macos')} / {delta('dl_linux')} |",
             f"| 🏷 Последний релиз | {cur.get('latest_tag', '?')}: {cur.get('latest_downloads', '?')} загрузок |",
             f"| 🍴 Форки / 👀 watchers | {delta('forks')} / {delta('watchers')} |"]
    t = read_csv(TRAFFIC)
    if t:
        v, pv = window_sum(t, "views", start, end), window_sum(t, "views", prev_start, prev_end)
        lines.append(f"| 📈 Просмотры репозитория | {v} (прошлая неделя: {pv}) |")
    s = read_csv(SITE_CSV)
    if s:
        v, pv = window_sum(s, "page_views", start, end), window_sum(s, "page_views", prev_start, prev_end)
        lines.append(f"| 🌐 Просмотры сайта (Cloudflare) | {v} (прошлая неделя: {pv}) |")
    refs = load_json(REFERRERS, {})
    if refs:
        latest = refs[max(refs)]
        lines += ["", "### Источники трафика в репозиторий (14 дней)", ""]
        lines += [f"- {r['referrer']}: {r['count']} просмотров, {r['uniques']} уникальных" for r in latest[:10]]

    sent = []
    for p in sorted((DATA / "sent").glob("*.json")):
        post = load_json(p, {})
        stamps = [d["at"][:10] for d in post.get("done", {}).values()]
        if stamps and max(stamps) >= start.isoformat():
            sent.append(post)
    queued = sorted((DATA / "outbox").glob("*.json"))
    lines += ["", "### Публикации", ""]
    for p in sent:
        refs_md = [f"[{c}]({d['ref']})" if d["ref"].startswith("http") else c for c, d in p["done"].items()]
        lines.append(f"- {p['title']} → {', '.join(refs_md)}")
    if not sent:
        lines.append("- за неделю ничего не опубликовано")
    if queued:
        lines.append(f"- в очереди: {', '.join(q.stem for q in queued)}")
    health = load_state().get("channels", {})
    bad = [f"{c}: {h['last_error']}" for c, h in health.items()
           if h.get("last_error") and h["last_error"][:10] >= h.get("last_ok", "")[:10]]
    if bad:
        lines += ["", "### ⚠️ Каналы с ошибками", ""] + [f"- {b}" for b in bad]

    mentions = read_csv(DATA / "mentions.csv")
    week = [r for r in mentions if r["date"] >= start.isoformat()]
    if week:
        lines += ["", f"### Упоминания и обсуждения ({len(week)})", ""]
        for r in week[:25]:
            lines.append(f"- [{r['kind']}] {r['source']}: [{r['title']}]({r['url']})")
    lines += ["", f"Сайт: {SITE}/ · История: `marketing/data/` · План: `marketing/README.md`"]
    return "\n".join(lines)


def open_issue(title: str, body: str, label: str) -> None:
    repo = os.environ.get("GITHUB_REPOSITORY")
    if not repo or not os.environ.get("GITHUB_TOKEN"):
        log(f"(no GITHUB_REPOSITORY/GITHUB_TOKEN — issue not created)\n# {title}\n{body}")
        return
    issue = github(f"repos/{repo}/issues", method="POST", body={"title": title, "body": body, "labels": [label]})
    log(f"opened {issue['html_url']}")


def weekly_report() -> None:
    body = report()
    (DATA / "report-latest.md").write_text(body + "\n")
    open_issue(f"📊 Маркетинг: отчёт за неделю до {today() - dt.timedelta(days=1)}", body, "marketing-report")


if __name__ == "__main__":
    import sys
    snapshot() if "report" not in sys.argv else weekly_report()
