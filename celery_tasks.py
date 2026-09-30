"""
Celery Task Definitions for EnviroMap-KG Agentic Pipeline.
Executes LangGraph 6-Agent workflow in parallel worker threads.
"""

import sys
import os
import logging
import threading

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from orchestrator.celery_app import celery_app, is_redis_available

logger = logging.getLogger("enviromap.tasks")

@celery_app.task(bind=True, max_retries=3, default_retry_delay=10)
def async_run_domain_pipeline(self, db_name: str, table_name: str, domain: str = None) -> dict:
    """
    Asynchronously executes the multi-agent alignment and validation cycle
    for a given database and table using the LangGraph StateGraph.
    """
    logger.info(f"[Celery Worker] Starting domain pipeline for {db_name}.{table_name} (Domain: {domain})")
    
    # Strictly do not ingest thingsboard, simulation, or digital twin data into Knowledge Graph
    db_l = (db_name or "").lower()
    tbl_l = (table_name or "").lower()
    dom_l = (domain or "").lower()
    if any(ex in db_l or ex in tbl_l or ex in dom_l for ex in ('thingsboard', 'digital_twin', 'digitaltwin', 'sim')):
        if not ("wq" in db_l or "water" in db_l):
            logger.info(f"[Celery Worker] Bypassing excluded platform {db_name}.{table_name} — strictly not stored in Knowledge Graph.")
            return {"status": "skipped", "reason": "thingsboard and digital_twin data are excluded from knowledge graph", "db": db_name, "table": table_name}

    try:
        # Import components lazily to conserve worker memory on cold start
        from components.data_acquisition import DataAcquisition
        from ontology_registry.registry import OntologyRegistry
        from components.embedding_model import EmbeddingModel
        from agents.discovery_agent import DiscoveryAgent
        from agents.alignment_agent import AlignmentAgent
        from agents.mapping_agent import MappingAgent
        from agents.reasoning_agent import ReasoningAgent
        from agents.validation_agent import ValidationAgent
        from agents.learning_agent import LearningAgent
        from semantic_layer.translator import SemanticTranslator

        registry = OntologyRegistry()
        embedding_model = EmbeddingModel()
        da = DataAcquisition()

        # 1. Discovery
        discovery_agent = DiscoveryAgent()
        profiles = discovery_agent.execute({
            "db_name": db_name,
            "schema": "public",
            "table": table_name,
            "domain": domain or db_name,
            "source_platform": "PostgreSQL-TimescaleDB",
            "data_acquisition": da
        })

        if not profiles:
            return {"status": "skipped", "reason": "no measurement columns discovered", "db": db_name, "table": table_name}

        # 2. Alignment & Mapping & Validation
        alignment_agent = AlignmentAgent()
        mapping_agent = MappingAgent()
        reasoning_agent = ReasoningAgent()
        validation_agent = ValidationAgent()
        learning_agent = LearningAgent()
        translator = SemanticTranslator()

        processed_count = 0
        valid_count = 0

        for profile in profiles:
            candidates = alignment_agent.execute({
                "discovery_profile": profile,
                "registry": registry,
                "embedding_model": embedding_model
            })
            mapping_record = mapping_agent.execute({
                "discovery_profile": profile,
                "candidates": candidates
            })
            decision = reasoning_agent.execute({
                "mapping_record": mapping_record,
                "registry": registry
            })
            validation = validation_agent.execute({
                "reasoning_decision": decision,
                "discovery_profile": profile,
                "registry": registry
            })
            learning_agent.execute({
                "validation_result": validation,
                "reasoning_decision": decision,
                "discovery_profile": profile
            })

            processed_count += 1
            if validation.status.value in ["valid", "valid_with_warnings"]:
                valid_count += 1

        da.close()
        logger.info(f"[Celery Worker] Completed {db_name}.{table_name}: {valid_count}/{processed_count} fields validated.")
        return {
            "status": "success",
            "db": db_name,
            "table": table_name,
            "profiles_count": processed_count,
            "validated_count": valid_count
        }

    except Exception as exc:
        logger.error(f"[Celery Worker] Error executing pipeline for {db_name}.{table_name}: {exc}")
        raise self.retry(exc=exc)

def _run_in_thread(db_name: str, table_name: str, domain: str = None):
    """Fallback executor in a background daemon thread."""
    try:
        async_run_domain_pipeline(db_name, table_name, domain)
    except Exception as e:
        logger.error(f"[Fallback Thread] Execution error: {e}")

def dispatch_domain_task(db_name: str, table_name: str, domain: str = None) -> dict:
    """
    Intelligent dispatcher:
    1. If Redis is available, dispatches to Celery distributed worker queue.
    2. If Redis is offline, gracefully executes in a non-blocking background thread.
    """
    if is_redis_available():
        task = async_run_domain_pipeline.delay(db_name, table_name, domain)
        logger.info(f"Dispatched {db_name}.{table_name} to Celery queue (Task ID: {task.id})")
        return {"mode": "celery", "task_id": str(task.id), "status": "queued"}
    else:
        logger.info(f"Redis not detected; running {db_name}.{table_name} in background daemon thread.")
        t = threading.Thread(target=_run_in_thread, args=(db_name, table_name, domain), daemon=True)
        t.start()
        return {"mode": "thread_fallback", "status": "started"}
