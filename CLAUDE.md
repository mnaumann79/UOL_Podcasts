# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

UOL Podcasts — a multi-course podcast hosting setup using GitHub Releases for direct MP3 hosting. Each course (CM3035, CM3036, etc.) lives in its own subfolder. Audio files are served via GitHub Releases download URLs; the RSS feed is generated locally and included in each release.

## Scripts

- **generate_podcast_rss.py** — Generates podcast.rss from audio files
- **generate_episodes_json.py** — Scaffolds episodes.json for initial episode metadata
- **start_podcast.sh / start_podcast.bat** — Scaffolds a new course folder

## One-time Setup

```bash
gh repo create UOL_Podcasts --public
git clone https://github.com/mnaumann79/UOL_Podcasts.git
cd UOL_Podcasts
```

## Add a New Course

```bash
./start_podcast.sh cm3035 "CM3035: Advanced Web Development" /path/to/mp3s
```

Then edit `cm3035/episodes.json` to add titles, descriptions, and durations.

## Publish a Course

```bash
git add cm3035/
git commit -m "Add cm3035"
git tag cm3035/v1
git push origin main cm3035/v1
gh release create cm3035/v1 --title "CM3035 v1"
```

## Generate RSS Feed

```bash
python generate_podcast_rss.py \
  --folder "cm3035" \
  --repo "mnaumann79/UOL_Podcasts" \
  --tag "cm3035/v1" \
  --title "CM3035: Advanced Web Development" \
  --description "Module description..." \
  --output "cm3035/podcast.rss"
```

Then add `podcast.rss` to the GitHub Release as an asset, or serve it from another URL.

## Optional Files

- **episodes.json** — Per-episode metadata (title, description, duration_seconds). Run `generate_episodes_json.py` first to scaffold it.
- **artwork.png** or **artwork.jpg** — Podcast artwork (required for Apple Podcasts)

## Architecture

Single-script design: `generate_podcast_rss.py` handles all RSS generation inline with no dependencies beyond the Python standard library.
