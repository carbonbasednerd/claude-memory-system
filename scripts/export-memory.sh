#!/usr/bin/env bash
# Export memory to backup archive

set -e

OUTPUT="${1:-memory-backup-$(date +%Y%m%d-%H%M%S).tar.gz}"

echo "Exporting memory to $OUTPUT..."

# Determine what to backup
if [ -d ".claude" ]; then
    # In a project, backup project memory
    tar -czf "$OUTPUT" .claude/
    echo "✓ Exported project memory"
elif [ -d "$HOME/.claude" ]; then
    # Backup global memory
    tar -czf "$OUTPUT" -C "$HOME" .claude/
    echo "✓ Exported global memory"
else
    echo "✗ No memory found to export"
    exit 1
fi

echo "Backup saved to: $OUTPUT"
