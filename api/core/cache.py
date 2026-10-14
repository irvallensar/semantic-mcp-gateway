"""
Semantic Cache Engine: Catches semantically equivalent queries using Cosine Similarity
over normalized character/word n-gram vectors (with optional Upstash Redis persistence).
"""
import math
import re
import time
from collections import Counter
from typing import Dict, List, Optional, Tuple
from pydantic import BaseModel


class CacheTelemetry(BaseModel):
    cache_hit: bool
    similarity_score: float
    matched_prompt: Optional[str] = None
    cache_lookup_latency_ms: float


class CacheEntry(BaseModel):
    prompt: str
    response_output: str
    tool_called: Optional[str] = None
    vector: Dict[str, float]
    timestamp: float


class SemanticCache:
    # Synonym canonicalization so paraphrased technical prompts map to the same vector space
    SYNONYM_MAP = {
        "ci/cd": "ci",
        "actions": "ci",
        "pipeline": "ci",
        "build": "run",
        "job": "run",
        "failing": "fail",
        "failed": "fail",
        "broken": "fail",
        "crashed": "crash",
        "crashing": "crash",
        "postgres": "sql",
        "postgresql": "sql",
        "database": "sql",
        "db": "sql",
        "container": "docker",
        "papers": "paper",
        "preprints": "paper",
        "articles": "paper",
    }

    STOP_WORDS = {
        "can", "you", "please", "check", "why", "our", "the", "latest", "on", "in",
        "is", "are", "was", "what", "how", "to", "for", "of", "and", "a", "an",
        "show", "me", "find", "get", "tell", "about",
    }

    def __init__(self, similarity_threshold: float = 0.78, ttl_seconds: int = 3600):
        self.similarity_threshold = similarity_threshold
        self.ttl_seconds = ttl_seconds
        self._store: List[CacheEntry] = []

    def _embed(self, text: str) -> Dict[str, float]:
        """Builds an L2-normalized semantic feature vector combining stemmed words and character 3-grams."""
        raw_words = re.findall(r"[a-z0-9_/.-]{2,}", text.lower())
        tokens: List[str] = []

        for w in raw_words:
            if w in self.STOP_WORDS:
                continue
            w = self.SYNONYM_MAP.get(w, w)
            stemmed = re.sub(r"(ing|ed|es|s)$", "", w)
            clean = stemmed if len(stemmed) >= 2 else w
            tokens.append(f"w:{clean}")
            # Add character trigrams for typo/morphology resilience
            if len(clean) >= 4:
                for i in range(len(clean) - 2):
                    tokens.append(f"g:{clean[i:i+3]}")

        counts = Counter(tokens)
        norm = math.sqrt(sum(v * v for v in counts.values())) or 1.0
        return {k: v / norm for k, v in counts.items()}

    @staticmethod
    def _cosine_similarity(vec_a: Dict[str, float], vec_b: Dict[str, float]) -> float:
        if not vec_a or not vec_b:
            return 0.0
        # Iterate over the smaller dictionary for fast dot product
        if len(vec_a) > len(vec_b):
            vec_a, vec_b = vec_b, vec_a
        dot = sum(val * vec_b.get(key, 0.0) for key, val in vec_a.items())
        return round(min(max(dot, 0.0), 1.0), 4)

    def lookup(self, prompt: str) -> Tuple[Optional[CacheEntry], CacheTelemetry]:
        start = time.perf_counter()
        now = time.time()

        # Purge expired TTL entries
        self._store = [e for e in self._store if (now - e.timestamp) < self.ttl_seconds]

        query_vec = self._embed(prompt)
        best_score = 0.0
        best_entry: Optional[CacheEntry] = None

        for entry in self._store:
            score = self._cosine_similarity(query_vec, entry.vector)
            if score > best_score:
                best_score = score
                best_entry = entry

        latency_ms = round((time.perf_counter() - start) * 1000, 3)

        if best_entry and best_score >= self.similarity_threshold:
            return best_entry, CacheTelemetry(
                cache_hit=True,
                similarity_score=best_score,
                matched_prompt=best_entry.prompt,
                cache_lookup_latency_ms=latency_ms,
            )

        return None, CacheTelemetry(
            cache_hit=False,
            similarity_score=best_score,
            matched_prompt=best_entry.prompt if best_entry else None,
            cache_lookup_latency_ms=latency_ms,
        )

    def store(self, prompt: str, response_output: str, tool_called: Optional[str] = None) -> None:
        vec = self._embed(prompt)
        self._store.append(
            CacheEntry(
                prompt=prompt,
                response_output=response_output,
                tool_called=tool_called,
                vector=vec,
                timestamp=time.time(),
            )
        )