"""
Root Cause Analysis Engine
Uses K-Means clustering and frequency analysis to detect systemic issues.
"""

import os
import sys
import pandas as pd
import numpy as np
from collections import Counter, defaultdict
from datetime import datetime, timedelta

from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import silhouette_score

sys.path.insert(0, os.path.dirname(__file__))
from preprocessing import clean_text

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_PATH = os.path.join(BASE_DIR, 'data', 'complaints.csv')


def _load_complaints():
    """Load complaints data."""
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(f"Complaints data not found at {DATA_PATH}")
    df = pd.read_csv(DATA_PATH)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df


def cluster_complaints(n_clusters: int = 6) -> dict:
    """
    Cluster complaints using TF-IDF + K-Means.
    
    Returns cluster info with representative complaints.
    """
    df = _load_complaints()
    df['cleaned'] = df['description'].apply(clean_text)
    
    # Vectorize
    vectorizer = TfidfVectorizer(max_features=500, ngram_range=(1, 2))
    X = vectorizer.fit_transform(df['cleaned'])
    
    # Determine optimal clusters (bounded)
    actual_clusters = min(n_clusters, len(df) - 1)
    
    kmeans = KMeans(n_clusters=actual_clusters, random_state=42, n_init=10)
    df['cluster'] = kmeans.fit_predict(X)
    
    # Calculate silhouette score
    if actual_clusters > 1 and len(df) > actual_clusters:
        sil_score = silhouette_score(X, df['cluster'])
    else:
        sil_score = 0.0
    
    # Analyze each cluster
    clusters = []
    feature_names = vectorizer.get_feature_names_out()
    
    for c in range(actual_clusters):
        cluster_data = df[df['cluster'] == c]
        
        # Get top terms for this cluster
        center = kmeans.cluster_centers_[c]
        top_indices = center.argsort()[-5:][::-1]
        top_terms = [feature_names[i] for i in top_indices]
        
        # Most common category and location
        top_category = cluster_data['category'].mode().iloc[0] if len(cluster_data) > 0 else 'Unknown'
        top_location = cluster_data['location'].mode().iloc[0] if len(cluster_data) > 0 else 'Unknown'
        
        clusters.append({
            'cluster_id': int(c),
            'size': len(cluster_data),
            'top_terms': top_terms,
            'primary_category': top_category,
            'primary_location': top_location,
            'sample_complaints': cluster_data['description'].head(3).tolist(),
            'priority_distribution': cluster_data['priority'].value_counts().to_dict()
        })
    
    return {
        'n_clusters': actual_clusters,
        'silhouette_score': round(float(sil_score), 4),
        'clusters': clusters,
        'total_complaints': len(df)
    }


def detect_repeated_issue_patterns(window_days: int = 14, min_count: int = 3) -> list:
    """
    Detect locations or categories with repeated issues within a time window.
    
    Args:
        window_days: Time window to look for patterns
        min_count: Minimum complaint count to flag as pattern
    
    Returns:
        List of detected patterns with details
    """
    df = _load_complaints()
    
    patterns = []
    
    # Group by location + category and detect repeats
    for (location, category), group in df.groupby(['location', 'category']):
        group = group.sort_values('timestamp')
        
        # Sliding window analysis
        if len(group) < min_count:
            continue
        
        for i in range(len(group)):
            window_start = group.iloc[i]['timestamp']
            window_end = window_start + timedelta(days=window_days)
            
            window_complaints = group[
                (group['timestamp'] >= window_start) &
                (group['timestamp'] <= window_end)
            ]
            
            if len(window_complaints) >= min_count:
                patterns.append({
                    'location': location,
                    'category': category,
                    'complaint_count': len(window_complaints),
                    'window_start': window_start.strftime('%Y-%m-%d'),
                    'window_end': window_end.strftime('%Y-%m-%d'),
                    'complaints': window_complaints['description'].tolist(),
                    'severity': 'Critical' if len(window_complaints) >= 5 else 'High'
                })
                break  # Avoid duplicate patterns for same location+category
    
    patterns.sort(key=lambda x: x['complaint_count'], reverse=True)
    return patterns


