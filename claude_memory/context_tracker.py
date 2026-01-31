"""Context usage tracking utilities for debug mode."""

from pathlib import Path
from typing import Optional
import json


class ContextTracker:
    """Track and estimate context usage for memory system."""

    def __init__(self, global_dir: Path, project_dir: Optional[Path] = None):
        """Initialize context tracker.

        Args:
            global_dir: Global .claude directory
            project_dir: Project .claude directory (if in project)
        """
        self.global_dir = global_dir
        self.project_dir = project_dir
        self.debug_enabled = self._is_debug_enabled()

    def _is_debug_enabled(self) -> bool:
        """Check if debug mode is enabled.

        Returns:
            True if debug flag exists
        """
        debug_flag = self.global_dir / "sessions" / "debug.flag"
        return debug_flag.exists()

    def estimate_file_tokens(self, file_path: Path) -> int:
        """Estimate tokens in a file.

        Uses rough approximation: 1 token ≈ 4 characters

        Args:
            file_path: Path to file

        Returns:
            Estimated token count
        """
        if not file_path.exists():
            return 0

        try:
            content = file_path.read_text()
            return len(content) // 4
        except Exception:
            return 0

    def get_claude_md_usage(self) -> dict:
        """Get token usage of CLAUDE.md files.

        Returns:
            Dictionary with global and project token counts
        """
        usage = {
            "global_claude_md": 0,
            "project_claude_md": 0,
            "total_claude_md": 0,
        }

        # Global CLAUDE.md
        global_claude = self.global_dir / "CLAUDE.md"
        usage["global_claude_md"] = self.estimate_file_tokens(global_claude)

        # Project CLAUDE.md
        if self.project_dir:
            project_claude = self.project_dir / "CLAUDE.md"
            usage["project_claude_md"] = self.estimate_file_tokens(project_claude)

        usage["total_claude_md"] = usage["global_claude_md"] + usage["project_claude_md"]

        return usage

    def get_manifest_usage(self) -> dict:
        """Get token usage of manifest files.

        Returns:
            Dictionary with global and project manifest token counts
        """
        usage = {
            "global_manifest": 0,
            "project_manifest": 0,
            "total_manifests": 0,
        }

        # Global manifest
        global_manifest = self.global_dir / "memory" / "manifest.json"
        usage["global_manifest"] = self.estimate_file_tokens(global_manifest)

        # Project manifest
        if self.project_dir:
            project_manifest = self.project_dir / "memory" / "manifest.json"
            usage["project_manifest"] = self.estimate_file_tokens(project_manifest)

        usage["total_manifests"] = usage["global_manifest"] + usage["project_manifest"]

        return usage

    def get_memory_stats(self) -> dict:
        """Get statistics about memories from manifests.

        Returns:
            Dictionary with memory statistics
        """
        stats = {
            "total_memories": 0,
            "global_memories": 0,
            "project_memories": 0,
            "total_memory_tokens": 0,
        }

        # Global manifest
        global_manifest_file = self.global_dir / "memory" / "manifest.json"
        if global_manifest_file.exists():
            try:
                with open(global_manifest_file, 'r') as f:
                    manifest = json.load(f)
                    stats["global_memories"] = manifest.get("stats", {}).get("total_memories", 0)
                    global_tokens = manifest.get("stats", {}).get("total_tokens", 0)
                    stats["total_memory_tokens"] += global_tokens
            except Exception:
                pass

        # Project manifest
        if self.project_dir:
            project_manifest_file = self.project_dir / "memory" / "manifest.json"
            if project_manifest_file.exists():
                try:
                    with open(project_manifest_file, 'r') as f:
                        manifest = json.load(f)
                        stats["project_memories"] = manifest.get("stats", {}).get("total_memories", 0)
                        project_tokens = manifest.get("stats", {}).get("total_tokens", 0)
                        stats["total_memory_tokens"] += project_tokens
                except Exception:
                    pass

        stats["total_memories"] = stats["global_memories"] + stats["project_memories"]

        return stats

    def get_context_report(self, context_limit: int = 200000, memory_budget: int = 5000) -> str:
        """Generate context usage report.

        Args:
            context_limit: Total context limit (default 200k tokens)
            memory_budget: Memory system budget (default 5k tokens)

        Returns:
            Formatted report string
        """
        claude_usage = self.get_claude_md_usage()
        manifest_usage = self.get_manifest_usage()
        memory_stats = self.get_memory_stats()

        # Calculate memory system overhead
        memory_overhead = claude_usage["total_claude_md"] + manifest_usage["total_manifests"]
        memory_percent = (memory_overhead / memory_budget) * 100 if memory_budget > 0 else 0

        report = []
        # Calculate always loaded vs on-demand
        always_loaded = claude_usage['total_claude_md']
        always_percent = (always_loaded / memory_budget) * 100 if memory_budget > 0 else 0

        report.append("📊 Memory System Context Usage")
        report.append("")
        report.append(f"**Context Budget:**")
        report.append(f"  Total limit: {context_limit:,} tokens")
        report.append(f"  Memory budget: {memory_budget:,} tokens ({(memory_budget/context_limit)*100:.1f}%)")
        report.append("")
        report.append(f"**Always Loaded: {always_loaded:,} tokens ({always_percent:.1f}% of budget)**")
        report.append("")
        report.append("**Breakdown:**")
        report.append(f"• CLAUDE.md files (always loaded): {claude_usage['total_claude_md']:,} tokens")
        report.append(f"  ├─ Global: {claude_usage['global_claude_md']:,}")
        report.append(f"  └─ Project: {claude_usage['project_claude_md']:,}")
        report.append("")
        report.append(f"• Manifest files (on-demand only): {manifest_usage['total_manifests']:,} tokens")
        report.append(f"  ├─ Global: {manifest_usage['global_manifest']:,}")
        report.append(f"  └─ Project: {manifest_usage['project_manifest']:,}")
        report.append("")
        report.append(f"**Memory Catalog:**")
        report.append(f"  Total memories: {memory_stats['total_memories']}")
        report.append(f"  ├─ Global: {memory_stats['global_memories']}")
        report.append(f"  └─ Project: {memory_stats['project_memories']}")
        report.append(f"  Total content size: ~{memory_stats['total_memory_tokens']:,} tokens")
        report.append(f"  (Loaded on-demand, not in context)")
        report.append("")

        # Status indicators (based on always-loaded only)
        if always_loaded > memory_budget:
            report.append("⚠️ Always-loaded overhead exceeds budget!")
            report.append(f"   Over by: {always_loaded - memory_budget:,} tokens")
        elif always_loaded > memory_budget * 0.5:
            report.append(f"⚠️ Always-loaded using {always_percent:.0f}% of budget")
            report.append(f"   Suggestion: Consider further template optimization")
        else:
            report.append("✅ Well within memory budget")
            report.append(f"   {memory_budget - always_loaded:,} tokens available for on-demand loading")

        return "\n".join(report)

    def log_memory_load(self, memory_id: str, tokens: int):
        """Log a memory load event (for future enhancement).

        Args:
            memory_id: ID of loaded memory
            tokens: Token count of loaded content
        """
        if not self.debug_enabled:
            return

        # Future: log to a session file
        # For now, this is a placeholder for when we implement detailed tracking
        pass
