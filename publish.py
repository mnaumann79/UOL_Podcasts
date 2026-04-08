"""
Publish podcast episodes to GitHub Pages.

Drop new audio files into the Nextcloud sync folder, then run:

    python publish.py cm3035

This will:
  1. Detect new audio files not yet in episodes.json
  2. Add them with auto-generated titles and durations
  3. Regenerate the RSS feed (audio URLs point to Nextcloud)
  4. Commit and push to GitHub (triggers Pages deployment)

Requires: ffprobe (from ffmpeg) for audio duration detection.
"""

import json
import re
import subprocess
import sys
from pathlib import Path


def get_pages_base_url():
    """Derive GitHub Pages base URL from git remote."""
    result = subprocess.run(
        ["git", "remote", "get-url", "origin"],
        capture_output=True, text=True,
    )
    remote = result.stdout.strip()
    if remote.startswith("https://"):
        parts = remote.replace("https://github.com/", "").replace(".git", "").split("/")
    elif "git@github.com:" in remote:
        parts = remote.split(":")[-1].replace(".git", "").split("/")
    else:
        print(f"Error: unrecognized remote format: {remote}")
        sys.exit(1)
    owner, repo = parts[0], parts[1]
    return f"https://{owner}.github.io/{repo}"


def load_config():
    """Load config.json from project root."""
    script_dir = Path(__file__).parent.resolve()
    config_path = script_dir / "config.json"
    if not config_path.exists():
        print(f"Error: config.json not found at {config_path}")
        sys.exit(1)
    return json.loads(config_path.read_text(encoding="utf-8"))


def get_duration(filepath):
    """Get audio duration in seconds using ffprobe."""
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", str(filepath)],
            capture_output=True, text=True,
        )
        return int(float(result.stdout.strip()))
    except (ValueError, FileNotFoundError):
        return None


def slug_to_title(filename):
    """Convert a filename to a readable title."""
    name = Path(filename).stem
    parts = re.split(r"[-_.]+", name)
    num = parts[0] if parts else ""
    rest = " ".join(word.capitalize() for word in parts[1:]) if len(parts) > 1 else ""
    return f"{num}. {rest}" if rest else num


def main():
    if len(sys.argv) < 2:
        print("Usage: python publish.py <course-folder>")
        print("Example: python publish.py cm3035")
        sys.exit(1)

    course = sys.argv[1]
    script_dir = Path(__file__).parent.resolve()
    course_folder = script_dir / course

    if not course_folder.is_dir():
        print(f"Error: folder '{course}' not found at {course_folder}")
        sys.exit(1)

    # Load course config
    config_path = course_folder / "course.json"
    if not config_path.exists():
        print(f"Error: {config_path} not found. Create it with title and description.")
        sys.exit(1)
    course_config = json.loads(config_path.read_text(encoding="utf-8"))

    # Load global config (Nextcloud settings)
    config = load_config()
    nc_folder = Path(config["nextcloud_path"]) / course

    if not nc_folder.is_dir():
        print(f"Error: Nextcloud folder not found: {nc_folder}")
        sys.exit(1)

    # Load existing episodes
    episodes_path = course_folder / "episodes.json"
    if episodes_path.exists():
        episodes = json.loads(episodes_path.read_text(encoding="utf-8"))
    else:
        episodes = []
    known_files = {ep["filename"] for ep in episodes}

    # Find new audio files in Nextcloud folder
    audio_files = sorted(nc_folder.glob("*.mp3")) + sorted(nc_folder.glob("*.m4a"))
    new_files = [f for f in audio_files if f.name not in known_files]

    if not new_files:
        print("No new audio files found.")
    else:
        print(f"Found {len(new_files)} new episode(s) in {nc_folder}:")
        for f in new_files:
            duration = get_duration(f)
            title = slug_to_title(f.name)
            entry = {"filename": f.name, "title": title, "description": ""}
            if duration:
                entry["duration_seconds"] = duration
            episodes.append(entry)
            dur_str = f" ({duration}s)" if duration else ""
            print(f"  + {f.name} -> {title}{dur_str}")

        episodes_path.write_text(
            json.dumps(episodes, indent=2, ensure_ascii=False), encoding="utf-8",
        )
        print(f"Updated {episodes_path}")

    # Regenerate RSS with Nextcloud URLs
    pages_url = get_pages_base_url()
    feed_url = f"{pages_url}/{course}/podcast.rss"
    result = subprocess.run(
        [sys.executable, "generate_podcast_rss.py",
         "--folder", str(nc_folder),
         "--nextcloud-url", config["nextcloud_url"],
         "--nextcloud-course", course,
         "--feed-url", feed_url,
         "--title", course_config["title"],
         "--description", course_config.get("description", ""),
         "--output", str(course_folder / "podcast.rss")],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        print(f"Error generating RSS:\n{result.stderr}")
        sys.exit(1)
    print(result.stdout.strip())

    # Git add, commit, push
    subprocess.run(["git", "-C", str(script_dir), "add", course], check=True)

    status = subprocess.run(
        ["git", "-C", str(script_dir), "diff", "--cached", "--quiet"],
        capture_output=True,
    )
    if status.returncode == 0:
        print("\nNo changes to commit.")
        return

    n_new = len(new_files)
    msg = f"Add {n_new} episode(s) to {course}" if n_new else f"Update {course} podcast feed"
    subprocess.run(["git", "-C", str(script_dir), "commit", "-m", msg], check=True)
    subprocess.run(["git", "-C", str(script_dir), "push"], check=True)

    print(f"\nPublished! Feed: {feed_url}")


if __name__ == "__main__":
    main()