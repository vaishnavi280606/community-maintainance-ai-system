"""
Sentiment Analysis Module
Analyzes resident feedback / complaint text sentiment using VADER (NLTK).
"""

import os
import sys
import nltk

# Download VADER lexicon if needed
try:
    nltk.data.find('sentiment/vader_lexicon.zip')
except LookupError:
    nltk.download('vader_lexicon', quiet=True)

from nltk.sentiment.vader import SentimentIntensityAnalyzer

sys.path.insert(0, os.path.dirname(__file__))
from preprocessing import clean_text

_analyzer = None


def _get_analyzer():
    global _analyzer
    if _analyzer is None:
        _analyzer = SentimentIntensityAnalyzer()
    return _analyzer


def analyze_sentiment(text: str) -> dict:
    """
    Analyze sentiment of a given text.
    
    Returns:
        dict with 'label' (Positive/Negative/Neutral),
        'compound', 'pos', 'neg', 'neu' scores
    """
    if not isinstance(text, str) or not text.strip():
        return {
            'label': 'Neutral',
            'compound': 0.0,
            'pos': 0.0,
            'neg': 0.0,
            'neu': 1.0
        }
    
    analyzer = _get_analyzer()
    scores = analyzer.polarity_scores(text)
    
    compound = scores['compound']
    if compound >= 0.05:
        label = 'Positive'
    elif compound <= -0.05:
        label = 'Negative'
    else:
        label = 'Neutral'
    
    return {
        'label': label,
        'compound': round(compound, 4),
        'pos': round(scores['pos'], 4),
        'neg': round(scores['neg'], 4),
        'neu': round(scores['neu'], 4)
    }


def get_sentiment_score(text: str) -> float:
    """
    Returns a float sentiment score between -1 (very negative) and 1 (very positive).
    """
    result = analyze_sentiment(text)
    return result['compound']


def analyze_batch_sentiment(texts: list) -> list:
    """Analyze sentiment for a batch of texts."""
    return [analyze_sentiment(t) for t in texts]


if __name__ == "__main__":
    samples = [
        "Quick resolution, thanks! Very happy with the service.",
        "Terrible service. Staff was rude and took 3 days to come.",
        "Okay work. Took some time but fixed.",
        "Still not working. Waste of time.",
        "Excellent work. Issue fixed permanently.",
    ]
    
    print("--- Sentiment Analysis Test ---")
    for text in samples:
        result = analyze_sentiment(text)
        print(f"Text: '{text}'")
        print(f"  Sentiment: {result['label']} (compound={result['compound']})")
        print()
