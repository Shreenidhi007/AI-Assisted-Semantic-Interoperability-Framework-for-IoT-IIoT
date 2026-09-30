"""
Semantic Translation Layer for EnviroMap-KG.

Converts validated mapping decisions and raw source observations
into canonical SOSA/SAREF RDF observations using the Unified
Semantic Model structure.
"""

import logging
import os
import sys
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from models.data_models import (
    CanonicalObservation, DiscoveryProfile, ReasoningDecision,
    ValidationResult, Domain,
)
from ontology_registry.registry import OntologyRegistry


logger = logging.getLogger("enviromap.translator")

# Unit string -> QUDT URI mapping
UNIT_TO_QUDT = {
    "°C": "http://qudt.org/vocab/unit/DEG_C",
    "°F": "http://qudt.org/vocab/unit/DEG_F",
    "K": "http://qudt.org/vocab/unit/K",
    "%": "http://qudt.org/vocab/unit/PERCENT",
    "ppm": "http://qudt.org/vocab/unit/PPM",
    "mg/L": "http://qudt.org/vocab/unit/MilliGM-PER-L",
    "µg/m³": "http://qudt.org/vocab/unit/MicroGM-PER-M3",
    "NTU": "http://qudt.org/vocab/unit/NTU",
    "pH": "http://qudt.org/vocab/unit/PH",
    "mS/cm": "http://qudt.org/vocab/unit/MilliS-PER-CM",
    "µS/cm": "http://qudt.org/vocab/unit/MicroS-PER-CM",
    "lux": "http://qudt.org/vocab/unit/LUX",
    "mm": "http://qudt.org/vocab/unit/MilliM",
    "m": "http://qudt.org/vocab/unit/M",
    "cm": "http://qudt.org/vocab/unit/CentiM",
    "m/s": "http://qudt.org/vocab/unit/M-PER-SEC",
    "L/min": "http://qudt.org/vocab/unit/L-PER-MIN",
    "bar": "http://qudt.org/vocab/unit/BAR",
    "hPa": "http://qudt.org/vocab/unit/HectoPA",
}

# Domain -> Feature of Interest type
DOMAIN_FOI = {
    "air_quality": "AmbientAir",
    "hydroponics": "NutrientSolution",
    "smart_garden": "GardenSoil",
    "smart_water": "WaterBody",
}


class SemanticTranslator:
    """
    Converts validated source observations into canonical
    SOSA/SAREF observations for the Unified Semantic Model.
    """

    def __init__(self, registry: OntologyRegistry):
        self.registry = registry
        self._observation_counter = 0

    def translate_record(
        self,
        record: Dict[str, Any],
        field_mappings: Dict[str, ValidationResult],
        field_decisions: Dict[str, ReasoningDecision],
        domain: str,
        source_table: str,
        profiles: Dict[str, DiscoveryProfile],
    ) -> List[CanonicalObservation]:
        """
        Translate a single source record into canonical observations.

        Each measurement field in the record that has a valid mapping
        produces one CanonicalObservation.
        """
        observations = []

        # Find timestamp field in the record
        timestamp = self._extract_timestamp(record)

        # Find device/sensor info if available
        sensor_id = self._extract_sensor_info(record)
        location = self._extract_location(record)

        for field_name, value in record.items():
            # Skip non-measurement fields
            if field_name not in field_mappings:
                continue

            validation = field_mappings[field_name]
            if not validation.is_valid:
                continue

            decision = field_decisions.get(field_name)
            if not decision:
                continue

            # Skip null values
            if value is None:
                continue

            profile = profiles.get(field_name)
            unit = profile.unit if profile else None
            unit_uri = UNIT_TO_QUDT.get(unit, None) if unit else None

            # Generate observation
            self._observation_counter += 1
            obs_id = f"obs_{domain}_{field_name}_{self._observation_counter}"

            foi = DOMAIN_FOI.get(domain, "Unknown")

            # Generate deterministic SOSA Sensor and Platform metadata
            domain_clean = domain.replace(" ", "_").capitalize()
            field_clean = field_name.replace(" ", "_")
            platform_uri = f"https://w3id.org/enviromap/Platform_{domain_clean}"
            platform_label = f"{domain_clean} IoT Platform"
            sensor_uri = f"https://w3id.org/enviromap/Sensor_{domain_clean}_{field_clean}"
            sensor_label = f"{domain_clean} {field_clean.replace('_', ' ').title()} Sensor"

            observation = CanonicalObservation(
                observation_id=obs_id,
                observed_property_uri=decision.selected_concept_uri,
                observed_property_label=decision.selected_concept_label,
                value=value,
                unit=unit,
                unit_uri=unit_uri,
                result_time=str(timestamp) if timestamp else None,
                domain=domain,
                feature_of_interest=foi,
                location=location,
                source_table=source_table,
                source_field=field_name,
                source_value=value,
                mapping_confidence=decision.confidence,
                mapping_method=decision.mapping_method,
                sensor_uri=sensor_uri,
                sensor_label=sensor_label,
                platform_uri=platform_uri,
                platform_label=platform_label,
                provenance={
                    "agent_pipeline": "agentic",
                    "concept_uri": decision.selected_concept_uri,
                    "ontology_source": decision.selected_ontology_source,
                    "confidence": decision.confidence,
                    "llm_used": decision.llm_used,
                    "validation_status": validation.status,
                    "reasoning_chain": decision.reasoning_chain,
                },
            )
            observations.append(observation)

        return observations

    def _extract_timestamp(self, record: Dict[str, Any]) -> Optional[str]:
        """Extract timestamp from a record."""
        timestamp_keys = [
            "timestamp", "time", "datetime", "created_at", "observed_at",
            "result_time", "ts", "date_time", "observation_time",
            "reading_time", "recorded_at",
        ]
        for key in timestamp_keys:
            if key in record and record[key] is not None:
                val = record[key]
                if isinstance(val, datetime):
                    return val.isoformat()
                return str(val)
        return None

    def _extract_sensor_info(self, record: Dict[str, Any]) -> Optional[str]:
        """Extract sensor/device identifier from a record."""
        sensor_keys = [
            "sensor_id", "device_id", "sensor", "device", "node_id",
            "station_id", "device_name", "sensor_name",
        ]
        for key in sensor_keys:
            if key in record and record[key] is not None:
                return str(record[key])
        return None

    def _extract_location(self, record: Dict[str, Any]) -> Optional[str]:
        """Extract location/zone from a record."""
        location_keys = [
            "location", "zone", "site", "area", "position",
            "station", "region", "place",
        ]
        for key in location_keys:
            if key in record and record[key] is not None:
                return str(record[key])
        return None

