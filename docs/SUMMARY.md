# CM3035 Podcast Project — Work in Progress Summary

## What Was Built

A podcast hosting system on GitHub using Releases for audio storage and RSS feeds for podcast app subscriptions.

**Repository:** https://github.com/mnaumann79/UOL_Podcasts (public)

---

## Current State

### Scripts Created/Modified

- `generate_podcast_rss.py` — Generates podcast RSS feeds. Supports two hosting modes:
  - `--base-url` — Nextcloud/self-hosted URLs
  - `--repo owner/repo --tag tag` — GitHub Releases URLs
- `generate_episodes_json.py` — Scaffolds episode metadata. `--course` flag creates a subfolder for the course.
- `start_podcast.sh` / `start_podcast.bat` — Scaffolds a new course folder.

### CM3035 Course

**Location:** `D:/Projects/podcasts/cm3035/`

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

**Published:** Tag `cm3035/v1` pushed, GitHub Release created at:
https://github.com/mnaumann79/UOL_Podcasts/releases/tag/cm3035/v1

---

## Known Issue: Temporary URLs

### Problem
GitHub Releases download URLs are **signed temporary URLs** that expire (typically within hours). Podcast apps store the episode URLs at subscription time — when the signed URL expires, episodes become unavailable ("temporarily unavailable" error).

Additionally, the `Content-Disposition: attachment` header forces a download instead of streaming.

### Why the Current Setup Doesn't Work Reliably
- GitHub Releases are designed for **downloadable binaries**, not streaming media
- Signed URLs expire and break podcast subscriptions
- No CDN URL support for permanent, stable streaming URLs

---

## Next Step: GitHub Pages (TODO)

The proper solution is to serve both audio files and RSS feeds via **GitHub Pages**, which provides permanent CDN URLs.

### What Needs to Be Done

1. **Enable GitHub Pages** on `UOL_Podcasts` repository, source set to `main` branch

2. **Organize files** in the repo as:
   ```
   UOL_Podcasts/
   ├── cm3035/
   │   ├── 1.Scaling.Django.from.TCP.to.ORM.mp3
   │   ├── 2.Django.ORM.Performance.mp3
   │   ├── ...
   │   ├── artwork.png
   │   └── podcast.rss
   └── index.html (redirect or listing page)
   ```

3. **Update RSS generation** to use GitHub Pages base URL:
   ```
   https://mnaumann79.github.io/UOL_Podcasts/cm3035/podcast.rss
   ```

4. **Update CLAUDE.md** with the GitHub Pages workflow

### Why GitHub Pages Works for Podcasts
- Permanent, stable CDN URLs (no signed tokens)
- Proper `Content-Disposition: inline` headers for streaming
- Free hosting via GitHub's CDN
- Works with all podcast apps

---

## Workflow for Publishing a New Episode (Current)

```bash
# 1. Add new MP3 to course folder, update episodes.json

# 2. Commit and push
git add cm3035/
git commit -m "Add episode 10 to CM3035"
git tag cm3035/v2
git push origin main cm3035/v2

# 3. Create release
gh release create cm3035/v2 --title "CM3035 v2"

# 4. Upload audio files as release assets
gh release upload cm3035/v2 cm3035/*.mp3 cm3035/*.m4a --clobber

# 5. Regenerate RSS with new filenames (GitHub sanitizes spaces to dots)
python generate_episodes_json.py --folder cm3035 --course cm3035
# Edit episodes.json with correct GitHub sanitized filenames

# 6. Generate and upload RSS
python generate_podcast_rss.py \
  --folder cm3035 \
  --repo mnaumann79/UOL_Podcasts \
  --tag cm3035/v2 \
  --title "CM3035: Advanced Web Development" \
  --description "..." \
  --output cm3035/podcast.rss

gh release upload cm3035/v2 cm3035/podcast.rss --clobber
```

---

## File Naming Note

GitHub Releases sanitizes filenames: **spaces become dots**. The `episodes.json` filenames must match the sanitized names in the release. Episodes 1-5 had spaces that became dots when uploaded as release assets.

Current `episodes.json` filenames (GitHub-sanitized):
```
1.Scaling.Django.from.TCP.to.ORM.mp3
2.Django.ORM.Performance.mp3
3.Django.Generic.Views.and.CSS.Specificity.m4a
4.Stateless.API.Architecture.with.Django.REST.m4a
5.Moving.rendering.logic.into.the.browser.m4a
6_Asynchronous_Django_with_Celery_and_Channels.m4a
7_From_SOAP_to_Automated_OpenAPI_Contracts.m4a
8_How_to_stop_silent_Django_exploits.m4a
9_Django_Deployment_from_Localhost_to_Production.m4a
```
