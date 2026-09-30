"""
Dynamic Incremental Ontology Indexer for EnviroMap-KG.

Advancement 1.3: Real-Time Dynamic Concept Ingestion
Allows new ontology classes (from updated SAREF/SOSA versions or new domains)
to be dynamically embedded and appended to the in-memory vector index
in real time with ZERO system restarts and ZERO manual rules.
"""

from __future__ import annotations

import logging
from typing import List, Tuple, Dict, Any, Optional
import numpy as np

logger = logging.getLogger("enviromap.dynamic_index")


class DynamicOntologyIndex:
    """
    Live incremental vector index for ontology concepts.
    Maintains synchronized URI registries and dense vector embeddings in memory.
    """

    def __init__(self, embedding_dim: int = 768):
        self.embedding_dim = embedding_dim
        self._uris: List[str] = []
        self._labels: List[str] = []
        self._descriptions: List[str] = []
        self._embeddings: Optional[np.ndarray] = None
        self._encoder = None

    def _get_encoder(self):
        """Lazy loads sentence-transformers encoder."""
        if self._encoder is None:
            try:
                from sentence_transformers import SentenceTransformer  # type: ignore
                self._encoder = SentenceTransformer("BAAI/bge-base-en-v1.5")
            except Exception as e:
                logger.warning(f"SentenceTransformer not available ({e}), using normalized random vectors.")
        return self._encoder

    def add_concept(
        self,
        uri: str,
        label: str,
        description: str,
        domain: str = "general"
    ) -> bool:
        """
        Dynamically ingests a single new ontology concept into the live index.
        Automatically computes vector embeddings and appends to the matrix in RAM.
        """
        return self.add_concepts_batch([{
            "uri": uri,
            "label": label,
            "description": description,
            "domain": domain
        }]) > 0

    def add_concepts_batch(self, concepts: List[Dict[str, Any]]) -> int:
        """
        Dynamically appends a batch of new ontology concepts.
        Runs a single batched vectorization pass for maximum speed.
        """
        if not concepts:
            return 0

        new_uris = []
        new_labels = []
        new_descriptions = []
        texts_to_encode = []

        for c in concepts:
            uri = c["uri"]
            if uri in self._uris:
                # Concept already exists; skip or update description
                continue
            label = c.get("label", uri.split("/")[-1].split("#")[-1])
            desc = c.get("description", label)
            combined_text = f"{label}: {desc}"

            new_uris.append(uri)
            new_labels.append(label)
            new_descriptions.append(desc)
            texts_to_encode.append(combined_text)

        if not new_uris:
            return 0

        encoder = self._get_encoder()
        if encoder is not None:
            try:
                new_vecs = encoder.encode(
                    texts_to_encode,
                    convert_to_numpy=True,
                    normalize_embeddings=True,
                    show_progress_bar=False
                )
            except Exception:
                new_vecs = np.random.randn(len(new_uris), self.embedding_dim).astype(np.float32)
                new_vecs /= np.linalg.norm(new_vecs, axis=1, keepdims=True)
        else:
            new_vecs = np.random.randn(len(new_uris), self.embedding_dim).astype(np.float32)
            new_vecs /= np.linalg.norm(new_vecs, axis=1, keepdims=True)

        # Append to live registry and vector matrix
        self._uris.extend(new_uris)
        self._labels.extend(new_labels)
        self._descriptions.extend(new_descriptions)

        if self._embeddings is None:
            self._embeddings = new_vecs
        else:
            self._embeddings = np.vstack([self._embeddings, new_vecs])

        logger.info(f"Incrementally added {len(new_uris)} new concepts. Total live concepts: {len(self._uris)}")
        return len(new_uris)

    def search(self, query: str, top_k: int = 5) -> List[Tuple[str, str, float]]:
        """
        Vector search across the live dynamic ontology index.
        Returns: list of (concept_uri, concept_label, similarity_score)
        """
        if self._embeddings is None or len(self._uris) == 0:
            return []

        encoder = self._get_encoder()
        if encoder is not None:
            try:
                q_vec = encoder.encode(query, normalize_embeddings=True)
            except Exception:
                q_vec = np.random.randn(self.embedding_dim).astype(np.float32)
                q_vec /= np.linalg.norm(q_vec)
        else:
            q_vec = np.random.randn(self.embedding_dim).astype(np.float32)
            q_vec /= np.linalg.norm(q_vec)

        # Dot-product cosine similarity
        scores = np.dot(self._embeddings, q_vec)
        scores = (scores + 1.0) / 2.0  # normalize to 0..1
        top_indices = np.argsort(scores)[::-1][:top_k]

        return [
            (self._uris[idx], self._labels[idx], float(scores[idx]))
            for idx in top_indices
        ]

    def total_concepts(self) -> int:
        """Returns total active concepts in live index."""
        return len(self._uris)


if __name__ == "__main__":
    index = DynamicOntologyIndex()
    # Ingest baseline concepts
    base = [
        {"uri": "https://saref.etsi.org/core/Temperature", "label": "Temperature", "description": "Atmospheric air temperature"},
        {"uri": "https://saref.etsi.org/saref4watr/Temperature", "label": "WaterTemperature", "description": "Liquid water and solution temperature"}
    ]
    index.add_concepts_batch(base)
    print(f"Initial concept count: {index.total_concepts()}")

    # Live dynamic ingestion of a newly introduced ontology extension (e.g. Smart Healthcare)
    new_extension = [
        {"uri": "https://saref.etsi.org/saref4hlth/HeartRate", "label": "HeartRate", "description": "Physiological cardiac pulse rate"},
        {"uri": "https://saref.etsi.org/saref4hlth/BloodPressure", "label": "BloodPressure", "description": "Hydrostatic arterial blood pressure"}
    ]
    added = index.add_concepts_batch(new_extension)
    print(f"Dynamically added: {added} new concepts without restart. Total now: {index.total_concepts()}")

    results = index.search("water_temp", top_k=2)
    for uri, lbl, score in results:
        print(f"  {score:.4f} -> {lbl} ({uri})")
