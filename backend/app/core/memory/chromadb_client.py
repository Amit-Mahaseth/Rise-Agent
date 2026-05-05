"""
ChromaDB client for vector storage and retrieval.
"""

import chromadb
from chromadb.config import Settings
import structlog

from app.core.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class ChromaDBClient:
    """
    Client for ChromaDB vector database operations.
    """

    def __init__(self):
        self.client = None
        self.collection = None

    async def initialize(self):
        """
        Initialize ChromaDB client and collection.
        """
        try:
            self.client = chromadb.PersistentClient(
                path=settings.chroma_path,
                settings=Settings(anonymized_telemetry=False)
            )

            # Create or get collection
            self.collection = self.client.get_or_create_collection(
                name="riseagent_memories",
                metadata={"description": "Conversation memories and context"}
            )

            logger.info("ChromaDB initialized", path=settings.chroma_path)

        except Exception as e:
            logger.error("Failed to initialize ChromaDB", error=str(e))
            raise

    async def store_memory(
        self,
        text: str,
        metadata: dict,
        id: str
    ):
        """
        Store text in vector database.

        Args:
            text: Text content to store
            metadata: Metadata dictionary
            id: Unique identifier
        """
        if not self.collection:
            await self.initialize()

        try:
            self.collection.add(
                documents=[text],
                metadatas=[metadata],
                ids=[id]
            )

            logger.debug("Memory stored", id=id, text_length=len(text))

        except Exception as e:
            logger.error("Failed to store memory", error=str(e), id=id)

    async def search_memories(
        self,
        query: str,
        n_results: int = 5,
        where: dict = None
    ) -> list:
        """
        Search for similar memories.

        Args:
            query: Search query
            n_results: Number of results to return
            where: Metadata filters

        Returns:
            List of similar documents with metadata
        """
        if not self.collection:
            await self.initialize()

        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                where=where,
                include=["documents", "metadatas", "distances"]
            )

            # Format results
            formatted_results = []
            if results["documents"] and results["documents"][0]:
                for i, doc in enumerate(results["documents"][0]):
                    formatted_results.append({
                        "content": doc,
                        "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                        "similarity": 1 - results["distances"][0][i] if results["distances"] else 0
                    })

            logger.debug(
                "Memory search completed",
                query=query[:50],
                results_count=len(formatted_results)
            )

            return formatted_results

        except Exception as e:
            logger.error("Failed to search memories", error=str(e), query=query)
            return []

    async def delete_memory(self, id: str):
        """
        Delete a memory by ID.

        Args:
            id: Memory identifier
        """
        if not self.collection:
            await self.initialize()

        try:
            self.collection.delete(ids=[id])
            logger.debug("Memory deleted", id=id)

        except Exception as e:
            logger.error("Failed to delete memory", error=str(e), id=id)

    async def get_collection_stats(self) -> dict:
        """
        Get collection statistics.

        Returns:
            Statistics dictionary
        """
        if not self.collection:
            await self.initialize()

        try:
            count = self.collection.count()
            return {
                "total_memories": count,
                "collection_name": self.collection.name
            }

        except Exception as e:
            logger.error("Failed to get collection stats", error=str(e))
            return {"error": str(e)}


# Global instance
chroma_client = ChromaDBClient()


async def initialize_chromadb():
    """
    Initialize the global ChromaDB client.
    """
    await chroma_client.initialize()