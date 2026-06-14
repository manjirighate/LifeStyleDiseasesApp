import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    classification_report
)

DATASET_PATH = "lifestyle_health_dataset.csv"
MODEL_DIR = "../static/models/"

TARGETS = ["diabetes", "hypertension", "heart_disease", "obesity"]

DISEASE_FEATURES = {
    "diabetes": [
        "age",
        "gender",
        "bmi",
        "sugar_intake",
        "exercise_minutes_per_day",
        "fiber_intake",
        "sleep_hours",
        "stress_level",
        "family_history_diabetes"
    ],

    "hypertension": [
        "age",
        "gender",
        "bmi",
        "stress_level",
        "exercise_minutes_per_day",
        "sleep_hours",
        "smoking_status"
    ],

    "heart_disease": [
        "age",
        "gender",
        "exercise_minutes_per_day",
        "sitting_hours_per_day",
        "smoking_status",
        "alcohol_consumption",
        "stress_level",
        "family_history_heart_disease"
    ],

    "obesity": [
        "age",
        "gender",
        "bmi",
        "fruit_intake",
        "vegetable_intake",
        "fiber_intake",
        "fast_food_intake",
        "exercise_minutes_per_day",
        "sitting_hours_per_day",
        "sleep_hours"
    ]
}


df = pd.read_csv(DATASET_PATH)

results = []

print("\n===== MODEL PERFORMANCE REPORT =====")

for disease in TARGETS:
    print(f"\n🔹 Evaluating {disease.upper()}")

    X = df[DISEASE_FEATURES[disease]]
    y = df[disease]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    model = joblib.load(f"{MODEL_DIR}{disease}_lgbm.pkl")

    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]

    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred, zero_division=0)
    rec = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    auc = roc_auc_score(y_test, y_prob)

    print("Confusion Matrix:")
    print(confusion_matrix(y_test, y_pred))

    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, zero_division=0))

    results.append({
        "Disease": disease.upper(),
        "Accuracy": round(acc, 3),
        "Precision": round(prec, 3),
        "Recall": round(rec, 3),
        "F1": round(f1, 3),
        "ROC_AUC": round(auc, 3)
    })

summary = pd.DataFrame(results)
print("\n===== SUMMARY =====")
print(summary)

summary.to_csv("model_performance_report.csv", index=False)
print("\n✅ Saved model_performance_report.csv")
