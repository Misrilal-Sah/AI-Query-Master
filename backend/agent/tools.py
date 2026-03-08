"""
AI Query Master - Tool Calling Layer
External tools the agent can invoke during analysis.
"""
import logging
import re
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


# ============================================================
# Tool: analyze_query
# ============================================================
def analyze_query(query: str, db_type: str = "mysql") -> Dict[str, Any]:
    """
    Statically analyze a SQL query for common issues.
    Returns detected issues categorized by type.
    """
    issues = []
    query_upper = query.upper().strip()
    query_lower = query.lower().strip()

    # --- Performance Issues ---
    if "SELECT *" in query_upper:
        issues.append({
            "type": "performance",
            "severity": "warning",
            "title": "SELECT * Usage",
            "description": "Using SELECT * retrieves all columns, which can cause unnecessary I/O and network overhead. Specify only the columns you need.",
            "line": _find_pattern_line(query, r"SELECT\s+\*"),
        })

    # Nested subqueries in WHERE IN
    if re.search(r"WHERE\s+\w+\s+IN\s*\(\s*SELECT", query_upper):
        issues.append({
            "type": "performance",
            "severity": "error",
            "title": "Subquery in WHERE IN",
            "description": "Using a subquery inside WHERE IN can be very slow. Consider using a JOIN instead.",
            "line": _find_pattern_line(query, r"WHERE\s+\w+\s+IN\s*\(\s*SELECT"),
        })

    # Missing WHERE clause on UPDATE/DELETE
    if re.search(r"(UPDATE|DELETE\s+FROM)\s+\w+\s*(?!.*WHERE)", query_upper):
        issues.append({
            "type": "security",
            "severity": "critical",
            "title": "Missing WHERE Clause",
            "description": "UPDATE or DELETE without a WHERE clause will affect ALL rows in the table.",
            "line": _find_pattern_line(query, r"(UPDATE|DELETE\s+FROM)"),
        })

    # ORDER BY without LIMIT
    if "ORDER BY" in query_upper and "LIMIT" not in query_upper:
        if "INSERT" not in query_upper and "UPDATE" not in query_upper:
            issues.append({
                "type": "performance",
                "severity": "warning",
                "title": "ORDER BY Without LIMIT",
                "description": "Sorting large result sets without LIMIT can be expensive. Consider adding LIMIT if you don't need all rows.",
                "line": _find_pattern_line(query, r"ORDER\s+BY"),
            })

    # Multiple JOINs without indexes hint
    join_count = len(re.findall(r"\bJOIN\b", query_upper))
    if join_count >= 3:
        issues.append({
            "type": "performance",
            "severity": "warning",
            "title": f"Multiple JOINs ({join_count})",
            "description": f"Query uses {join_count} JOINs. Ensure proper indexes exist on all join columns for optimal performance.",
        })

    # LIKE with leading wildcard
    if re.search(r"LIKE\s+['\"]%", query_upper):
        issues.append({
            "type": "performance",
            "severity": "warning",
            "title": "Leading Wildcard in LIKE",
            "description": "LIKE '%value' cannot use indexes and causes full table scans. Consider full-text search instead.",
            "line": _find_pattern_line(query, r"LIKE\s+['\"]%"),
        })

    # OR in WHERE clause
    if re.search(r"WHERE\s+.*\bOR\b", query_upper):
        issues.append({
            "type": "performance",
            "severity": "info",
            "title": "OR in WHERE Clause",
            "description": "OR conditions can prevent index usage. Consider using UNION or restructuring the query.",
            "line": _find_pattern_line(query, r"\bOR\b"),
        })

    # NOT IN usage
    if "NOT IN" in query_upper:
        issues.append({
            "type": "performance",
            "severity": "warning",
            "title": "NOT IN Usage",
            "description": "NOT IN can be slow with subqueries and doesn't handle NULLs well. Consider using NOT EXISTS or LEFT JOIN ... IS NULL.",
            "line": _find_pattern_line(query, r"NOT\s+IN"),
        })

    # --- Security Issues ---
    # String concatenation patterns (potential SQL injection)
    if re.search(r"['\"]?\s*\+\s*\w+\s*\+\s*['\"]?", query) or re.search(r"\$\{?\w+\}?", query):
        issues.append({
            "type": "security",
            "severity": "critical",
            "title": "Potential SQL Injection",
            "description": "Query appears to use string concatenation for building SQL. Use parameterized queries instead.",
        })

    # --- Readability Issues ---
    # No aliases on JOINed tables
    if join_count > 0 and not re.search(r"\bAS\s+\w+", query_upper):
        issues.append({
            "type": "readability",
            "severity": "info",
            "title": "Missing Table Aliases",
            "description": "Using aliases for joined tables improves query readability.",
        })

    # Very long query without formatting
    lines = query.strip().split("\n")
    if len(lines) == 1 and len(query) > 200:
        issues.append({
            "type": "readability",
            "severity": "info",
            "title": "Query Format",
            "description": "Long single-line queries are hard to read. Consider formatting with line breaks.",
        })

    # --- Database-specific Issues ---
    if db_type == "mysql":
        if "OFFSET" in query_upper and "LIMIT" in query_upper:
            # Check for large OFFSET
            offset_match = re.search(r"OFFSET\s+(\d+)", query_upper)
            if offset_match and int(offset_match.group(1)) > 10000:
                issues.append({
                    "type": "performance",
                    "severity": "warning",
                    "title": "Large OFFSET Value",
                    "description": "MySQL handles large OFFSET values poorly. Consider keyset pagination instead.",
                })

    if db_type == "postgresql":
        if "DISTINCT ON" in query_upper and "ORDER BY" not in query_upper:
            issues.append({
                "type": "readability",
                "severity": "warning",
                "title": "DISTINCT ON Without ORDER BY",
                "description": "DISTINCT ON in PostgreSQL should be paired with ORDER BY to get deterministic results.",
            })

    return {
        "issues": issues,
        "total_issues": len(issues),
        "by_type": _group_issues(issues),
        "query_length": len(query),
        "join_count": join_count,
    }


