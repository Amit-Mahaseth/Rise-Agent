"""
Knowledge base loader — loads AP script and objection FAQ into ChromaDB
for RAG retrieval during conversations.
"""

from __future__ import annotations

import logging
from pathlib import Path

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_chroma import Chroma

from config import get_settings

logger = logging.getLogger("riseagent.knowledge")

_retriever = None
_vectorstore = None


def _get_embeddings() -> HuggingFaceEmbeddings:
    """Multilingual embeddings for Hindi/Tamil/Telugu/etc."""
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )


def load_knowledge_base() -> Chroma:
    """Load AP script + objection FAQ into ChromaDB and return the vectorstore."""
    global _vectorstore
    if _vectorstore is not None:
        return _vectorstore

    settings = get_settings()
    knowledge_dir = settings.knowledge_dir
    persist_dir = str(settings.chroma_persist_dir / "rupeezy_knowledge")

    # Load documents
    docs = []
    for filename in ["ap_script.txt", "objections_faq.txt"]:
        filepath = knowledge_dir / filename
        if filepath.exists():
            loader = TextLoader(str(filepath), encoding="utf-8")
            docs.extend(loader.load())
            logger.info("Loaded knowledge file: %s", filename)
        else:
            logger.warning("Knowledge file not found: %s", filepath)

    if not docs:
        logger.error("No knowledge documents loaded!")
        raise FileNotFoundError("No knowledge base files found")

    # Split into chunks
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["\n\n", "\n", ". ", " "],
    )
    chunks = splitter.split_documents(docs)
    logger.info("Split knowledge base into %d chunks", len(chunks))

    # Embed and store in ChromaDB
    embeddings = _get_embeddings()
    _vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        collection_name="rupeezy_knowledge",
        persist_directory=persist_dir,
    )
    logger.info("Knowledge base loaded into ChromaDB at %s", persist_dir)
    return _vectorstore


def get_retriever(k: int = 3):
    """Return a LangChain retriever backed by the knowledge base."""
    global _retriever
    if _retriever is None:
        vs = load_knowledge_base()
        _retriever = vs.as_retriever(
            search_type="similarity",
            search_kwargs={"k": k},
        )
    return _retriever
