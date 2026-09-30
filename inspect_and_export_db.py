#!/usr/bin/env python3
"""
Diagnostic script to inspect local PostgreSQL on the server,
discover tables and columns, and print the live row counts and latest values.
"""
import sys
import os

try:
    import psycopg2
    import psycopg2.extras
except ImportError:
    print("psycopg2 not installed in current environment")
    sys.exit(1)

def inspect():
    print("--- Inspecting PostgreSQL Databases ---")
    
    # Connection attempts
    connections = [
        {"host": "127.0.0.1", "port": 5432, "user": "postgres", "password": "postgres"},
        {"host": "127.0.0.1", "port": 5432, "user": "postgres", "password": ""},
        {"host": "127.0.0.1", "port": 5432, "user": "cse-dept", "password": ""},
        {"user": "cse-dept"},
        {"user": "postgres"}
    ]
    
    working_conn_params = None
    
    for p in connections:
        try:
            conn = psycopg2.connect(dbname="postgres", **p)
            working_conn_params = p
            print(f"✅ Connected to 'postgres' with params: {p}")
            conn.close()
            break
        except Exception:
            continue
            
    if not working_conn_params:
        # Try connecting directly to hydroponics
        for p in connections:
            try:
                conn = psycopg2.connect(dbname="hydroponics", **p)
                working_conn_params = p
                print(f"✅ Connected directly to 'hydroponics' with params: {p}")
                conn.close()
                break
            except Exception:
                continue

    if not working_conn_params:
        print("❌ Could not connect to PostgreSQL with any test parameters.")
        return

    # List all databases
    try:
        conn = psycopg2.connect(dbname="postgres", **working_conn_params)
        cur = conn.cursor()
        cur.execute("SELECT datname FROM pg_database WHERE datistemplate = false;")
        dbs = [r[0] for r in cur.fetchall()]
        print(f"Available Databases: {dbs}")
        cur.close()
        conn.close()
    except Exception as e:
        dbs = ["hydroponics", "Air quality", "air_quality"]

    for db in dbs:
        try:
            conn = psycopg2.connect(dbname=db, **working_conn_params)
            cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cur.execute("""
                SELECT table_schema, table_name 
                FROM information_schema.tables 
                WHERE table_schema NOT IN ('pg_catalog', 'information_schema');
            """)
            tables = cur.fetchall()
            print(f"\n📂 Database: '{db}'")
            for t in tables:
                schema = t["table_schema"]
                table = t["table_name"]
                cur.execute(f'SELECT COUNT(*) as cnt FROM "{schema}"."{table}";')
                cnt = cur.fetchone()["cnt"]
                
                cur.execute(f"""
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_schema = %s AND table_name = %s
                    ORDER BY ordinal_position;
                """, (schema, table))
                cols = cur.fetchall()
                col_names = [c["column_name"] for c in cols]
                print(f"  📊 Table: {schema}.{table} | Total Rows: {cnt}")
                print(f"     Columns: {', '.join(col_names)}")
                
                # Fetch 3 latest rows
                cur.execute(f'SELECT * FROM "{schema}"."{table}" ORDER BY id DESC LIMIT 3;')
                latest_rows = cur.fetchall()
                print("     Latest 3 rows:")
                for r in latest_rows:
                    print(f"       {dict(r)}")
            cur.close()
            conn.close()
        except Exception as e:
            print(f"  ⚠️ Could not inspect db '{db}': {e}")

if __name__ == "__main__":
    inspect()

