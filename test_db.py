#!/usr/bin/env python3
"""
Test direct PostgreSQL connectivity on the server for Hydroponics and Air Quality databases.
"""
import psycopg2
import sys

def test_db():
    print("Testing PostgreSQL connections...")
    
    # Try different user/passwords if needed
    auth_options = [
        {"user": "postgres", "password": "postgres", "host": "127.0.0.1", "port": 5432},
        {"user": "postgres", "password": "", "host": "127.0.0.1", "port": 5432},
        {"user": "cse-dept", "password": "", "host": "127.0.0.1", "port": 5432}
    ]
    
    conn = None
    working_auth = None
    
    for auth in auth_options:
        try:
            conn = psycopg2.connect(dbname="postgres", **auth)
            working_auth = auth
            print(f"✅ Connected to 'postgres' db with {auth['user']}")
            break
        except Exception as e:
            continue
            
    if not conn:
        print("❌ Could not connect to default postgres db")
        return

    # List all databases
    cur = conn.cursor()
    cur.execute("SELECT datname FROM pg_database WHERE datistemplate = false;")
    dbs = [row[0] for row in cur.fetchall()]
    print(f"Available databases: {dbs}")
    cur.close()
    conn.close()

    # Check hydroponics
    for db_name in ["hydroponics", "Air quality", "air_quality", "airquality"]:
        if db_name in dbs:
            try:
                c = psycopg2.connect(dbname=db_name, **working_auth)
                cur = c.cursor()
                cur.execute("""
                    SELECT table_schema, table_name 
                    FROM information_schema.tables 
                    WHERE table_schema NOT IN ('pg_catalog', 'information_schema');
                """)
                tables = cur.fetchall()
                print(f"\nDB '{db_name}' tables:")
                for schema, tbl in tables:
                    cur.execute(f'SELECT COUNT(*) FROM "{schema}"."{tbl}";')
                    cnt = cur.fetchone()[0]
                    cur.execute(f'SELECT column_name, data_type FROM information_schema.columns WHERE table_schema = %s AND table_name = %s;', (schema, tbl))
                    cols = [f"{col[0]} ({col[1]})" for col in cur.fetchall()]
                    print(f"  - {schema}.{tbl} ({cnt} rows):")
                    print(f"    Columns: {', '.join(cols[:10])}")
                    
                    # Check for -1 in water_temperature if column exists
                    col_names = [col.split(" ")[0] for col in cols]
                    if "water_temperature" in col_names:
                        cur.execute(f'SELECT COUNT(*) FROM "{schema}"."{tbl}" WHERE water_temperature = -1 OR water_temperature < 0;')
                        neg_cnt = cur.fetchone()[0]
                        print(f"    ⚠️ 'water_temperature' <= 0 count: {neg_cnt} rows!")
                        
                cur.close()
                c.close()
            except Exception as e:
                print(f"Error inspecting {db_name}: {e}")

if __name__ == "__main__":
    test_db()

