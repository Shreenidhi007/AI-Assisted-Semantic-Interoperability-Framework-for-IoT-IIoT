#!/usr/bin/env python3
"""
Migrate Air quality database on 192.168.0.21 to TimescaleDB hypertable with compression.
"""
import psycopg2
import sys

def migrate_air_quality():
    print("=== Migrating Air quality Database to TimescaleDB ===")
    try:
        conn = psycopg2.connect(
            host="192.168.0.21",
            port=5432,
            dbname="Air quality",
            user="postgres",
            password="postgres",
            connect_timeout=5
        )
        conn.autocommit = True
        cur = conn.cursor()

        # 1. Enable extension
        print("1. Installing TimescaleDB extension...")
        cur.execute("CREATE EXTENSION IF NOT EXISTS timescaledb;")
        cur.execute("SELECT extversion FROM pg_extension WHERE extname = 'timescaledb';")
        version = cur.fetchone()[0]
        print(f"   TimescaleDB version: {version}")

        # 2. Adjust primary key to include timestamp
        print("2. Adjusting primary key to (id, timestamp)...")
        try:
            cur.execute('ALTER TABLE public."air quality 1" DROP CONSTRAINT IF EXISTS "air quality 1_pkey";')
            cur.execute('ALTER TABLE public."air quality 1" ADD PRIMARY KEY (id, timestamp);')
            print("   Primary key updated successfully.")
        except Exception as e:
            print(f"   Primary key already configured or notice: {e}")

        # 3. Create hypertable with migrate_data => true
        print("3. Converting 'air quality 1' to Hypertable...")
        cur.execute('SELECT create_hypertable(\'public."air quality 1"\', \'timestamp\', migrate_data => true, if_not_exists => TRUE);')
        res = cur.fetchone()
        print(f"   Hypertable status: {res}")

        # 4. Enable compression
        print("4. Enabling columnstore compression...")
        try:
            cur.execute("""
                ALTER TABLE public."air quality 1" SET (
                    timescaledb.compress,
                    timescaledb.compress_orderby = 'timestamp DESC'
                );
            """)
            print("   Compression enabled on table.")
        except Exception as e:
            print(f"   Compression settings notice: {e}")

        # 5. Add compression policy (compress after 3 days)
        print("5. Adding 3-day compression policy...")
        try:
            cur.execute("SELECT add_compression_policy('public.\"air quality 1\"', INTERVAL '3 days', if_not_exists => TRUE);")
            job_id = cur.fetchone()
            print(f"   Compression policy active with job: {job_id}")
        except Exception as e:
            print(f"   Policy notice: {e}")

        # 6. Verify
        cur.execute("SELECT hypertable_name, compression_enabled FROM timescaledb_information.hypertables;")
        print("6. Active Hypertables in 'Air quality':", cur.fetchall())

        cur.close()
        conn.close()
        print("=== Migration of Air quality to TimescaleDB Complete! ===")
        return True
    except Exception as e:
        print(f"Error during migration: {e}")
        return False

if __name__ == "__main__":
    success = migrate_air_quality()
    sys.exit(0 if success else 1)
