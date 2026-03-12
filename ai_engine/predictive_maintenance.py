"""
Predictive Maintenance Engine
Uses historical maintenance logs to predict next failure window.
"""

import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from collections import defaultdict
import pickle

from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_PATH = os.path.join(BASE_DIR, 'data', 'maintenance_logs.csv')
MODEL_DIR = os.path.join(BASE_DIR, 'models')


def _load_maintenance_data():
    """Load and preprocess maintenance logs."""
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(f"Maintenance logs not found at {DATA_PATH}")
    
    df = pd.read_csv(DATA_PATH)
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values(['asset_name', 'date'])
    return df


def _compute_failure_intervals(df):
    """
    Compute the interval (in days) between consecutive maintenance events
    per asset to create training data for prediction.
    """
    records = []
    for asset, group in df.groupby('asset_name'):
        group = group.sort_values('date').reset_index(drop=True)
        for i in range(1, len(group)):
            interval = (group.loc[i, 'date'] - group.loc[i-1, 'date']).days
            prev_cost = group.loc[i-1, 'cost']
            prev_downtime = group.loc[i-1, 'downtime_hours']
            mtype = 1 if group.loc[i-1, 'maintenance_type'] == 'Corrective' else 0
            event_count = i  # cumulative event count
            
            records.append({
                'asset_name': asset,
                'interval_days': interval,
                'prev_cost': prev_cost,
                'prev_downtime': prev_downtime,
                'prev_was_corrective': mtype,
                'cumulative_events': event_count,
            })
    
    return pd.DataFrame(records)


def train_failure_prediction_model():
    """Train a model to predict the interval until next maintenance event."""
    df = _load_maintenance_data()
    intervals_df = _compute_failure_intervals(df)
    
    if len(intervals_df) < 10:
        print("Not enough data to train prediction model.")
        return None
    
    features = ['prev_cost', 'prev_downtime', 'prev_was_corrective', 'cumulative_events']
    X = intervals_df[features]
    y = intervals_df['interval_days']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model = GradientBoostingRegressor(
        n_estimators=100,
        max_depth=4,
        learning_rate=0.1,
        random_state=42
    )
    model.fit(X_train, y_train)
    
    y_pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    
    print(f"--- Predictive Maintenance Model ---")
    print(f"MAE: {mae:.2f} days")
    print(f"RMSE: {rmse:.2f} days")
    
    # Save model
    os.makedirs(MODEL_DIR, exist_ok=True)
    model_path = os.path.join(MODEL_DIR, 'predictive_maintenance.pkl')
    with open(model_path, 'wb') as f:
        pickle.dump(model, f)
    print(f"Model saved to {model_path}")
    
    return model


def predict_next_failure(asset_name: str = None) -> list:
    """
    Predict next failure/maintenance window for assets.
    
    Returns a list of dicts with asset predictions.
    """
    df = _load_maintenance_data()
    
    model_path = os.path.join(MODEL_DIR, 'predictive_maintenance.pkl')
    if os.path.exists(model_path):
        with open(model_path, 'rb') as f:
            model = pickle.load(f)
    else:
        model = train_failure_prediction_model()
        if model is None:
            return []
    
    predictions = []
    assets = [asset_name] if asset_name else df['asset_name'].unique()
    
    for asset in assets:
        asset_data = df[df['asset_name'] == asset].sort_values('date')
        if len(asset_data) < 2:
            continue
        
        last_event = asset_data.iloc[-1]
        last_date = last_event['date']
        
        features = pd.DataFrame([{
            'prev_cost': last_event['cost'],
            'prev_downtime': last_event['downtime_hours'],
            'prev_was_corrective': 1 if last_event['maintenance_type'] == 'Corrective' else 0,
            'cumulative_events': len(asset_data),
        }])
        
        predicted_interval = max(int(model.predict(features)[0]), 7)
        predicted_date = last_date + timedelta(days=predicted_interval)
        
        # Suggest preventive maintenance 2 weeks before predicted failure
        preventive_date = predicted_date - timedelta(days=14)
        
        predictions.append({
            'asset_name': asset,
            'last_maintenance': last_date.strftime('%Y-%m-%d'),
            'predicted_next_failure': predicted_date.strftime('%Y-%m-%d'),
            'suggested_preventive_date': preventive_date.strftime('%Y-%m-%d'),
            'predicted_interval_days': predicted_interval,
            'total_events': len(asset_data),
            'risk_level': 'High' if predicted_interval < 30 else ('Medium' if predicted_interval < 60 else 'Low')
        })
    
    predictions.sort(key=lambda x: x['predicted_next_failure'])
    return predictions


def recommend_preventive_maintenance() -> list:
    """Get maintenance recommendations sorted by urgency."""
    predictions = predict_next_failure()
    today = datetime.now()
    
    recommendations = []
    for pred in predictions:
        pred_date = datetime.strptime(pred['predicted_next_failure'], '%Y-%m-%d')
        days_until = (pred_date - today).days
        
        if days_until < 0:
            urgency = 'Overdue'
        elif days_until < 14:
            urgency = 'Urgent'
        elif days_until < 30:
            urgency = 'Soon'
        else:
            urgency = 'Scheduled'
        
        recommendations.append({
            **pred,
            'days_until_failure': days_until,
            'urgency': urgency
        })
    
    # Sort: Overdue first, then by days
    urgency_order = {'Overdue': 0, 'Urgent': 1, 'Soon': 2, 'Scheduled': 3}
    recommendations.sort(key=lambda x: (urgency_order.get(x['urgency'], 4), x['days_until_failure']))
    
    return recommendations


if __name__ == "__main__":
    print("Training predictive maintenance model...")
    train_failure_prediction_model()
    
    print("\n--- Predictions ---")
    preds = predict_next_failure()
    for p in preds:
        print(f"  {p['asset_name']}: next failure ~{p['predicted_next_failure']}, "
              f"preventive by {p['suggested_preventive_date']} [{p['risk_level']}]")
    
    print("\n--- Recommendations ---")
    recs = recommend_preventive_maintenance()
    for r in recs:
        print(f"  [{r['urgency']}] {r['asset_name']}: "
              f"{r['days_until_failure']} days until predicted failure")
