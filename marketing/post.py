"""Sends queued announcements (marketing/data/outbox/*.json) to social channels.

A channel is active when its secrets are set; unset channels are skipped, so
channels can be switched on one at a time. Each post records which channels
it reached, a failed channel is retried on the next run (up to 3 runs), and
a finished post moves to marketing/data/sent/. Posts go out only inside the
configured UTC window (FORCE_POST=1 overrides); DRY_RUN=1 prints instead.

Secrets:
  Bluesky   BLUESKY_HANDLE, BLUESKY_APP_PASSWORD
  Mastodon  MASTODON_INSTANCE (e.g. https://infosec.exchange), MASTODON_TOKEN
  X         X_API_KEY, X_API_SECRET, X_ACCESS_TOKEN, X_ACCESS_SECRET
  LinkedIn  LINKEDIN_TOKEN, LINKEDIN_AUTHOR (urn:li:person:… or urn:li:organization:…)
"""
from __future__ import annotations

import base64
import datetime as dt
import hashlib
import hmac
import os
import re
import secrets
import urllib.parse

import json

from lib import (CONFIG, DATA, OUTBOX, ROOT, dry_run, http, load_json, load_state, log,
                 now, save_json, save_state, warn)

MAX_ATTEMPTS = 3
CHANNELS = {
    "bluesky": ("BLUESKY_HANDLE", "BLUESKY_APP_PASSWORD"),
    "mastodon": ("MASTODON_INSTANCE", "MASTODON_TOKEN"),
    "x": ("X_API_KEY", "X_API_SECRET", "X_ACCESS_TOKEN", "X_ACCESS_SECRET"),
    "linkedin": ("LINKEDIN_TOKEN", "LINKEDIN_AUTHOR"),
}


def env(name: str) -> str:
    return os.environ.get(name, "").strip()


def configured() -> list:
    return [c for c, keys in CHANNELS.items() if all(env(k) for k in keys)]


def hashtags(post: dict, n: int) -> str:
    return " ".join("#" + t for t in post["tags"][:n])


def fit(text: str, limit: int) -> str:
    return text if len(text) <= limit else text[:limit - 1].rstrip() + "…"


# ── X (OAuth 1.0a user context) ─────────────────────────────────────────────

def _q(s: str) -> str:
    return urllib.parse.quote(s, safe="~")


def oauth1(method: str, url: str) -> str:
    params = {
        "oauth_consumer_key": env("X_API_KEY"),
        "oauth_nonce": secrets.token_hex(16),
        "oauth_signature_method": "HMAC-SHA1",
        "oauth_timestamp": str(int(now().timestamp())),
        "oauth_token": env("X_ACCESS_TOKEN"),
        "oauth_version": "1.0",
    }
    # A JSON body is not part of the OAuth 1.0a signature base string.
    base = "&".join([method, _q(url), _q("&".join(f"{_q(k)}={_q(v)}" for k, v in sorted(params.items())))])
    key = f"{_q(env('X_API_SECRET'))}&{_q(env('X_ACCESS_SECRET'))}"
    params["oauth_signature"] = base64.b64encode(
        hmac.new(key.encode(), base.encode(), hashlib.sha1).digest()).decode()
    return "OAuth " + ", ".join(f'{_q(k)}="{_q(v)}"' for k, v in sorted(params.items()))


def post_x(post: dict) -> str:
    # t.co counts every URL as 23 characters.
    budget = 280 - 23 - 1
    text = post["short"]
    tags = hashtags(post, 2)
    if len(text) + 2 + len(tags) <= budget:
        text += "\n\n" + tags
    text = fit(text, budget) + "\n" + post["url"]
    url = "https://api.x.com/2/tweets"
    if dry_run():
        return f"[dry-run] {text!r}"
    _, raw, _ = http("POST", url, headers={"Authorization": oauth1("POST", url)}, json_body={"text": text})
    tid = json.loads(raw)["data"]["id"]
    return f"https://x.com/i/web/status/{tid}"


