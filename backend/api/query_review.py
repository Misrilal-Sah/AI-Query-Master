"""
AI Query Master - Query Review API
POST /api/review-query
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api", tags=["Query Review"])


class QueryReviewRequest(BaseModel):
    query: str = Field(..., description="SQL query to analyze", min_length=1)
    db_type: str = Field(default="mysql", description="Database type")


@router.post("/review-query")
async def review_query(request: QueryReviewRequest):
    """Analyze a SQL query for performance, security, and readability issues."""
    from agent.agent import get_agent

    agent = get_agent()
    result = await agent.review_query(request.query, "mysql")

    if "error" in result:
        raise HTTPException(500, result["error"])

    return result
