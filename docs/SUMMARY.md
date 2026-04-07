# CM3035 Podcast Project — Summary

## What Was Built

A podcast hosting system on GitHub using GitHub Pages for audio streaming and RSS feeds for podcast app subscriptions.

**Repository:** https://github.com/mnaumann79/UOL_Podcasts (public)
**GitHub Pages:** https://mnaumann79.github.io/UOL_Podcasts/

---

## Current State: Working

The podcast is live and subscribable via:

```
https://mnaumann79.github.io/UOL_Podcasts/cm3035/podcast.rss
```

### Hosting: GitHub Pages

Audio files and the RSS feed are served directly from the repository via GitHub Pages, which provides:
- Permanent, stable CDN URLs (no signed tokens, no expiry)
- Proper streaming (no forced download)
- Works with all podcast apps

### Scripts

- `generate_podcast_rss.py` — Generates podcast RSS feeds. Supports two hosting modes:
  - `--base-url` — GitHub Pages / self-hosted URLs (current approach)
  - `--repo owner/repo --tag tag` — GitHub Releases URLs (deprecated, URLs expire)
- `generate_episodes_json.py` — Scaffolds episode metadata. `--course` flag creates a subfolder.
- `start_podcast.sh` / `start_podcast.bat` — Scaffolds a new course folder.

### CM3035 Course

**Location:** `cm3035/`

Contains 9 episodes:
1. Scaling Django from TCP to ORM (22:41)
2. Django ORM Performance (20:31)
3. Django Generic Views and CSS Specificity (20:12)
4. Stateless API Architecture with Django REST (19:45)
5. Moving rendering logic into the browser (20:47)
6. Asynchronous Django with Celery and Channels (19:23)
7. From SOAP to Automated OpenAPI Contracts (22:22)
8. How to Stop Silent Django Exploits (19:39)
9. Django Deployment from Localhost to Production (23:35)

---

## Issues Resolved

### 1. Expiring URLs (GitHub Releases)

**Problem:** GitHub Releases download URLs are signed temporary URLs that expire within hours. Podcast apps store episode URLs at subscription time, so episodes became unavailable after the URLs expired. Additionally, `Content-Disposition: attachment` forced downloads instead of streaming.

**Fix:** Switched to GitHub Pages. Audio files are committed to the repo and served via `mnaumann79.github.io`, which provides permanent URLs.

### 2. Missing `<itunes:duration>` on Episodes 1-5

**Problem:** `episodes.json` used GitHub-sanitized filenames (dots replacing spaces, e.g., `1.Scaling.Django.from.TCP.to.ORM.mp3`) but the actual files on disk used spaces (e.g., `1. Scaling Django from TCP to ORM.mp3`). The RSS generator looked up metadata by disk filename, so episodes 1-5 had no match and were missing duration tags.

**Fix:** Updated `episodes.json` filenames to match the actual disk filenames. All 9 episodes now have `<itunes:duration>` tags.

### 3. Missing `xmlns:atom` Namespace

**Problem:** The RSS feed used `<atom:link>` without declaring the atom namespace, making the XML technically invalid.

**Fix:** Added `xmlns:atom="http://www.w3.org/2005/Atom"` to the `<rss>` element in `generate_podcast_rss.py`.

### 4. Spaces in URLs

**Problem:** Filenames with spaces (episodes 1-5) produced broken URLs.

**Fix:** Added `urllib.parse.quote()` to URL-encode filenames in `generate_podcast_rss.py`.

---

## Workflow: Publish a New Course

```bash
# 1. Scaffold the course folder
./start_podcast.sh cm30xx "CM30XX: Course Title" /path/to/mp3s

# 2. Generate episode metadata
python generate_episodes_json.py --folder cm30xx --course cm30xx
# Edit cm30xx/episodes.json to add titles, descriptions, durations

# 3. Generate RSS feed
python generate_podcast_rss.py \
  --folder cm30xx \
  --base-url "https://mnaumann79.github.io/UOL_Podcasts/cm30xx" \
  --title "CM30XX: Course Title" \
  --description "Course description..." \
  --output cm30xx/podcast.rss

# 4. Commit and push (Pages deploys automatically)
git add cm30xx/
git commit -m "Add CM30XX"
git push origin master
```

Feed URL: `https://mnaumann79.github.io/UOL_Podcasts/cm30xx/podcast.rss`

## Workflow: Add Episodes to an Existing Course

```bash
# 1. Add new MP3/M4A files to the course folder

# 2. Update episodes.json with new episode metadata
#    (filenames must match the actual filenames on disk)

# 3. Regenerate RSS
python generate_podcast_rss.py \
  --folder cm3035 \
  --base-url "https://mnaumann79.github.io/UOL_Podcasts/cm3035" \
  --title "CM3035: Advanced Web Development" \
  --description "This module covers server-side web development..." \
  --output cm3035/podcast.rss

# 4. Commit and push
git add cm3035/
git commit -m "Add episode to CM3035"
git push origin master
```

---

## Important Notes

- **Filename convention:** `episodes.json` filenames must match the actual filenames on disk exactly. The RSS generator uses disk filenames for metadata lookup and URL generation.
- **URL encoding:** Filenames with spaces are automatically URL-encoded by the RSS generator.
- **Repo size:** Audio files are committed to git. The 9 CM3035 episodes total ~365 MB. GitHub repos have a soft limit of 1 GB and Pages sites have a 1 GB limit. This works for a few courses but may need an alternative (e.g., Git LFS or external hosting) if many courses are added.
- **GitHub Pages source:** Set to `master` branch, root `/`.
