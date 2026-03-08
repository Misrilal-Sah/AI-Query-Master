"""
AI Query Master - MySQL Connector
Read-only live database connection for schema inspection and EXPLAIN.
"""
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class MySQLConnector:
    """MySQL database connector for live analysis."""

    def __init__(self, host: str, port: int, database: str,
                 username: str, password: str):
        self.config = {
            "host": host,
            "port": port,
            "database": database,
            "user": username,
            "password": password,
        }
        self.connection = None

    def connect(self) -> Dict[str, Any]:
        """Establish a read-only MySQL connection."""
        try:
            import pymysql

            self.connection = pymysql.connect(
                **self.config,
                charset="utf8mb4",
                cursorclass=pymysql.cursors.DictCursor,
                connect_timeout=10,
                read_timeout=30,
            )

            # Set read-only mode
            with self.connection.cursor() as cursor:
                cursor.execute("SET SESSION TRANSACTION READ ONLY")

            logger.info(f"Connected to MySQL: {self.config['host']}:{self.config['port']}"
                         f"/{self.config['database']}")

            return {
                "success": True,
                "message": f"Connected to {self.config['database']} "
                           f"at {self.config['host']}:{self.config['port']}",
                "db_type": "mysql",
            }

        except Exception as e:
            logger.error(f"MySQL connection failed: {e}")
            return {
                "success": False,
                "error": str(e),
            }

    def disconnect(self):
        """Close the connection."""
        if self.connection:
            try:
                self.connection.close()
            except Exception:
                pass
            self.connection = None

    def get_schema(self) -> Dict[str, Any]:
        """Get database schema information."""
        if not self.connection:
            return {"error": "Not connected"}

        try:
            tables = []
            with self.connection.cursor() as cursor:
                # Get tables
                cursor.execute("""
                    SELECT TABLE_NAME, TABLE_ROWS, TABLE_COMMENT, ENGINE
                    FROM INFORMATION_SCHEMA.TABLES
                    WHERE TABLE_SCHEMA = %s
                    ORDER BY TABLE_NAME
                """, (self.config["database"],))
                table_rows = cursor.fetchall()

                for table in table_rows:
                    table_name = table["TABLE_NAME"]

                    # Get columns
                    cursor.execute("""
                        SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE,
                               COLUMN_KEY, COLUMN_DEFAULT, EXTRA,
                               CHARACTER_MAXIMUM_LENGTH
                        FROM INFORMATION_SCHEMA.COLUMNS
                        WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s
                        ORDER BY ORDINAL_POSITION
                    """, (self.config["database"], table_name))
                    columns = cursor.fetchall()

                    # Get indexes
                    cursor.execute("""
                        SELECT INDEX_NAME, COLUMN_NAME, NON_UNIQUE,
                               INDEX_TYPE
                        FROM INFORMATION_SCHEMA.STATISTICS
                        WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s
                        ORDER BY INDEX_NAME, SEQ_IN_INDEX
                    """, (self.config["database"], table_name))
                    indexes = cursor.fetchall()

                    # Get foreign keys
                    cursor.execute("""
                        SELECT CONSTRAINT_NAME, COLUMN_NAME,
                               REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME
                        FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
                        WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s
                        AND REFERENCED_TABLE_NAME IS NOT NULL
                    """, (self.config["database"], table_name))
                    foreign_keys = cursor.fetchall()

                    tables.append({
                        "name": table_name,
                        "rows": table.get("TABLE_ROWS"),
                        "engine": table.get("ENGINE"),
                        "comment": table.get("TABLE_COMMENT", ""),
                        "columns": columns,
                        "indexes": indexes,
                        "foreign_keys": foreign_keys,
                    })

            return {
                "success": True,
                "database": self.config["database"],
                "tables": tables,
                "table_count": len(tables),
            }

        except Exception as e:
            logger.error(f"Schema retrieval failed: {e}")
            return {"success": False, "error": str(e)}

    def run_explain(self, query: str) -> Dict[str, Any]:
        """Run EXPLAIN on a query."""
        if not self.connection:
            return {"error": "Not connected"}

        # Safety check — only allow SELECT/WITH queries
        clean = query.strip().upper()
        if not clean.startswith(("SELECT", "WITH")):
            return {
                "success": False,
                "error": "EXPLAIN only allowed for SELECT queries (read-only mode)",
            }

        try:
            with self.connection.cursor() as cursor:
                # Regular EXPLAIN
                cursor.execute(f"EXPLAIN {query}")
                explain_result = cursor.fetchall()

                # EXPLAIN FORMAT=JSON for detailed info
                cursor.execute(f"EXPLAIN FORMAT=JSON {query}")
                explain_json = cursor.fetchone()

            return {
                "success": True,
                "explain": explain_result,
                "explain_json": explain_json,
            }

        except Exception as e:
            logger.error(f"EXPLAIN failed: {e}")
            return {"success": False, "error": str(e)}

    def __del__(self):
        self.disconnect()
