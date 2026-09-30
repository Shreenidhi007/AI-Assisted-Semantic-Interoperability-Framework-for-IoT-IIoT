"""
Embedding Model wrapper for EnviroMap-KG Alignment Agent.

Uses sentence-transformers ('BAAI/bge-base-en-v1.5') for semantic embeddings,
with a robust rapidfuzz fallback if sentence-transformers or PyTorch is unavailable.
"""

from __future__ import annotations

import sys
import os
import logging
from builtins import (
    str, int, float, len, max, min, sum, enumerate, Exception, ImportError
)
from typing import List, Tuple, Optional, Dict, Any

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class EmbeddingModel:
    """
    Computes semantic similarity embeddings between source terms and ontology concepts.
    """

    def __init__(self, model_name: str = 'BAAI/bge-base-en-v1.5', use_reranker: bool = False):
        self.logger = logging.getLogger("enviromap.embedding_model")
        self.model_name = model_name
        self.use_reranker = use_reranker
        self._model = None
        self._reranker = None
        self._registry_embeddings = None
        self._registry_uris: List[str] = []
        self._registry_texts: List[str] = []
        self._use_fallback = False

    def _get_reranker(self):
        """Lazy loads the CrossEncoderReranker component."""
        if self._reranker is None:
            import importlib
            for mod_name in ["reranker", "agents.reranker", "components.reranker"]:
                try:
                    mod = importlib.import_module(mod_name)
                    cls = getattr(mod, "CrossEncoderReranker", None)
                    if cls:
                        self._reranker = cls()
                        break
                except Exception:
                    pass
        return self._reranker

    def _lazy_load_model(self):
        """Loads the sentence transformer model lazily."""
        if self._model is None and not self._use_fallback:
            try:
                from sentence_transformers import SentenceTransformer  # type: ignore
                self._model = SentenceTransformer(self.model_name)
                self.logger.info(f"Loaded sentence-transformers model '{self.model_name}'")
            except Exception as e:
                self.logger.warning(f"sentence-transformers not available ({e}). Using rapidfuzz fallback for similarity.")
                self._use_fallback = True

    def precompute_registry_embeddings(self, registry_entries: List[Tuple[str, str]]):
        """
        Precomputes and caches embeddings for the ontology registry.
        registry_entries: list of (concept_uri, text_description)
        """
        if not registry_entries:
            return

        self._lazy_load_model()
        self._registry_uris = [entry[0] for entry in registry_entries]
        self._registry_texts = [entry[1] for entry in registry_entries]

        if not self._use_fallback and self._model is not None:
            try:
                self._registry_embeddings = self._model.encode(
                    self._registry_texts,
                    convert_to_numpy=True,
                    show_progress_bar=False,
                    normalize_embeddings=True
                )
                self.logger.info(f"Successfully encoded {len(self._registry_texts)} ontology concepts into embeddings.")
            except Exception as e:
                self.logger.warning(f"Failed to precompute embeddings ({e}), enabling fallback.")
                self._use_fallback = True
        else:
            self._use_fallback = True

    def compute_similarity(self, query: str, target: str) -> float:
        """
        Computes cosine or fuzzy similarity between two strings.
        """
        self._lazy_load_model()
        if not self._use_fallback and self._model is not None:
            try:
                import numpy as np  # type: ignore
                q_emb = self._model.encode(query, normalize_embeddings=True)
                t_emb = self._model.encode(target, normalize_embeddings=True)
                sim = float(np.dot(q_emb, t_emb))
                return max(0.0, min(1.0, (sim + 1.0) / 2.0))
            except Exception:
                pass

        # Rapidfuzz fallback
        try:
            from rapidfuzz import fuzz  # type: ignore
            return float(fuzz.token_set_ratio(query.lower(), target.lower()) / 100.0)
        except ImportError:
            return 0.5 if query.lower() in target.lower() or target.lower() in query.lower() else 0.0

    def find_similar(
        self,
        query_text: str,
        top_k: int = 5,
        rerank: bool = False
    ) -> List[Tuple[str, float]]:
        """
        Finds the top-k most similar ontology concepts for query_text.
        If rerank or self.use_reranker is True, executes Two-Stage retrieval:
          Stage 1: Bi-Encoder dot-product candidate pool (k=10)
          Stage 2: Cross-Encoder joint token cross-attention reranking
        Returns: list of (concept_uri, similarity_score 0.0-1.0)
        """
        if not self._registry_uris:
            return []

        should_rerank = rerank or self.use_reranker
        # Expand candidate pool if reranking
        pool_k = min(len(self._registry_uris), max(top_k * 2, 8)) if should_rerank else top_k

        self._lazy_load_model()
        candidates_raw: List[Dict[str, Any]] = []

        if not self._use_fallback and self._registry_embeddings is not None:
            try:
                import numpy as np  # type: ignore
                q_emb = self._model.encode(query_text, normalize_embeddings=True)
                # Cosine similarities since both are normalized
                scores = np.dot(self._registry_embeddings, q_emb)
                # Map -1..1 to 0..1
                scores = (scores + 1.0) / 2.0

                top_indices = np.argsort(scores)[::-1][:pool_k]
                candidates_raw = [
                    {
                        "uri": self._registry_uris[idx],
                        "text": self._registry_texts[idx],
                        "bi_score": float(scores[idx])
                    }
                    for idx in top_indices
                ]
            except Exception as e:
                self.logger.warning(f"Vector search failed ({e}), using lexical fallback.")

        if not candidates_raw:
            # Fallback using rapidfuzz
            try:
                from rapidfuzz import fuzz, process  # type: ignore
                results = process.extract(
                    query_text.lower(),
                    [t.lower() for t in self._registry_texts],
                    scorer=fuzz.token_sort_ratio,
                    limit=pool_k
                )
                candidates_raw = [
                    {
                        "uri": self._registry_uris[idx],
                        "text": self._registry_texts[idx],
                        "bi_score": float(score / 100.0)
                    }
                    for match, score, idx in results
                ]
            except Exception:
                # Basic token overlap fallback
                q_lower = query_text.lower()
                scored = []
                for i, text in enumerate(self._registry_texts):
                    common = sum(1 for w in q_lower.split() if w in text.lower())
                    score = min(1.0, common * 0.3)
                    scored.append({
                        "uri": self._registry_uris[i],
                        "text": text,
                        "bi_score": score
                    })
                scored.sort(key=lambda x: x["bi_score"], reverse=True)
                candidates_raw = scored[:pool_k]

        # Stage 2: Cross-Encoder Reranking
        if should_rerank and candidates_raw:
            reranker = self._get_reranker()
            if reranker:
                reranked = reranker.rerank(query_text, candidates_raw, top_k=top_k)
                return [(item["uri"], item.get("final_score", item.get("cross_score", 0.5))) for item in reranked]

        # Return standard Stage 1 results
        return [(c["uri"], c["bi_score"]) for c in candidates_raw[:top_k]]

