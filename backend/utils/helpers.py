"""
AI Query Master - Utility Helpers
"""
import re
from typing import Optional


def extract_sql_from_markdown(text: str) -> Optional[str]:
    """Extract SQL code from markdown code blocks."""
    match = re.search(r"```sql\s*\n(.*?)```", text, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()

    match = re.search(r"```\s*\n(.*?)```", text, re.DOTALL)
    if match:
        return match.group(1).strip()

    return None


def truncate_text(text: str, max_length: int = 500) -> str:
    """Truncate text to max length with ellipsis."""
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."


def format_schema_for_display(schema_data: dict) -> str:
    """Format schema data from live DB into readable text."""
    lines = []
    for table in schema_data.get("tables", []):
        lines.append(f"Table: {table['name']}")
        if table.get("rows"):
            lines.append(f"  Rows: ~{table['rows']}")

        for col in table.get("columns", []):
            col_name = col.get("column_name") or col.get("COLUMN_NAME", "")
            col_type = col.get("data_type") or col.get("DATA_TYPE", "")
            nullable = col.get("is_nullable") or col.get("IS_NULLABLE", "")
            lines.append(f"  - {col_name} {col_type} {'NULL' if nullable == 'YES' else 'NOT NULL'}")

        if table.get("indexes"):
            lines.append("  Indexes:")
            for idx in table["indexes"]:
                idx_name = idx.get("indexname") or idx.get("INDEX_NAME", "")
                lines.append(f"    - {idx_name}")

        lines.append("")

    return "\n".join(lines)
