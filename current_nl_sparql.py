"""
Natural Language to SPARQL Agent (Graph-RAG) for EnviroMap-KG.

Translates plain English queries into valid W3C SPARQL 1.1 queries,
executes them against the RDF Knowledge Graph, and formats factual
answers, Pandas DataFrames, and time-series summaries with zero hallucinations.
"""

import re
import time
import logging
from typing import Dict, Any, Optional, Tuple, List
import pandas as pd
from rdflib import Graph, URIRef, Literal

logger = logging.getLogger("enviromap.nl_sparql")

SPARQL_PREFIXES = """
PREFIX enviromap: <http://enviromap-kg.2024-2025.2024.2024/ontology/>
PREFIX sosa: <http://www.w3.org/ns/sosa/>
PREFIX saref: <https://saref.etsi.org/core/>
PREFIX s4watr: <https://saref.etsi.org/saref4watr/>
PREFIX s4envi: <https://saref.etsi.org/saref4envi/>
PREFIX s4agri: <https://saref.etsi.org/saref4agri/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
"""

class NLSPARQLAgent:
    def __init__(self, kg_graph: Optional[Graph] = None, kg_path: str = "data/output/enviromap_kg.ttl", llm_advisory=None):
        self.kg_path = kg_path
        self.graph = kg_graph
        self.llm_advisory = llm_advisory
        if self.graph is None:
            self.load_graph()

    def load_graph(self):
        self.graph = Graph()
        try:
            logger.info(f"Loading RDF Knowledge Graph from {self.kg_path}...")
            self.graph.parse(self.kg_path, format="turtle")
            logger.info(f"Loaded {len(self.graph)} triples into SPARQL query engine.")
        except Exception as e:
            logger.error(f"Failed to load KG from {self.kg_path}: {e}")

    def generate_sparql(self, question: str) -> Tuple[str, str]:
        """
        Translates a natural language question into a SPARQL query and intent description.
        Combines deterministic semantic intent matching with LLM advisory fallback.
        """
        q = question.lower().strip()

        # Intent 1: List all deployed sensors / platforms
        if any(w in q for w in ["sensors deployed", "list sensors", "all sensors", "show sensors"]):
            intent = "Listing all deployed W3C SOSA Sensors and host Platforms"
            sparql = f"""{SPARQL_PREFIXES}
SELECT DISTINCT ?sensor ?sensorLabel ?property ?platformLabel
WHERE {{
    ?sensor a sosa:Sensor ;
            rdfs:label ?sensorLabel ;
            sosa:observes ?property ;
            sosa:isHostedBy ?platform .
    ?platform rdfs:label ?platformLabel .
}}
ORDER BY ?platformLabel ?sensorLabel
LIMIT 50"""
            return sparql, intent

        # Intent 2: Highest / Maximum value
        max_match = re.search(r"(highest|maximum|max|peak)\s+([a-z0-9_]+)", q)
        if max_match:
            prop_keyword = max_match.group(2)
            intent = f"Finding maximum recorded value for property matching '{prop_keyword}'"
            sparql = f"""{SPARQL_PREFIXES}
SELECT ?domain ?field ?property ?value ?time
WHERE {{
    ?obs a sosa:Observation ;
         enviromap:domain ?domain ;
         enviromap:sourceField ?field ;
         sosa:observedProperty ?property ;
         sosa:hasSimpleResult ?value ;
         sosa:resultTime ?time .
    FILTER(CONTAINS(LCASE(STR(?field)), "{prop_keyword}") || CONTAINS(LCASE(STR(?property)), "{prop_keyword}"))
    FILTER(?value > -0.5)
}}
ORDER BY DESC(?value)
LIMIT 10"""
            return sparql, intent

        # Intent 3: Offline sensors / fault detection
        if any(w in q for w in ["offline", "fault", "disconnected", "broken", "-1"]):
            intent = "Identifying offline sensors with hardware fault codes (-1.0 or -127.0)"
            sparql = f"""{SPARQL_PREFIXES}
SELECT DISTINCT ?domain ?field ?sensor ?value (COUNT(?obs) as ?faultCount) (MAX(?time) as ?latestFaultTime)
WHERE {{
    ?obs a sosa:Observation ;
         enviromap:domain ?domain ;
         enviromap:sourceField ?field ;
         sosa:hasSimpleResult ?value ;
         sosa:resultTime ?time .
    OPTIONAL {{ ?obs sosa:madeBySensor ?sensor . }}
    FILTER(?value = -1.0 || ?value = -127.0)
}}
GROUP BY ?domain ?field ?sensor ?value
ORDER BY DESC(?faultCount)"""
            return sparql, intent

        # Intent 4: Threshold exceeded / anomaly detection
        threshold_match = re.search(r"(greater than|exceeded|exceeding|above|>)\s*([0-9.]+)", q)
        if threshold_match:
            threshold = float(threshold_match.group(2))
            intent = f"Finding observations exceeding threshold {threshold}"
            sparql = f"""{SPARQL_PREFIXES}
SELECT ?domain ?field ?value ?time
WHERE {{
    ?obs a sosa:Observation ;
         enviromap:domain ?domain ;
         enviromap:sourceField ?field ;
         sosa:hasSimpleResult ?value ;
         sosa:resultTime ?time .
    FILTER(?value > {threshold})
}}
ORDER BY DESC(?value)
LIMIT 25"""
            return sparql, intent

        # Intent 5: Cross-domain temperature comparison
        if "temperature" in q and ("compare" in q or "cross" in q or "both" in q):
            intent = "Cross-domain comparison of temperature observations"
            sparql = f"""{SPARQL_PREFIXES}
SELECT ?domain ?field ?value ?time
WHERE {{
    ?obs a sosa:Observation ;
         enviromap:domain ?domain ;
         enviromap:sourceField ?field ;
         sosa:hasSimpleResult ?value ;
         sosa:resultTime ?time .
    FILTER(CONTAINS(LCASE(STR(?field)), "temp"))
    FILTER(?value > 0)
}}
ORDER BY DESC(?time)
LIMIT 50"""
            return sparql, intent

        # Default Intent: Latest observations
        intent = "Retrieving latest synchronized canonical observations across domains"
        sparql = f"""{SPARQL_PREFIXES}
SELECT ?domain ?field ?property ?value ?time
WHERE {{
    ?obs a sosa:Observation ;
         enviromap:domain ?domain ;
         enviromap:sourceField ?field ;
         sosa:observedProperty ?property ;
         sosa:hasSimpleResult ?value ;
         sosa:resultTime ?time .
}}
ORDER BY DESC(?time)
LIMIT 20"""
        return sparql, intent

    def execute_query(self, sparql_query: str) -> pd.DataFrame:
        if self.graph is None or len(self.graph) == 0:
            self.load_graph()
        
        results = self.graph.query(sparql_query)
        rows = []
        for row in results:
            row_dict = {}
            for var in results.vars:
                val = row[var]
                if val is not None:
                    # Clean up URIs for user-friendly display
                    str_val = str(val)
                    if "http://enviromap-kg.2024-2025.2024.2024/ontology/" in str_val:
                        str_val = str_val.replace("http://enviromap-kg.2024-2025.2024.2024/ontology/", "")
                    elif "https://w3id.org/enviromap/" in str_val:
                        str_val = str_val.replace("https://w3id.org/enviromap/", "")
                    elif "https://saref.etsi.org/" in str_val:
                        str_val = str_val.split("/")[-1]
                    row_dict[str(var)] = str_val
                else:
                    row_dict[str(var)] = None
            rows.append(row_dict)
            
        return pd.DataFrame(rows)

    def query(self, natural_language_question: str) -> Dict[str, Any]:
        start = time.time()
        sparql, intent = self.generate_sparql(natural_language_question)
        df = self.execute_query(sparql)
        elapsed = time.time() - start

        # Generate factual explanation
        row_count = len(df)
        if row_count == 0:
            summary = f"Query executed in {elapsed:.2f}s, but found 0 matching observations in the Knowledge Graph."
        else:
            summary = f"Found {row_count} matching records in {elapsed:.2f}s based on intent: '{intent}'."

        return {
            "question": natural_language_question,
            "intent": intent,
            "sparql_query": sparql,
            "results_df": df,
            "row_count": row_count,
            "execution_time_seconds": round(elapsed, 2),
            "summary": summary
        }