# ============================================================
# Tool: analyze_schema
# ============================================================
def analyze_schema(schema: str, db_type: str = "mysql") -> Dict[str, Any]:
    """
    Analyze database schema (DDL) for common issues.
    """
    issues = []
    schema_upper = schema.upper()

    # Parse CREATE TABLE statements
    tables = re.findall(
        r"CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?[`\"]?(\w+)[`\"]?\s*\((.*?)\)\s*;",
        schema,
        re.IGNORECASE | re.DOTALL,
    )

    for table_name, table_body in tables:
        table_upper = table_body.upper()

        # Missing PRIMARY KEY
        if "PRIMARY KEY" not in table_upper and "SERIAL" not in table_upper:
            issues.append({
                "type": "schema",
                "severity": "critical",
                "title": f"Missing Primary Key: {table_name}",
                "description": f"Table '{table_name}' has no primary key. Every table should have a primary key for data integrity and performance.",
            })

        # Using TEXT for everything
        text_count = len(re.findall(r"\bTEXT\b", table_upper))
        varchar_count = len(re.findall(r"\bVARCHAR\b", table_upper))
        if text_count > 2 and varchar_count == 0:
            issues.append({
                "type": "schema",
                "severity": "warning",
                "title": f"Overuse of TEXT Type: {table_name}",
                "description": f"Table '{table_name}' uses TEXT extensively. Use VARCHAR(n) for columns with known max length for better performance.",
            })

        # Missing NOT NULL on important columns
        columns = re.findall(r"(\w+)\s+(INT|INTEGER|VARCHAR|TEXT|BOOLEAN|TIMESTAMP|DATE)", table_upper)
        nullable_count = 0
        for col_name, col_type in columns:
            col_pattern = f"{col_name}\\s+{col_type}"
            if not re.search(col_pattern + r".*NOT\s+NULL", table_upper):
                nullable_count += 1

        if nullable_count > len(columns) * 0.7 and len(columns) > 2:
            issues.append({
                "type": "schema",
                "severity": "info",
                "title": f"Many Nullable Columns: {table_name}",
                "description": f"Table '{table_name}' has {nullable_count} nullable columns. Consider adding NOT NULL constraints where appropriate.",
            })

        # Missing created_at / updated_at timestamps
        if "CREATED_AT" not in table_upper and "CREATEDAT" not in table_upper:
            issues.append({
                "type": "schema",
                "severity": "info",
                "title": f"Missing Timestamps: {table_name}",
                "description": f"Table '{table_name}' has no created_at column. Consider adding timestamp columns for auditing.",
            })

        # No indexes defined
        if "INDEX" not in table_upper and "KEY" not in table_upper:
            if "FOREIGN" not in table_upper:
                issues.append({
                    "type": "performance",
                    "severity": "warning",
                    "title": f"No Indexes Defined: {table_name}",
                    "description": f"Table '{table_name}' has no indexes other than the primary key. Consider adding indexes on frequently queried columns.",
                })

        # Naming convention issues
        if table_name != table_name.lower() and table_name != table_name.upper():
            issues.append({
                "type": "readability",
                "severity": "info",
                "title": f"Inconsistent Naming: {table_name}",
                "description": f"Table name '{table_name}' uses mixed case. Use consistent snake_case naming.",
            })

    if not tables:
        issues.append({
            "type": "schema",
            "severity": "info",
            "title": "No CREATE TABLE Found",
            "description": "Could not parse any CREATE TABLE statements. Make sure the schema is valid DDL.",
        })

    return {
        "issues": issues,
        "total_issues": len(issues),
        "tables_found": len(tables),
        "table_names": [t[0] for t in tables],
        "by_type": _group_issues(issues),
    }


