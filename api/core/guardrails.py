"""
Pre-Flight Guardrail (< 0.05ms Execution):
Deterministic ingress filter for prompt & MCP tool-argument security.
"""
import re
import time
from typing import Optional


class PreFlightGuard:
    PATTERNS = {
        "Path Traversal / LFI": re.compile(r"(\.\./|\.\.\\|/etc/passwd|/etc/shadow|c:\\windows)", re.IGNORECASE),
        "Destructive SQLi": re.compile(r"\b(DROP\s+TABLE|DELETE\s+FROM|TRUNCATE\s+TABLE|--;\s*DROP)\b", re.IGNORECASE),
        "Adversarial System Override": re.compile(
            r"(ignore\s+all\s+(previous|prior)\s+instructions|system\s+prompt\s+override|you\s+are\s+now\s+DAN)",
            re.IGNORECASE,
        ),
        "Credential / Secret Leak Attempt": re.compile(r"(process\.env|os\.environ|printenv|cat\s+\.env)", re.IGNORECASE),
    }

    @classmethod
    def inspect(cls, text: str) -> tuple[bool, Optional[str], float]:
        start = time.perf_counter()
        for threat_name, pattern in cls.PATTERNS.items():
            if pattern.search(text):
                latency = (time.perf_counter() - start) * 1000
                return False, f"Blocked by Pre-Flight Shield: {threat_name} detected.", round(latency, 3)

        latency = (time.perf_counter() - start) * 1000
        return True, None, round(latency, 3)