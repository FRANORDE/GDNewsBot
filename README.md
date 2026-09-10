<h1>
  <img src="assets/gdnewsbotlogo.png" width="90" valign="middle" alt="GDNewsBot logo">
  GDNewsBot
</h1>

<p>
  <img src="https://img.shields.io/badge/python-3.10%2B-blue" alt="Python 3.10+">
  <img src="https://img.shields.io/github/last-commit/FRANORDE/GDNewsBot" alt="Last commit">
  <img src="https://img.shields.io/github/issues/FRANORDE/GDNewsBot" alt="Issues">
</p>

GDNewsBot is a set of open-source Discord webhook bots.

# Usage
GDNewsBot is used in Discord servers for receiving Geometry Dash news and community content from Pointercrate, Dashword, and the r/GeometryDash subreddit.
It can be run via the `init.bat` file.

## Features

- **Dashword.net** — posts new articles with title, description, and image, sorted by real publish date (not by page order, which isn't always reliable).
- **r/GeometryDash** — posts new subreddit threads via Reddit's free RSS feed, with optional flair filtering (e.g. only "Discussion" posts, skipping memes and other fluff).
- **Pointercrate Demon List** — tracks the official Demon List and posts when a level enters the top 100 or changes position, complete with a video thumbnail.

Shared across all three bots:
- Configurable Discord role/everyone/here pings per bot
- No duplicate posts — each bot tracks what it's already posted in a small local file
- No paid APIs or third-party services required
- One-command setup via `init.bat` (installs dependencies and initializes tracking state)
