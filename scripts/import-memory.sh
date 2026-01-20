#!/usr/bin/env bash
# Import memory from backup archive

set -e

ARCHIVE="$1"

if [ -z "$ARCHIVE" ]; then
    echo "Usage: $0 <backup-file.tar.gz>"
    exit 1
fi

if [ ! -f "$ARCHIVE" ]; then
    echo "✗ Archive not found: $ARCHIVE"
    exit 1
fi

echo "Importing memory from $ARCHIVE..."

# Extract to current directory or home
if [ -d ".git" ]; then
    # In a project
    tar -xzf "$ARCHIVE"
    echo "✓ Imported to project directory"
else
    # Import to global
    tar -xzf "$ARCHIVE" -C "$HOME"
    echo "✓ Imported to global directory"
fi

echo "✓ Import complete"
