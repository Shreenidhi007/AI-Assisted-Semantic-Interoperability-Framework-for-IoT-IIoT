import psycopg2
import psycopg2.extras
import json

users = ['postgres', 'cse-dept']
passwords = ['postgres', '', 'cse-dept', 'password']
databases = ['postgres', 'hydroponics', 'air_quality', 'Air quality']

connected_conn = None
connected_user = None
connected_db = None

for u in users:
    for p in passwords:
        try:
            conn = psycopg2.connect(host='192.168.0.21', port=5432, user=u, password=p, dbname='postgres', connect_timeout=2)
            connected_conn = conn
            connected_user = u
            connected_pass = p
            print(f"Connected to postgres as user={u} pass={p}")
            break
        except Exception as e:
            pass
    if connected_conn:
        break

if not connected_conn:
    print("Could not connect to postgres database directly from host.")
    exit(1)

cur = connected_conn.cursor()
cur.execute("SELECT datname FROM pg_database WHERE datistemplate = false;")
all_dbs = [r[0] for r in cur.fetchall()]
print(f"All databases on 192.168.0.21: {all_dbs}")
cur.close()
connected_conn.close()

results = {}

for db in all_dbs:
    try:
        conn = psycopg2.connect(host='192.168.0.21', port=5432, user=connected_user, password=connected_pass, dbname=db, connect_timeout=2)
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        # Get all tables in public schema
        cur.execute("""
            SELECT table_schema, table_name 
            FROM information_schema.tables 
            WHERE table_schema NOT IN ('pg_catalog', 'information_schema');
        """)
        tables = cur.fetchall()
        results[db] = {}
        
        for t in tables:
            s_name = t['table_schema']
            t_name = t['table_name']
            
            # Columns
            cur.execute("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_schema = %s AND table_name = %s
                ORDER BY ordinal_position;
            """, (s_name, t_name))
            cols = cur.fetchall()
            
            # Count
            try:
                cur.execute(f'SELECT COUNT(*) as count FROM "{s_name}"."{t_name}";')
                cnt = cur.fetchone()['count']
            except Exception:
                cnt = 0
                conn.rollback()
                
            # Latest 3 rows
            sample_rows = []
            try:
                # Find timestamp or id column
                col_names = [c['column_name'] for c in cols]
                order_col = 'timestamp' if 'timestamp' in col_names else ('id' if 'id' in col_names else col_names[0])
                cur.execute(f'SELECT * FROM "{s_name}"."{t_name}" ORDER BY "{order_col}" DESC LIMIT 3;')
                sample_rows = cur.fetchall()
                # convert timestamps to str
                for r in sample_rows:
                    for k, v in r.items():
                        if hasattr(v, 'isoformat'):
                            r[k] = v.isoformat()
            except Exception as e:
                conn.rollback()
            
            results[db][f"{s_name}.{t_name}"] = {
                "columns": cols,
                "count": cnt,
                "latest_rows": sample_rows
            }
            
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error inspecting db {db}: {e}")

with open('db_inspection.json', 'w') as f:
    json.dump(results, f, indent=2, default=str)

print("Inspection completed and saved to db_inspection.json!")

