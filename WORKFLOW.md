# Podcast Workflow

## Architecture

- **Audio hosting:** GitHub Releases (supports HTTP Range requests for streaming)
- **RSS hosting:** GitHub Pages (deployed on push)
- **Feed URL pattern:** `https://mnaumann79.github.io/UOL_Podcasts/<course>/podcast.rss`

## Why GitHub Releases?

Nextcloud WebDAV returned `500` on HTTP Range requests, which broke streaming in Apple Podcasts and most podcast players. GitHub Releases handles Range requests natively and is free for public repositories.

## Prerequisites

- Python 3
- ffmpeg/ffprobe (for audio duration detection)
- git
- `gh` CLI (for creating releases and uploading assets)
- Audio files (MP3 or M4A) and `artwork.png` (1400×1400 minimum)

## Creating a New Course

### 1. Prepare audio files

Place the audio files (MP3/M4A) and `artwork.png` in a local folder (e.g. `D:/NC_Data/Documents/Podcasts/cm3036/` or `~/Downloads/cm3036/`).

> **Apple Podcasts requires artwork.** The feed will be rejected without an `itunes:image` tag.

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

### 4. Create a GitHub Release and upload files

```bash
gh release create cm3036/v1 --title "CM3036 v1" --notes "Initial release"
gh release upload cm3036/v1 D:/NC_Data/Documents/Podcasts/cm3036/*.mp3 D:/NC_Data/Documents/Podcasts/cm3036/*.m4a D:/NC_Data/Documents/Podcasts/cm3036/artwork.png
```

> **Note:** GitHub replaces spaces in filenames with dots (e.g. `1. Scaling.mp3` → `1.Scaling.mp3`). `generate_podcast_rss.py` handles this automatically in `--repo` mode.

### 5. Generate the RSS feed

```bash
python generate_podcast_rss.py \
  --folder "D:/NC_Data/Documents/Podcasts/cm3036" \
  --episodes "cm3036/episodes.json" \
  --repo "mnaumann79/UOL_Podcasts" \
  --tag "cm3036/v1" \
  --title "CM3036: Course Title" \
  --description "Course description..." \
  --feed-url "https://mnaumann79.github.io/UOL_Podcasts/cm3036/podcast.rss" \
  --output "cm3036/podcast.rss"
```

### 6. Commit and push

```bash
git add cm3036/
git commit -m "Add cm3036 podcast"
git push
```

GitHub Actions deploys the feed to Pages.

### 7. Subscribe

Add the feed URL to a podcast app:

```
https://mnaumann79.github.io/UOL_Podcasts/cm3036/podcast.rss
```

## Adding Episodes to an Existing Course

### 1. Add audio files locally

Drop the new MP3/M4A files into the local folder for the course.

### 2. Upload to the GitHub Release

```bash
gh release upload cm3035/v1 D:/NC_Data/Documents/Podcasts/cm3035/new_episode.m4a --clobber
```

### 3. Update `episodes.json`

Add the new episode entry with its title and duration. You can get the duration with:

```bash
ffprobe -v quiet -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 new_episode.m4a
```

Or edit `episodes.json` by hand.

### 4. Regenerate the RSS feed

```bash
python generate_podcast_rss.py \
  --folder "D:/NC_Data/Documents/Podcasts/cm3035" \
  --episodes "cm3035/episodes.json" \
  --repo "mnaumann79/UOL_Podcasts" \
  --tag "cm3035/v1" \
  --title "CM3035: Advanced Web Development" \
  --description "This module covers server-side web development..." \
  --feed-url "https://mnaumann79.github.io/UOL_Podcasts/cm3035/podcast.rss" \
  --output "cm3035/podcast.rss"
```

### 5. Commit and push

```bash
git add cm3035/
git commit -m "Add episode(s) to cm3035"
git push
```

## Important Notes

### M4A MIME Type

Apple Podcasts requires `audio/x-m4a` for M4A files. `generate_podcast_rss.py` uses this automatically.

### Artwork is Required

Apple Podcasts rejects feeds without `<itunes:image>`. Always include `artwork.png` (or `artwork.jpg`) in the release.

### `publish.py` Status

`publish.py` is currently configured for the old Nextcloud workflow. Until it is updated for GitHub Releases, use the manual steps above.

## File Reference

| File | Purpose |
|------|---------|
| `config.json` | Nextcloud URL and sync folder path *(legacy)* |
| `<course>/course.json` | Course title and description |
| `<course>/episodes.json` | Episode titles, descriptions, durations |
| `<course>/podcast.rss` | Generated RSS feed (do not edit by hand) |
| `<course>/artwork.png` | Podcast artwork (required for Apple Podcasts) |
| `publish.py` | One-command publish script *(Nextcloud-only, needs update)* |
| `generate_podcast_rss.py` | RSS generator — supports `--repo` + `--tag` for GitHub Releases |
| `generate_episodes_json.py` | Scaffolds episodes.json for a new course |
| `start_podcast.sh/.bat` | Scaffolds a new course folder |
| `.github/workflows/pages.yml` | GitHub Actions workflow for Pages deployment |
