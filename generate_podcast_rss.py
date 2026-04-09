"""
Podcast RSS Generator
=====================
Generates an RSS feed from MP3/M4A files for subscription in any podcast app.

Two hosting modes:
  - Nextcloud:         --nextcloud-url + --nextcloud-course
  - GitHub Releases:    --repo + --tag

Optional: place an episodes.json next to your MP3s to add per-episode titles,
descriptions, and duration:

  [
    {
      "filename": "01-introduction.mp3",
      "title": "Introduction to the Module",
      "description": "Overview of course structure and objectives.",
      "duration_seconds": 3600
    }
  ]

If episodes.json is absent, the filename (without extension) is used as the title.

Optional: place artwork.png (or artwork.jpg) next to your MP3s for podcast artwork.
Apple Podcasts requires artwork for the feed to be playable.

Usage (Nextcloud):
    python generate_podcast_rss.py \
        --folder "d:/path/to/cm3035" \
        --nextcloud-url "https://nc.example.com/s/TOKEN" \
        --nextcloud-course "cm3035" \
        --feed-url "https://example.com/cm3035/podcast.rss" \
        --title "CM3035: Advanced Web Development" \
        --output "d:/path/to/cm3035/podcast.rss"

Usage (GitHub Releases):
    python generate_podcast_rss.py \
        --folder "d:/path/to/cm3035" \
        --repo "username/UOL_Podcasts" \
        --tag "cm3035/v1" \
        --title "CM3035: Advanced Web Development" \
        --output "d:/path/to/cm3035/podcast.rss"
"""

import argparse
import datetime
import html
import json
import re
from pathlib import Path
from urllib.parse import quote

GITHUB_RELEASES_URL = "https://github.com/{owner}/{repo}/releases/download/{tag}"


def natural_sort_key(path):
    """Sort key that handles leading numbers naturally (2 before 10)."""
    parts = re.split(r"(\d+)", path.name)
    return [int(p) if p.isdigit() else p.lower() for p in parts]


def parse_duration(seconds: int) -> str:
    """Convert seconds to HH:MM:SS format for itunes:duration."""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    if hours > 0:
        return f"{hours}:{minutes:02}:{secs:02}"
    return f"{minutes}:{secs:02}"


def load_episodes(path: Path) -> dict:
    """Load episodes.json if it exists. Returns dict keyed by filename.

    path can be a directory (looks for episodes.json inside) or a file path.
    """
    episodes_file = path / "episodes.json" if path.is_dir() else path
    if not episodes_file.exists():
        return {}
    with open(episodes_file, encoding="utf-8") as f:
        raw = json.load(f)
    return {ep["filename"]: ep for ep in raw}


