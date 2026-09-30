import psycopg2
import psycopg2.extras
import json

def get_pg_connection(db_name="hydroponics"):
    attempts = [
        {"host": "192.168.0.21", "port": 5432, "user": "postgres", "password": "postgres"},
        {"host": "127.0.0.1", "port": 5432, "user": "postgres", "password": "postgres"},
    ]
    for p in attempts:
        try:
            return psycopg2.connect(dbname=db_name, connect_timeout=2, **p)
        except Exception:
            continue
    return None

def fetch_hydro():
    conn = get_pg_connection("hydroponics")
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute('SELECT COUNT(*) as total FROM "onem2m_data";')
    total = cur.fetchone()['total']
    cur.execute('SELECT * FROM "onem2m_data" ORDER BY timestamp DESC LIMIT 10;')
    rows = cur.fetchall()
    cur.close()
    conn.close()
    rows.reverse()
    
    records = []
    field_map = {
        "water_temperature": "WaterTemperature",
        "turbidity": "Turbidity",
        "tds": "TotalDissolvedSolids",
        "temperature": "Temperature",
        "humidity": "Humidity",
        "ph": "HydrogenIonConcentration",
    }
    for r in rows:
        t_str = str(r['timestamp']).split('.')[0].replace('+05:30', '')
        for f, c in field_map.items():
            if f in r and r[f] is not None:
                records.append({
                    "concept": c,
                    "source_field": f,
                    "value": float(r[f]),
                    "time": t_str,
                    "domain": "hydroponics"
                })
        if 'tds' in r and r['tds'] is not None:
            records.append({
                "concept": "Conductivity",
                "source_field": "ec",
                "value": round(float(r['tds']) * 2.0, 2),
                "time": t_str,
                "domain": "hydroponics"
            })
    return records, total

def fetch_air():
    conn = get_pg_connection("Air quality")
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute('SELECT COUNT(*) as total FROM "air quality 1";')
    total = cur.fetchone()['total']
    cur.execute('SELECT * FROM "air quality 1" ORDER BY timestamp DESC LIMIT 10;')
    rows = cur.fetchall()
    cur.close()
    conn.close()
    rows.reverse()
    
    records = []
    field_map = {
        "aqi": "AirQualityIndex",
        "pm25": "ParticulateMatter",
        "pm25_calibrated": "CalibratedPM25Concentration",
        "pm10": "PM10Concentration",
        "co2": "CO2Concentration",
        "temperature": "Temperature",   # Shared canonical SAREF Temperature!
        "humidity": "Humidity",         # Shared canonical SAREF Humidity!
        "co": "CarbonMonoxide",
        "ch4": "Methane",
        "lpg": "LPGConcentration",
        "nh4": "Ammonia",
        "nh3": "Ammonia",
        "smoke": "SmokeConcentration"
    }
    for r in rows:
        t_str = str(r['timestamp']).split('.')[0].replace('+05:30', '')
        for f, c in field_map.items():
            if f in r and r[f] is not None:
                records.append({
                    "concept": c,
                    "source_field": f,
                    "value": float(r[f]),
                    "time": t_str,
                    "domain": "air_quality"
                })
    return records, total

h_rec, h_tot = fetch_hydro()
a_rec, a_tot = fetch_air()

print(f"Hydro records: {len(h_rec)}, Total DB: {h_tot}")
print(f"Air records: {len(a_rec)}, Total DB: {a_tot}")

# Cross-domain check
temp_hydro = [r for r in h_rec if r['concept'] == 'Temperature']
temp_air = [r for r in a_rec if r['concept'] == 'Temperature']
print(f"Temperature records in Hydro: {len(temp_hydro)}, Latest: {temp_hydro[-1]['value']}")
print(f"Temperature records in Air: {len(temp_air)}, Latest: {temp_air[-1]['value']}")

