#!/usr/bin/env python3
import psycopg2

for db in ["hydroponics", "wq_bus_sensor"]:
    print(f"=== Checking constraints in {db} ===")
    conn = psycopg2.connect(host='192.168.0.21', port=5432, dbname=db, user='postgres', password='postgres')
    cur = conn.cursor()
    cur.execute("""
        SELECT tc.table_name, tc.constraint_type, ccu.column_name
        FROM information_schema.table_constraints tc
        JOIN information_schema.constraint_column_usage ccu ON tc.constraint_name = ccu.constraint_name
        WHERE tc.table_schema = 'public';
    """)
    print(cur.fetchall())
    
    # Check if compression is already enabled on hypertables
    cur.execute("""
        SELECT hypertable_name, compression_enabled 
        FROM timescaledb_information.hypertables;
    """)
    print("Hypertables compression status:", cur.fetchall())
    cur.close()
    conn.close()

