"""
FastAPI Entrypoint for the Semantic MCP & LLM Gateway.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from core_gateway import SemanticGateway, GatewayResponse
from api.mcp_engine.registry import ALL_MCP_TOOLS

app = FastAPI(
    title="Semantic MCP & LLM Gateway",
    description="High-Throughput Semantic Router, MCP Tool Pruner, Pre-Flight Guardrail & Multi-Provider Circuit Breaker.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Singleton gateway instance (preserves in-memory Semantic Cache across requests)
gateway = SemanticGateway()


class ExecuteRequest(BaseModel):
    prompt: str = Field(..., example="Can you check why our latest GitHub Actions CI run failed on branch staging in repo irvallen/gateway?")
    enable_mcp_tools: bool = Field(default=True)
    use_cache: bool = Field(default=True)
    simulate_primary_outage: bool = Field(default=False)


@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "registered_mcp_tools": len(ALL_MCP_TOOLS),
        "cached_entries": len(gateway.cache._store),
        "tiers": {
            "fast": gateway.fast_model,
            "heavy": gateway.heavy_model,
            "fallback_chain": gateway.fallback_chain,
        },
    }


@app.get("/api/tools")
async def list_mcp_tools():
    return {
        "total": len(ALL_MCP_TOOLS),
        "tools": [t.model_dump() for t in ALL_MCP_TOOLS],
    }


@app.post("/api/execute", response_model=GatewayResponse)
async def execute_prompt(req: ExecuteRequest):
    return await gateway.execute(
        prompt=req.prompt,
        enable_mcp_tools=req.enable_mcp_tools,
        use_cache=req.use_cache,
        simulate_primary_outage=req.simulate_primary_outage,
    )