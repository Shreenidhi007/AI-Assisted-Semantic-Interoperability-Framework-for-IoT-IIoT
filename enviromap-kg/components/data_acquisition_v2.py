"""
EnviroMap-KG — True Auto-Discovery Data Acquisition
====================================================
When ANY new database/environment is added to config/database.yaml with just
credentials, this module automatically:
  1. Connects to the database
  2. Discovers ALL schemas
  3. Discovers ALL tables in each schema
  4. Discovers ALL columns in each table (with data types)
  5. Identifies numeric sensor columns automatically
  6. Identifies the timestamp column automatically
  7. Fetches all rows up to row_limit

No hardcoding of table names or column names is needed.
"""

import psycopg2
import psycopg2.extras
import pandas as pd
import logging
from typing import Optional

logger = logging.getLogger("enviromap.DataAcquisition")


class DataAcquisitionAgent:
    """
    Fully auto-discovering database agent.
    Given only a database name + credentials, it finds everything automatically.
    """

    # Column name patterns that are likely timestamps
    TIMESTAMP_PATTERNS = [
        "timestamp", "time", "created_at", "updated_at",
        "datetime", "date_time", "recorded_at", "ts", "event_time"
    ]

    # Column name patterns to SKIP (non-sensor, metadata columns)
    SKIP_PATTERNS = [
        "id", "uid", "uuid", "key", "hash", "token",
        "name", "label", "description", "comment", "notes",
        "status", "type", "category", "tag", "flag"
    ]

    # PostgreSQL data types considered numeric (sensor values)
    NUMERIC_TYPES = {
        "integer", "bigint", "smallint", "numeric", "decimal",
        "real", "double precision", "float4", "float8",
        "int2", "int4", "int8"
    }

    def __init__(self, config: dict):
        self.config = config
        self.db_config = config.get("database", {})
        self.row_limit = self.db_config.get("row_limit", 15000)
        self.host = self.db_config.get("host", "127.0.0.1")
        self.port = self.db_config.get("port", 5432)
        self.user = self.db_config.get("user", "postgres")
        self.password = self.db_config.get("password", "postgres")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def discover_and_fetch_all(self) -> list[dict]:
        """
        Main entry point. Auto-discovers ALL databases, tables, and columns.
        Returns a list of domain datasets ready for profiling + mapping.

        Returns:
            [
              {
                "domain": "hydroponics",
                "database": "hydroponics",
                "schema": "public",
                "table": "onem2m_data",
                "timestamp_col": "timestamp",
                "sensor_columns": ["temperature", "humidity", "ph", ...],
                "all_columns": [...],
                "dataframe": pd.DataFrame(...)
              },
              ...
            ]
        """
        databases = self.db_config.get("databases", [])
        results = []

        for db_entry in databases:
            db_name = db_entry.get("name")
            domain = db_entry.get("domain", db_name)

            logger.info(f"Auto-discovering database: {db_name} (domain: {domain})")

            try:
                conn = self._connect(db_name)
            except Exception as e:
                logger.error(f"Cannot connect to {db_name}: {e}")
                continue

            try:
                # Step 1: Find all tables (auto or from config)
                configured_schema = db_entry.get("schema")
                configured_table = db_entry.get("table")

                if configured_schema and configured_table:
                    # Config explicitly specifies a table — still auto-discover columns
                    tables = [(configured_schema, configured_table)]
                    logger.info(f"  Using configured table: {configured_schema}.{configured_table}")
                else:
                    # True auto-discovery: find ALL tables
                    tables = self._discover_tables(conn, db_name)
                    logger.info(f"  Auto-discovered {len(tables)} table(s): {tables}")

                for schema, table in tables:
                    try:
                        dataset = self._process_table(
                            conn, db_name, domain, schema, table
                        )
                        if dataset is not None:
                            results.append(dataset)
                    except Exception as e:
                        logger.error(f"  Error processing {schema}.{table}: {e}")
                        continue

            finally:
                conn.close()

        logger.info(f"Auto-discovery complete: {len(results)} domain dataset(s) loaded")
        return results

    # ------------------------------------------------------------------
    # Step 1: Discover all tables in a database
    # ------------------------------------------------------------------

    def _discover_tables(self, conn, db_name: str) -> list[tuple[str, str]]:
        """
        Returns list of (schema, table) tuples for all user tables.
        Skips system schemas: pg_catalog, information_schema, pg_toast, etc.
        """
        query = """
            SELECT table_schema, table_name
            FROM information_schema.tables
            WHERE table_type = 'BASE TABLE'
              AND table_schema NOT IN (
                  'pg_catalog', 'information_schema',
                  'pg_toast', 'pg_temp_1', 'pg_toast_temp_1'
              )
            ORDER BY table_schema, table_name;
        """
        with conn.cursor() as cur:
            cur.execute(query)
            rows = cur.fetchall()

        tables = [(row[0], row[1]) for row in rows]
        logger.info(f"  [{db_name}] Found tables: {tables}")
        return tables

    # ------------------------------------------------------------------
    # Step 2: Discover all columns in a table
    # ------------------------------------------------------------------

    def _discover_columns(self, conn, schema: str, table: str) -> list[dict]:
        """
        Returns a list of column descriptors:
          [{"name": "temperature", "type": "double precision", "ordinal": 1}, ...]
        Uses information_schema for portability.
        """
        query = """
            SELECT
                column_name,
                data_type,
                ordinal_position,
                is_nullable
            FROM information_schema.columns
            WHERE table_schema = %s
              AND table_name   = %s
            ORDER BY ordinal_position;
        """
        with conn.cursor() as cur:
            cur.execute(query, (schema, table))
            rows = cur.fetchall()

        columns = [
            {
                "name": row[0],
                "type": row[1],
                "ordinal": row[2],
                "nullable": row[3] == "YES"
            }
            for row in rows
        ]
        logger.info(f"  [{schema}.{table}] Discovered {len(columns)} column(s): "
                    f"{[c['name'] for c in columns]}")
        return columns

    # ------------------------------------------------------------------
    # Step 3: Classify columns automatically
    # ------------------------------------------------------------------

    def _classify_columns(self, columns: list[dict]) -> dict:
        """
        Automatically classifies columns into:
          - timestamp_col : the time column (string, column name)
          - id_col        : primary key / row ID
          - sensor_cols   : numeric sensor measurement columns
          - skip_cols     : non-sensor columns to ignore
        """
        timestamp_col = None
        id_col = None
        sensor_cols = []
        skip_cols = []

        for col in columns:
            name_lower = col["name"].lower()
            dtype = col["type"].lower()

            # Identify timestamp column
            if any(p in name_lower for p in self.TIMESTAMP_PATTERNS):
                if "timestamp" in dtype or "time" in dtype or "date" in dtype:
                    timestamp_col = col["name"]
                    continue

            # Identify ID / key columns
            if name_lower in ("id", "uid", "uuid", "pk"):
                id_col = col["name"]
                skip_cols.append(col["name"])
                continue

            # Identify numeric sensor columns
            if dtype in self.NUMERIC_TYPES:
                # Skip columns with skip patterns
                if any(p in name_lower for p in self.SKIP_PATTERNS):
                    skip_cols.append(col["name"])
                else:
                    sensor_cols.append(col["name"])
            else:
                # Non-numeric, non-timestamp → skip
                if col["name"] != timestamp_col:
                    skip_cols.append(col["name"])

        result = {
            "timestamp_col": timestamp_col,
            "id_col": id_col,
            "sensor_cols": sensor_cols,
            "skip_cols": skip_cols
        }

        logger.info(f"  Column classification: "
                    f"timestamp={timestamp_col}, "
                    f"sensor_cols={sensor_cols}, "
                    f"skipped={skip_cols}")
        return result

    # ------------------------------------------------------------------
    # Step 4: Fetch data using discovered structure
    # ------------------------------------------------------------------

    def _fetch_data(self, conn, schema: str, table: str,
                    timestamp_col: Optional[str], limit: int) -> pd.DataFrame:
        """
        Fetches up to `limit` rows from the table, ordered by timestamp DESC
        (most recent first) if a timestamp column was discovered.
        Uses quoted identifiers to handle spaces in table/schema names.
        """
        safe_schema = f'"{schema}"'
        safe_table = f'"{table}"'

        if timestamp_col:
            safe_ts = f'"{timestamp_col}"'
            query = (
                f"SELECT * FROM {safe_schema}.{safe_table} "
                f"ORDER BY {safe_ts} DESC "
                f"LIMIT %s"
            )
        else:
            query = f"SELECT * FROM {safe_schema}.{safe_table} LIMIT %s"

        logger.info(f"  Fetching up to {limit} rows from {schema}.{table}")

        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(query, (limit,))
            rows = cur.fetchall()

        df = pd.DataFrame([dict(r) for r in rows])
        logger.info(f"  Fetched {len(df)} rows, {len(df.columns)} columns")
        return df

    # ------------------------------------------------------------------
    # Step 5: Combine everything into one processed dataset
    # ------------------------------------------------------------------

    def _process_table(self, conn, db_name: str, domain: str,
                       schema: str, table: str) -> Optional[dict]:
        """
        Full pipeline for one table:
          discover columns → classify → fetch → return structured dataset
        """
        # Discover all columns
        columns = self._discover_columns(conn, schema, table)
        if not columns:
            logger.warning(f"  {schema}.{table} has no columns — skipping")
            return None

        # Classify columns automatically
        classification = self._classify_columns(columns)
        sensor_cols = classification["sensor_cols"]
        timestamp_col = classification["timestamp_col"]

        if not sensor_cols:
            logger.warning(f"  {schema}.{table} has no numeric sensor columns — skipping")
            return None

        # Fetch data
        df = self._fetch_data(conn, schema, table, timestamp_col, self.row_limit)

        if df.empty:
            logger.warning(f"  {schema}.{table} returned 0 rows — skipping")
            return None

        # Filter to only sensor + timestamp columns
        keep_cols = sensor_cols.copy()
        if timestamp_col and timestamp_col in df.columns:
            keep_cols.insert(0, timestamp_col)

        df_sensor = df[[c for c in keep_cols if c in df.columns]].copy()

        logger.info(
            f"  [{domain}] {schema}.{table} ready: "
            f"{len(df_sensor)} rows x {len(sensor_cols)} sensor columns"
        )

        return {
            "domain": domain,
            "database": db_name,
            "schema": schema,
            "table": table,
            "timestamp_col": timestamp_col,
            "sensor_columns": sensor_cols,
            "all_columns": [c["name"] for c in columns],
            "column_types": {c["name"]: c["type"] for c in columns},
            "dataframe": df_sensor,
            "row_count": len(df_sensor),
        }

    # ------------------------------------------------------------------
    # Connection helper
    # ------------------------------------------------------------------

    def _connect(self, db_name: str):
        return psycopg2.connect(
            host=self.host,
            port=self.port,
            dbname=db_name,
            user=self.user,
            password=self.password,
            connect_timeout=10
        )

