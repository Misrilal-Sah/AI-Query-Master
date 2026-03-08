"""
AI Query Master - History API
GET /api/history
GET /api/history/{id}
DELETE /api/history/{id}
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional

router = APIRouter(prefix="/api", tags=["History"])


@router.get("/history")
async def get_history(
    limit: int = Query(default=20, le=100),
    offset: int = Query(default=0, ge=0),
    feature: Optional[str] = Query(default=None),
    db_type: Optional[str] = Query(default=None),
):
    """Get analysis history."""
    from db.supabase_client import get_supabase_client

    supabase = get_supabase_client()
    result = supabase.get_history(limit, offset, feature, db_type)
    return result


@router.get("/history/{analysis_id}")
async def get_analysis(analysis_id: str):
    """Get a single analysis by ID."""
    from db.supabase_client import get_supabase_client

    supabase = get_supabase_client()
    result = supabase.get_analysis(analysis_id)

    if result is None:
        raise HTTPException(404, "Analysis not found")

    return result


@router.delete("/history/{analysis_id}")
async def delete_analysis(analysis_id: str):
    """Delete an analysis by ID."""
    from db.supabase_client import get_supabase_client

    supabase = get_supabase_client()
    success = supabase.delete_analysis(analysis_id)

    if not success:
        raise HTTPException(500, "Failed to delete analysis")

    return {"success": True, "message": "Analysis deleted"}
