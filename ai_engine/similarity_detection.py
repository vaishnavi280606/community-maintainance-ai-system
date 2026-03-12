"""
Complaint Similarity Detection Module
Uses Sentence-BERT embeddings + Cosine Similarity to detect duplicate complaints.
Threshold > 0.85 triggers merge suggestion.
"""

import os
import sys
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

sys.path.insert(0, os.path.dirname(__file__))

# Try to load sentence-transformers; fall back to TF-IDF if unavailable
try:
    from sentence_transformers import SentenceTransformer
    USE_SBERT = True
except ImportError:
    USE_SBERT = False

from preprocessing import clean_text

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_PATH = os.path.join(BASE_DIR, 'data', 'complaints.csv')
MODEL_DIR = os.path.join(BASE_DIR, 'models')

SIMILARITY_THRESHOLD = 0.85

# Cache the model in memory
_sbert_model = None


def _get_sbert_model():
    """Lazy-load the Sentence-BERT model."""
    global _sbert_model
    if _sbert_model is None:
        _sbert_model = SentenceTransformer('all-MiniLM-L6-v2')
    return _sbert_model


def generate_embedding(text: str) -> np.ndarray:
    """Generate a sentence embedding for the given text."""
    if USE_SBERT:
        model = _get_sbert_model()
        embedding = model.encode([text])
        return embedding[0]
    else:
        # Fallback: basic TF-IDF based embedding
        from sklearn.feature_extraction.text import TfidfVectorizer
        cleaned = clean_text(text)
        vectorizer = TfidfVectorizer(max_features=384)
        vec = vectorizer.fit_transform([cleaned])
        return vec.toarray()[0]


def generate_embeddings_batch(texts: list) -> np.ndarray:
    """Generate sentence embeddings for a batch of texts."""
    if USE_SBERT:
        model = _get_sbert_model()
        return model.encode(texts, show_progress_bar=False)
    else:
        from sklearn.feature_extraction.text import TfidfVectorizer
        cleaned = [clean_text(t) for t in texts]
        vectorizer = TfidfVectorizer(max_features=384)
        vecs = vectorizer.fit_transform(cleaned)
        return vecs.toarray()


def calculate_similarity(text1: str, text2: str) -> float:
    """Calculate cosine similarity between two texts."""
    emb1 = generate_embedding(text1).reshape(1, -1)
    emb2 = generate_embedding(text2).reshape(1, -1)
    similarity = cosine_similarity(emb1, emb2)[0][0]
    return float(similarity)


def detect_duplicate_complaint(new_complaint: str, existing_complaints: list,
                                threshold: float = SIMILARITY_THRESHOLD) -> dict:
    """
    Check if a new complaint is a duplicate of any existing complaints.
    
    Args:
        new_complaint: The text of the new complaint
        existing_complaints: List of dicts with 'complaint_id' and 'description'
        threshold: Similarity threshold (default 0.85)
    
    Returns:
        dict with 'is_duplicate', 'similar_complaint_id', 'similarity_score'
    """
    if not existing_complaints:
        return {
            'is_duplicate': False,
            'similar_complaint_id': None,
            'similarity_score': 0.0,
            'similar_complaints': []
        }
    
    existing_texts = [c['description'] for c in existing_complaints]
    existing_ids = [c['complaint_id'] for c in existing_complaints]
    
    # Generate embeddings
    new_emb = generate_embedding(new_complaint).reshape(1, -1)
    existing_embs = generate_embeddings_batch(existing_texts)
    
    # Calculate similarities
    similarities = cosine_similarity(new_emb, existing_embs)[0]
    
    # Find similar complaints above threshold
    similar_complaints = []
    for i, sim in enumerate(similarities):
        if sim >= threshold:
            similar_complaints.append({
                'complaint_id': existing_ids[i],
                'description': existing_texts[i],
                'similarity_score': round(float(sim), 4)
            })
    
    # Sort by similarity descending
    similar_complaints.sort(key=lambda x: x['similarity_score'], reverse=True)
    
    if similar_complaints:
        best_match = similar_complaints[0]
        return {
            'is_duplicate': True,
            'similar_complaint_id': best_match['complaint_id'],
            'similarity_score': best_match['similarity_score'],
            'similar_complaints': similar_complaints
        }
    else:
        return {
            'is_duplicate': False,
            'similar_complaint_id': None,
            'similarity_score': float(max(similarities)) if len(similarities) > 0 else 0.0,
            'similar_complaints': []
        }


if __name__ == "__main__":
    # Test with sample complaints
    test_complaints = [
        {'complaint_id': 'CMP001', 'description': 'No electricity in Block B'},
        {'complaint_id': 'CMP002', 'description': 'Water leakage in apartment bathroom'},
        {'complaint_id': 'CMP003', 'description': 'Lift stuck between floors'},
        {'complaint_id': 'CMP004', 'description': 'Garbage not collected today'},
    ]
    
    new = "Power cut in block B"
    result = detect_duplicate_complaint(new, test_complaints)
    print(f"\nNew complaint: '{new}'")
    print(f"Is duplicate: {result['is_duplicate']}")
    print(f"Most similar: {result['similar_complaint_id']}")
    print(f"Similarity: {result['similarity_score']}")
    
    new2 = "The elevator is not working and stuck"
    result2 = detect_duplicate_complaint(new2, test_complaints)
    print(f"\nNew complaint: '{new2}'")
    print(f"Is duplicate: {result2['is_duplicate']}")
    print(f"Most similar: {result2['similar_complaint_id']}")
    print(f"Similarity: {result2['similarity_score']}")
