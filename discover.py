import psycopg2

conn = psycopg2.connect(host='192.168.0.21', port=5432, user='postgres', password='postgres')
cur = conn.cursor()
cur.execute("SELECT datname FROM pg_database WHERE datistemplate = false ORDER BY datname;")
dbs = [r[0] for r in cur.fetchall() if r[0] != 'postgres']
print("==================================================")
print(f"DISCOVERED DATABASES ({len(dbs)}): {dbs}")
print("==================================================")

for db in dbs:
    c2 = psycopg2.connect(host='192.168.0.21', port=5432, user='postgres', password='postgres', dbname=db)
    cur2 = c2.cursor()
    cur2.execute("""
        SELECT table_schema, table_name 
        FROM information_schema.tables 
        WHERE table_schema NOT IN ('information_schema', 'pg_catalog', '_timescaledb_catalog', '_timescaledb_cache', '_timescaledb_internal') 
          AND table_type = 'BASE TABLE'
        ORDER BY table_name;
    """)
    tables = cur2.fetchall()
    print(f"\n[Database: '{db}'] - {len(tables)} tables found:")
    for s, t in tables:
        try:
            cur2.execute(f'SELECT count(*) FROM "{s}"."{t}"')
            cnt = cur2.fetchone()[0]
        except Exception:
            cnt = "?"
        cur2.execute(f"SELECT column_name, data_type FROM information_schema.columns WHERE table_schema = '{s}' AND table_name = '{t}' ORDER BY ordinal_position;")
        cols = [f"{col[0]} ({col[1]})" for col in cur2.fetchall()]
        print(f"  • Table: {s}.{t} (Total Rows: {cnt:,})")
        print(f"    Columns ({len(cols)}): {', '.join(cols)}")

