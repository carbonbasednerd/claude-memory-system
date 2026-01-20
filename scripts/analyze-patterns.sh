#!/usr/bin/env bash
# Analyze memory for skill candidates

set -e

SCOPE="${1:-both}"
MIN_OCCURRENCES="${2:-3}"
DAYS="${3:-90}"

echo "Analyzing memory for skill patterns..."
echo "  Scope: $SCOPE"
echo "  Minimum occurrences: $MIN_OCCURRENCES"
echo "  Time window: $DAYS days"
echo

claude-memory analyze-skills \
    --scope "$SCOPE" \
    --min-occurrences "$MIN_OCCURRENCES" \
    --days "$DAYS"

echo "✓ Analysis complete"
