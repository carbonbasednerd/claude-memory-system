#!/usr/bin/env bash
# Rebuild memory index from log entries

set -e

# Default to project scope
SCOPE="${1:-project}"

echo "Rebuilding $SCOPE index..."
claude-memory rebuild-index --scope "$SCOPE"

echo "✓ Index rebuild complete"
