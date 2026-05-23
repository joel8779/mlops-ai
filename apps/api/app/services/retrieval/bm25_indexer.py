"""BM25 Indexer - Keyword-based search using BM25 algorithm."""

import math
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Any, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.domain import Candidate, Resume


@dataclass
class BM25Document:
    """Document for BM25 indexing."""

    doc_id: UUID
    tokens: list[str]
    metadata: dict


class BM25Indexer:
    """BM25 indexer for keyword search."""

    def __init__(
        self,
        db: AsyncSession,
        k1: float = 1.5,
        b: float = 0.75,
    ) -> None:
        """Initialize BM25 indexer.

        Args:
            db: Database session
            k1: BM25 k1 parameter (term saturation)
            b: BM25 b parameter (length normalization)
        """
        self.db = db
        self.k1 = k1
        self.b = b
        self.index: dict[UUID, dict[str, float]] = {}
        self.doc_lengths: dict[UUID, int] = {}
        self.avg_doc_length: float = 0.0
        self.total_docs: int = 0

    async def build_index(self, organization_id: UUID) -> None:
        """Build BM25 index for organization.

        Args:
            organization_id: Organization ID
        """
        # Get all candidates with resumes
        query = (
            select(Candidate, Resume)
            .join(Resume, Candidate.id == Resume.candidate_id)
            .where(Candidate.organization_id == organization_id)
        )
        result = await self.db.execute(query)
        rows = result.all()

        documents = []
        for candidate, resume in rows:
            text = self._extract_text(candidate, resume)
            tokens = self._tokenize(text)
            documents.append(
                BM25Document(
                    doc_id=candidate.id,
                    tokens=tokens,
                    metadata={"candidate_id": candidate.id},
                )
            )

        self._build_bm25_index(documents)

    def _extract_text(self, candidate: Candidate, resume: Resume) -> str:
        """Extract searchable text from candidate and resume.

        Args:
            candidate: Candidate object
            resume: Resume object

        Returns:
            Extracted text
        """
        parts = [
            candidate.full_name or "",
            candidate.headline or "",
            candidate.location or "",
            resume.extracted_text or "",
        ]
        return " ".join(parts)

    def _tokenize(self, text: str) -> list[str]:
        """Tokenize text into terms.

        Args:
            text: Text to tokenize

        Returns:
            List of tokens
        """
        # Convert to lowercase
        text = text.lower()

        # Remove special characters
        text = re.sub(r"[^a-z0-9\s]", " ", text)

        # Tokenize
        tokens = text.split()

        # Remove stop words (basic list)
        stop_words = {
            "a", "an", "and", "are", "as", "at", "be", "by", "for", "from",
            "has", "he", "in", "is", "it", "its", "of", "on", "that", "the",
            "to", "was", "were", "will", "with",
        }
        tokens = [t for t in tokens if t not in stop_words and len(t) > 2]

        return tokens

    def _build_bm25_index(self, documents: list[BM25Document]) -> None:
        """Build BM25 index from documents.

        Args:
            documents: List of BM25Document objects
        """
        self.total_docs = len(documents)

        # Calculate document lengths
        self.doc_lengths = {doc.doc_id: len(doc.tokens) for doc in documents}
        self.avg_doc_length = sum(self.doc_lengths.values()) / self.total_docs if self.total_docs > 0 else 0

        # Build inverted index
        inverted_index = defaultdict(list)
        for doc in documents:
            term_freqs = Counter(doc.tokens)
            for term, freq in term_freqs.items():
                inverted_index[term].append((doc.doc_id, freq))

        # Calculate IDF for each term
        idf = {}
        for term, postings in inverted_index.items():
            df = len(postings)  # Document frequency
            idf[term] = math.log((self.total_docs - df + 0.5) / (df + 0.5) + 1)

        # Build final index with BM25 scores
        self.index = {}
        for doc in documents:
            doc_index = {}
            term_freqs = Counter(doc.tokens)
            doc_length = self.doc_lengths[doc.doc_id]

            for term, freq in term_freqs.items():
                idf_score = idf.get(term, 0)
                numerator = freq * (self.k1 + 1)
                denominator = freq + self.k1 * (1 - self.b + self.b * (doc_length / self.avg_doc_length))
                bm25_score = idf_score * (numerator / denominator)
                doc_index[term] = bm25_score

            self.index[doc.doc_id] = doc_index

    async def search(
        self,
        query: str,
        organization_id: UUID,
        job_description_id: Optional[UUID] = None,
        limit: int = 10,
    ) -> list[Any]:
        """Search using BM25.

        Args:
            query: Search query
            organization_id: Organization ID
            job_description_id: Optional job description ID
            limit: Number of results

        Returns:
            List of search results with scores
        """
        # Ensure index is built
        if not self.index:
            await self.build_index(organization_id)

        # Tokenize query
        query_tokens = self._tokenize(query)

        # Calculate scores for each document
        scores = {}
        for doc_id, doc_index in self.index.items():
            score = 0.0
            for token in query_tokens:
                score += doc_index.get(token, 0)
            if score > 0:
                scores[doc_id] = score

        # Sort by score
        sorted_results = sorted(scores.items(), key=lambda x: x[1], reverse=True)

        # Return results
        results = []
        for doc_id, score in sorted_results[:limit]:
            results.append(
                {
                    "id": doc_id,
                    "score": score,
                    "metadata": {"search_method": "bm25"},
                }
            )

        return results

    def get_index_stats(self) -> dict[str, Any]:
        """Get index statistics.

        Returns:
            Dictionary with index statistics
        """
        return {
            "total_documents": self.total_docs,
            "average_document_length": self.avg_doc_length,
            "k1": self.k1,
            "b": self.b,
        }
