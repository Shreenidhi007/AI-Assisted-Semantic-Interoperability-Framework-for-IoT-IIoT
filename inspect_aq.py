#!/usr/bin/env python3
import psycopg2

try:
    conn = psycopg2.connect(host='192.168.0.21', port=5432, dbname='Air quality', user='postgres', password='postgres')
    cur = conn.cursor()
    cur.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'air quality 1';")
    cols = cur.fetchall()
    print("Air quality columns:", cols)
    cur.execute('SELECT count(*) FROM public."air quality 1";')
    print("Row count:", cur.fetchone()[0])
    cur.execute('SELECT * FROM public."air quality 1" LIMIT 1;')
    print("Sample row:", cur.fetchone())
    
    # Check if primary key exists
    cur.execute("""
        SELECT tc.constraint_type, ccu.column_name
        FROM information_schema.table_constraints tc
        JOIN information_schema.constraint_column_usage ccu ON tc.constraint_name = ccu.constraint_name
        WHERE tc.table_name = 'air quality 1';
    """)
    print("Constraints:", cur.fetchall())
except Exception as e:
    print("Error:", e)

