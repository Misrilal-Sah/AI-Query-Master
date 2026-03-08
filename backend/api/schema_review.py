"""
AI Query Master - Schema Review API
POST /api/review-schema
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api", tags=["Schema Review"])


class SchemaReviewRequest(BaseModel):
    schema: str = Field(..., description="DDL schema to analyze", min_length=1)
    db_type: str = Field(default="mysql", description="Database type: mysql or postgresql")


@router.post("/review-schema")
async def review_schema(request: SchemaReviewRequest):
    """Analyze database schema for design issues."""
    from agent.agent import get_agent
    from db.supabase_client import get_supabase_client

    if request.db_type not in ("mysql", "postgresql"):
        raise HTTPException(400, "db_type must be 'mysql' or 'postgresql'")

    agent = get_agent()
    result = await agent.review_schema(request.schema, request.db_type)

    if "error" in result:
        raise HTTPException(500, result["error"])

    try:
        supabase = get_supabase_client()
        supabase.save_analysis(result)
    except Exception:
        pass

    return result
