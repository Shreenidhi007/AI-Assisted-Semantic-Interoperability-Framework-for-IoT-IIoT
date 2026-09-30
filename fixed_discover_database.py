#!/usr/bin/env python3
"""
Database Discovery Script for EnviroMap-KG.
Connects to PostgreSQL and discovers all available databases,
schemas, tables, and their column metadata.
"""

import argparse
import json
import os
import sys

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

import psycopg2
import psycopg2.extras

def main():
    parser = argparse.ArgumentParser(description="Discover PostgreSQL database structure")
    parser.add_argument("--host", default="127.0.0.1", help="PostgreSQL host")
    parser.add_argument("--port", default=5432, type=int, help="PostgreSQL port")
    parser.add_argument("--user", default="postgres", help="PostgreSQL user")
    parser.add_argument("--password", default="postgres", help="PostgreSQL password")
    parser.add_argument("--output", default=None, help="Output JSON file path")
    args = parser.parse_args()

    print("=" * 70)
    print("EnviroMap-KG — Database & Environment Discovery")
    print(f"Host: {args.host}:{args.port}")
    print("=" * 70)

    # Step 1: Connect to PostgreSQL server to discover all databases
    try:
        conn = psycopg2.connect(
            host=args.host, port=args.port, user=args.user, password=args.password, dbname="postgres",
            connect_timeout=5
        )
    except Exception:
        # Fallback to local socket / peer
        conn = psycopg2.connect(dbname="postgres")

    cur = conn.cursor()
    cur.execute("SELECT datname FROM pg_database WHERE datistemplate = false ORDER BY datname;")
    all_dbs = [r[0] for r in cur.fetchall() if r[0] not in ('postgres',)]
    conn.close()

    print(f"\nDiscovered {len(all_dbs)} Environment Database(s):")
    for db in all_dbs:
        print(f"  • {db}")

    all_metadata = {}

    # Step 2: Discover tables and columns for each database
    for db_name in all_dbs:
        print(f"\n{'─' * 50}")
        print(f"Database: {db_name}")
        print(f"{'─' * 50}")

        try:
            try:
                db_conn = psycopg2.connect(
                    host=args.host, port=args.port, user=args.user, password=args.password, dbname=db_name,
                    connect_timeout=5
                )
            except Exception:
                db_conn = psycopg2.connect(dbname=db_name)

            db_cur = db_conn.cursor()
            
            # Query non-system tables
            db_cur.execute("""
                SELECT table_schema, table_name 
                FROM information_schema.tables 
                WHERE table_schema NOT IN ('information_schema', 'pg_catalog', '_timescaledb_catalog', '_timescaledb_cache', '_timescaledb_internal') 
                  AND table_type = 'BASE TABLE'
                ORDER BY table_schema, table_name;
            """)
            tables = db_cur.fetchall()

            if not tables:
                print("  (no user tables found)")
                db_conn.close()
                continue

            db_metadata = []

            for schema, table_name in tables:
                # Skip TimescaleDB partition chunks and system tables
                if table_name.startswith(("pg_", "sql_", "_", "stats_event", "ts_kv_20")):
                    continue

                # Row count
                try:
                    db_cur.execute(f'SELECT count(*) FROM "{schema}"."{table_name}"')
                    row_cnt = db_cur.fetchone()[0]
                except Exception:
                    row_cnt = "?"

                # Columns
                db_cur.execute(f"""
                    SELECT column_name, data_type, is_nullable
                    FROM information_schema.columns 
                    WHERE table_schema = '{schema}' AND table_name = '{table_name}' 
                    ORDER BY ordinal_position;
                """)
                columns = db_cur.fetchall()

                col_desc = [f"{c[0]} ({c[1]})" for c in columns if not c[0].startswith(("id", "tenant", "version", "additional"))]
                
                row_display = f"{row_cnt:,}" if isinstance(row_cnt, int) else str(row_cnt)
                print(f"\n  Table: {schema}.{table_name} [Total Rows: {row_display}]")
                if col_desc:
                    print(f"    Sensor/Measurement Columns ({len(col_desc)}):")
                    for i in range(0, len(col_desc), 4):
                        print(f"      {', '.join(col_desc[i:i+4])}")

                db_metadata.append({
                    "schema": schema,
                    "table": table_name,
                    "rows": row_cnt,
                    "columns": [{"name": c[0], "type": c[1]} for c in columns]
                })

            all_metadata[db_name] = db_metadata
            db_conn.close()

        except Exception as e:
            print(f"  Error accessing database '{db_name}': {e}")

    # Step 3: Save results
    output_path = args.output or os.path.join(
        os.path.dirname(__file__), '..', 'data', 'database_discovery.json'
    )
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(all_metadata, f, indent=2, default=str)
    print(f"\nDiscovery results saved to: {output_path}")
    print("Discovery complete!")

if __name__ == "__main__":
    main()
