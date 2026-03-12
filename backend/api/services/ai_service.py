"""
AI Service — integrates AI engine modules with the Django backend.
Handles complaint classification, duplicate detection, sentiment analysis.
"""

import os
import sys
import importlib
from django.conf import settings

# Ensure ai_engine is importable
ai_engine_dir = settings.AI_ENGINE_DIR
if ai_engine_dir not in sys.path:
    sys.path.insert(0, ai_engine_dir)

# Import AI engine modules (loaded from ai_engine directory via sys.path)
_preprocessing = importlib.import_module('preprocessing')
_complaint_classifier = importlib.import_module('complaint_classifier')
_sentiment_analysis = importlib.import_module('sentiment_analysis')
_similarity_detection = importlib.import_module('similarity_detection')
_root_cause_engine = importlib.import_module('root_cause_engine')
_predictive_maintenance = importlib.import_module('predictive_maintenance')
_rsi_calculation = importlib.import_module('rsi_calculation')

clean_text = _preprocessing.clean_text
predict_complaint_category = _complaint_classifier.predict_complaint_category
train_classifier = _complaint_classifier.train_classifier
analyze_sentiment = _sentiment_analysis.analyze_sentiment
get_sentiment_score = _sentiment_analysis.get_sentiment_score
detect_duplicate_complaint = _similarity_detection.detect_duplicate_complaint
identify_root_cause = _root_cause_engine.identify_root_cause
cluster_complaints = _root_cause_engine.cluster_complaints
predict_next_failure = _predictive_maintenance.predict_next_failure
recommend_preventive_maintenance = _predictive_maintenance.recommend_preventive_maintenance
calculate_rsi = _rsi_calculation.calculate_rsi
generate_rsi_heatmap_data = _rsi_calculation.generate_rsi_heatmap_data


# Priority keywords for AI-based priority scoring
SAFETY_KEYWORDS = ['fire', 'stuck', 'trapped', 'electrocution', 'shock', 'flood',
                   'gas leak', 'collapse', 'emergency', 'danger', 'smoke', 'sparking']
URGENCY_KEYWORDS = ['urgent', 'asap', 'immediately', 'critical', 'broken', 'not working',
                    'failure', 'stopped', 'dangerous']


def classify_complaint(text: str) -> dict:
    """
    Classify complaint text and determine category + priority.
    Returns category, priority, and explanation.
    """
    # Predict category
    try:
        category = predict_complaint_category(text)
    except FileNotFoundError:
        # Train models if not exist
        train_classifier()
        category = predict_complaint_category(text)
    
    # Determine priority based on keywords + sentiment
    sentiment = analyze_sentiment(text)
    priority = _determine_priority(text, sentiment)
    
    # Generate explanation
    explanation = _generate_explanation(text, category, priority, sentiment)
    
    return {
        'category': category,
        'priority': priority,
        'sentiment': sentiment,
        'explanation': explanation
    }


def _determine_priority(text: str, sentiment: dict) -> str:
    """Determine complaint priority based on text analysis."""
    text_lower = text.lower()
    score = 0
    
    # Safety keywords → high boost
    for kw in SAFETY_KEYWORDS:
        if kw in text_lower:
            score += 3
    
    # Urgency keywords → medium boost
    for kw in URGENCY_KEYWORDS:
        if kw in text_lower:
            score += 2
    
    # Negative sentiment → boost
    if sentiment['compound'] <= -0.5:
        score += 2
    elif sentiment['compound'] <= -0.2:
        score += 1
    
    # Determine priority
    if score >= 5:
        return 'Critical'
    elif score >= 3:
        return 'High'
    elif score >= 1:
        return 'Medium'
    else:
        return 'Low'


def _generate_explanation(text: str, category: str, priority: str, sentiment: dict) -> str:
    """Generate explainable AI reasoning."""
    reasons = []
    text_lower = text.lower()
    
    reasons.append(f"Category: {category} (AI classification via TF-IDF + Logistic Regression)")
    reasons.append(f"Priority: {priority}")
    
    # Check for safety keywords
    found_safety = [kw for kw in SAFETY_KEYWORDS if kw in text_lower]
    if found_safety:
        reasons.append(f"Safety keywords detected: {', '.join(found_safety)}")
    
    # Sentiment
    if sentiment['compound'] <= -0.2:
        reasons.append(f"Negative sentiment detected (score: {sentiment['compound']})")
    elif sentiment['compound'] >= 0.2:
        reasons.append(f"Positive sentiment (score: {sentiment['compound']})")
    
    return ' | '.join(reasons)


def check_duplicate(complaint_text: str, existing_complaints: list) -> dict:
    """Check if a complaint is a duplicate of existing ones."""
    return detect_duplicate_complaint(complaint_text, existing_complaints)


def get_root_cause_analysis() -> list:
    """Get root cause analysis results."""
    return identify_root_cause()


def get_complaint_clusters() -> dict:
    """Get complaint clustering results."""
    return cluster_complaints()


def get_maintenance_predictions() -> list:
    """Get predictive maintenance results."""
    return predict_next_failure()


def get_maintenance_recommendations() -> list:
    """Get maintenance recommendations."""
    return recommend_preventive_maintenance()


def get_rsi_scores() -> dict:
    """Get RSI scores for all locations."""
    return calculate_rsi()


def get_rsi_heatmap() -> list:
    """Get RSI heatmap data."""
    return generate_rsi_heatmap_data()
