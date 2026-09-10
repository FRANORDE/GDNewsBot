#!/usr/bin/env python3
"""
Dashword.net -> Discord webhook

Periodically checks the Dashword.net news page, finds articles that are
new since the last run, and posts them to a Discord channel via webhook.

Setup:
    pip install requests beautifulsoup4 python-dotenv
    Copy .env.example to .env and fill in DASHWORD_WEBHOOK_URL.

Usage:
    1. Run the script once to "initialize" the state
       (it won't post anything the first time, just saves what already exists).
    2. Schedule periodic execution, e.g. with cron every 15 minutes:
       */15 * * * * /usr/bin/python3 /path/to/dashword_to_discord.py
"""

import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

# ---- CONFIGURATION ----
WEBHOOK_URL = os.environ["DASHWORD_WEBHOOK_URL"]
DASHWORD_URL = "https://www.dashword.net/categories/news/"
STATE_FILE = Path(__file__).parent / "data" / "dashword_seen.jsonc"
USER_AGENT = "Mozilla/5.0 (compatible; DashwordDiscordBot/1.0)"

# Text sent BEFORE the embed to ping someone. Examples:
#   "@everyone"              -> ping everyone
#   "@here"                  -> ping only online users
#   "<@&123456789012345678>" -> ping a specific role (role ID)
# Leave empty in .env to ping no one.
PING_MESSAGE = os.environ.get("DASHWORD_PING_MESSAGE", "")

# Matches dates in the format "June 14, 2026" (as shown on the site)
DATE_PATTERN = re.compile(r"^[A-Z][a-z]+ \d{1,2}, \d{4}$")


def fetch_latest_posts():
    """Download the Dashword News page and extract articles with their real date."""
    resp = requests.get(DASHWORD_URL, headers={"User-Agent": USER_AGENT}, timeout=15)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    posts = {}

    # Each article has a link whose text is the date ("June 14, 2026") that
    # points to the article page itself: we use this to reliably identify
    # each post and its real date, regardless of where the links appear on
    # the page ("Featured" box, sidebar, etc.).
    for a in soup.find_all("a", href=True):
        text = a.get_text(strip=True)
        if not DATE_PATTERN.match(text):
            continue

        href = a["href"]
        url = href if href.startswith("http") else f"https://www.dashword.net{href}"
        url = url.split("#")[0]

        if "/posts/" not in url or url in posts:
            continue

        try:
            date = datetime.strptime(text, "%B %d, %Y")
        except ValueError:
            continue

        # The title is another link with the same href, but with text
        # different from the date (it usually appears earlier on the page).
        title = None
        for candidate in soup.find_all("a", href=href):
            cand_text = candidate.get_text(strip=True)
            if cand_text and not DATE_PATTERN.match(cand_text):
                title = cand_text
                break

        if title:
            posts[url] = {"title": title, "url": url, "date": date}

    # Explicitly sort from newest to oldest
    return sorted(posts.values(), key=lambda p: p["date"], reverse=True)


def fetch_post_details(url):
    """Open the article page and extract description and image (OG meta tags)."""
    try:
        resp = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=15)
        resp.raise_for_status()
    except requests.RequestException:
        return {"description": None, "image": None}

    soup = BeautifulSoup(resp.text, "html.parser")

    def meta(prop):
        tag = soup.find("meta", property=prop) or soup.find("meta", attrs={"name": prop})
        return tag["content"].strip() if tag and tag.get("content") else None

    return {
        "description": meta("og:description"),
        "image": meta("og:image"),
    }


STATE_FILE_COMMENT = (
    "// This is the DashWord news bot's tracking list — it stores which "
    "articles have already been posted to Discord.\n"
    "// Please don't edit or delete this file: doing so may cause old "
    "articles to be reposted, or new ones to be skipped.\n"
)


def load_seen():
    if STATE_FILE.exists():
        raw = STATE_FILE.read_text()
        # Strip comment lines (starting with //) before JSON parsing
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


def post_to_discord(post, details):
    embed = {
        "title": post["title"],
        "url": post["url"],
        "color": 0x0067EE,  # Dashword brand color
        "footer": {"text": "Dashword.net"},
    }

    if details.get("description"):
        embed["description"] = details["description"]

    if details.get("image"):
        # Normalize relative URLs (e.g. /assets/img/xxx.webp)
        image_url = details["image"]
        if image_url.startswith("/"):
            image_url = f"https://www.dashword.net{image_url}"
        embed["image"] = {"url": image_url}

    payload = {
        "username": "Dashword News",
        "content": PING_MESSAGE if PING_MESSAGE else None,
        "embeds": [embed],
    }
    resp = requests.post(WEBHOOK_URL, json=payload, timeout=15)
    resp.raise_for_status()


def main():
    seen = load_seen()
    posts = fetch_latest_posts()

    if not posts:
        print("No articles found: check the structure of the Dashword page.")
        sys.exit(1)

    first_run = len(seen) == 0
    new_posts = [p for p in posts if p["url"] not in seen]

    if first_run:
        # On the very first run we only save the state, without spamming
        # every existing article into the channel.
        print(f"First run: saving {len(posts)} articles as already seen.")
    else:
        # new_posts is already sorted from newest to oldest
        for post in new_posts:
            print(f"New article: {post['title']}")
            details = fetch_post_details(post["url"])
            post_to_discord(post, details)

    for p in posts:
        seen.add(p["url"])
    save_seen(seen)


if __name__ == "__main__":
    main()