# ── Bluesky (AT Protocol) ───────────────────────────────────────────────────

def _facet(text_bytes_before: str, value: str, feature: dict) -> dict:
    start = len(text_bytes_before.encode())
    return {"index": {"byteStart": start, "byteEnd": start + len(value.encode())}, "features": [feature]}


def post_bluesky(post: dict) -> str:
    pds = "https://bsky.social/xrpc/"
    display = re.sub(r"^https?://(www\.)?", "", post["url"])
    display = display if len(display) <= 40 else display[:39] + "…"
    tags = post["tags"][:3]
    tag_str = " ".join("#" + t for t in tags)
    body = post["short"]
    if len(body) + len(display) + len(tag_str) + 4 > 300:
        tag_str, tags = "", []
    body = fit(body, 300 - len(display) - len(tag_str) - 4)
    text = f"{body}\n\n{display}" + (f"\n{tag_str}" if tag_str else "")
    facets = [_facet(f"{body}\n\n", display, {"$type": "app.bsky.richtext.facet#link", "uri": post["url"]})]
    offset = f"{body}\n\n{display}\n"
    for t in tags:
        facets.append(_facet(offset, "#" + t, {"$type": "app.bsky.richtext.facet#tag", "tag": t}))
        offset += f"#{t} "
    if dry_run():
        return f"[dry-run] {text!r}"
    _, raw, _ = http("POST", pds + "com.atproto.server.createSession",
                     json_body={"identifier": env("BLUESKY_HANDLE"), "password": env("BLUESKY_APP_PASSWORD")})
    sess = json.loads(raw)
    auth = {"Authorization": f"Bearer {sess['accessJwt']}"}
    external = {"uri": post["url"], "title": post["title"], "description": post["description"]}
    try:
        _, raw, _ = http("POST", pds + "com.atproto.repo.uploadBlob", data=(ROOT / "assets/og-image.png").read_bytes(),
                         headers={**auth, "Content-Type": "image/png"})
        external["thumb"] = json.loads(raw)["blob"]
    except Exception as e:  # a card without a thumbnail is still fine
        warn(f"bluesky thumbnail upload failed: {e}")
    record = {
        "$type": "app.bsky.feed.post", "text": text, "facets": facets, "langs": ["en"],
        "createdAt": now().isoformat().replace("+00:00", "Z"),
        "embed": {"$type": "app.bsky.embed.external", "external": external},
    }
    _, raw, _ = http("POST", pds + "com.atproto.repo.createRecord", headers=auth,
                     json_body={"repo": sess["did"], "collection": "app.bsky.feed.post", "record": record})
    rkey = json.loads(raw)["uri"].rsplit("/", 1)[-1]
    return f"https://bsky.app/profile/{sess['handle']}/post/{rkey}"


# ── Mastodon ────────────────────────────────────────────────────────────────

def post_mastodon(post: dict) -> str:
    tags = hashtags(post, 4)
    # Mastodon counts every URL as 23 characters.
    text = fit(post["long"], 500 - 23 - len(tags) - 4) + f"\n{post['url']}\n\n{tags}"
    if dry_run():
        return f"[dry-run] {text!r}"
    _, raw, _ = http("POST", env("MASTODON_INSTANCE").rstrip("/") + "/api/v1/statuses",
                     headers={"Authorization": f"Bearer {env('MASTODON_TOKEN')}",
                              "Idempotency-Key": post["id"]},
                     form={"status": text, "visibility": "public", "language": "en"})
    return json.loads(raw)["url"]


# ── LinkedIn ────────────────────────────────────────────────────────────────

def _li_escape(s: str) -> str:
    # LinkedIn "little text": these characters are markup unless escaped.
    # URLs are left intact (odd parts of the split) so links stay clickable.
    parts = re.split(r"(https?://\S+)", s)
    return "".join(p if i % 2 else re.sub(r"([\\|{}@\[\]()<>#*_~])", r"\\\1", p)
                   for i, p in enumerate(parts))


