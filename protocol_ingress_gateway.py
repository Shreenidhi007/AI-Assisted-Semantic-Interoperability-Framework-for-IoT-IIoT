"""
Multi-Protocol Ingress Gateway for EnviroMap-KG.
Ingests live telemetry across 6 heterogeneous protocols:
  1. MQTT (EMQX / Mosquitto wildcard subscription '#')
  2. CoAP (Constrained Application Protocol datagrams)
  3. oneM2M (ContentInstance resource notifications)
  4. OPC UA (Variable NodeID DataChange subscriptions)
  5. HTTP (REST webhook / async ingestion endpoint)
  6. AMQP (RabbitMQ message queue topic bindings)

Normalizes all data into standard event envelopes on Kafka topic 'city.telemetry.raw'.
Runs 100% on-premise at $0.00 cloud operational cost with zero emojis.
"""

from __future__ import annotations

import json
import time
import uuid
import logging
from typing import Dict, Any, Optional

logging.basicConfig(level=logging.INFO, format="%(asctime)s [INGRESS-%(levelname)s] %(message)s")
logger = logging.getLogger("enviromap.ingress_gateway")

KAFKA_BOOTSTRAP = "192.168.0.21:9092"
RAW_TOPIC = "city.telemetry.raw"


class ProtocolIngressGateway:
    def __init__(self, bootstrap_servers: str = KAFKA_BOOTSTRAP, use_kafka: bool = True):
        self.bootstrap_servers = bootstrap_servers
        self.use_kafka = use_kafka
        self.producer = None
        self._fallback_buffer = []

        if self.use_kafka:
            try:
                from kafka import KafkaProducer
                self.producer = KafkaProducer(
                    bootstrap_servers=[self.bootstrap_servers],
                    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
                    linger_ms=2,
                    batch_size=32768,
                    max_block_ms=3000
                )
                logger.info("KafkaProducer successfully connected to %s", self.bootstrap_servers)
            except Exception as e:
                logger.warning("KafkaProducer unavailable (%s). Operating in-memory mode.", e)
                self.producer = None

    def emit_envelope(
        self,
        protocol: str,
        source_id: str,
        domain_hint: str,
        telemetry: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Creates standard event envelope and dispatches to Kafka topic 'city.telemetry.raw'.
        """
        envelope = {
            "event_id": str(uuid.uuid4()),
            "protocol": protocol,
            "source_id": source_id,
            "domain_hint": domain_hint,
            "ingress_timestamp": time.time(),
            "telemetry": telemetry,
            "metadata": metadata or {}
        }

        if self.producer:
            try:
                self.producer.send(RAW_TOPIC, value=envelope)
            except Exception as err:
                logger.error("Failed to emit to Kafka: %s", err)
                self._fallback_buffer.append(envelope)
        else:
            self._fallback_buffer.append(envelope)

        return envelope

    # =========================================================================
    # 1. MQTT INGRESS (Subscribed to '#' on EMQX)
    # =========================================================================
    def handle_mqtt_message(self, topic: str, payload_bytes: bytes) -> Dict[str, Any]:
        """
        Parses MQTT message published to e.g. 'city/smart_water/station_4/telemetry'
        or arbitrary cryptic topics e.g. 'aaaaa.i.xxx_y'.
        """
        parts = topic.strip("/").split("/")
        if len(parts) >= 3 and parts[0] == "city":
            domain_hint = parts[1]
            source_id = parts[2]
        elif len(parts) == 1:
            domain_hint = "unclassified"
            source_id = parts[0]
        else:
            domain_hint = parts[0]
            source_id = parts[1] if len(parts) > 1 else topic

        try:
            payload = json.loads(payload_bytes.decode("utf-8"))
        except Exception:
            payload = {"raw_value": payload_bytes.decode("utf-8", errors="ignore")}

        return self.emit_envelope("MQTT", source_id, domain_hint, payload, {"raw_topic": topic})

    # =========================================================================
    # 2. CoAP INGRESS (Lightweight UDP datagrams)
    # =========================================================================
    def handle_coap_datagram(self, uri_path: str, datagram_bytes: bytes) -> Dict[str, Any]:
        """
        Processes CoAP request e.g. 'coap://sensor-node-12/water_temp'.
        """
        parts = uri_path.strip("/").split("/")
        domain_hint = parts[0] if parts else "constrained_iot"
        source_id = parts[1] if len(parts) > 1 else "coap_node"

        try:
            payload = json.loads(datagram_bytes.decode("utf-8"))
        except Exception:
            payload = {"coap_reading": datagram_bytes.decode("utf-8", errors="ignore")}

        return self.emit_envelope("CoAP", source_id, domain_hint, payload, {"uri": uri_path})

    # =========================================================================
    # 3. oneM2M INGRESS (ContentInstance <cin> notification)
    # =========================================================================
    def handle_onem2m_notification(self, notification_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parses oneM2M CSE subscription event containing a <cin> representation.
        """
        cin = notification_dict.get("m2m:sgn", {}).get("nev", {}).get("rep", {}).get("m2m:cin", {})
        sur = notification_dict.get("m2m:sgn", {}).get("sur", "onem2m/cse")
        con = cin.get("con", {})
        
        if isinstance(con, str):
            try:
                con = json.loads(con)
            except Exception:
                con = {"val": con}

        source_id = cin.get("rn", sur.split("/")[-1])
        domain_hint = "smart_city"
        return self.emit_envelope("oneM2M", source_id, domain_hint, con, {"sur": sur})

    # =========================================================================
    # 4. OPC UA INGRESS (NodeID DataChange event)
    # =========================================================================
    def handle_opcua_datachange(self, node_id: str, value: float, namespace: str = "ns=2") -> Dict[str, Any]:
        """
        Translates OPC UA MonitoredItem notification into an event envelope.
        """
        clean_name = node_id.split(";")[-1].replace("s=", "")
        domain_hint = "industrial_iot"
        return self.emit_envelope(
            "OPC_UA",
            source_id=namespace,
            domain_hint=domain_hint,
            telemetry={clean_name: float(value)},
            metadata={"node_id": node_id}
        )

    # =========================================================================
    # 5. HTTP INGRESS (FastAPI / REST Webhook)
    # =========================================================================
    def handle_http_post(self, domain: str, device_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Direct REST ingestion from HTTP webhooks and edge API gateways.
        """
        return self.emit_envelope("HTTP", device_id, domain, payload)

    # =========================================================================
    # 6. AMQP INGRESS (RabbitMQ message queue consumer)
    # =========================================================================
    def handle_amqp_message(self, routing_key: str, body_bytes: bytes) -> Dict[str, Any]:
        """
        Parses AMQP routing key e.g. 'city.environment.hydroponics.sensor_01'.
        """
        parts = routing_key.split(".")
        domain_hint = parts[2] if len(parts) > 2 else "amqp_stream"
        source_id = parts[3] if len(parts) > 3 else routing_key

        try:
            payload = json.loads(body_bytes.decode("utf-8"))
        except Exception:
            payload = {"reading": body_bytes.decode("utf-8", errors="ignore")}

        return self.emit_envelope("AMQP", source_id, domain_hint, payload, {"routing_key": routing_key})

    def close(self):
        if self.producer:
            self.producer.flush()
            self.producer.close()
            logger.info("KafkaProducer flushed and closed.")
