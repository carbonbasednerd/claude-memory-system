#!/usr/bin/env bash
# Validate memory index integrity

set -e

SCOPE="${1:-both}"

echo "Validating memory index..."

# Check global index
if [ "$SCOPE" = "global" ] || [ "$SCOPE" = "both" ]; then
    if [ -f "$HOME/.claude/memory/index.json" ]; then
        echo "Checking global index..."

        # Validate JSON
        if python3 -m json.tool "$HOME/.claude/memory/index.json" > /dev/null 2>&1; then
            echo "  ✓ Global index is valid JSON"
        else
            echo "  ✗ Global index has invalid JSON"
            exit 1
        fi

        # Count memories
        GLOBAL_COUNT=$(python3 -c "import json; data=json.load(open('$HOME/.claude/memory/index.json')); print(len(data.get('memories', [])))")
        echo "  ✓ Global index contains $GLOBAL_COUNT memories"

        # Check for log entries
        if [ -d "$HOME/.claude/memory/index-log" ]; then
            LOG_COUNT=$(ls -1 "$HOME/.claude/memory/index-log"/*.json 2>/dev/null | wc -l)
            if [ "$LOG_COUNT" -gt 0 ]; then
                echo "  ⚠ $LOG_COUNT unmerged log entries (consider rebuilding index)"
            else
                echo "  ✓ No pending log entries"
            fi
        fi
    else
        echo "  ⚠ Global index not found"
    fi
fi

# Check project index
if [ "$SCOPE" = "project" ] || [ "$SCOPE" = "both" ]; then
    if [ -f ".claude/memory/index.json" ]; then
        echo "Checking project index..."

        # Validate JSON
        if python3 -m json.tool ".claude/memory/index.json" > /dev/null 2>&1; then
            echo "  ✓ Project index is valid JSON"
        else
            echo "  ✗ Project index has invalid JSON"
            exit 1
        fi

        # Count memories
        PROJECT_COUNT=$(python3 -c "import json; data=json.load(open('.claude/memory/index.json')); print(len(data.get('memories', [])))")
        echo "  ✓ Project index contains $PROJECT_COUNT memories"

        # Check for log entries
        if [ -d ".claude/memory/index-log" ]; then
            LOG_COUNT=$(ls -1 ".claude/memory/index-log"/*.json 2>/dev/null | wc -l)
            if [ "$LOG_COUNT" -gt 0 ]; then
                echo "  ⚠ $LOG_COUNT unmerged log entries (consider rebuilding index)"
            else
                echo "  ✓ No pending log entries"
            fi
        fi
    else
        echo "  ⚠ Project index not found"
    fi
fi

echo "✓ Validation complete"