# ============================================================
# Tool: generate_index_recommendation
# ============================================================
def generate_index_recommendation(query: str, schema: str = "", db_type: str = "mysql") -> List[Dict]:
    """Generate index recommendations based on query patterns."""
    recommendations = []
    query_upper = query.upper()

    # Extract WHERE columns
    where_cols = re.findall(r"WHERE\s+(?:.*?)(\w+)\s*[=<>!]", query, re.IGNORECASE)

    # Extract JOIN columns
    join_cols = re.findall(r"(?:JOIN|ON)\s+.*?(\w+)\.(\w+)\s*=\s*(\w+)\.(\w+)", query, re.IGNORECASE)

    # Extract ORDER BY columns
    order_cols = re.findall(r"ORDER\s+BY\s+([\w.,\s]+)", query, re.IGNORECASE)

    # Extract GROUP BY columns
    group_cols = re.findall(r"GROUP\s+BY\s+([\w.,\s]+)", query, re.IGNORECASE)

    # Recommend indexes for WHERE columns
    for col in where_cols:
        recommendations.append({
            "column": col,
            "reason": "Used in WHERE clause filter",
            "index_type": "B-tree",
            "sql": f"CREATE INDEX idx_{col.lower()} ON table_name({col});",
            "priority": "high",
        })

    # Recommend indexes for JOIN columns
    for match in join_cols:
        t1, c1, t2, c2 = match
        recommendations.append({
            "column": f"{t1}.{c1}",
            "reason": f"JOIN condition between {t1} and {t2}",
            "index_type": "B-tree",
            "sql": f"CREATE INDEX idx_{t1}_{c1} ON {t1}({c1});",
            "priority": "high",
        })

    # Recommend indexes for ORDER BY
    if order_cols:
        cols = [c.strip() for c in order_cols[0].split(",")]
        for col in cols:
            col_clean = col.replace(" ASC", "").replace(" DESC", "").strip()
            recommendations.append({
                "column": col_clean,
                "reason": "Used in ORDER BY clause",
                "index_type": "B-tree",
                "sql": f"CREATE INDEX idx_{col_clean.lower()} ON table_name({col_clean});",
                "priority": "medium",
            })

    return recommendations


# ============================================================
# Helpers
# ============================================================
def _find_pattern_line(query: str, pattern: str) -> Optional[int]:
    """Find the line number where a pattern first appears."""
    lines = query.split("\n")
    for i, line in enumerate(lines, 1):
        if re.search(pattern, line, re.IGNORECASE):
            return i
    return None


def _group_issues(issues: List[Dict]) -> Dict[str, int]:
    """Group issues by type."""
    groups = {}
    for issue in issues:
        t = issue.get("type", "other")
        groups[t] = groups.get(t, 0) + 1
    return groups


# ============================================================
# Tool Registry (for agent tool-calling)
# ============================================================
TOOL_REGISTRY = {
    "analyze_query": {
        "function": analyze_query,
        "description": "Analyze a SQL query for performance, security, and readability issues",
        "parameters": {"query": "str", "db_type": "str"},
    },
    "analyze_schema": {
        "function": analyze_schema,
        "description": "Analyze database schema (DDL) for design issues",
        "parameters": {"schema": "str", "db_type": "str"},
    },
    "generate_index_recommendation": {
        "function": generate_index_recommendation,
        "description": "Generate index recommendations for a query",
        "parameters": {"query": "str", "schema": "str", "db_type": "str"},
    },
}
