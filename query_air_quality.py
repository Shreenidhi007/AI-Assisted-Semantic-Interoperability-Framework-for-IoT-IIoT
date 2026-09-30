import psycopg2
import psycopg2.extras

conn = psycopg2.connect(host='192.168.0.21', port=5432, user='postgres', password='postgres', dbname='Air quality')
cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
cur.execute('SELECT * FROM "air quality 1" ORDER BY timestamp DESC LIMIT 15;')
rows = cur.fetchall()
print("Latest 15 Air Quality rows:")
for r in rows:
    print(f"ID {r['id']} | {r['timestamp']} | temp: {r['temperature']} | humid: {r['humidity']} | aqi: {r['aqi']} | pm25_cal: {r['pm25_calibrated']} | pm10: {r['pm10']} | co2: {r['co2']}")

cur.execute('SELECT MIN(temperature), MAX(temperature), MIN(humidity), MAX(humidity) FROM "air quality 1";')
stats = cur.fetchone()
print("\nStats for Air Quality 1:")
print(stats)

cur.close()
conn.close()

