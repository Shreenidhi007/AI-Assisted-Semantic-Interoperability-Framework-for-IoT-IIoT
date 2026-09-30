import psycopg2
import psycopg2.extras
from datetime import datetime

attempts = [{'host': '192.168.0.21', 'port': 5432, 'user': 'postgres', 'password': 'postgres'}]
conn = psycopg2.connect(dbname='postgres', **attempts[0])
cur = conn.cursor()
cur.execute("SELECT datname FROM pg_database WHERE datistemplate = false AND datname NOT IN ('postgres');")
dbs = [r[0] for r in cur.fetchall()]
print("Discovered Databases:", dbs)

live_domains = {}
for db in dbs:
    try:
        c = psycopg2.connect(dbname=db, **attempts[0])
        c_cur = c.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        c_cur.execute("""SELECT table_schema, table_name FROM information_schema.tables 
                         WHERE table_schema NOT IN ('information_schema', 'pg_catalog', '_timescaledb_catalog', '_timescaledb_cache', '_timescaledb_internal') 
                           AND table_type = 'BASE TABLE';""")
        tables = c_cur.fetchall()
        for t in tables:
            s, tbl = t['table_schema'], t['table_name']
            if tbl.startswith(('pg_', 'sql_', '_', 'stats_event', 'ts_kv_20')):
                continue
            try:
                c_cur.execute(f'SELECT count(*) as cnt FROM "{s}"."{tbl}"')
                cnt = c_cur.fetchone()['cnt']
            except Exception:
                continue
            if cnt > 0 and tbl in ('onem2m_data', 'air quality 1', 'thingsboard_data'):
                print(f"Active live table: {db}.{s}.{tbl} ({cnt} rows)")
                # Get columns
                c_cur.execute(f"SELECT column_name, data_type FROM information_schema.columns WHERE table_schema = '{s}' AND table_name = '{tbl}' ORDER BY ordinal_position;")
                cols = c_cur.fetchall()
                meas = [col['column_name'] for col in cols if col['data_type'] in ('double precision', 'real', 'numeric', 'integer', 'float')]
                print(f"  Measurement cols ({len(meas)}): {meas}")
                live_domains[db] = {'table': f'{s}.{tbl}', 'count': cnt, 'columns': meas}
        c.close()
    except Exception as e:
        print(f"Error inspecting {db}: {e}")

print("\nLive Domains Summary:", live_domains)

