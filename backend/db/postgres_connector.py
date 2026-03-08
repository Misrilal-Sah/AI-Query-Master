"""
AI Query Master - PostgreSQL Connector
Read-only live database connection for schema inspection and EXPLAIN.
"""
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class PostgresConnector:
    """PostgreSQL database connector for live analysis."""

    def __init__(self, host: str, port: int, database: str,
                 username: str, password: str):
        self.config = {
            "host": host,
            "port": port,
            "dbname": database,
            "user": username,
            "password": password,
        }
        self.connection = None

    def connect(self) -> Dict[str, Any]:
        """Establish a read-only PostgreSQL connection."""
        try:
            import psycopg2
            import psycopg2.extras

            self.connection = psycopg2.connect(
                **self.config,
                connect_timeout=10,
                options="-c statement_timeout=30000",
            )
            self.connection.set_session(readonly=True, autocommit=True)

            logger.info(f"Connected to PostgreSQL: {self.config['host']}:{self.config['port']}"
                         f"/{self.config['dbname']}")

            return {
                "success": True,
                "message": f"Connected to {self.config['dbname']} "
                           f"at {self.config['host']}:{self.config['port']}",
                "db_type": "postgresql",
            }

        except Exception as e:
            logger.error(f"PostgreSQL connection failed: {e}")
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
            import psycopg2.extras
            tables = []

            with self.connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                # Get tables
                cursor.execute("""
                    SELECT t.table_name,
                           pg_stat_user_tables.n_live_tup as row_count,
                           obj_description(pgc.oid) as comment
                    FROM information_schema.tables t
                    LEFT JOIN pg_stat_user_tables
                        ON pg_stat_user_tables.relname = t.table_name
                    LEFT JOIN pg_class pgc
                        ON pgc.relname = t.table_name
                    WHERE t.table_schema = 'public'
                    AND t.table_type = 'BASE TABLE'
                    ORDER BY t.table_name
                """)
                table_rows = cursor.fetchall()

                for table in table_rows:
                    table_name = table["table_name"]

                    # Get columns
                    cursor.execute("""
                        SELECT column_name, data_type, is_nullable,
                               column_default, character_maximum_length,
                               udt_name
                        FROM information_schema.columns
                        WHERE table_schema = 'public' AND table_name = %s
                        ORDER BY ordinal_position
                    """, (table_name,))
                    columns = [dict(row) for row in cursor.fetchall()]

                    # Get indexes
                    cursor.execute("""
                        SELECT indexname, indexdef
                        FROM pg_indexes
                        WHERE schemaname = 'public' AND tablename = %s
                    """, (table_name,))
                    indexes = [dict(row) for row in cursor.fetchall()]

                    # Get foreign keys
                    cursor.execute("""
                        SELECT
                            kcu.column_name,
                            ccu.table_name AS referenced_table,
                            ccu.column_name AS referenced_column,
                            tc.constraint_name
                        FROM information_schema.table_constraints tc
                        JOIN information_schema.key_column_usage kcu
                            ON tc.constraint_name = kcu.constraint_name
                        JOIN information_schema.constraint_column_usage ccu
                            ON ccu.constraint_name = tc.constraint_name
                        WHERE tc.constraint_type = 'FOREIGN KEY'
                        AND tc.table_name = %s
                    """, (table_name,))
                    foreign_keys = [dict(row) for row in cursor.fetchall()]

                    # Get primary key columns
                    cursor.execute("""
                        SELECT kcu.column_name
                        FROM information_schema.table_constraints tc
                        JOIN information_schema.key_column_usage kcu
                            ON tc.constraint_name = kcu.constraint_name
                        WHERE tc.constraint_type = 'PRIMARY KEY'
                        AND tc.table_name = %s
                    """, (table_name,))
                    pk_cols = [row["column_name"] for row in cursor.fetchall()]

                    tables.append({
                        "name": table_name,
                        "rows": table.get("row_count"),
                        "comment": table.get("comment", ""),
                        "columns": columns,
                        "indexes": indexes,
                        "foreign_keys": foreign_keys,
                        "primary_key": pk_cols,
                    })

            return {
                "success": True,
                "database": self.config["dbname"],
                "tables": tables,
                "table_count": len(tables),
            }

        except Exception as e:
            logger.error(f"Schema retrieval failed: {e}")
            return {"success": False, "error": str(e)}

    def run_explain(self, query: str) -> Dict[str, Any]:
        """Run EXPLAIN ANALYZE on a query."""
        if not self.connection:
            return {"error": "Not connected"}

        # Safety — only allow SELECT/WITH
        clean = query.strip().upper()
        if not clean.startswith(("SELECT", "WITH")):
            return {
                "success": False,
                "error": "EXPLAIN only allowed for SELECT queries (read-only mode)",
            }

        try:
            import psycopg2.extras

            with self.connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                # EXPLAIN with JSON format
                cursor.execute(f"EXPLAIN (FORMAT JSON, ANALYZE, BUFFERS) {query}")
                explain_json = cursor.fetchone()[0]

                # Text format too
                cursor.execute(f"EXPLAIN (ANALYZE, BUFFERS) {query}")
                explain_text = cursor.fetchall()

            return {
                "success": True,
                "explain_json": explain_json,
                "explain_text": [row[0] if isinstance(row, tuple) else str(row)
                                 for row in explain_text],
            }

        except Exception as e:
            logger.error(f"EXPLAIN failed: {e}")
            return {"success": False, "error": str(e)}

    def __del__(self):
        self.disconnect()
