#!/bin/bash
# Package the Read-a-Thon databases (db/ folder) into a dated zip for backup
# or for moving to another computer. The code itself comes from git.
#
# Usage: ./package_data.sh [output folder]      (default: ~/Desktop)
#
# Restore on the other computer (after git clone/pull, with the app stopped):
#   cd <repo folder> && unzip -o <zip file>

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
OUTPUT_DIR="${1:-$HOME/Desktop}"
ZIP_NAME="readathon_data_$(date +%Y-%m-%d_%H%M).zip"

cd "$SCRIPT_DIR"

# A copy taken while the app is writing (e.g. mid-upload) can be inconsistent
if lsof -ti:5001 > /dev/null 2>&1; then
    echo "❌ The Read-a-Thon app is running (port 5001). Stop it first:"
    echo "   lsof -ti:5001 | xargs kill"
    exit 1
fi

if [ ! -d "$OUTPUT_DIR" ]; then
    echo "❌ Output folder not found: $OUTPUT_DIR"
    exit 1
fi

DB_FILES=$(ls db/*.db 2>/dev/null || true)
if [ -z "$DB_FILES" ]; then
    echo "❌ No database files found in $SCRIPT_DIR/db"
    exit 1
fi

zip -q "$OUTPUT_DIR/$ZIP_NAME" $DB_FILES

echo "✅ Created $OUTPUT_DIR/$ZIP_NAME"
echo ""
echo "Included:"
for f in $DB_FILES; do
    echo "   $f ($(du -h "$f" | cut -f1 | xargs))"
done
echo ""
echo "⚠️  Contains student names - share privately (not in a public/shared folder)."
echo ""
echo "To restore on another computer (app stopped, inside the repo folder):"
echo "   unzip -o $ZIP_NAME"