def identify_root_cause() -> list:
    """
    Combines clustering and pattern detection to identify systemic root causes.
    
    Returns:
        List of root cause analyses with recommendations.
    """
    cluster_result = cluster_complaints()
    patterns = detect_repeated_issue_patterns()
    
    root_causes = []
    
    # Analyze patterns for root causes
    for pattern in patterns:
        category = pattern['category']
        location = pattern['location']
        count = pattern['complaint_count']
        
        # Generate recommendation based on category
        recommendations = _generate_recommendations(category, count, location)
        
        root_causes.append({
            'issue': f"Repeated {category} issues at {location}",
            'location': location,
            'category': category,
            'evidence': f"{count} complaints within {14} days",
            'severity': pattern['severity'],
            'root_cause_hypothesis': _infer_root_cause(category, count),
            'recommendations': recommendations
        })
    
    # Add cluster-based insights
    for cluster in cluster_result['clusters']:
        if cluster['size'] >= 10:  # Significant cluster
            root_causes.append({
                'issue': f"High volume of {cluster['primary_category']} complaints",
                'location': cluster['primary_location'],
                'category': cluster['primary_category'],
                'evidence': f"Cluster of {cluster['size']} similar complaints",
                'severity': 'High' if cluster['size'] >= 20 else 'Medium',
                'root_cause_hypothesis': _infer_root_cause(
                    cluster['primary_category'], cluster['size']
                ),
                'recommendations': _generate_recommendations(
                    cluster['primary_category'], cluster['size'],
                    cluster['primary_location']
                )
            })
    
    # Deduplicate by location + category
    seen = set()
    unique_causes = []
    for rc in root_causes:
        key = (rc['location'], rc['category'])
        if key not in seen:
            seen.add(key)
            unique_causes.append(rc)
    
    return unique_causes


def _infer_root_cause(category: str, count: int) -> str:
    """Infer a root cause hypothesis based on category and frequency."""
    causes = {
        'Plumbing': 'Main pipeline deterioration or joint failure',
        'Electrical': 'Transformer overload or aging wiring infrastructure',
        'Elevator': 'Motor wear or control panel malfunction requiring overhaul',
        'Security': 'Inadequate security staffing or equipment failure',
        'Cleanliness': 'Housekeeping schedule gaps or staff shortage',
        'Carpentry': 'Poor quality materials or humidity damage',
    }
    base = causes.get(category, 'Recurring infrastructure issue')
    if count >= 5:
        return f"{base} — systemic issue requiring immediate intervention"
    return base


def _generate_recommendations(category: str, count: int, location: str) -> list:
    """Generate actionable recommendations."""
    recs = {
        'Plumbing': [
            f'Inspect main pipeline at {location}',
            'Schedule comprehensive plumbing audit',
            'Consider pipeline replacement for aging sections'
        ],
        'Electrical': [
            f'Inspect transformers and wiring at {location}',
            'Schedule electrical safety audit',
            'Evaluate vendor performance for electrical maintenance'
        ],
        'Elevator': [
            f'Schedule full elevator inspection at {location}',
            'Review elevator maintenance contract',
            'Consider motor/control panel replacement'
        ],
        'Security': [
            f'Review security deployment at {location}',
            'Audit CCTV camera coverage',
            'Evaluate security vendor contract'
        ],
        'Cleanliness': [
            f'Review housekeeping schedule for {location}',
            'Increase cleaning frequency',
            'Add additional housekeeping staff'
        ],
        'Carpentry': [
            f'Inspect fixtures at {location}',
            'Use moisture-resistant materials for replacements',
            'Schedule preventive carpentry maintenance'
        ],
    }
    return recs.get(category, [f'Investigate recurring issues at {location}'])


if __name__ == "__main__":
    print("--- Complaint Clustering ---")
    clusters = cluster_complaints()
    print(f"Silhouette Score: {clusters['silhouette_score']}")
    for c in clusters['clusters']:
        print(f"  Cluster {c['cluster_id']}: {c['size']} complaints, "
              f"Category={c['primary_category']}, Location={c['primary_location']}")
        print(f"    Top terms: {c['top_terms']}")
    
    print("\n--- Repeated Issue Patterns ---")
    patterns = detect_repeated_issue_patterns()
    for p in patterns:
        print(f"  {p['location']} - {p['category']}: {p['complaint_count']} complaints "
              f"[{p['severity']}]")
    
    print("\n--- Root Cause Analysis ---")
    causes = identify_root_cause()
    for rc in causes:
        print(f"  Issue: {rc['issue']}")
        print(f"  Root Cause: {rc['root_cause_hypothesis']}")
        print(f"  Recommendations: {rc['recommendations']}")
        print()
