"""
models/forecast.py
Thin wrapper so app.py can import from models/ consistently.
The actual logic lives in ml/predict.py.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from ml.predict import predict_next_72h

__all__ = ['predict_next_72h']
