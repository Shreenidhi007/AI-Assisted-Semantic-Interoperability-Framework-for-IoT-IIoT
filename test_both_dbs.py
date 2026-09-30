import psycopg2
import psycopg2.extras
import json

def test_fetch():
    # 1. Hydroponics
    conn_h = psycopg2.connect(host='192.168.0.21', port=5432, user='postgres', password='postgres', dbname='hydroponics')
    cur_h = conn_h.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur_h.execute('SELECT COUNT(*) as total FROM onem2m_data;')
    h_count = cur_h.fetchone()['total']
    cur_h.execute('SELECT * FROM onem2m_data ORDER BY timestamp DESC LIMIT 5;')
    h_rows = cur_h.fetchall()
    cur_h.close()
    conn_h.close()
    
    print(f"Hydroponics onem2m_data count: {h_count}")
    print(f"Latest Hydroponics row: {h_rows[0]}")
    
    # 2. Air quality
    conn_a = psycopg2.connect(host='192.168.0.21', port=5432, user='postgres', password='postgres', dbname='Air quality')
    cur_a = conn_a.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur_a.execute('SELECT COUNT(*) as total FROM "air quality 1";')
    a_count = cur_a.fetchone()['total']
    cur_a.execute('SELECT * FROM "air quality 1" ORDER BY timestamp DESC LIMIT 5;')
    a_rows = cur_a.fetchall()
    cur_a.close()
    conn_a.close()
    
    print(f"\nAir quality count: {a_count}")
    print(f"Latest Air quality row: {a_rows[0]}")

test_fetch()

