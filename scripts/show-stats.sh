#!/usr/bin/env bash
# Show memory usage statistics

set -e

echo "Memory Statistics"
echo "================="
echo

claude-memory stats

echo
echo "Active Sessions:"
echo "----------------"
claude-memory list-sessions