def build_rss(
    folder_path: Path,
    title: str,
    description: str,
    url_pattern: str,
    feed_url: str,
    channel_link: str,
    episodes_path: Path | None = None,
) -> str:
    """Build a podcast RSS feed from MP3 files in the given folder.

    url_pattern: a format string with a {filename} placeholder, e.g.
        "https://nc.example.com/s/TOKEN/download?path=/cm3035&files={filename}"
        or "https://github.com/owner/repo/releases/download/v1/{filename}"
    episodes_path: optional path to episodes.json (defaults to folder_path)
    """

    audio_files = sorted(
        list(folder_path.glob("*.mp3")) + list(folder_path.glob("*.m4a")),
        key=natural_sort_key,
    )
    if not audio_files:
        raise ValueError(f"No MP3 or M4A files found in {folder_path}")

    episodes = load_episodes(episodes_path or folder_path)

    now = datetime.datetime.now(datetime.timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")
    pub_date = datetime.datetime.now(datetime.timezone.utc).strftime("%a, %d %b %Y %H:%M:%S +0000")

    # Check for artwork
    artwork_url = None
    for ext in ("png", "jpg", "jpeg"):
        artwork = folder_path / f"artwork.{ext}"
        if artwork.exists():
            artwork_url = html.escape(url_pattern.format(filename=quote(f"artwork.{ext}")))
            break

    items = []
    for audio in audio_files:
        file_url = url_pattern.format(filename=quote(audio.name))
        file_size = audio.stat().st_size
        episode_meta = episodes.get(audio.name, {})
        item_title = episode_meta.get("title") or audio.stem
        item_desc = episode_meta.get("description", "")
        duration_secs = episode_meta.get("duration_seconds")

        xml_url = html.escape(file_url)
        mime_type = "audio/mpeg" if audio.suffix == ".mp3" else "audio/x-m4a"
        duration_tag = f"      <itunes:duration>{parse_duration(duration_secs)}</itunes:duration>\n" if duration_secs else ""

        item = f"""    <item>
      <title>{html.escape(item_title)}</title>
      <description>{html.escape(item_desc)}</description>
      <link>{xml_url}</link>
      <guid isPermaLink="true">{xml_url}</guid>
      <enclosure url="{xml_url}" type="{mime_type}" length="{file_size}"/>
      <pubDate>{pub_date}</pubDate>
{duration_tag}    </item>"""
        items.append(item)

    artwork_tag = f'    <itunes:image href="{artwork_url}"/>\n' if artwork_url else ""
    author_tag = f"    <itunes:author>{html.escape(title)}</itunes:author>\n"

    rss = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>{html.escape(title)}</title>
    <link>{html.escape(channel_link)}</link>
    <description>{html.escape(description)}</description>
    <language>en-us</language>
    <lastBuildDate>{now}</lastBuildDate>
{author_tag}{artwork_tag}    <atom:link href="{feed_url}" rel="self" type="application/rss+xml"/>
{chr(10).join(items)}
  </channel>
</rss>"""
    return rss


def main():
    parser = argparse.ArgumentParser(
        description="Generate podcast RSS from a folder of MP3s. "
        "Use --nextcloud-url (with --nextcloud-course) or --repo+--tag (GitHub Releases)."
    )
    parser.add_argument("--folder", required=True, help="Path to folder containing MP3 files")
    parser.add_argument("--episodes", help="Path to episodes.json (defaults to --folder)")
    parser.add_argument("--nextcloud-url", help="Nextcloud public share URL base (e.g. https://nc.example.com/s/TOKEN)")
    parser.add_argument("--nextcloud-course", help="Course folder name on Nextcloud (used as path param)")
    parser.add_argument("--feed-url", help="Full URL where the RSS feed will be served")
    parser.add_argument("--repo", help="GitHub repo in owner/repo format (use with --tag)")
    parser.add_argument("--tag", help="GitHub release tag (use with --repo)")
    parser.add_argument("--title", default="Podcast", help="Podcast feed title")
    parser.add_argument("--description", default="Audio files", help="Podcast feed description")
    parser.add_argument("--output", default="podcast.rss", help="Output RSS file path")

    args = parser.parse_args()

    if bool(args.repo) != bool(args.tag):
        print("Error: both --repo and --tag must be provided together")
        return 1
    if args.nextcloud_url and not args.nextcloud_course:
        print("Error: --nextcloud-course is required when using --nextcloud-url")
        return 1
    if not args.nextcloud_url and not args.repo:
        print("Error: must provide either --nextcloud-url or --repo (with --tag)")
        return 1

    folder = Path(args.folder)
    if not folder.exists():
        print(f"Error: Folder not found: {folder}")
        return 1

    audio_files = sorted(folder.glob("*.mp3")) + sorted(folder.glob("*.m4a"))

    if args.nextcloud_url:
        # Build WebDAV URL with embedded share token for direct file access
        # Input: https://nextcloud.mnaumann.com/s/TOKEN
        # Output: https://TOKEN:@nextcloud.mnaumann.com/public.php/webdav/COURSE/FILENAME
        from urllib.parse import urlparse
        parsed = urlparse(args.nextcloud_url.rstrip("/"))
        token = parsed.path.rstrip("/").split("/")[-1]
        webdav_base = f"{parsed.scheme}://{token}:@{parsed.hostname}/public.php/webdav/{args.nextcloud_course}"
        url_pattern = f"{webdav_base}/{{filename}}"
        channel_link = args.nextcloud_url
        feed_url = args.feed_url or f"{webdav_base}/podcast.rss"
    else:
        owner, repo = args.repo.split("/", 1)
        base = GITHUB_RELEASES_URL.format(owner=owner, repo=repo, tag=args.tag)
        url_pattern = f"{base}/{{filename}}"
        channel_link = f"https://github.com/{owner}/{repo}/releases/tag/{args.tag}"
        feed_url = f"{base}/podcast.rss"

    episodes_path = Path(args.episodes) if args.episodes else None
    rss = build_rss(folder, args.title, args.description, url_pattern, feed_url, channel_link, episodes_path)
    Path(args.output).write_text(rss, encoding="utf-8")

    print(f"RSS feed written to: {args.output}")
    print(f"Found {len(audio_files)} audio files.")
    print()
    print(f"Subscribe in your podcast app at:")
    print(f"  {feed_url}")

    return 0


if __name__ == "__main__":
    exit(main())