"""Vector database client for storing and searching code embeddings."""

import hashlib
import logging
from typing import Any

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

from ..core.config import get_settings

logger = logging.getLogger(__name__)


class VectorStore:
    """Client for Qdrant vector database operations."""

    def __init__(self) -> None:
        """Initialize Qdrant client and embedding model."""
        settings = get_settings()

        # Initialize Qdrant client
        self.client = QdrantClient(
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key,
        )

        # Initialize embedding model (converts text to vectors)
        self._encoder = None  # Lazy load on first use
        self.embedding_size = 384

        logger.info("VectorStore initialized (model loads on first use)")

    @property
    def encoder(self):
        """Lazy load the sentence transformer model on first use."""
        if self._encoder is None:
            logger.info("Loading SentenceTransformer model...")
            from sentence_transformers import SentenceTransformer

            self._encoder = SentenceTransformer("all-MiniLM-L6-v2")
            logger.info("SentenceTransformer model loaded OK")
        return self._encoder

        # Create collections if they don't exist
        self._ensure_collections()

    def _ensure_collections(self) -> None:
        """Create collections if they don't exist."""
        collections = ["code_snippets", "pr_history", "bug_patterns"]

        for collection_name in collections:
            try:
                self.client.get_collection(collection_name)
                logger.info(f"Collection '{collection_name}' already exists")
            except Exception:
                self.client.create_collection(
                    collection_name=collection_name,
                    vectors_config=VectorParams(
                        size=self.embedding_size,
                        distance=Distance.COSINE,
                    ),
                )
                logger.info(f"Created collection '{collection_name}'")

    def _string_to_id(self, text: str) -> int:
        """Convert string to numeric ID for Qdrant."""
        hash_bytes = hashlib.md5(text.encode(), usedforsecurity=False).digest()[:8]  # nosec B324
        return int.from_bytes(hash_bytes, byteorder="big")

    def encode_text(self, text: str) -> list[float]:
        """Convert text to embedding vector."""
        embedding = self.encoder.encode(text)
        return embedding.tolist()

    def store_code_snippet(
        self,
        code: str,
        metadata: dict[str, Any],
        snippet_id: str | None = None,
    ) -> int:
        """Store a code snippet with its embedding."""
        embedding = self.encode_text(code)

        if snippet_id is None:
            snippet_id = code
        numeric_id = self._string_to_id(snippet_id)

        self.client.upsert(
            collection_name="code_snippets",
            points=[
                PointStruct(
                    id=numeric_id,
                    vector=embedding,
                    payload={
                        "code": code,
                        "snippet_id": snippet_id,
                        **metadata,
                    },
                )
            ],
        )

        logger.info(f"Stored code snippet {snippet_id} (ID: {numeric_id})")
        return numeric_id

    def search_similar_code(
        self,
        code: str,
        limit: int = 5,
        score_threshold: float = 0.7,
    ) -> list[dict[str, Any]]:
        """Find similar code snippets."""
        query_embedding = self.encode_text(code)

        # Use query_points instead of search
        response = self.client.query_points(
            collection_name="code_snippets",
            query=query_embedding,
            limit=limit,
            score_threshold=score_threshold,
        )

        results = response.points

        similar_snippets = []
        for result in results:
            similar_snippets.append(
                {
                    "id": result.id,
                    "snippet_id": result.payload.get("snippet_id", str(result.id)),
                    "score": result.score,
                    "code": result.payload.get("code", ""),
                    "metadata": {
                        k: v for k, v in result.payload.items() if k not in ["code", "snippet_id"]
                    },
                }
            )

        logger.info(f"Found {len(similar_snippets)} similar code snippets")
        return similar_snippets
