"""
Semantic MCP Tool Pruner: Ranks 30 MCP tools and injects only top-K into context.
"""
import json
import math
import re
import time
from typing import List, Tuple
from pydantic import BaseModel
from api.mcp_engine.registry import MCPTool, ALL_MCP_TOOLS


class PruningTelemetry(BaseModel):
    total_tools_registered: int
    selected_tools_count: int
    selected_tool_names: List[str]
    original_schema_tokens_est: int
    pruned_schema_tokens_est: int
    tokens_saved: int
    token_reduction_pct: float
    pruning_latency_ms: float


class SemanticToolPruner:
    def __init__(self, tools: List[MCPTool] = ALL_MCP_TOOLS):
        self.tools = tools
        self._precompute_corpus()

    STOP_WORDS = {
        "the", "and", "for", "with", "from", "that", "this", "are", "was",
        "can", "you", "our", "why", "how", "what", "show", "find", "check",
        "into", "over", "given", "all", "any", "has", "have",
    }

    def _tokenize(self, text: str) -> List[str]:
        raw_tokens = re.findall(r"[a-z0-9_]{2,}", text.lower())
        expanded: List[str] = []
        for t in raw_tokens:
            parts = [t] + ([sub for sub in t.split("_") if len(sub) > 2] if "_" in t else [])
            for p in parts:
                if p in self.STOP_WORDS:
                    continue
                # Lightweight suffix stemming so "failed" == "failing" == "fail"
                stemmed = re.sub(r"(ing|ed|es|s)$", "", p)
                expanded.append(stemmed if len(stemmed) >= 3 else p)
        return expanded

    def _precompute_corpus(self):
        """Indexes all tool descriptions into an inverted index with TF-IDF weights."""
        self.doc_tokens = []
        self.df = {}
        total_docs = len(self.tools)

        for tool in self.tools:
            doc_text = f"{tool.name} {tool.category} {tool.description} {' '.join(tool.parameters.get('properties', {}).keys())}"
            tokens = self._tokenize(doc_text)
            self.doc_tokens.append(tokens)
            for unique_token in set(tokens):
                self.df[unique_token] = self.df.get(unique_token, 0) + 1

        # Calculate IDF
        self.idf = {
            t: math.log(1.0 + (total_docs - freq + 0.5) / (freq + 0.5))
            for t, freq in self.df.items()
        }

    @staticmethod
    def _estimate_tokens(tools: List[MCPTool]) -> int:
        """Estimates token footprint of JSON tool schemas (~4 chars per token)."""
        raw_json = json.dumps([t.model_dump() for t in tools])
        return len(raw_json) // 4

    def prune(self, user_prompt: str, top_k: int = 3) -> Tuple[List[MCPTool], PruningTelemetry]:
        start = time.perf_counter()
        query_tokens = self._tokenize(user_prompt)

        scores: List[Tuple[float, int]] = []
        for doc_idx, doc_toks in enumerate(self.doc_tokens):
            score = 0.0
            doc_token_counts = {}
            for t in doc_toks:
                doc_token_counts[t] = doc_token_counts.get(t, 0) + 1

            for q in query_tokens:
                if q in doc_token_counts:
                    # BM25-style frequency weighting
                    tf = doc_token_counts[q]
                    idf_val = self.idf.get(q, 1.0)
                    score += idf_val * (tf / (tf + 1.2))

            scores.append((score, doc_idx))

        # Sort descending by score
        scores.sort(key=lambda x: x[0], reverse=True)
        top_indices = [idx for _, idx in scores[:top_k]]
        pruned_tools = [self.tools[idx] for idx in top_indices]

        latency_ms = (time.perf_counter() - start) * 1000

        # Calculate telemetry metrics
        orig_tokens = self._estimate_tokens(self.tools)
        pruned_tokens = self._estimate_tokens(pruned_tools)
        tokens_saved = orig_tokens - pruned_tokens
        reduction_pct = round((tokens_saved / orig_tokens) * 100, 1)

        telemetry = PruningTelemetry(
            total_tools_registered=len(self.tools),
            selected_tools_count=len(pruned_tools),
            selected_tool_names=[t.name for t in pruned_tools],
            original_schema_tokens_est=orig_tokens,
            pruned_schema_tokens_est=pruned_tokens,
            tokens_saved=tokens_saved,
            token_reduction_pct=reduction_pct,
            pruning_latency_ms=round(latency_ms, 3),
        )

        return pruned_tools, telemetry


# ==========================================
# CLI TEST HARNESS
# ==========================================
if __name__ == "__main__":
    from rich.console import Console
    from rich.table import Table

    console = Console()
    pruner = SemanticToolPruner()

    test_queries = [
        "Can you check why our latest GitHub Actions CI run failed on branch staging?",
        "Find the latest research papers about speculative decoding on arXiv",
        "Inspect the slow SELECT queries and table indexes on the users database table",
        "The web service is crashing, show me the recent Docker container logs",
    ]

    for q in test_queries:
        console.rule(f"[bold cyan]Query: {q}[/bold cyan]")
        selected, stats = pruner.prune(q, top_k=3)

        table = Table(title="Semantic MCP Pruning Result", show_header=True)
        table.add_column("Rank", style="dim", width=6)
        table.add_column("Selected MCP Tool", style="bold green")
        table.add_column("Category", style="magenta")
        table.add_column("Description", style="white")

        for rank, tool in enumerate(selected, 1):
            table.add_row(str(rank), tool.name, tool.category, tool.description[:70] + "...")

        console.print(table)
        console.print(
            f"[bold yellow]Tokens:[/bold yellow] {stats.original_schema_tokens_est} -> "
            f"[bold green]{stats.pruned_schema_tokens_est}[/bold green] "
            f"([bold cyan]-{stats.token_reduction_pct}% overhead saved[/bold cyan] in {stats.pruning_latency_ms}ms)\n"
        )