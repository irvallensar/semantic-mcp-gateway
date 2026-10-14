"""
Complexity Router:
Scores prompt complexity from 0.0 to 1.0 to route between Fast Tier (20B) and Heavy Tier (120B).
"""
import re
from typing import Literal


class ComplexityRouter:
    REASONING_MARKERS = {
        "implement", "architecture", "optimize", "debug", "refactor", "algorithm",
        "concurrency", "distributed", "compare", "trade-offs", "prove", "step-by-step",
        "sql", "schema", "regex", "async", "deadlock", "complexity",
    }

    @classmethod
    def score(cls, prompt: str, threshold: float = 0.45) -> tuple[float, Literal["FAST_TIER", "HEAVY_TIER"]]:
        words = prompt.lower().split()
        length_score = min(len(words) / 120.0, 0.35)
        matched_keywords = sum(1 for w in set(words) if w.strip(".,?!():;") in cls.REASONING_MARKERS)
        keyword_score = min(matched_keywords * 0.12, 0.40)
        has_code_or_json = bool(re.search(r"(```|\{|\}|SELECT\s+|def\s+|function\s+|class\s+)", prompt))
        structure_score = 0.25 if has_code_or_json else 0.0

        total_score = round(min(length_score + keyword_score + structure_score, 1.0), 2)
        tier = "HEAVY_TIER" if total_score >= threshold else "FAST_TIER"
        return total_score, tier