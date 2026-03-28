"""
ml/train_model.py
Trains a Random Forest model on sample historical data and saves it as hea_model.pkl.
Run once before starting the server: python ml/train_model.py
"""
import os, sys
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
import pickle

DATA_PATH  = os.path.join(os.path.dirname(__file__), 'sample_data.csv')
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'hea_model.pkl')

TARGETS = ['admissions', 'icu_admissions', 'emergency_admissions']
FEATURES = ['day_of_week', 'month', 'is_holiday']


def train():
    df = pd.read_csv(DATA_PATH)
    models = {}

    for target in TARGETS:
        X = df[FEATURES]
        y = df[target]
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        preds = model.predict(X_test)
        mae = mean_absolute_error(y_test, preds)
        print(f"Model for '{target}' — MAE: {mae:.1f}")
        models[target] = model

    with open(MODEL_PATH, 'wb') as f:
        pickle.dump(models, f)

    print(f"Models saved to {MODEL_PATH}")


if __name__ == '__main__':
    train()
