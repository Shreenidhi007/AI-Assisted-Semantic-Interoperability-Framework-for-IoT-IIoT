"""
Apache Jena Fuseki TDB2 Persistent Triplestore Connector.
Provides high-performance SPARQL 1.1 Query, Update, and Graph Store HTTP protocol operations
for city-scale knowledge graph storage with disk-backed B-Tree indexing.
"""

import os
import logging
import urllib.request
import urllib.parse
import json

logger = logging.getLogger("enviromap.jena")

class JenaFusekiConnector:
    def __init__(self, endpoint_url: str = None):
        # Reads from environment variable or defaults to local Fuseki instance
        self.endpoint_url = endpoint_url or os.getenv("JENA_FUSEKI_ENDPOINT", "http://127.0.0.1:3030/enviromap")
        self.query_url = f"{self.endpoint_url.rstrip('/')}/query"
        self.update_url = f"{self.endpoint_url.rstrip('/')}/update"
        self.data_url = f"{self.endpoint_url.rstrip('/')}/data"

    def is_alive(self, timeout: float = 1.5) -> bool:
        """Ping the Fuseki server to check availability."""
        try:
            req = urllib.request.Request(
                f"{self.endpoint_url.rstrip('/')}/$/ping",
                headers={"User-Agent": "EnviroMap-KG/2.0"}
            )
            with urllib.request.urlopen(req, timeout=timeout) as response:
                return response.status in [200, 204]
        except Exception:
            # Try a lightweight query probe if ping endpoint is disabled
            try:
                test_query = urllib.parse.urlencode({"query": "ASK { ?s ?p ?o }"})
                req = urllib.request.Request(
                    f"{self.query_url}?{test_query}",
                    headers={"Accept": "application/sparql-results+json"}
                )
                with urllib.request.urlopen(req, timeout=timeout) as resp:
                    return resp.status == 200
            except Exception:
                return False

    def query(self, sparql_query: str, timeout: float = 10.0) -> dict:
        """
        Executes a SPARQL 1.1 query against Jena Fuseki and returns standard JSON results.
        """
        data = urllib.parse.urlencode({"query": sparql_query}).encode("utf-8")
        req = urllib.request.Request(
            self.query_url,
            data=data,
            headers={
                "Accept": "application/sparql-results+json",
                "Content-Type": "application/x-www-form-urlencoded"
            },
            method="POST"
        )
        try:
            with urllib.request.urlopen(req, timeout=timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except Exception as e:
            logger.error(f"Jena SPARQL query failed: {e}")
            raise

    def update(self, sparql_update: str, timeout: float = 15.0) -> bool:
        """
        Executes a SPARQL 1.1 Update (INSERT DATA / DELETE DATA).
        """
        data = urllib.parse.urlencode({"update": sparql_update}).encode("utf-8")
        req = urllib.request.Request(
            self.update_url,
            data=data,
            headers={
                "Content-Type": "application/x-www-form-urlencoded"
            },
            method="POST"
        )
        try:
            with urllib.request.urlopen(req, timeout=timeout) as response:
                return response.status in [200, 204]
        except Exception as e:
            logger.error(f"Jena SPARQL update failed: {e}")
            raise

    def upload_turtle(self, turtle_file_path: str, timeout: float = 60.0) -> bool:
        """
        Bulk loads a W3C Turtle file into Fuseki TDB2 using the Graph Store HTTP Protocol (PUT /data?default).
        """
        if not os.path.exists(turtle_file_path):
            raise FileNotFoundError(f"Turtle file not found: {turtle_file_path}")

        url = f"{self.data_url}?default"
        with open(turtle_file_path, "rb") as f:
            data = f.read()

        req = urllib.request.Request(
            url,
            data=data,
            headers={"Content-Type": "text/turtle; charset=utf-8"},
            method="PUT"
        )
        try:
            with urllib.request.urlopen(req, timeout=timeout) as response:
                logger.info(f"Successfully uploaded {os.path.basename(turtle_file_path)} to Jena Fuseki TDB2.")
                return response.status in [200, 201, 204]
        except Exception as e:
            logger.error(f"Failed to upload Turtle file to Jena: {e}")
            raise

