"""
Generate episodes.json from MP3/M4A files in a folder.

Scans the folder for audio files and creates an episodes.json with
titles derived from filenames (hyphens/underscores replaced with spaces,
extension removed) and empty descriptions.

Usage:
    python generate_episodes_json.py --folder "/path/to/audio"

Run this once to scaffold episodes.json, then edit the titles and
descriptions by hand before running generate_podcast_rss.py.
"""

import argparse
import json
import re
from pathlib import Path


def slug_to_title(slug: str) -> str:
    """Convert a filename slug to a readable title. Number is always prepended with a period."""
    name = Path(slug).stem  # remove extension
    # Split on hyphens, underscores, or periods to separate number from rest
    parts = re.split(r"[-_.]+", name)
    num = parts[0] if parts else ""
    rest = " ".join(word.capitalize() for word in parts[1:]) if len(parts) > 1 else ""
    return f"{num}. {rest}" if rest else num


def generate_episodes(folder: Path) -> list[dict]:
    """Scan folder for audio files and generate episode metadata."""
    audio_files = sorted(folder.glob("*.mp3")) + sorted(folder.glob("*.m4a"))
    return [
        {
            "filename": af.name,
            "title": slug_to_title(af.name),
            "description": "",
        }
        for af in audio_files
    ]


def main():
    parser = argparse.ArgumentParser(description="Scaffold episodes.json from audio files")
    parser.add_argument("--folder", required=True, help="Path to folder containing MP3/M4A files")
    parser.add_argument(
        "--output",
        default="episodes.json",
        help="Output episodes.json path (default: episodes.json in --folder)",
    )

    args = parser.parse_args()

    folder = Path(args.folder)
    if not folder.exists():
        print(f"Error: Folder not found: {folder}")
        return 1

    audio_files = list(sorted(folder.glob("*.mp3")) + sorted(folder.glob("*.m4a")))
    if not audio_files:
        print(f"No audio files found in {folder}")
        return 1

    episodes = generate_episodes(folder)

    output_path = Path(args.output)
    if output_path.is_absolute():
        output_path.write_text(json.dumps(episodes, indent=2, ensure_ascii=False), encoding="utf-8")
    else:
        (folder / args.output).write_text(json.dumps(episodes, indent=2, ensure_ascii=False), encoding="utf-8")
        output_path = folder / args.output

    print(f"Written {len(episodes)} episodes to {output_path}")
    for ep in episodes:
        print(f"  {ep['filename']} -> {ep['title']}")

    return 0


if __name__ == "__main__":
    exit(main())
