#!/usr/bin/env bash
# Cleanup stale sessions (no activity for 24+ hours)

set -e

HOURS="${1:-24}"

echo "Finding sessions with no activity for $HOURS+ hours..."
claude-memory cleanup-sessions --hours "$HOURS" --auto-archive

echo "✓ Cleanup complete"
