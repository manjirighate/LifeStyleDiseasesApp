import pandas as pd
import lightgbm as lgb
import joblib
import os

from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import roc_auc_score

df = pd.read_csv("lifestyle_health_dataset_v2.csv")

TARGETS = ["diabetes", "hypertension", "heart_disease", "obesity"]
DISEASE_FEATURES = {
    "diabetes": [
        "age", "gender", "bmi",
        "sugar_intake",
        "exercise_minutes_per_day",
        "fiber_intake",
        "sleep_hours",
        "stress_level",
        "family_history_diabetes"
    ],

    "hypertension": [
        "age", "gender", "bmi",
        "stress_level",
        "exercise_minutes_per_day",
        "sleep_hours",
        "smoking_status"
    ],

    "heart_disease": [
        "age", "gender",
        "exercise_minutes_per_day",
        "sitting_hours_per_day",
        "smoking_status",
        "alcohol_consumption",
        "stress_level",
        "family_history_heart_disease"
    ],

    "obesity": [
        "age", "gender", "bmi",
        "fruit_intake",
        "vegetable_intake",
        "fiber_intake",
        "fast_food_intake",
        "exercise_minutes_per_day",
        "sitting_hours_per_day",
        "sleep_hours"
    ]
}
 

os.makedirs("../static/models", exist_ok=True)

models = {}

print("\n===== TRAINING MODELS =====")

for target in TARGETS:
    print(f"\nTraining {target.upper()}")

    X = df[DISEASE_FEATURES[target]]
    y = df[target]

    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    aucs = []

    model = lgb.LGBMClassifier(
        objective="binary",
        n_estimators=400,
        learning_rate=0.05,
        max_depth=-1,
        num_leaves=31,
        min_data_in_leaf=30,
        subsample=0.8,
        colsample_bytree=0.8,
        class_weight="balanced",
        random_state=42
    )
    

    for train_idx, test_idx in skf.split(X, y):
        model.fit(X.iloc[train_idx], y.iloc[train_idx])
        probs = model.predict_proba(X.iloc[test_idx])[:, 1]
        aucs.append(roc_auc_score(y.iloc[test_idx], probs))

    print(f"Mean AUC: {sum(aucs)/len(aucs):.3f}")

    model.fit(X, y)  # train on full data
    joblib.dump(model, f"../static/models/{target}_lgbm.pkl")
    models[target] = model
importances = pd.Series(
    model.feature_importances_,
    index=DISEASE_FEATURES[target]
).sort_values(ascending=False)

print("Top Risk Factors:")
print(importances.head(5))

new_patient = {
    "age": 45,
    "gender": 1,
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
    "family_history_heart_disease":0,
    "family_history_diabetes":0

}

def risk_level(p):
    if p < 0.25:
        return "Low"
    elif p < 0.6:
        return "Moderate"
    else:
        return "High"

print("\n===== LIFESTYLE DISEASE RISK =====")

for disease in TARGETS:
    model = joblib.load(f"../static/models/{disease}_lgbm.pkl")
    features = DISEASE_FEATURES[disease]

    X_new = pd.DataFrame([{k: new_patient[k] for k in features}])
    prob = model.predict_proba(X_new)[0][1]

    print(f"{disease.upper()}: {prob*100:.1f}% → {risk_level(prob)} risk")
