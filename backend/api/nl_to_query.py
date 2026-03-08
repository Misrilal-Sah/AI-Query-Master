"""
AI Query Master - Natural Language to Query API
POST /api/nl-to-query
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

router = APIRouter(prefix="/api", tags=["NL to Query"])


class NLToQueryRequest(BaseModel):
    description: str = Field(..., description="Natural language query description", min_length=1)
    db_type: str = Field(default="mysql", description="Database type: mysql or postgresql")
    schema_context: Optional[str] = Field(default="", description="Optional schema for context")


@router.post("/nl-to-query")
async def nl_to_query(request: NLToQueryRequest):
    """Generate a database query from natural language description."""
    from agent.agent import get_agent
    from db.supabase_client import get_supabase_client

    if request.db_type not in ("mysql", "postgresql"):
        raise HTTPException(400, "db_type must be 'mysql' or 'postgresql'")

    agent = get_agent()
    result = await agent.nl_to_query(
        request.description,
        request.db_type,
        request.schema_context or "",
    )

    if "error" in result:
        raise HTTPException(500, result["error"])

    try:
        supabase = get_supabase_client()
        supabase.save_analysis(result)
    except Exception:
        pass

    return result
