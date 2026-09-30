"""
Live MQTT Ingress Bridge for EnviroMap-KG.
Continuously listens to '#' on the MQTT broker (EMQX on 192.168.0.21:18883 or Mosquitto on 1883)
and immediately forwards all incoming physical sensor packets into Kafka topic 'city.telemetry.raw'.
Runs 100% on-premise at $0.00 cloud operational cost with zero emojis.
"""

from __future__ import annotations

import sys
import json
import time
import logging
import argparse
import paho.mqtt.client as mqtt
from protocol_ingress_gateway import ProtocolIngressGateway

logging.basicConfig(level=logging.INFO, format="%(asctime)s [MQTT-BRIDGE-%(levelname)s] %(message)s")
logger = logging.getLogger("enviromap.mqtt_bridge")

gateway = ProtocolIngressGateway(use_kafka=True)


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logger.info("Connected to MQTT Broker successfully! Subscribing to wildcard '#'...")
        client.subscribe("#")
    elif rc == 5:
        logger.error("Connection refused: Not authorized (Return code 5). Check username/password or switch to EMQX on port 18883.")
    else:
        logger.error("Failed to connect to MQTT broker, return code %d", rc)


def on_message(client, userdata, msg):
    try:
        topic = msg.topic
        payload = msg.payload
        logger.info("Live packet received on topic '%s' (%d bytes)", topic, len(payload))
        gateway.handle_mqtt_message(topic, payload)
    except Exception as e:
        logger.error("Error forwarding MQTT message: %s", e)


def start_bridge():
    parser = argparse.ArgumentParser(description="Live MQTT Ingress Bridge for EnviroMap-KG")
    parser.add_argument("--host", default="127.0.0.1", help="MQTT Broker Host")
    parser.add_argument("--port", type=int, default=18883, help="MQTT Port (Default 18883 for EMQX container, 1883 for Mosquitto)")
    parser.add_argument("--user", default=None, help="MQTT Username (if auth required)")
    parser.add_argument("--password", default=None, help="MQTT Password (if auth required)")
    args = parser.parse_args()

    # Use paho-mqtt CallbackAPIVersion to suppress deprecation warning
    try:
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
    except AttributeError:
        client = mqtt.Client()

    if args.user and args.password:
        client.username_pw_set(args.user, args.password)

    client.on_connect = on_connect
    client.on_message = on_message

    logger.info("Connecting to MQTT Broker on %s:%d...", args.host, args.port)
    try:
        client.connect(args.host, args.port, 60)
    except Exception as err:
        logger.error("Could not connect to %s:%d: %s", args.host, args.port, err)
        sys.exit(1)

    logger.info("Live MQTT Ingress Bridge active. Forwarding all sensor events to Kafka...")
    client.loop_forever()


if __name__ == "__main__":
    start_bridge()
