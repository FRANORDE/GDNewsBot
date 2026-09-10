#!/usr/bin/env python3
"""
r/geometrydash -> Discord webhook

Periodically checks the r/geometrydash subreddit's official RSS feed,
finds posts that are new since the last run, and posts them to a
Discord channel via webhook.

Setup:
    pip install requests feedparser python-dotenv
    Copy .env.example to .env and fill in REDDIT_WEBHOOK_URL.

Usage:
    1. Run the script once to "initialize" the state
       (it won't post anything the first time, just saves what already exists).
    2. Schedule periodic execution (Task Scheduler on Windows, cron on Linux/Mac).

Note: Reddit's public RSS feeds are free and need no API key or login,
but Reddit does block requests without a proper User-Agent header —
that's why USER_AGENT below is set to something descriptive.
"""

import json
import os
import sys
from pathlib import Path

import feedparser
import requests
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

# ---- CONFIGURATION ----
WEBHOOK_URL = os.environ["REDDIT_WEBHOOK_URL"]
REDDIT_FEED_URL = "https://www.reddit.com/r/geometrydash/new/.rss"
STATE_FILE = Path(__file__).parent / "data" / "reddit_seen.jsonc"
USER_AGENT = os.environ.get(
    "REDDIT_USER_AGENT", "DashwordDiscordBot/1.0 (by /u/YOUR_REDDIT_USERNAME)"
)

# Text sent BEFORE the embed to ping someone. Examples:
#   "@everyone"              -> ping everyone
#   "@here"                  -> ping only online users
#   "<@&123456789012345678>" -> ping a specific role (role ID)
# Leave empty in .env to ping no one.
PING_MESSAGE = os.environ.get("REDDIT_PING_MESSAGE", "")

# Reddit's feed mixes news, memes, questions, showcases, etc. If you only
# want posts with certain flairs (e.g. "News", "Discussion"), list them
# here in lowercase. Leave empty to post everything.
ALLOWED_FLAIRS = []


def fetch_latest_posts():
    """Download the subreddit's RSS feed and return its entries, newest first."""
    resp = requests.get(REDDIT_FEED_URL, headers={"User-Agent": USER_AGENT}, timeout=15)
    resp.raise_for_status()

    feed = feedparser.parse(resp.content)
    posts = []

    for entry in feed.entries:
        url = entry.link.split("?")[0]
        title = entry.title
        author = entry.get("author", "unknown").replace("/u/", "")

        flair = None
        # Reddit's Atom feed doesn't expose flair directly, but the category
        # tag (when present) usually carries it.
        if entry.get("tags"):
            flair = entry.tags[0].get("term", "").lower()

        if ALLOWED_FLAIRS and (flair not in ALLOWED_FLAIRS):
            continue

        # entry.summary contains an HTML snippet, sometimes with a thumbnail
        thumbnail = None
        if entry.get("media_thumbnail"):
            thumbnail = entry.media_thumbnail[0].get("url")

        posts.append(
            {
                "title": title,
                "url": url,
                "author": author,
                "flair": flair,
                "thumbnail": thumbnail,
            }
        )

    # The feed is already newest-first, but we reverse-then-reverse
    # nothing here since Reddit already guarantees that order.
    return posts


STATE_FILE_COMMENT = (
    "// This is the r/geometrydash bot's tracking list — it stores which "
    "posts have already been posted to Discord.\n"
    "// Please don't edit or delete this file: doing so may cause old "
    "posts to be reposted, or new ones to be skipped.\n"
)


def load_seen():
    if STATE_FILE.exists():
        raw = STATE_FILE.read_text()
        json_only = "\n".join(
            line for line in raw.splitlines() if not line.strip().startswith("//")
        )
        if json_only.strip():
            return set(json.loads(json_only))
    return set()


def save_seen(seen_urls):
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    body = json.dumps(sorted(seen_urls), indent=2)
    STATE_FILE.write_text(STATE_FILE_COMMENT + body)


def post_to_discord(post):
    embed = {
        "title": post["title"],
        "url": post["url"],
        "color": 0xFF4500,  # Reddit brand color
        "footer": {"text": f"r/geometrydash · posted by u/{post['author']}"},
    }

    if post.get("flair"):
        embed["description"] = f"Flair: {post['flair']}"

    if post.get("thumbnail"):
        embed["image"] = {"url": post["thumbnail"]}

    payload = {
        "username": "r/geometrydash",
        "content": PING_MESSAGE if PING_MESSAGE else None,
        "embeds": [embed],
    }
    resp = requests.post(WEBHOOK_URL, json=payload, timeout=15)
    resp.raise_for_status()


def main():
    seen = load_seen()
    posts = fetch_latest_posts()

    if not posts:
        print("No posts found: check the subreddit feed URL and User-Agent.")
        sys.exit(1)

    first_run = len(seen) == 0
    new_posts = [p for p in posts if p["url"] not in seen]

    if first_run:
        print(f"First run: saving {len(posts)} posts as already seen.")
    else:
        for post in new_posts:
            print(f"New post: {post['title']}")
            post_to_discord(post)

    for p in posts:
        seen.add(p["url"])
    save_seen(seen)


if __name__ == "__main__":
    main()
