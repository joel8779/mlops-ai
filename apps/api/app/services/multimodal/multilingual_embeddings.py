"""Multilingual Embedding Service - Generate embeddings for multiple languages."""

from typing import Optional

from sentence_transformers import SentenceTransformer


class MultilingualEmbeddingService:
    """Service for generating multilingual text embeddings."""

    def __init__(
        self,
        model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
    ) -> None:
        """Initialize multilingual embedding service.

        Args:
            model_name: Name of the multilingual model
        """
        self.model_name = model_name
        self.model: Optional[SentenceTransformer] = None
        self._load_model()

    def _load_model(self) -> None:
        """Load the embedding model."""
        try:
            self.model = SentenceTransformer(self.model_name)
        except Exception as e:
            raise RuntimeError(f"Failed to load multilingual embedding model: {e}")

    async def embed(self, text: str) -> list[float]:
        """Generate embedding for text.

        Args:
            text: Text to embed

        Returns:
            Embedding vector as list of floats
        """
        if not self.model:
            raise RuntimeError("Model not loaded")

        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding.tolist()

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for multiple texts.

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors
        """
        if not self.model:
            raise RuntimeError("Model not loaded")

        embeddings = self.model.encode(texts, convert_to_numpy=True)
        return [emb.tolist() for emb in embeddings]

    def get_embedding_dimension(self) -> int:
        """Get the dimension of embeddings.

        Returns:
            Embedding dimension
        """
        if not self.model:
            raise RuntimeError("Model not loaded")
        return self.model.get_sentence_embedding_dimension()

    def get_supported_languages(self) -> list[str]:
        """Get list of supported languages.

        Returns:
            List of language codes
        """
        # paraphrase-multilingual-MiniLM-L12-v2 supports 50+ languages
        return [
            "ar", "bg", "ca", "cs", "da", "de", "el", "en", "es", "et", "fi", "fr", "ga",
            "gl", "gu", "he", "hi", "hr", "hu", "id", "it", "ja", "ka", "ko", "lt", "lv",
            "mk", "ms", "nl", "no", "pl", "pt", "ro", "ru", "sk", "sl", "sq", "sr", "sv",
            "th", "tr", "uk", "vi", "zh",
        ]
