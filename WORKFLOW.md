# Podcast Workflow

## Architecture

- **Audio hosting:** Nextcloud (public share via WebDAV)
- **RSS hosting:** GitHub Pages (deployed via GitHub Actions on push)
- **Feed URL pattern:** `https://mnaumann79.github.io/UOL_Podcasts/<course>/podcast.rss`

## Prerequisites

- Python 3
- ffmpeg/ffprobe (for audio duration detection)
- git
- Nextcloud sync folder at the path specified in `config.json`

## Creating a New Course

### 1. Create the Nextcloud folder

Create a folder for the course (e.g., `cm3036`) inside the Nextcloud sync directory (`D:/NC_Data/Documents/Podcasts/`). Place the audio files (MP3/M4A) and `artwork.png` there.

### 2. Scaffold the course metadata

```bash
python generate_episodes_json.py --folder "D:/NC_Data/Documents/Podcasts/cm3036" --course cm3036
```

This creates `cm3036/episodes.json` with auto-generated titles from filenames. Edit it to fix titles and add descriptions.

### 3. Create the course config

Create `cm3036/course.json`:

```json
{
  "title": "CM3036: Course Title",
  "description": "Course description for the podcast feed."
}
```

### 4. Publish

```bash
python publish.py cm3036
```

This generates the RSS feed, commits, and pushes. GitHub Actions deploys the feed to Pages.

### 5. Subscribe

Add the feed URL to a podcast app:

```
https://mnaumann79.github.io/UOL_Podcasts/cm3036/podcast.rss
```

## Adding Episodes to an Existing Course

### 1. Add audio files

Drop the new MP3/M4A files into the Nextcloud sync folder for the course (`D:/NC_Data/Documents/Podcasts/cm3035/`).

### 2. Publish

```bash
python publish.py cm3035
```

The script automatically detects new files, adds them to `episodes.json` with titles and durations, regenerates the RSS, commits, and pushes.

### 3. Edit metadata (optional)

If you want to fix an auto-generated title or add a description, edit `cm3035/episodes.json` and run `publish.py` again.

## File Reference

| File | Purpose |
|------|---------|
| `config.json` | Nextcloud URL and sync folder path |
| `<course>/course.json` | Course title and description |
| `<course>/episodes.json` | Episode titles, descriptions, durations |
| `<course>/podcast.rss` | Generated RSS feed (do not edit by hand) |
| `publish.py` | One-command publish script |
| `generate_podcast_rss.py` | RSS generator (called by publish.py) |
| `generate_episodes_json.py` | Scaffolds episodes.json for a new course |
| `start_podcast.sh/.bat` | Scaffolds a new course folder |
| `.github/workflows/pages.yml` | GitHub Actions workflow for Pages deployment |
