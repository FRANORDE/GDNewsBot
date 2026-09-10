#!/usr/bin/env python3
"""
Pointercrate Demon List -> Discord webhook

Periodically checks the top of Pointercrate's official Demon List API,
compares it against the last saved snapshot, and posts to Discord when:
  - a demon enters the tracked list for the first time
  - a demon's position changes (moved up or down)

Setup:
    pip install requests python-dotenv
    Copy .env.example to .env and fill in POINTERCRATE_WEBHOOK_URL.

Usage:
    1. Run the script once to "initialize" the state
       (it won't post anything the first time, just saves the current list).
    2. Schedule periodic execution (Task Scheduler on Windows, cron on Linux/Mac).

Note: Pointercrate's API is free and needs no API key. This script only
tracks the top LIST_LIMIT positions (max 100 per API request) — deeper
list changes (Extended/Legacy list) aren't covered without extra pagination.
"""

import json
import os
import re
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

# ---- CONFIGURATION ----
WEBHOOK_URL = os.environ["POINTERCRATE_WEBHOOK_URL"]
API_URL = "https://pointercrate.com/api/v2/demons/listed"
LIST_LIMIT = 100  # max allowed by the API in a single request (1-100)
STATE_FILE = Path(__file__).parent / "data" / "pointercrate_seen.jsonc"
USER_AGENT = "DashwordDiscordBot/1.0"

# Text sent BEFORE the embed to ping someone. Examples:
#   "@everyone"              -> ping everyone
#   "@here"                  -> ping only online users
#   "<@&123456789012345678>" -> ping a specific role (role ID)
# Leave empty in .env to ping no one.
PING_MESSAGE = os.environ.get("POINTERCRATE_PING_MESSAGE", "")

YOUTUBE_ID_PATTERN = re.compile(r"(?:v=|youtu\.be/)([\w-]{11})")


def fetch_current_list():
    """Download the top LIST_LIMIT demons, sorted by position."""
    resp = requests.get(
        API_URL,
        headers={"User-Agent": USER_AGENT, "Accept": "application/json"},
        params={"limit": LIST_LIMIT},
        timeout=15,
    )
    resp.raise_for_status()
    data = resp.json()

    demons = {}
    for d in data:
        demons[str(d["id"])] = {
            "id": d["id"],
            "position": d["position"],
            "name": d["name"],
            "publisher": (d.get("publisher") or {}).get("name", "Unknown"),
            "verifier": (d.get("verifier") or {}).get("name", "Unknown"),
            "video": d.get("video"),
        }
    return demons


def thumbnail_for(video_url):
    if not video_url:
        return None
    match = YOUTUBE_ID_PATTERN.search(video_url)
    if not match:
        return None
    return f"https://img.youtube.com/vi/{match.group(1)}/hqdefault.jpg"


STATE_FILE_COMMENT = (
    "// This is the Pointercrate bot's tracking list — it stores the last "
    "known position of each demon in the top list.\n"
    "// Please don't edit or delete this file: doing so may cause incorrect "
    "'entered/moved' messages on the next run.\n"
)


def load_previous():
    if STATE_FILE.exists():
        raw = STATE_FILE.read_text()
        json_only = "\n".join(
            line for line in raw.splitlines() if not line.strip().startswith("//")
        )
        if json_only.strip():
            return json.loads(json_only)
    return {}


def save_current(demons):
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    body = json.dumps(demons, indent=2)
    STATE_FILE.write_text(STATE_FILE_COMMENT + body)


def post_entry(demon):
    embed = {
        "title": f"{demon['name']} enters the list at #{demon['position']}",
        "url": demon["video"] or "https://pointercrate.com/demonlist/",
        "color": 0x2ECC71,  # green
        "description": f"Verified by **{demon['verifier']}**, published by **{demon['publisher']}**.",
        "footer": {"text": "Pointercrate Demon List"},
    }
    thumb = thumbnail_for(demon["video"])
    if thumb:
        embed["image"] = {"url": thumb}

    _send(embed)


def post_move(demon, old_position):
    direction = "up" if demon["position"] < old_position else "down"
    arrow = "⬆️" if direction == "up" else "⬇️"
    embed = {
        "title": f"{arrow} {demon['name']} moved {direction}: #{old_position} → #{demon['position']}",
        "url": demon["video"] or "https://pointercrate.com/demonlist/",
        "color": 0x3498DB if direction == "up" else 0xE67E22,
        "footer": {"text": "Pointercrate Demon List"},
    }
    thumb = thumbnail_for(demon["video"])
    if thumb:
        embed["image"] = {"url": thumb}

    _send(embed)


def _send(embed):
    payload = {
        "username": "Pointercrate",
        "content": PING_MESSAGE if PING_MESSAGE else None,
        "embeds": [embed],
    }
    resp = requests.post(WEBHOOK_URL, json=payload, timeout=15)
    resp.raise_for_status()


def main():
    previous = load_previous()
    current = fetch_current_list()

    if not current:
        print("No demons found: check the Pointercrate API response.")
        sys.exit(1)

    first_run = len(previous) == 0

    if first_run:
        print(f"First run: saving the current top {len(current)} demons as baseline.")
    else:
        for demon_id, demon in current.items():
            old = previous.get(demon_id)
            if old is None:
                print(f"New entry: {demon['name']} at #{demon['position']}")
                post_entry(demon)
            elif old["position"] != demon["position"]:
                print(f"Moved: {demon['name']} #{old['position']} -> #{demon['position']}")
                post_move(demon, old["position"])

    save_current(current)


if __name__ == "__main__":
    main()
