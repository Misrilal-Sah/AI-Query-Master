"""
AI Query Master - Live Database API
POST /api/connect-db
POST /api/db-schema
POST /api/explain
POST /api/disconnect-db
"""
import json
import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["Live Database"])

# In-memory session store for database connections (never persisted)
_active_connections: Dict[str, Any] = {}


class ConnectDBRequest(BaseModel):
    host: str = Field(..., description="Database host")
    port: int = Field(..., description="Database port")
    database: str = Field(..., description="Database name")
    username: str = Field(..., description="Username")
    password: str = Field(..., description="Password")
    db_type: str = Field(..., description="mysql or postgresql")


class ExplainRequest(BaseModel):
    query: str = Field(..., description="Query to EXPLAIN")
    session_id: str = Field(..., description="Session ID from connect")


class AnalyzeRequest(BaseModel):
    session_id: str = Field(..., description="Session ID from connect")
    query: Optional[str] = Field(default="", description="Optional query to analyze")


@router.post("/connect-db")
async def connect_db(request: ConnectDBRequest):
    """
    Connect to a database (in-memory only, never stored).
    Returns a session_id for subsequent requests.
    """
    if request.db_type not in ("mysql", "postgresql"):
        raise HTTPException(400, "db_type must be 'mysql' or 'postgresql'")

    try:
        if request.db_type == "mysql":
            from db.mysql_connector import MySQLConnector
            connector = MySQLConnector(
                host=request.host,
                port=request.port,
                database=request.database,
                username=request.username,
                password=request.password,
            )
        else:
            from db.postgres_connector import PostgresConnector
            connector = PostgresConnector(
                host=request.host,
                port=request.port,
                database=request.database,
                username=request.username,
                password=request.password,
            )

        result = connector.connect()

        if not result.get("success"):
            raise HTTPException(400, result.get("error", "Connection failed"))

        # Store in memory with a session ID
        import uuid
        session_id = str(uuid.uuid4())
        _active_connections[session_id] = {
            "connector": connector,
            "db_type": request.db_type,
            "database": request.database,
        }

        return {
            "success": True,
            "session_id": session_id,
            "message": result["message"],
            "db_type": request.db_type,
            "notice": "⚠️ Connection is in-memory only. Credentials are NOT stored. "
                      "Connection uses READ-ONLY mode.",
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Connection failed: {str(e)}")


@router.post("/db-schema")
async def get_db_schema(request: dict):
    """Get schema from a connected database."""
    session_id = request.get("session_id")
    if not session_id or session_id not in _active_connections:
        raise HTTPException(400, "Invalid or expired session. Please reconnect.")

    session = _active_connections[session_id]
    connector = session["connector"]

    result = connector.get_schema()
    if not result.get("success"):
        raise HTTPException(500, result.get("error", "Failed to read schema"))

    return result


@router.post("/explain")
async def run_explain(request: ExplainRequest):
    """Run EXPLAIN on a query using the connected database."""
    if request.session_id not in _active_connections:
        raise HTTPException(400, "Invalid or expired session. Please reconnect.")

    session = _active_connections[request.session_id]
    connector = session["connector"]

    result = connector.run_explain(request.query)
    if not result.get("success"):
        raise HTTPException(400, result.get("error", "EXPLAIN failed"))

    return result


@router.post("/analyze-live")
async def analyze_live(request: AnalyzeRequest):
    """Analyze a live database using the AI agent."""
    if request.session_id not in _active_connections:
        raise HTTPException(400, "Invalid or expired session. Please reconnect.")

    session = _active_connections[request.session_id]
    connector = session["connector"]
    db_type = session["db_type"]

    # Get schema
    schema_result = connector.get_schema()
    if not schema_result.get("success"):
        raise HTTPException(500, "Failed to read schema")

    # Build compact schema summary — prioritize tables mentioned in the query
    import re
    all_tables = schema_result.get("tables", [])
    table_names_lower = {t["name"].lower(): t for t in all_tables}

    # Extract table names referenced in the query
    query_tables = []
    if request.query:
        # Match FROM/JOIN/UPDATE/INTO + table name
        matches = re.findall(
            r'(?:FROM|JOIN|UPDATE|INTO)\s+[`"]?(\w+)[`"]?',
            request.query, re.IGNORECASE
        )
        for m in matches:
            if m.lower() in table_names_lower:
                query_tables.append(table_names_lower[m.lower()])

    # Build: query tables first (full detail), then remaining tables (summary)
    seen = {t["name"] for t in query_tables}
    remaining = [t for t in all_tables if t["name"] not in seen]

    def build_table_line(table):
        cols = []
        for c in (table.get("columns") or []):
            col_name = c.get("COLUMN_NAME") or c.get("column_name", "?")
            col_type = c.get("DATA_TYPE") or c.get("data_type", "?")
            pk = " PK" if c.get("COLUMN_KEY") == "PRI" else ""
            cols.append(f"{col_name} {col_type}{pk}")
        row_info = f" (~{table.get('rows', '?')} rows)" if table.get("rows") else ""
        return f"{table['name']}({', '.join(cols)}){row_info}"

    schema_lines = []
    # Always include tables from the query
    for t in query_tables:
        schema_lines.append(build_table_line(t))
    # Fill remaining up to 30 tables
    for t in remaining[:max(0, 30 - len(query_tables))]:
        schema_lines.append(build_table_line(t))
    schema_summary = "\n".join(schema_lines)

    # Get EXPLAIN if query provided
    explain_output = ""
    if request.query:
        explain_result = connector.run_explain(request.query)
        if explain_result.get("success"):
            explain_output = json.dumps(explain_result, indent=2)

    # Run AI analysis
    from agent.agent import get_agent
    agent = get_agent()

    result = await agent.analyze_live_db(
        schema_info=schema_summary,
        query=request.query or "",
        explain_output=explain_output,
        db_type=db_type,
    )

    return result


@router.post("/disconnect-db")
async def disconnect_db(request: dict):
    """Disconnect from a database and clear session."""
    session_id = request.get("session_id")
    if session_id and session_id in _active_connections:
        session = _active_connections.pop(session_id)
        connector = session["connector"]
        connector.disconnect()
        return {"success": True, "message": "Disconnected successfully"}

    return {"success": True, "message": "No active connection"}
