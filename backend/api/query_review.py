"""
AI Query Master - Query Review API
POST /api/review-query
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

router = APIRouter(prefix="/api", tags=["Query Review"])


class QueryReviewRequest(BaseModel):
    query: str = Field(..., description="SQL query to analyze", min_length=1)
    db_type: str = Field(default="mysql", description="Database type: mysql or postgresql")


@router.post("/review-query")
async def review_query(request: QueryReviewRequest):
    """Analyze a SQL query for performance, security, and readability issues."""
    from agent.agent import get_agent
    from db.supabase_client import get_supabase_client

    if request.db_type not in ("mysql", "postgresql"):
        raise HTTPException(400, "db_type must be 'mysql' or 'postgresql'")

    agent = get_agent()
    result = await agent.review_query(request.query, request.db_type)

    if "error" in result:
        raise HTTPException(500, result["error"])

    # Save to history (async, don't block)
    try:
        supabase = get_supabase_client()
        supabase.save_analysis(result)
    except Exception:
        pass  # Don't fail the request if history save fails

    return result
