"""
AI Query Master - Supabase Client
Application database for query history and saved analyses.
"""
import os
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class SupabaseClient:
    """Client for Supabase application database."""

    def __init__(self):
        self.url = os.getenv("SUPABASE_URL")
        self.key = os.getenv("SUPABASE_KEY")
        self.client = None

        if self.url and self.key:
            try:
                from supabase import create_client
                self.client = create_client(self.url, self.key)
                logger.info("Supabase client initialized")
            except Exception as e:
                logger.warning(f"Supabase init failed: {e}. History features disabled.")
        else:
            logger.warning("Supabase credentials not configured. History features disabled.")

    @property
    def is_available(self) -> bool:
        return self.client is not None

    def save_analysis(self, data: Dict[str, Any]) -> Optional[str]:
        """Save an analysis to history."""
        if not self.is_available:
            logger.warning("Supabase not available, skipping save")
            return None

        try:
            record = {
                "db_type": data.get("db_type", "mysql"),
                "feature": data.get("feature", "query_review"),
                "input_text": data.get("input", "")[:10000],
                "result": {
                    "analysis": data.get("analysis", ""),
                    "static_issues": data.get("static_issues", []),
                    "index_recommendations": data.get("index_recommendations", []),
                    "provider": data.get("provider", ""),
                    "sources": data.get("sources", []),
                    "steps": data.get("steps", []),
                    "reflection_log": data.get("reflection_log", []),
                },
                "scores": data.get("scores"),
                "confidence": data.get("confidence"),
            }

            result = self.client.table("query_history").insert(record).execute()

            if result.data:
                record_id = result.data[0].get("id")
                logger.info(f"Analysis saved to Supabase: {record_id}")
                return record_id

            return None

        except Exception as e:
            logger.error(f"Failed to save analysis: {e}")
            return None

    def get_history(
        self,
        limit: int = 20,
        offset: int = 0,
        feature: str = None,
        db_type: str = None,
    ) -> Dict[str, Any]:
        """Get analysis history."""
        if not self.is_available:
            return {"items": [], "total": 0}

        try:
            query = self.client.table("query_history") \
                .select("*", count="exact") \
                .order("created_at", desc=True) \
                .range(offset, offset + limit - 1)

            if feature:
                query = query.eq("feature", feature)
            if db_type:
                query = query.eq("db_type", db_type)

            result = query.execute()

            return {
                "items": result.data or [],
                "total": result.count or 0,
            }

        except Exception as e:
            logger.error(f"Failed to get history: {e}")
            return {"items": [], "total": 0}

    def get_analysis(self, analysis_id: str) -> Optional[Dict]:
        """Get a single analysis by ID."""
        if not self.is_available:
            return None

        try:
            result = self.client.table("query_history") \
                .select("*") \
                .eq("id", analysis_id) \
                .limit(1) \
                .execute()

            if result.data:
                return result.data[0]
            return None

        except Exception as e:
            logger.error(f"Failed to get analysis: {e}")
            return None

    def delete_analysis(self, analysis_id: str) -> bool:
        """Delete an analysis by ID."""
        if not self.is_available:
            return False

        try:
            self.client.table("query_history") \
                .delete() \
                .eq("id", analysis_id) \
                .execute()
            return True
        except Exception as e:
            logger.error(f"Failed to delete analysis: {e}")
            return False


# Singleton
_supabase_client: Optional[SupabaseClient] = None


def get_supabase_client() -> SupabaseClient:
    """Get or create the singleton Supabase client."""
    global _supabase_client
    if _supabase_client is None:
        _supabase_client = SupabaseClient()
    return _supabase_client
