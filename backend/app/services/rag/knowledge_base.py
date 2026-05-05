from pathlib import Path

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

from app.core.config import Settings


class KnowledgeBaseService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        self.vectorstore = Chroma(
            collection_name="rupeezy_knowledge_base",
            persist_directory=str(settings.chroma_dir),
            embedding_function=self.embeddings,
        )
        self._bootstrap()

    def _bootstrap(self) -> None:
        self.settings.chroma_dir.mkdir(parents=True, exist_ok=True)
        if self.vectorstore._collection.count() > 0:
            return

        splitter = RecursiveCharacterTextSplitter(chunk_size=700, chunk_overlap=120)
        documents: list[Document] = []

        for filename, topic in (("base_script.md", "base_script"), ("faq.md", "faq")):
            file_path = Path(self.settings.knowledge_dir / filename)
            if not file_path.exists():
                continue
            content = file_path.read_text(encoding="utf-8")
            chunks = splitter.split_text(content)
            for index, chunk in enumerate(chunks):
                documents.append(
                    Document(
                        page_content=chunk,
                        metadata={"source": filename, "topic": topic, "chunk_index": index},
                    )
                )

        if documents:
            self.vectorstore.add_documents(documents)

    def retrieve(self, query: str, k: int = 4) -> list[Document]:
        return self.vectorstore.similarity_search(query=query, k=k)

