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

# Features

- **GD News Bot (DashWord)** — posts new articles of Dashword.net with title, description, and image, sorted by real publish date (not by page order, which isn't always reliable).
- **GD Reddit Bot** — posts new subreddit threads via Reddit's free RSS feed, with optional flair filtering (e.g. only "Discussion" posts, skipping memes and other fluff).
- **GD News Bot (Pointercrate)** — tracks the official Demon List and posts when a level enters the top 100 or changes position, complete with a video thumbnail.

## Customization

- Custom Role and Member pinging
- Custom Webhooks
- Flair Filtering for GD Reddit Bot [BETA]

<h1>
  <img src="assets/carbon.png" width="500" valign="middle" alt="GDNewsBot logo">
</h1>


# Setup

## Step 1

Clone the repo using the options below:

### Using Git

```bash
git clone https://github.com/FRANORDE/GDNewsBot.git
cd GDNewsBot
```

### Using GitHub

Click on the Code button, then download as ZIP

## Step 2

Copy the `env.example` content, create a new file, name it `.env` and paste the content copied in `env.example`. Fill in your credentials.
