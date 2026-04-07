"""
Podcast RSS Generator for Nextcloud-shared MP3 folders
=======================================================
Drop MP3s or M4As into a publicly shared Nextcloud folder, then run this script
to generate an RSS feed you can subscribe to in any podcast app.

Optional: place an episodes.json next to your MP3s to add per-episode titles,
descriptions, and duration. Each entry maps a filename to its metadata:

  [
    {
      "filename": "django-module3-auth.mp3",
      "title": "Django Authentication Deep Dive",
      "description": "Covers session management, token auth, and permissions.",
      "duration_seconds": 3600
    }
  ]

If episodes.json is absent, the filename (without extension) is used as the title
and no description is added.

Optional: place artwork.png (or artwork.jpg) next to your MP3s to add podcast
artwork. Apple Podcasts requires artwork for the feed to be playable.

Usage:
    python generate_podcast_rss.py --folder "/path/to/audio" --base-url "https://nc.example.com/s/TOKEN/download"
    python generate_podcast_rss.py --folder "/path/to/audio" --base-url "https://nc.example.com/s/TOKEN/download" --title "My Podcast"

The --base-url should be the share URL from Nextcloud, without the filename.
For example, if your share link is:
  https://nc.example.com/s/abc123/download/myfile.mp3
Your --base-url would be:
  https://nc.example.com/s/abc123/download
"""

import argparse
import datetime
import html
import json
from pathlib import Path


def parse_duration(seconds: int) -> str:
    """Convert seconds to HH:MM:SS format for itunes:duration."""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    if hours > 0:
        return f"{hours}:{minutes:02}:{secs:02}"
    return f"{minutes}:{secs:02}"


def load_episodes(folder: Path) -> dict:
    """Load episodes.json if it exists. Returns dict keyed by filename."""
    episodes_file = folder / "episodes.json"
    if not episodes_file.exists():
        return {}
    with open(episodes_file, encoding="utf-8") as f:
        raw = json.load(f)
    return {ep["filename"]: ep for ep in raw}


def build_rss(folder_path: Path, base_url: str, title: str, description: str) -> str:
    """Build a podcast RSS feed from MP3 files in the given folder."""

    # Strip trailing slash from base_url
    base_url = base_url.rstrip("/")

    # Collect MP3s and M4As sorted by filename
    audio_files = sorted(folder_path.glob("*.mp3")) + sorted(folder_path.glob("*.m4a"))
    audio_files = sorted(audio_files)
    if not audio_files:
        raise ValueError(f"No MP3 or M4A files found in {folder_path}")

    episodes = load_episodes(folder_path)

    now = datetime.datetime.now(datetime.timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")
    pub_date = datetime.datetime.now(datetime.timezone.utc).strftime("%a, %d %b %Y %H:%M:%S +0000")

    channel_link = base_url.rstrip("/")
    feed_url = f"{channel_link}/podcast.rss"

    # Check for artwork (optional but recommended for Apple Podcasts)
    artwork_url = None
    for ext in ("png", "jpg", "jpeg"):
        artwork = folder_path / f"artwork.{ext}"
        if artwork.exists():
            artwork_url = f"{channel_link}/artwork.{ext}"
            break

    items = []
    for audio in audio_files:
        file_url = f"{base_url}/{html.escape(audio.name)}"
        file_size = audio.stat().st_size
        episode_meta = episodes.get(audio.name, {})
        item_title = episode_meta.get("title") or audio.stem
        item_desc = episode_meta.get("description", "")
        duration_secs = episode_meta.get("duration_seconds")

        guid = html.escape(file_url)
        mime_type = "audio/mpeg" if audio.suffix == ".mp3" else "audio/x-m4a"
        duration_tag = f"      <itunes:duration>{parse_duration(duration_secs)}</itunes:duration>\n" if duration_secs else ""

        item = f"""    <item>
      <title>{html.escape(item_title)}</title>
      <description>{html.escape(item_desc)}</description>
      <link>{file_url}</link>
      <guid isPermaLink="true">{guid}</guid>
      <enclosure url="{file_url}" type="{mime_type}" length="{file_size}"/>
      <pubDate>{pub_date}</pubDate>
{duration_tag}    </item>"""
        items.append(item)

    artwork_tag = f"    <itunes:image href=\"{artwork_url}\"/>\n" if artwork_url else ""
    author_tag = f"    <itunes:author>{html.escape(title)}</itunes:author>\n"

    rss = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd">
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
    parser = argparse.ArgumentParser(description="Generate podcast RSS from a folder of MP3s")
    parser.add_argument("--folder", required=True, help="Path to folder containing MP3 files")
    parser.add_argument("--base-url", required=True, help="Nextcloud share base URL (without trailing slash or filename)")
    parser.add_argument("--title", default="Podcast", help="Podcast feed title")
    parser.add_argument("--description", default="Audio files", help="Podcast feed description")
    parser.add_argument("--output", default="podcast.rss", help="Output RSS file path")

    args = parser.parse_args()

    folder = Path(args.folder)
    if not folder.exists():
        print(f"Error: Folder not found: {folder}")
        return 1

    audio_files = sorted(folder.glob("*.mp3")) + sorted(folder.glob("*.m4a"))
    rss = build_rss(folder, args.base_url, args.title, args.description)
    Path(args.output).write_text(rss, encoding="utf-8")
    print(f"RSS feed written to: {args.output}")
    print(f"Found {len(audio_files)} audio files.")
    print()
    print(f"Subscribe in your podcast app at:")
    print(f"  {args.base_url.rstrip('/')}/{args.output}")

    return 0


if __name__ == "__main__":
    exit(main())
