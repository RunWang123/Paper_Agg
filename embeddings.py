"""
Embedding service for semantic search using sentence-transformers.
Uses pgvector for storing and querying embeddings in PostgreSQL.
"""

from sentence_transformers import SentenceTransformer
from typing import List, Optional
import numpy as np

# Global model instance (lazy loaded)
_model = None

# Embedding model configuration
# BAAI/bge-base-en-v1.5: Best quality-to-size ratio for CPU deployment
# MTEB Score: 63.5, Model size: ~440MB, 768 dimensions
MODEL_NAME = "BAAI/bge-base-en-v1.5"
EMBEDDING_DIMENSION = 768


def get_model() -> SentenceTransformer:
    """Lazy load the embedding model."""
    global _model
    if _model is None:
        print(f"Loading embedding model: {MODEL_NAME}...")
        _model = SentenceTransformer(MODEL_NAME)
        print("Model loaded successfully!")
    return _model


def generate_embedding(text: str) -> List[float]:
    """Generate embedding for a single text."""
    model = get_model()
    embedding = model.encode(text, normalize_embeddings=True)
    return embedding.tolist()


def generate_embeddings_batch(texts: List[str], batch_size: int = 32) -> List[List[float]]:
    """Generate embeddings for multiple texts efficiently."""
    model = get_model()
    embeddings = model.encode(
        texts, 
        batch_size=batch_size,
        normalize_embeddings=True,
        show_progress_bar=True
    )
    return [emb.tolist() for emb in embeddings]


def create_paper_embedding_text(title: str, authors: str = "", abstract: str = "") -> str:
    """
    Create a combined text for embedding from paper metadata.
    Uses title, authors, and abstract for richer semantic representation.
    """
    parts = [title]
    
    if authors:
        parts.append(f"Authors: {authors}")
    
    if abstract:
        parts.append(abstract)
    
    return " ".join(parts)


def cosine_similarity(embedding1: List[float], embedding2: List[float]) -> float:
    """Calculate cosine similarity between two embeddings."""
    a = np.array(embedding1)
    b = np.array(embedding2)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))
