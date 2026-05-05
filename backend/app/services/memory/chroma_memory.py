from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

from app.core.config import Settings


class ChromaMemoryService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        self.vectorstore = Chroma(
            collection_name="lead_memory",
            persist_directory=str(settings.chroma_dir),
            embedding_function=self.embeddings,
        )

    def store_turn(self, *, lead_id: str, call_id: str, speaker: str, text: str) -> None:
        # Production cost control: avoid persisting long raw transcripts.
        # We keep only the most recent/salient chunk per turn.
        max_chars = 280
        safe_text = (text or "").strip()
        if len(safe_text) > max_chars:
            safe_text = safe_text[:max_chars].rsplit(" ", 1)[0] + "..."

        document = Document(
            page_content=f"{speaker}: {safe_text}",
            metadata={"lead_id": lead_id, "call_id": call_id, "speaker": speaker, "kind": "turn"},
        )
        self.vectorstore.add_documents([document])

    def store_summary(self, *, lead_id: str, call_id: str, summary: str) -> None:
        document = Document(
            page_content=summary,
            metadata={"lead_id": lead_id, "call_id": call_id, "speaker": "system", "kind": "summary"},
        )
        self.vectorstore.add_documents([document])

    def retrieve_memories(self, *, lead_id: str, query: str, k: int = 4) -> list[Document]:
        return self.vectorstore.similarity_search(query=query, k=k, filter={"lead_id": lead_id})

