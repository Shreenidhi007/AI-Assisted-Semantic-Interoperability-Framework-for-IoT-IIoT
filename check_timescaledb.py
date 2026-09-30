#!/usr/bin/env python3
import psycopg2
import json

hosts = ["192.168.0.21", "127.0.0.1"]
credentials = [
    {"user": "postgres", "password": "postgres"},
    {"user": "cse-dept", "password": ""},
    {"user": "postgres", "password": ""}
]

target_dbs = ["hydroponics", "wq_bus_sensor", "Air quality", "postgres"]

def check_db(host, cred, db_name):
    try:
        conn = psycopg2.connect(host=host, port=5432, dbname=db_name, connect_timeout=3, **cred)
        cur = conn.cursor()
        
        # Check extensions
        cur.execute("SELECT extname, extversion FROM pg_extension;")
        extensions = dict(cur.fetchall())
        
        # Check if timescaledb is installed
        has_timescale = "timescaledb" in extensions
        
        hypertables = []
        if has_timescale:
            try:
                # Query timescaledb hypertables
                cur.execute("""
                    SELECT hypertable_schema, hypertable_name, num_dimensions 
                    FROM timescaledb_information.hypertables;
                """)
                hypertables = [f"{row[0]}.{row[1]} ({row[2]} dims)" for row in cur.fetchall()]
            except Exception as e:
                hypertables = [f"Error querying hypertables: {e}"]
                
        # Also list tables
        cur.execute("""
            SELECT table_schema, table_name 
            FROM information_schema.tables 
            WHERE table_schema NOT IN ('information_schema', 'pg_catalog', '_timescaledb_catalog', '_timescaledb_internal', '_timescaledb_config')
            AND table_type = 'BASE TABLE';
        """)
        tables = [f"{r[0]}.{r[1]}" for r in cur.fetchall()]
        
        cur.close()
        conn.close()
        return {
            "success": True,
            "extensions": extensions,
            "has_timescaledb": has_timescale,
            "timescale_version": extensions.get("timescaledb"),
            "hypertables": hypertables,
            "tables": tables
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

print("=== CHECKING TIMESCALEDB ON POSTGRESQL ===")
working_conn = None
for h in hosts:
    for c in credentials:
        res = check_db(h, c, "postgres")
        if res.get("success"):
            working_conn = (h, c)
            print(f"Connected to {h} using user={c['user']}")
            break
    if working_conn:
        break

if not working_conn:
    print("Could not connect directly from Windows. Checking if we can probe 192.168.0.21...")
else:
    h, c = working_conn
    for db in target_dbs:
        print(f"\n--- Checking Database: {db} ---")
        info = check_db(h, c, db)
        if info["success"]:
            print(f"TimescaleDB Extension: {'INSTALLED (' + str(info['timescale_version']) + ')' if info['has_timescaledb'] else 'NOT INSTALLED'}")
            print(f"Hypertables: {info['hypertables']}")
            print(f"Base Tables: {info['tables']}")
            print(f"All Extensions: {list(info['extensions'].keys())}")
        else:
            print(f"Error: {info['error']}")