def linkedin_version() -> str:
    # Versions are monthly (YYYYMM) and supported for about a year; two months
    # back is always live. LINKEDIN_VERSION pins one explicitly.
    if env("LINKEDIN_VERSION"):
        return env("LINKEDIN_VERSION")
    d = now().date().replace(day=1)
    for _ in range(2):
        d = (d - dt.timedelta(days=1)).replace(day=1)
    return d.strftime("%Y%m")


def post_linkedin(post: dict) -> str:
    tags = " ".join("{hashtag|\\#|%s}" % t for t in post["tags"][:4])
    text = _li_escape(post["long"]) + f"\n\n{post['url']}\n\n" + tags
    if dry_run():
        return f"[dry-run] {text!r}"
    body = {
        "author": env("LINKEDIN_AUTHOR"), "commentary": text, "visibility": "PUBLIC",
        "distribution": {"feedDistribution": "MAIN_FEED", "targetEntities": [], "thirdPartyDistributionChannels": []},
        "content": {"article": {"source": post["url"], "title": post["title"][:200],
                                "description": post["description"][:250]}},
        "lifecycleState": "PUBLISHED", "isReshareDisabledByAuthor": False,
    }
    _, _, headers = http("POST", "https://api.linkedin.com/rest/posts", json_body=body, headers={
        "Authorization": f"Bearer {env('LINKEDIN_TOKEN')}", "LinkedIn-Version": linkedin_version(),
        "X-Restli-Protocol-Version": "2.0.0"})
    urn = {k.lower(): v for k, v in headers.items()}.get("x-restli-id", "")
    return f"https://www.linkedin.com/feed/update/{urn}/" if urn else "posted"


SENDERS = {"bluesky": post_bluesky, "mastodon": post_mastodon, "x": post_x, "linkedin": post_linkedin}


def in_window() -> bool:
    if env("FORCE_POST") or dry_run():
        return True
    t = now()
    lo, hi = CONFIG["post_window_utc"]
    if CONFIG.get("post_weekdays_only") and t.weekday() >= 5:
        return False
    return lo <= t.hour < hi


def main() -> int:
    posts = sorted(OUTBOX.glob("*.json"))
    if not posts:
        log("outbox empty")
        return 0
    channels = configured()
    if not channels:
        warn("no social channel secrets configured — posts stay queued")
        return 0
    if not in_window():
        log(f"outside the posting window — {len(posts)} post(s) stay queued")
        return 0
    state = load_state()
    health = state.setdefault("channels", {})
    sent = 0
    for path in posts:
        post = load_json(path, None)
        post["attempts"] = post.get("attempts", 0) + 1
        for ch in channels:
            if ch in post["done"]:
                continue
            try:
                ref = SENDERS[ch](post)
                log(f"{post['id']} → {ch}: {ref}")
                if dry_run():
                    continue
                post["done"][ch] = {"at": now().isoformat(timespec="seconds"), "ref": ref}
                health.setdefault(ch, {})["last_ok"] = now().isoformat(timespec="seconds")
                sent += 1
            except Exception as e:
                warn(f"{post['id']} → {ch} failed: {e}")
                post.setdefault("errors", {})[ch] = str(e)[:500]
                health.setdefault(ch, {})["last_error"] = f"{now():%Y-%m-%d} {str(e)[:200]}"
        if dry_run():
            continue
        finished = all(ch in post["done"] for ch in channels)
        if finished or post["attempts"] >= MAX_ATTEMPTS:
            save_json(DATA / "sent" / path.name, post)
            path.unlink()
        else:
            save_json(path, post)
    if not dry_run():
        save_state(state)
    log(f"posted {sent} message(s) via {', '.join(channels)}")
    return sent


if __name__ == "__main__":
    main()
