"""
Resident Satisfaction Index (RSI) Calculator

RSI = 0.3 * (resolution speed score)
    + 0.3 * (sentiment score)
    + 0.2 * (complaint frequency inverse)
    + 0.2 * (payment reliability)

Output: Score per block (0-100)
"""

import os
import sys
import pandas as pd
import numpy as np
from collections import defaultdict

sys.path.insert(0, os.path.dirname(__file__))
from sentiment_analysis import get_sentiment_score

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
COMPLAINTS_PATH = os.path.join(BASE_DIR, 'data', 'complaints.csv')
FEEDBACK_PATH = os.path.join(BASE_DIR, 'data', 'feedback.csv')


def _load_data():
    """Load complaints and feedback data."""
    complaints = pd.read_csv(COMPLAINTS_PATH)
    complaints['timestamp'] = pd.to_datetime(complaints['timestamp'])
    
    feedback = pd.read_csv(FEEDBACK_PATH)
    return complaints, feedback


def _calculate_resolution_speed_score(complaints: pd.DataFrame) -> dict:
    """
    Calculate resolution speed score per location.
    Based on the ratio of Resolved/Closed complaints vs total.
    Score 0-100.
    """
    scores = {}
    for location, group in complaints.groupby('location'):
        total = len(group)
        resolved = len(group[group['status'].isin(['Resolved', 'Closed'])])
        ratio = resolved / total if total > 0 else 0.5
        scores[location] = ratio * 100
    return scores


def _calculate_sentiment_score(feedback: pd.DataFrame, complaints: pd.DataFrame) -> dict:
    """
    Calculate average sentiment score per location.
    Map feedback to complaints via complaint_id, then group by location.
    Score normalized to 0-100.
    """
    # Merge feedback with complaints to get location
    merged = feedback.merge(
        complaints[['complaint_id', 'location']],
        on='complaint_id',
        how='left'
    )
    
    scores = {}
    for location, group in merged.groupby('location'):
        # Analyze sentiment of feedback comments
        sentiments = group['comment'].apply(
            lambda x: get_sentiment_score(str(x))
        )
        # VADER compound is -1 to 1, normalize to 0-100
        avg_sentiment = sentiments.mean()
        scores[location] = (avg_sentiment + 1) * 50  # -1->0, 0->50, 1->100
    
    return scores


def _calculate_complaint_frequency_inverse(complaints: pd.DataFrame) -> dict:
    """
    Lower complaint frequency = higher score.
    Score 0-100 (inverse of frequency relative to max).
    """
    counts = complaints.groupby('location').size()
    max_count = counts.max() if len(counts) > 0 else 1
    
    scores = {}
    for location, count in counts.items():
        # Inverse: higher count = lower score
        scores[location] = max(0, (1 - count / max_count) * 100)
    
    return scores


def _calculate_payment_reliability(complaints: pd.DataFrame) -> dict:
    """
    Simulated payment reliability score.
    In production, integrate with payment system.
    Uses complaint assignment ratio as proxy.
    """
    scores = {}
    for location, group in complaints.groupby('location'):
        # Use % of complaints with assigned staff as proxy
        assigned = group['assigned_staff'].notna().sum()
        total = len(group)
        ratio = assigned / total if total > 0 else 0.5
        scores[location] = ratio * 100
    
    return scores


def calculate_rsi() -> dict:
    """
    Calculate Resident Satisfaction Index for each location/block.
    
    Returns:
        dict with location -> RSI score (0-100) and breakdown
    """
    complaints, feedback = _load_data()
    
    # Get all locations
    locations = complaints['location'].unique().tolist()
    
    resolution_scores = _calculate_resolution_speed_score(complaints)
    sentiment_scores = _calculate_sentiment_score(feedback, complaints)
    frequency_scores = _calculate_complaint_frequency_inverse(complaints)
    payment_scores = _calculate_payment_reliability(complaints)
    
    rsi_results = {}
    for location in locations:
        r_score = resolution_scores.get(location, 50)
        s_score = sentiment_scores.get(location, 50)
        f_score = frequency_scores.get(location, 50)
        p_score = payment_scores.get(location, 50)
        
        rsi = (0.3 * r_score +
               0.3 * s_score +
               0.2 * f_score +
               0.2 * p_score)
        
        rsi_results[location] = {
            'rsi_score': round(rsi, 1),
            'resolution_speed': round(r_score, 1),
            'sentiment': round(s_score, 1),
            'complaint_frequency_inv': round(f_score, 1),
            'payment_reliability': round(p_score, 1),
            'health': 'Good' if rsi >= 70 else ('Fair' if rsi >= 50 else 'Poor')
        }
    
    return rsi_results


def generate_rsi_heatmap_data() -> list:
    """
    Generate data suitable for heatmap visualization.
    
    Returns:
        List of dicts with location, score, and color coding.
    """
    rsi_data = calculate_rsi()
    
    heatmap = []
    for location, data in rsi_data.items():
        score = data['rsi_score']
        if score >= 70:
            color = '#4caf50'  # Green
        elif score >= 50:
            color = '#ff9800'  # Orange
        else:
            color = '#f44336'  # Red
        
        heatmap.append({
            'location': location,
            'score': score,
            'color': color,
            'health': data['health'],
            'breakdown': {
                'resolution_speed': data['resolution_speed'],
                'sentiment': data['sentiment'],
                'complaint_frequency': data['complaint_frequency_inv'],
                'payment_reliability': data['payment_reliability']
            }
        })
    
    heatmap.sort(key=lambda x: x['score'], reverse=True)
    return heatmap


if __name__ == "__main__":
    print("--- Resident Satisfaction Index ---")
    rsi = calculate_rsi()
    for location, data in sorted(rsi.items(), key=lambda x: x[1]['rsi_score'], reverse=True):
        print(f"  {location}: {data['rsi_score']}/100 [{data['health']}]")
        print(f"    Resolution: {data['resolution_speed']}, Sentiment: {data['sentiment']}, "
              f"Frequency: {data['complaint_frequency_inv']}, Payment: {data['payment_reliability']}")
    
    print("\n--- Heatmap Data ---")
    heatmap = generate_rsi_heatmap_data()
    for h in heatmap:
        print(f"  {h['location']}: {h['score']} {h['color']} [{h['health']}]")
