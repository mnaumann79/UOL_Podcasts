# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A lightweight podcast RSS generator that creates a subscribeable podcast feed from MP3/M4A files stored in a publicly shared Nextcloud folder. No server required — drop audio files in, generate RSS, subscribe in any podcast app.

## Scripts

- **generate_podcast_rss.py** — Generates podcast.rss from audio files in a folder
- **generate_episodes_json.py** — Scaffolds episodes.json for initial episode metadata

## Generate RSS Feed

```bash
python generate_podcast_rss.py --folder "/path/to/audio" --base-url "https://nc.example.com/s/TOKEN/download" --title "My Podcast"
```

Required arguments:
- `--folder` — Path to folder containing MP3/M4A files
- `--base-url` — Nextcloud share URL without trailing slash or filename

Optional:
- `--title` — Podcast title (default: "Podcast")
- `--description` — Podcast description (default: "Audio files")
- `--output` — Output RSS file path (default: podcast.rss)

## Optional Files

Place these alongside your audio files in the folder:

- **episodes.json** — Per-episode metadata (title, description, duration_seconds). Run `generate_episodes_json.py` first to scaffold it.
- **artwork.png** or **artwork.jpg** — Podcast artwork (required for Apple Podcasts)

## Architecture

Single-script design: `generate_podcast_rss.py` handles all RSS generation inline with no dependencies beyond the Python standard library.
