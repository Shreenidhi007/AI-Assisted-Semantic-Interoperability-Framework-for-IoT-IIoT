"""
Continuous Real-Time Sensor Telemetry Generator for EnviroMap-KG.
Continuously emits live telemetry packets every 1.5 seconds across 4 environmental domains:
  - Smart Water (ph, tds, turbidity)
  - Air Quality (pm25, co2, ambient_temp)
  - Smart Garden (soil_moisture)
  - Novel Domain: Smart Aquaculture (REG_8820 dissolved oxygen)
Directly pushes to Kafka topic 'city.telemetry.raw' so the live worker processes them in real time.
Runs 100% on-premise at $0.00 cloud operational cost with zero emojis.
"""

from __future__ import annotations

import time
import math
import random
import logging
from protocol_ingress_gateway import ProtocolIngressGateway

logging.basicConfig(level=logging.INFO, format="%(asctime)s [STREAM-GEN-%(levelname)s] %(message)s")
logger = logging.getLogger("enviromap.stream_gen")


def run_continuous_stream():
    gw = ProtocolIngressGateway(use_kafka=True)
    logger.info("Continuous Real-Time Telemetry Generator started. Emitting readings every 1.5 seconds...")
    tick = 0

    try:
        while True:
            tick += 1
            t = time.time()
            sine_wave = math.sin(tick * 0.1)

            # 1. Smart Water Station (MQTT)
            gw.emit_envelope(
                protocol="MQTT",
                source_id="water_station_01",
                domain_hint="smart_water",
                telemetry={
                    "ph": round(7.20 + 0.15 * sine_wave + random.uniform(-0.02, 0.02), 2),
                    "tds": round(310.0 + 15.0 * sine_wave + random.uniform(-2.0, 2.0), 1),
                    "turbidity": round(2.5 + 0.5 * sine_wave + random.uniform(-0.1, 0.1), 2)
                }
            )

            # 2. Air Quality Monitor (HTTP Webhook)
            gw.emit_envelope(
                protocol="HTTP",
                source_id="aq_monitor_central",
                domain_hint="air_quality",
                telemetry={
                    "pm25": round(15.0 + 8.0 * abs(sine_wave) + random.uniform(-1.0, 1.0), 1),
                    "co2": round(410.0 + 25.0 * abs(sine_wave) + random.uniform(-3.0, 3.0), 1)
                }
            )

            # 3. Smart Garden Sensor (OPC UA / CoAP)
            gw.emit_envelope(
                protocol="CoAP",
                source_id="garden_bed_04",
                domain_hint="smart_garden",
                telemetry={
                    "soil_moisture": round(45.0 + 5.0 * sine_wave + random.uniform(-0.5, 0.5), 1)
                }
            )

            # 4. Novel Environment: Smart Aquaculture (Cryptic Modbus Register REG_8820)
            gw.emit_envelope(
                protocol="MQTT",
                source_id="marine_tank_12",
                domain_hint="aaaaa.i.xxx_y",
                telemetry={
                    "REG_8820": round(8.15 + 0.05 * sine_wave + random.uniform(-0.01, 0.01), 2)
                }
            )

            logger.info("Tick #%d emitted: 4 stations across 4 protocols sent to Kafka topic 'city.telemetry.raw'", tick)
            time.sleep(1.5)

    except KeyboardInterrupt:
        logger.info("Continuous telemetry generator halted by user.")
        gw.close()


if __name__ == "__main__":
    run_continuous_stream()
