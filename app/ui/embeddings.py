from loguru import logger

_model = None


def _get_embedding_model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer

        logger.info("Loading embedding model...")
        _model = SentenceTransformer("all-MiniLM-L6-v2")
        logger.info("Embedding model loaded.")
    return _model


def embed_text(text: str) -> list[float]:
    """Embed text into a 384-dimensional vector using sentence-transformers."""
    if not text or not text.strip():
        return [0.0] * 384
    model = _get_embedding_model()
    return model.encode(text, show_progress_bar=False).tolist()
