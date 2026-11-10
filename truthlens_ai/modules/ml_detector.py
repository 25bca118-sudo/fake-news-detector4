import json
import joblib
import numpy as np
from pathlib import Path
from truthlens_ai.config import MODELS_DIR
from truthlens_ai.database.db_manager import execute_query

_MODELS_CACHE = {}

def get_loaded_models():
    """Loads and caches serialized ML models and TF-IDF vectorizer."""
    global _MODELS_CACHE
    if not _MODELS_CACHE:
        _MODELS_CACHE['vectorizer'] = joblib.load(MODELS_DIR / 'tfidf_vectorizer.pkl')
        _MODELS_CACHE['logistic'] = joblib.load(MODELS_DIR / 'logistic_model.pkl')
        _MODELS_CACHE['naive_bayes'] = joblib.load(MODELS_DIR / 'nb_model.pkl')
        _MODELS_CACHE['random_forest'] = joblib.load(MODELS_DIR / 'rf_model.pkl')
    return _MODELS_CACHE

def predict_ml(text: str) -> dict:
    """Runs input text through Logistic Regression, Naive Bayes, and Random Forest."""
    models = get_loaded_models()
    vectorizer = models['vectorizer']
    X = vectorizer.transform([text])
    
    # 1. Logistic Regression
    lr_prob = models['logistic'].predict_proba(X)[0] # [P(Fake), P(Real)]
    lr_fake_prob = float(lr_prob[0])
    lr_real_prob = float(lr_prob[1])
    lr_label = "Genuine" if lr_real_prob >= 0.5 else "Fake / Misleading"
    
    # 2. Naive Bayes
    nb_prob = models['naive_bayes'].predict_proba(X)[0]
    nb_fake_prob = float(nb_prob[0])
    nb_real_prob = float(nb_prob[1])
    nb_label = "Genuine" if nb_real_prob >= 0.5 else "Fake / Misleading"
    
    # 3. Random Forest
    rf_prob = models['random_forest'].predict_proba(X)[0]
    rf_fake_prob = float(rf_prob[0])
    rf_real_prob = float(rf_prob[1])
    rf_label = "Genuine" if rf_real_prob >= 0.5 else "Fake / Misleading"
    
    # Ensemble Probability (Weighted: 45% Logistic, 25% Naive Bayes, 30% Random Forest)
    ensemble_real_prob = (0.45 * lr_real_prob) + (0.25 * nb_real_prob) + (0.30 * rf_real_prob)
    ensemble_fake_prob = 1.0 - ensemble_real_prob
    
    if ensemble_real_prob >= 0.65:
        verdict = "Likely Genuine"
        confidence = ensemble_real_prob
    elif ensemble_real_prob <= 0.35:
        verdict = "Potentially Fake"
        confidence = ensemble_fake_prob
    else:
        verdict = "Inconclusive"
        confidence = max(ensemble_real_prob, ensemble_fake_prob)
        
    return {
        'verdict': verdict,
        'confidence_score': round(confidence * 100, 1),
        'real_probability': round(ensemble_real_prob * 100, 1),
        'fake_probability': round(ensemble_fake_prob * 100, 1),
        'models': {
            'logistic_regression': {
                'prediction': lr_label,
                'real_confidence': round(lr_real_prob * 100, 1),
                'fake_confidence': round(lr_fake_prob * 100, 1)
            },
            'naive_bayes': {
                'prediction': nb_label,
                'real_confidence': round(nb_real_prob * 100, 1),
                'fake_confidence': round(nb_fake_prob * 100, 1)
            },
            'random_forest': {
                'prediction': rf_label,
                'real_confidence': round(rf_real_prob * 100, 1),
                'fake_confidence': round(rf_fake_prob * 100, 1)
            }
        }
    }

def get_model_benchmarks() -> list[dict]:
    """Retrieves benchmark evaluation metrics from database."""
    benchmarks = execute_query("SELECT model_name, accuracy, precision_score, recall_score, f1_score, confusion_matrix FROM model_benchmarks")
    for b in benchmarks:
        if b.get('confusion_matrix'):
            try:
                b['confusion_matrix'] = json.loads(b['confusion_matrix'])
            except Exception:
                pass
    return benchmarks
