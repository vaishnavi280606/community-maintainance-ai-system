import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import pickle
import os

import sys
sys.path.insert(0, os.path.dirname(__file__))
from preprocessing import clean_text

MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models')
DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'complaints.csv')

def train_classifier():
    """Trains the TF-IDF and Logistic Regression model."""
    print("Loading data...")
    if not os.path.exists(DATA_PATH):
        print(f"Error: Dataset not found at {DATA_PATH}")
        return

    df = pd.read_csv(DATA_PATH)
    
    # Preprocess descriptions
    print("Preprocessing text...")
    df['cleaned_desc'] = df['description'].apply(clean_text)
    
    X = df['cleaned_desc']
    y = df['category']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # 1. TF-IDF Vectorization
    print("Vectorizing...")
    vectorizer = TfidfVectorizer(max_features=1000, ngram_range=(1, 2))
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)
    
    # 2. Train Logistic Regression
    print("Training model...")
    model = LogisticRegression(random_state=42, max_iter=200)
    model.fit(X_train_vec, y_train)
    
    # 3. Evaluate
    y_pred = model.predict(X_test_vec)
    print("\n--- Model Evaluation ---")
    print(f"Accuracy: {accuracy_score(y_test, y_pred):.4f}")
    print(classification_report(y_test, y_pred))
    
    # 4. Save Models
    os.makedirs(MODEL_DIR, exist_ok=True)
    
    vec_path = os.path.join(MODEL_DIR, 'tfidf_vectorizer.pkl')
    model_path = os.path.join(MODEL_DIR, 'complaint_classifier.pkl')
    
    with open(vec_path, 'wb') as f:
        pickle.dump(vectorizer, f)
        
    with open(model_path, 'wb') as f:
        pickle.dump(model, f)
        
    print(f"Models saved to:\n- {vec_path}\n- {model_path}")

def predict_complaint_category(text: str) -> str:
    """Predicts a category for a new complaint text."""
    vec_path = os.path.join(MODEL_DIR, 'tfidf_vectorizer.pkl')
    model_path = os.path.join(MODEL_DIR, 'complaint_classifier.pkl')
    
    if not os.path.exists(vec_path) or not os.path.exists(model_path):
        raise FileNotFoundError("Models not found. Train first using train_classifier()")
        
    with open(vec_path, 'rb') as f:
        vectorizer = pickle.load(f)
        
    with open(model_path, 'rb') as f:
        model = pickle.load(f)
        
    cleaned = clean_text(text)
    vec = vectorizer.transform([cleaned])
    
    prediction = model.predict(vec)[0]
    return prediction

if __name__ == "__main__":
    train_classifier()
    
    # Test Prediction
    test_text = "The lift is completely stuck on the 3rd floor please send help"
    predicted_cat = predict_complaint_category(test_text)
    print(f"\nTest Text: '{test_text}'")
    print(f"Predicted Category: {predicted_cat}")
