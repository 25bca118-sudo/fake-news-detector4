import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / 'truthlens.db'
MODELS_DIR = BASE_DIR / 'data' / 'models'
UPLOAD_DIR = BASE_DIR / 'static' / 'uploads'
REPORTS_DIR = BASE_DIR / 'static' / 'reports'
DATA_DIR = BASE_DIR / 'data'

# Ensure runtime directories exist
MODELS_DIR.mkdir(parents=True, exist_ok=True)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

# Application Security
# Set TRUTHLENS_SECRET_KEY in the hosting provider environment.
SECRET_KEY = os.environ.get('TRUTHLENS_SECRET_KEY')
if not SECRET_KEY:
    # Local development fallback only; production deployments should set the env var.
    SECRET_KEY = 'dev-only-change-this-secret-key'

SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_SECURE = os.environ.get('COOKIE_SECURE', 'false').lower() == 'true'
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max upload

# Model & Analysis Weights for Compound Credibility Score (0-100)
WEIGHTS = {
    'ml_detector': 0.35,
    'deep_learning': 0.25,
    'source_credibility': 0.20,
    'fact_verification': 0.15,
    'clickbait_penalty': 0.05
}

# Credibility Thresholds
THRESHOLDS = {
    'likely_genuine': 70.0,
    'inconclusive': 45.0,
    'potentially_fake': 0.0
}
