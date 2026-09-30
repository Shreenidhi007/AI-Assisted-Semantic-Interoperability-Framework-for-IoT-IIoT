"""
Federated SPARQL 1.1 Query Engine for EnviroMap-KG.
Intelligently routes queries to Apache Jena Fuseki TDB2 if available,
with automatic fallback to local in-memory RDFLib graph.
"""

import os
import sys
import logging
from typing import Dict, Any, List

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from knowledge_graph.jena_connector import JenaFusekiConnector

logger = logging.getLogger("enviromap.sparql")

_rdflib_graph = None
_jena_connector = None

def get_jena_connector() -> JenaFusekiConnector:
    global _jena_connector
    if _jena_connector is None:
        _jena_connector = JenaFusekiConnector()
    return _jena_connector

def get_rdflib_graph():
    global _rdflib_graph
    if _rdflib_graph is None:
        import rdflib
        kg_path = os.path.join(PROJECT_ROOT, "data", "output", "enviromap_kg.ttl")
        _rdflib_graph = rdflib.Graph()
        if os.path.exists(kg_path):
            logger.info(f"Loading RDFLib graph from {kg_path}...")
            _rdflib_graph.parse(kg_path, format="turtle")
            logger.info(f"Loaded {len(_rdflib_graph):,} triples into RDFLib.")
        else:
            logger.warning(f"Turtle file not found at {kg_path}; starting with empty graph.")
    return _rdflib_graph

def execute_sparql_query(query_str: str) -> List[Dict[str, Any]]:
    """
    Executes a SPARQL 1.1 query with automatic engine selection:
    1. Routes to Apache Jena Fuseki TDB2 if active and online.
    2. Falls back to local in-memory RDFLib engine seamlessly.
    """
    connector = get_jena_connector()
    if connector.is_alive():
        logger.info("Executing SPARQL query on Apache Jena Fuseki TDB2...")
        try:
            raw_res = connector.query(query_str)
            bindings = raw_res.get("results", {}).get("bindings", [])
            clean_results = []
            for row in bindings:
                clean_row = {}
                for var, val_obj in row.items():
                    clean_row[var] = val_obj.get("value")
                clean_results.append(clean_row)
            return clean_results
        except Exception as e:
            logger.warning(f"Jena query failed ({e}); falling back to local RDFLib...")

    # Fallback to RDFLib
    logger.info("Executing SPARQL query on local RDFLib engine...")
    g = get_rdflib_graph()
    qres = g.query(query_str)
    results = []
    for row in qres:
        if hasattr(row, "asdict"):
            results.append({str(k): str(v) for k, v in row.asdict().items()})
        else:
            # Simple tuple
            results.append({f"col_{i}": str(v) for i, v in enumerate(row)})
    return results
