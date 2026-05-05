"""
Per-lead memory service backed by ChromaDB.
Stores conversation history, objections, rebuttals, and classification
across multiple calls with the same lead.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Optional

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_chroma import Chroma

from config import get_settings

logger = logging.getLogger("riseagent.memory")


def _get_embeddings() -> HuggingFaceEmbeddings:
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )


def _get_lead_collection(lead_id: str) -> Chroma:
    """Get or create a ChromaDB collection for a specific lead."""
    settings = get_settings()
    persist_dir = str(settings.chroma_persist_dir / f"lead_{lead_id}")
    return Chroma(
        collection_name=f"lead_{lead_id}",
        embedding_function=_get_embeddings(),
        persist_directory=persist_dir,
    )


async def store_call_memory(
    lead_id: str,
    call_number: int,
    language_detected: str,
    objections_raised: list[str],
    rebuttals_used: list[str],
    interest_signals: list[str],
    conversation_summary: str,
    classification: str,
) -> None:
    """Store a call's results in the lead's ChromaDB collection."""
    try:
        collection = _get_lead_collection(lead_id)

        memory_doc = {
            "lead_id": lead_id,
            "call_number": call_number,
            "language_detected": language_detected,
            "objections_raised": objections_raised,
            "rebuttals_used": rebuttals_used,
            "interest_signals": interest_signals,
            "conversation_summary": conversation_summary,
            "classification": classification,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        # Store as a document with metadata
        doc_text = (
            f"Call #{call_number} with lead {lead_id}. "
            f"Language: {language_detected}. "
            f"Objections: {', '.join(objections_raised) if objections_raised else 'none'}. "
            f"Classification: {classification}. "
            f"Summary: {conversation_summary}"
        )

        collection.add_texts(
            texts=[doc_text],
            metadatas=[{
                "lead_id": lead_id,
                "call_number": str(call_number),
                "language": language_detected,
                "classification": classification,
                "objections": json.dumps(objections_raised),
                "rebuttals": json.dumps(rebuttals_used),
                "interest_signals": json.dumps(interest_signals),
                "summary": conversation_summary,
                "timestamp": memory_doc["timestamp"],
            }],
            ids=[f"{lead_id}_call_{call_number}"],
        )

        logger.info(
            "Stored memory for lead %s, call #%d [%s]",
            lead_id, call_number, classification,
        )
    except Exception as exc:
        logger.error("Failed to store call memory for lead %s: %s", lead_id, exc)


async def retrieve_lead_memory(lead_id: str, last_n: int = 2) -> str:
    """
    Retrieve the last N call records for a lead.
    Returns a formatted string for injection into the system prompt.
    """
    try:
        collection = _get_lead_collection(lead_id)
        results = collection.get(
            where={"lead_id": lead_id},
            include=["metadatas", "documents"],
        )

        if not results or not results.get("metadatas"):
            return "No previous interactions with this lead."

        # Sort by call number descending, take last N
        entries = list(zip(results["metadatas"], results["documents"]))
        entries.sort(key=lambda x: int(x[0].get("call_number", 0)), reverse=True)
        entries = entries[:last_n]

        memory_lines = []
        for meta, doc in entries:
            call_num = meta.get("call_number", "?")
            lang = meta.get("language", "unknown")
            classification = meta.get("classification", "unknown")
            objections = json.loads(meta.get("objections", "[]"))
            rebuttals = json.loads(meta.get("rebuttals", "[]"))
            summary = meta.get("summary", "No summary available.")

            memory_lines.append(
                f"--- Call #{call_num} ---\n"
                f"Language: {lang}\n"
                f"Classification: {classification}\n"
                f"Objections raised: {', '.join(objections) if objections else 'none'}\n"
                f"Rebuttals already used: {', '.join(rebuttals) if rebuttals else 'none'}\n"
                f"Summary: {summary}"
            )

        return "\n\n".join(memory_lines)
    except Exception as exc:
        logger.warning("Failed to retrieve memory for lead %s: %s", lead_id, exc)
        return "No previous interactions with this lead."


async def get_handled_objections(lead_id: str) -> list[str]:
    """Get list of objections already handled across all calls with this lead."""
    try:
        collection = _get_lead_collection(lead_id)
        results = collection.get(
            where={"lead_id": lead_id},
            include=["metadatas"],
        )

        if not results or not results.get("metadatas"):
            return []

        all_objections = set()
        for meta in results["metadatas"]:
            objs = json.loads(meta.get("objections", "[]"))
            all_objections.update(objs)

        return list(all_objections)
    except Exception as exc:
        logger.warning("Failed to get handled objections for lead %s: %s", lead_id, exc)
        return []


async def get_call_count(lead_id: str) -> int:
    """Get how many calls we've made to this lead."""
    try:
        collection = _get_lead_collection(lead_id)
        results = collection.get(
            where={"lead_id": lead_id},
            include=["metadatas"],
        )
        if results and results.get("ids"):
            return len(results["ids"])
        return 0
    except Exception:
        return 0
