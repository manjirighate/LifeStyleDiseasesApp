import pandas as pd
import numpy as np
import lightgbm as lgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, roc_auc_score, classification_report
import joblib
import os
# Load CSV file
df = pd.read_csv("lifestyle_health_dataset.csv")

print("Dataset shape:", df.shape)
print(df.head())
FEATURES = [
    "age", "gender", "bmi",
    "fruit_intake", "vegetable_intake", "fiber_intake",
    "sugar_intake", "fast_food_intake",
    "exercise_minutes_per_day",
    "sitting_hours_per_day",
    "sleep_hours",
    "stress_level",
    "smoking_status",
    "alcohol_consumption",
    "family_history_diabetes",
    "family_history_heart_disease"
]

TARGETS = [
    "diabetes",
    "hypertension",
    "heart_disease",
    "obesity"
]

X = df[FEATURES]
models = {}
metrics = {}

os.makedirs("models", exist_ok=True)

for target in TARGETS:
    print(f"\nTraining model for: {target.upper()}")

    y = df[target]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=0.2,
        random_state=42,
        stratify=y
    )

    model = lgb.LGBMClassifier(
        objective="binary",
        boosting_type="gbdt",
        n_estimators=300,
        learning_rate=0.05,
        max_depth=6,
        num_leaves=31,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42
    )

    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]

    acc = accuracy_score(y_test, y_pred)
    auc = roc_auc_score(y_test, y_prob)

    print(f"Accuracy: {acc:.3f}")
    print(f"AUC: {auc:.3f}")
    print(classification_report(y_test, y_pred))

    models[target] = model
    metrics[target] = {"accuracy": acc, "auc": auc}

    # Save model
    joblib.dump(model, f"../static/models/{target}_lgbm.pkl")
print("\n===== MODEL PERFORMANCE SUMMARY =====")
for disease, m in metrics.items():
    print(f"{disease.upper()} → Accuracy: {m['accuracy']:.3f}, AUC: {m['auc']:.3f}")
# Load saved models
loaded_models = {}
for target in TARGETS:
    loaded_models[target] = joblib.load(f"../static/models/{target}_lgbm.pkl")
new_patient = pd.DataFrame([{
    "age": 45,
    "gender": 1,              # 1 = Male, 0 = Female
    "bmi": 32.5,
    "fruit_intake": 1,
    "vegetable_intake": 2,
    "fiber_intake": 1,
    "sugar_intake": 4,
    "fast_food_intake": 3,
    "exercise_minutes_per_day": 1,
    "sitting_hours_per_day": 3,
    "sleep_hours": 6,
    "stress_level": 4,
    "smoking_status": 1,
    "alcohol_consumption": 1,
    "family_history_diabetes": 1,
    "family_history_heart_disease": 0
}])
print("\n===== LIFESTYLE DISEASE RISK PREDICTION =====")

for disease, model in loaded_models.items():
    probability = model.predict_proba(new_patient)[0][1]
    print(f"{disease.upper()}: {probability * 100:.2f}% risk")

def risk_level(prob):
    if prob < 0.3:
        return "Low"
    elif prob < 0.6:
        return "Moderate"
    else:
        return "High"

print("\n===== RISK LEVELS =====")
for disease, model in loaded_models.items():
    prob = model.predict_proba(new_patient)[0][1]
    print(f"{disease.upper()}: {risk_level(prob)} risk")
