#!/bin/bash
# Scaffold a new podcast course folder
# Usage: ./start_podcast.sh <course_code> "<title>" <source_folder>

set -e

if [ -z "$1" ] || [ -z "$2" ] || [ -z "$3" ]; then
    echo "Usage: ./start_podcast.sh <course_code> \"<title>\" <source_folder>"
    echo "Example: ./start_podcast.sh cm3035 \"CM3035: Advanced Web Development\" /path/to/mp3s"
    exit 1
fi

COURSE="$1"
TITLE="$2"
SOURCE="$3"
REPO="mnaumann79/UOL_Podcasts"

echo "=== Podcast Scaffolder ==="
echo "Course: $COURSE"
echo "Title:  $TITLE"
echo "Source: $SOURCE"
echo

if [ ! -d "$SOURCE" ]; then
    echo "Error: Source folder not found: $SOURCE"
    exit 1
fi

# Create course folder
mkdir -p "$COURSE"
echo "Created folder: $COURSE/"

# Copy audio files
cp "$SOURCE"/*.mp3 "$COURSE/" 2>/dev/null || true
cp "$SOURCE"/*.m4a "$COURSE/" 2>/dev/null || true
echo "Copied audio files to $COURSE/"

# Copy artwork if present
for ext in png jpg jpeg; do
    if [ -f "$SOURCE/artwork.$ext" ]; then
        cp "$SOURCE/artwork.$ext" "$COURSE/"
        echo "Copied artwork to $COURSE/"
        break
    fi
done

# Scaffold episodes.json
python generate_episodes_json.py --folder "$COURSE" --course "$COURSE"

echo
echo "=== Next Steps ==="
echo "1. Edit $COURSE/episodes.json to add titles, descriptions, and durations"
echo
echo "2. Commit and push:"
echo "   git add $COURSE/"
echo "   git commit -m \"Add $COURSE\""
echo "   git tag $COURSE/v1"
echo "   git push origin main $COURSE/v1"
echo
echo "3. Create GitHub release:"
echo "   gh release create $COURSE/v1 --title \"$TITLE v1\""
echo
echo "4. Generate RSS feed:"
echo "   python generate_podcast_rss.py \\"
echo "     --folder \"\$COURSE\" \\"
echo "     --repo \"$REPO\" \\"
echo "     --tag \"$COURSE/v1\" \\"
echo "     --title \"$TITLE\" \\"
echo "     --output \"\$COURSE/podcast.rss\""
echo
echo "5. Subscribe at:"
echo "   https://github.com/$REPO/releases/download/$COURSE/v1/podcast.rss"
