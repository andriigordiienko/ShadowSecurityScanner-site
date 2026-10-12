"""Finds new conversations worth joining and new mentions of the project.

Sources: Hacker News (Algolia), Stack Exchange, Reddit (RSS, best effort —
Reddit often blocks datacenter IPs) and GitHub issues/discussions. New hits
are appended to data/mentions.csv and listed in one issue per run. Replies
are always written by a human: automated posting on these sites breaks their
rules and gets accounts banned.
"""
from __future__ import annotations

import base64
import datetime as dt
import json
import os
import urllib.parse
import xml.etree.ElementTree as ET

from lib import (CONFIG, DATA, get_json, github, http, load_state, log, now, save_state, today,
                 warn)
from metrics import open_issue, upsert_csv

MENTIONS = DATA / "mentions.csv"
FIELDS = ["date", "id", "source", "kind", "title", "url"]


def hn(q: str, since: int) -> list:
    url = ("https://hn.algolia.com/api/v1/search_by_date?tags=(story,comment)&hitsPerPage=30&typoTolerance=false"
           f"&numericFilters=created_at_i>{since}&query={urllib.parse.quote(q)}")
    out = []
    for h in get_json(url)["hits"]:
        title = h.get("title") or h.get("story_title") or "(comment)"
        if h.get("comment_text"):
            title = f"comment on: {title}"
        out.append((f"hn-{h['objectID']}", "HN", title, f"https://news.ycombinator.com/item?id={h['objectID']}"))
    return out


def stackexchange(q: str, since: int) -> list:
    out = []
    for site in CONFIG["mentions"]["stackexchange_sites"]:
        url = ("https://api.stackexchange.com/2.3/search/excerpts?order=desc&sort=creation"
               f"&site={site}&fromdate={since}&q={urllib.parse.quote(q)}")
        for it in get_json(url).get("items", []):
            qid = it.get("question_id")
            out.append((f"se-{site}-{it.get('answer_id') or qid}", f"StackExchange/{site}",
                        it.get("title", "?"), f"https://{site}.stackexchange.com/q/{qid}"))
    return out


_reddit_token = None


def reddit(q: str, since: int) -> list:
    """Official API when REDDIT_CLIENT_ID/SECRET are set (app-only OAuth, a
    "script" app at reddit.com/prefs/apps); anonymous RSS otherwise."""
    global _reddit_token
    cid, secret = os.environ.get("REDDIT_CLIENT_ID"), os.environ.get("REDDIT_CLIENT_SECRET")
    if cid and secret:
        if not _reddit_token:
            basic = base64.b64encode(f"{cid}:{secret}".encode()).decode()
            _, raw, _ = http("POST", "https://www.reddit.com/api/v1/access_token",
                             headers={"Authorization": f"Basic {basic}"}, form={"grant_type": "client_credentials"})
            _reddit_token = json.loads(raw)["access_token"]
        res = get_json(f"https://oauth.reddit.com/search?sort=new&t=week&limit=50&q={urllib.parse.quote(q)}",
                       headers={"Authorization": f"Bearer {_reddit_token}"})
        return [(f"rd-t3_{c['data']['id']}", f"r/{c['data']['subreddit']}", c["data"]["title"],
                 "https://www.reddit.com" + c["data"]["permalink"])
                for c in res["data"]["children"] if c["data"]["created_utc"] >= since]
    _, raw, _ = http("GET", f"https://www.reddit.com/search.rss?sort=new&t=week&q={urllib.parse.quote(q)}")
    ns = {"a": "http://www.w3.org/2005/Atom"}
    out = []
    for e in ET.fromstring(raw).findall("a:entry", ns):
        updated = e.findtext("a:updated", "", ns)
        if updated and dt.datetime.fromisoformat(updated).timestamp() < since:
            continue
        cat = e.find("a:category", ns)
        sub = f"r/{cat.get('term')}" if cat is not None else "Reddit"
        out.append((f"rd-{e.findtext('a:id', '', ns)}", sub, e.findtext("a:title", "?", ns),
                    e.find("a:link", ns).get("href")))
    return out


def github_mentions(q: str, since: int) -> list:
    day = dt.datetime.fromtimestamp(since, dt.timezone.utc).date().isoformat()
    query = f"{q} created:>={day} -repo:safetylab/ShadowSecurityScanner -user:andriigordiienko"
    res = github("search/issues?per_page=30&q=" + urllib.parse.quote(query))
    return [(f"gh-{i['id']}", "GitHub", i["title"], i["html_url"]) for i in res.get("items", [])]


def main() -> int:
    state = load_state()
    since = int((now() - dt.timedelta(days=3)).timestamp())
    since = max(since, int(state.get("mentions_since", 0)))
    seen_list = state.get("mentions_seen", [])
    seen = set(seen_list)
    found = []
    failed = set()
    queries = [("brand", q) for q in CONFIG["mentions"]["brand"]] + \
              [("opportunity", q) for q in CONFIG["mentions"]["opportunity"]]
    for kind, q in queries:
        sources = [hn, stackexchange, reddit] + ([github_mentions] if kind == "brand" else [])
        for src in sources:
            if src.__name__ in failed:
                continue
            try:
                for mid, source, title, url in src(q, since):
                    if mid not in seen:
                        seen.add(mid)
                        seen_list.append(mid)
                        found.append({"date": today().isoformat(), "id": mid, "source": source,
                                      "kind": kind, "url": url,
                                      "title": title.strip()[:200].replace("[", "(").replace("]", ")")})
            except Exception as e:
                warn(f"mentions: {src.__name__} unavailable, skipped for this run: {e}")
                failed.add(src.__name__)
    if found:
        upsert_csv(MENTIONS, FIELDS, found, key="id")
        brand = [f for f in found if f["kind"] == "brand"]
        opp = [f for f in found if f["kind"] == "opportunity"]
        body = []
        if brand:
            body += ["### Упоминания проекта", ""] + [f"- **{f['source']}**: [{f['title']}]({f['url']})" for f in brand] + [""]
        if opp:
            body += ["### Обсуждения, где уместен полезный ответ", "",
                     "Отвечай по существу; инструмент упоминай, только если он реально решает вопрос, и не больше одной ссылки.", ""]
            body += [f"- [ ] **{f['source']}**: [{f['title']}]({f['url']})" for f in opp]
        open_issue(f"💬 Новые обсуждения: {len(found)} ({today()})", "\n".join(body), "marketing-mentions")
    state["mentions_since"] = int(now().timestamp())
    state["mentions_seen"] = seen_list[-3000:]
    save_state(state)
    log(f"mentions: {len(found)} new")
    return len(found)


if __name__ == "__main__":
    main()
