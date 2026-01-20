"""Skill candidate detection and extraction."""

from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path

from claude_memory.models import MemoryEntry, MemoryType, SkillCandidate
from claude_memory.utils import write_json_file


class SkillDetector:
    """Detects patterns that could become skills."""

    def __init__(self, memories: list[MemoryEntry]):
        self.memories = memories

    def detect_candidates(
        self,
        min_occurrences: int = 3,
        within_days: int = 90,
    ) -> list[dict]:
        """
        Detect skill candidates from memory patterns.

        Args:
            min_occurrences: Minimum number of similar patterns
            within_days: Look for patterns within this time window

        Returns:
            List of skill candidate information
        """
        candidates = []
        cutoff_date = datetime.now() - timedelta(days=within_days)

        # Filter recent memories
        recent_memories = [
            m for m in self.memories if m.created >= cutoff_date
        ]

        # Detect repeated procedures
        procedure_candidates = self._detect_procedures(
            recent_memories, min_occurrences
        )
        candidates.extend(procedure_candidates)

        # Detect decision frameworks
        decision_candidates = self._detect_decision_patterns(
            recent_memories, min_occurrences
        )
        candidates.extend(decision_candidates)

        # Detect problem-solution pairs
        problem_candidates = self._detect_problem_solutions(
            recent_memories, min_occurrences
        )
        candidates.extend(problem_candidates)

        return candidates

    def _detect_procedures(
        self, memories: list[MemoryEntry], min_occurrences: int
    ) -> list[dict]:
        """Detect repeated procedural patterns."""
        candidates = []

        # Look for similar tasks/titles
        task_counter = Counter()
        task_memories = {}

        for memory in memories:
            # Normalize title for matching
            normalized = self._normalize_text(memory.title)
            key_words = set(normalized.split())

            # Group by similar key words
            for existing_task, count in task_counter.items():
                existing_words = set(existing_task.split())
                # If >60% overlap, consider similar
                overlap = len(key_words & existing_words) / max(
                    len(key_words), len(existing_words)
                )
                if overlap > 0.6:
                    task_counter[existing_task] += 1
                    task_memories.setdefault(existing_task, []).append(memory)
                    break
            else:
                # New pattern
                task_counter[normalized] = 1
                task_memories[normalized] = [memory]

        # Find patterns that occur frequently enough
        for task, count in task_counter.items():
            if count >= min_occurrences:
                related = task_memories[task]
                candidates.append(
                    {
                        "type": "procedure",
                        "name": task.replace("-", " ").title(),
                        "confidence": (
                            "high" if count >= min_occurrences * 2 else "medium"
                        ),
                        "occurrences": count,
                        "related_memories": [m.id for m in related],
                        "tags": self._merge_tags(related),
                        "suggested_skill_name": self._generate_skill_name(task),
                    }
                )

        return candidates

    def _detect_decision_patterns(
        self, memories: list[MemoryEntry], min_occurrences: int
    ) -> list[dict]:
        """Detect repeated decision-making patterns."""
        candidates = []

        # Group memories with similar decision keywords
        decision_groups = {}

        for memory in memories:
            if memory.type == MemoryType.DECISION or memory.decisions:
                # Extract decision keywords
                keywords = set()
                if memory.decisions:
                    for decision in memory.decisions:
                        keywords.update(self._normalize_text(decision).split())

                # Find matching group
                for group_key, group_members in decision_groups.items():
                    group_keywords = set(group_key.split())
                    overlap = len(keywords & group_keywords) / max(
                        len(keywords), len(group_keywords), 1
                    )
                    if overlap > 0.5:
                        decision_groups[group_key].append(memory)
                        break
                else:
                    # New group
                    if keywords:
                        key = " ".join(sorted(keywords)[:5])
                        decision_groups[key] = [memory]

        # Find patterns
        for group_key, members in decision_groups.items():
            if len(members) >= min_occurrences:
                candidates.append(
                    {
                        "type": "decision_framework",
                        "name": f"{group_key[:50]} Decision Pattern",
                        "confidence": "medium",
                        "occurrences": len(members),
                        "related_memories": [m.id for m in members],
                        "tags": self._merge_tags(members),
                        "suggested_skill_name": f"decide-{group_key[:20].replace(' ', '-')}",
                    }
                )

        return candidates

    def _detect_problem_solutions(
        self, memories: list[MemoryEntry], min_occurrences: int
    ) -> list[dict]:
        """Detect repeated problem-solution patterns."""
        candidates = []

        # Look for similar tags/keywords indicating similar problems
        problem_groups = {}

        for memory in memories:
            # Use tags and keywords to group similar problems
            signature = tuple(sorted(memory.tags[:5]))

            if signature:
                problem_groups.setdefault(signature, []).append(memory)

        # Find patterns
        for signature, members in problem_groups.items():
            if len(members) >= min_occurrences:
                tag_str = "-".join(signature)
                candidates.append(
                    {
                        "type": "problem_solution",
                        "name": f"{tag_str.title()} Problem Pattern",
                        "confidence": "medium",
                        "occurrences": len(members),
                        "related_memories": [m.id for m in members],
                        "tags": list(signature),
                        "suggested_skill_name": f"fix-{tag_str[:30]}",
                    }
                )

        return candidates

    def _normalize_text(self, text: str) -> str:
        """Normalize text for pattern matching."""
        return (
            text.lower()
            .replace("_", "-")
            .replace("/", "-")
            .replace("  ", " ")
            .strip()
        )

    def _merge_tags(self, memories: list[MemoryEntry]) -> list[str]:
        """Merge tags from multiple memories."""
        all_tags = []
        for memory in memories:
            all_tags.extend(memory.tags)

        # Return most common tags
        tag_counts = Counter(all_tags)
        return [tag for tag, _ in tag_counts.most_common(10)]

    def _generate_skill_name(self, task: str) -> str:
        """Generate a skill name from a task description."""
        # Take first few meaningful words
        words = task.split("-")[:4]
        return "-".join(words)

    def generate_report(
        self, candidates: list[dict], output_file: Path
    ) -> None:
        """Generate a skill candidates report in markdown."""
        md = "# Skill Candidates\n\n"
        md += f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

        if not candidates:
            md += "No skill candidates detected.\n"
        else:
            # Group by confidence
            high_confidence = [c for c in candidates if c["confidence"] == "high"]
            medium_confidence = [
                c for c in candidates if c["confidence"] == "medium"
            ]
            low_confidence = [c for c in candidates if c["confidence"] == "low"]

            if high_confidence:
                md += "## High Confidence\n\n"
                for candidate in high_confidence:
                    md += self._format_candidate(candidate)

            if medium_confidence:
                md += "## Medium Confidence\n\n"
                for candidate in medium_confidence:
                    md += self._format_candidate(candidate)

            if low_confidence:
                md += "## Low Confidence\n\n"
                for candidate in low_confidence:
                    md += self._format_candidate(candidate)

        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(md)

    def _format_candidate(self, candidate: dict) -> str:
        """Format a skill candidate for markdown."""
        md = f"### {candidate['name']}\n"
        md += f"- **Type**: {candidate['type']}\n"
        md += f"- **Occurrences**: {candidate['occurrences']}\n"
        md += f"- **Tags**: {', '.join(candidate['tags'])}\n"
        md += f"- **Suggested Skill Name**: `{candidate['suggested_skill_name']}`\n"
        md += f"- **Related Memories**: {len(candidate['related_memories'])}\n"
        md += "\n"
        return md


def flag_skill_candidates(
    memories: list[MemoryEntry],
    min_occurrences: int = 3,
    within_days: int = 90,
) -> list[MemoryEntry]:
    """
    Flag memories that are skill candidates.

    Args:
        memories: List of memory entries to analyze
        min_occurrences: Minimum pattern occurrences
        within_days: Time window for analysis

    Returns:
        Updated memory entries with skill_candidate flags
    """
    detector = SkillDetector(memories)
    candidates = detector.detect_candidates(min_occurrences, within_days)

    # Create mapping of memory IDs to candidates
    memory_to_candidate = {}
    for candidate in candidates:
        for memory_id in candidate["related_memories"]:
            memory_to_candidate[memory_id] = candidate

    # Update memories
    for memory in memories:
        if memory.id in memory_to_candidate:
            candidate = memory_to_candidate[memory.id]
            memory.skill_candidate = SkillCandidate(
                flagged=True,
                candidate_name=candidate["suggested_skill_name"],
                confidence=candidate["confidence"],
                related_memories=candidate["related_memories"],
            )

    return memories
