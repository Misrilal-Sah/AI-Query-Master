"""
AI Query Master - Schema Review API
POST /api/review-schema
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api", tags=["Schema Review"])


class SchemaReviewRequest(BaseModel):
    schema_ddl: str = Field(..., alias="schema", description="DDL schema to analyze", min_length=1)
    db_type: str = Field(default="mysql", description="Database type")


@router.post("/review-schema")
async def review_schema(request: SchemaReviewRequest):
    """Analyze database schema for design issues."""
    from agent.agent import get_agent

    agent = get_agent()
    result = await agent.review_schema(request.schema_ddl, "mysql")

    if "error" in result:
        raise HTTPException(500, result["error"])

    return result
