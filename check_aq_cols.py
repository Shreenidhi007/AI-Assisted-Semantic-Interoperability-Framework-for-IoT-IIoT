import psycopg2
import psycopg2.extras

conn = psycopg2.connect(host='192.168.0.21', port=5432, user='postgres', password='postgres', dbname='Air quality')
cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

cur.execute('SELECT * FROM "air quality 1" LIMIT 1;')
cols = list(cur.fetchone().keys())

selects = [f'COUNT("{c}") as count_{c}' for c in cols if c not in ('id', 'timestamp')]
sql = f'SELECT COUNT(*) as total, {", ".join(selects)} FROM "air quality 1";'
cur.execute(sql)
stats = cur.fetchone()
print("Column statistics in air quality 1:")
for k, v in stats.items():
    print(f"  {k}: {v}")
cur.close()
conn.close()

