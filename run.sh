#!/bin/bash
# Start the Read-a-Thon app and open it in the browser.
#
# Usage: ./run.sh                          last database you used
#        ./run.sh --db sample              sample data
#        ./run.sh --db "2026 Read-a-Thon"  a specific year
#
# Stop with CTRL+C (or: lsof -ti:5001 | xargs kill)

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
URL="http://127.0.0.1:5001"

# The app uses paths like db/..., so it must run from the project folder
cd "$SCRIPT_DIR"

if lsof -ti:5001 > /dev/null 2>&1; then
    echo "ℹ️  The Read-a-Thon app is already running: $URL"
    open "$URL"
    exit 0
fi

# Open the browser once the server has had a moment to start
(sleep 2 && open "$URL") &

python3 app.py "$@"
