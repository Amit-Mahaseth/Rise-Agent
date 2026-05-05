"""
RAG retriever for script and FAQ knowledge base.
"""

import os
from typing import List, Optional
from pathlib import Path
import structlog

from app.core.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class RAGRetriever:
    """
    Retrieves relevant information from scripts and FAQ knowledge base.
    """

    def __init__(self):
        self.scripts_path = Path(settings.SCRIPTS_PATH)
        self.faq_path = Path(settings.FAQ_PATH)
        self._script_cache = {}
        self._faq_cache = {}

    async def get_script_content(self, language: str = "en") -> str:
        """
        Get conversation script content for specified language.

        Args:
            language: Language code

        Returns:
            Script content as string
        """
        try:
            if language in self._script_cache:
                return self._script_cache[language]

            # Try language-specific script first
            script_file = self.scripts_path / f"script_{language}.txt"
            if not script_file.exists():
                # Fallback to default script
                script_file = self.scripts_path / "base_script.txt"

            if script_file.exists():
                content = script_file.read_text(encoding='utf-8')
                self._script_cache[language] = content
                return content

            # Return default script if nothing found
            default_script = """
            Hello! I'm RiseAgent from Rupeezy. I'm here to help you understand our financial products and see if they're right for you.

            Could you tell me a bit about what you're looking for? Are you interested in a personal loan, credit card, or something else?

            What is your monthly income range?
            How much are you looking to borrow?
            What is the purpose of the loan?

            I understand your concern. Let me explain how our products work...
            """
            self._script_cache[language] = default_script
            return default_script

        except Exception as e:
            logger.error("Failed to load script", error=str(e), language=language)
            return "Hello! How can I help you today?"

    async def get_faq_content(self, query: str, language: str = "en") -> str:
        """
        Get relevant FAQ content based on query.

        Args:
            query: Search query
            language: Language code

        Returns:
            Relevant FAQ content
        """
        try:
            # Load FAQ content
            faq_content = await self._load_faq_content(language)

            if not faq_content:
                return ""

            # Simple keyword matching (in production, use semantic search)
            query_lower = query.lower()
            relevant_parts = []

            for line in faq_content.split('\n'):
                if any(keyword in query_lower for keyword in
                      ["interest", "rate", "fee", "charge", "eligible", "requirement",
                       "document", "process", "time", "approve", "disburse"]):
                    if any(keyword in line.lower() for keyword in
                          ["interest", "rate", "fee", "charge", "eligible", "requirement",
                           "document", "process", "time", "approve", "disburse"]):
                        relevant_parts.append(line)

            return '\n'.join(relevant_parts[:3]) if relevant_parts else faq_content[:500]

        except Exception as e:
            logger.error("Failed to get FAQ content", error=str(e), query=query)
            return ""

    async def _load_faq_content(self, language: str) -> str:
        """
        Load FAQ content for specified language.

        Args:
            language: Language code

        Returns:
            FAQ content as string
        """
        try:
            cache_key = f"faq_{language}"
            if cache_key in self._faq_cache:
                return self._faq_cache[cache_key]

            # Try language-specific FAQ
            faq_file = self.faq_path / f"faq_{language}.txt"
            if not faq_file.exists():
                faq_file = self.faq_path / "faq.txt"

            if faq_file.exists():
                content = faq_file.read_text(encoding='utf-8')
                self._faq_cache[cache_key] = content
                return content

            # Default FAQ content
            default_faq = """
            INTEREST RATES: Our personal loan rates start from 10.99% per annum.
            ELIGIBILITY: You need to be 21-60 years old, have a stable income, and good credit score.
            DOCUMENTS: PAN card, Aadhaar, bank statements, income proof, and address proof.
            PROCESSING TIME: Loan approval within 24 hours, disbursement within 2-3 business days.
            FEES: Processing fee of 1-2% of loan amount, no hidden charges.
            PREPAYMENT: No prepayment charges, you can repay anytime.
            """
            self._faq_cache[cache_key] = default_faq
            return default_faq

        except Exception as e:
            logger.error("Failed to load FAQ content", error=str(e), language=language)
            return ""

    async def search_similar_content(
        self,
        query: str,
        content_type: str = "faq",
        language: str = "en",
        limit: int = 3
    ) -> List[str]:
        """
        Search for similar content in knowledge base.

        Args:
            query: Search query
            content_type: Type of content (faq, script)
            language: Language code
            limit: Maximum results

        Returns:
            List of relevant content snippets
        """
        try:
            if content_type == "faq":
                content = await self._load_faq_content(language)
            else:
                content = await self.get_script_content(language)

            if not content:
                return []

            # Simple text search (in production, use vector search)
            query_words = set(query.lower().split())
            lines = content.split('\n')
            scored_lines = []

            for line in lines:
                line_words = set(line.lower().split())
                score = len(query_words.intersection(line_words))
                if score > 0:
                    scored_lines.append((score, line))

            # Sort by relevance and return top results
            scored_lines.sort(reverse=True, key=lambda x: x[0])
            return [line for score, line in scored_lines[:limit]]

        except Exception as e:
            logger.error("Failed to search content", error=str(e), query=query)
            return []