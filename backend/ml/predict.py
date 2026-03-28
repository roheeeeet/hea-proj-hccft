"""
ml/predict.py
Loads the trained model and produces 72-hour (3-day) admission forecasts.
Falls back to rule-based estimates if the model file hasn't been trained yet.
"""
import os, pickle
from datetime import date, timedelta

MODEL_PATH = os.path.join(os.path.dirname(__file__), 'hea_model.pkl')

# Indian public holidays (MM-DD format) for surge detection
INDIAN_HOLIDAYS = {
    "01-01", "01-26", "03-25", "04-14", "05-01",
    "08-15", "10-02", "10-12", "10-13", "11-01",
    "11-02", "12-25",
}

DAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def _is_holiday(d: date) -> int:
    return 1 if d.strftime("%m-%d") in INDIAN_HOLIDAYS else 0


def _rule_based(d: date):
    """Simple heuristic fallback when model isn't trained yet."""
    base = 42
    if d.weekday() >= 5:
        base = 30          # weekend dip
    if _is_holiday(d):
        base += 12         # holiday surge
    return {
        "admissions":          base,
        "icu_admissions":      max(4, round(base * 0.17)),
        "emergency_admissions": max(8, round(base * 0.40)),
    }


def predict_next_72h():
    today = date.today()
    results = []

    # Try to load trained model
    models = None
    if os.path.exists(MODEL_PATH):
        try:
            with open(MODEL_PATH, 'rb') as f:
                models = pickle.load(f)
        except Exception:
            models = None

    for offset in range(3):
        d = today + timedelta(days=offset)
        is_holiday = _is_holiday(d)

        if models:
            features = [[d.weekday(), d.month, is_holiday]]
            adm   = max(0, round(models['admissions'].predict(features)[0]))
            icu   = max(0, round(models['icu_admissions'].predict(features)[0]))
            emerg = max(0, round(models['emergency_admissions'].predict(features)[0]))
        else:
            rb = _rule_based(d)
            adm, icu, emerg = rb['admissions'], rb['icu_admissions'], rb['emergency_admissions']

        results.append({
            "day":                    DAY_NAMES[d.weekday()],
            "date":                   d.isoformat(),
            "predicted_admissions":   adm,
            "predicted_icu":          icu,
            "predicted_emergency":    emerg,
            "is_holiday":             bool(is_holiday),
            "surge_alert":            adm > 50 or icu > 10,
            "model_used":             "trained_rf" if models else "rule_based_fallback",
        })

    return results
