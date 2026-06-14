import joblib
import pandas as pd
import os

MODEL_DIR = "static/models/"
 
DISEASE_FEATURES = {
    "diabetes": [
        'age', 'gender', 'bmi', 'sugar_intake', 'exercise_minutes_per_day', 
        'fiber_intake', 'sleep_hours', 'stress_level', 'family_history_diabetes'
    ],
    "hypertension": [
        "age","gender","bmi",
        "stress_level","exercise_minutes_per_day",
        "sleep_hours","smoking_status"
    ], 
    "heart_disease": [
        "age","gender",
        "exercise_minutes_per_day","sitting_hours_per_day",
        "smoking_status","alcohol_consumption","stress_level","family_history_heart_disease"
    ],
    "obesity": [
        "age","gender","bmi",
        "fruit_intake","vegetable_intake","fiber_intake",
        "fast_food_intake","exercise_minutes_per_day",
        "sitting_hours_per_day","sleep_hours"
    ]
}
def needs_advice(level):
    return level in ["Moderate", "High"]
def risk_level(prob):
    if prob < 0.30:
        return "Low"
    elif prob < 0.60:
        return "Moderate"
    else:
        return "High"

def predict_diseases(features):
    results = {}
    import joblib

    model = joblib.load("static/models/heart_disease_lgbm.pkl")

    print("Number of features:", model.n_features_in_)
    print("Feature names:", model.feature_name_)

    for disease, cols in DISEASE_FEATURES.items():
        model = joblib.load(os.path.join(MODEL_DIR, f"{disease}_lgbm.pkl"))
        X = pd.DataFrame([{c: features[c] for c in cols}])
        prob = model.predict_proba(X)[0][1]

        results[f"{disease}_risk"] = {
            "probability": round(prob * 100, 1),
            "level": risk_level(prob)
        }

    return results
