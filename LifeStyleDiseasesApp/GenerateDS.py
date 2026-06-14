import random
import pandas as pd
import numpy as np

np.random.seed(42)
random.seed(42)

N = 25000
data = []

def sigmoid(x):
    return 1 / (1 + np.exp(-x))

for _ in range(N):

    # ---------------- DEMOGRAPHICS ----------------
    age = np.clip(int(np.random.normal(45, 15)), 18, 80)
    gender = np.random.choice([0, 1])
    bmi = round(np.clip(np.random.normal(27, 4.5), 18, 42), 1)

    # ---------------- DIET ----------------
    fruit = np.random.choice([0,1,2,3,4], p=[0.25,0.30,0.25,0.15,0.05])
    vegetables = np.random.choice([0,1,2,3,4], p=[0.20,0.30,0.30,0.15,0.05])
    fiber = np.clip(int((fruit + vegetables) / 2 + np.random.normal(0,1)), 0, 4)

    sugar = np.random.choice([0,1,2,3,4], p=[0.10,0.20,0.30,0.25,0.15])
    fast_food = np.random.choice([0,1,2,3,4], p=[0.15,0.25,0.30,0.20,0.10])

    # ---------------- ACTIVITY ----------------
    exercise = np.random.choice([0,1,2,3,4], p=[0.20,0.30,0.25,0.15,0.10])
    sitting = np.random.choice([0,1,2,3], p=[0.20,0.35,0.30,0.15])

    sleep = np.clip(int(np.random.normal(7, 1)), 4, 9)
    stress = np.random.choice([0,1,2,3,4], p=[0.10,0.20,0.30,0.25,0.15])

    # ---------------- HABITS ----------------
    smoking = np.random.choice([0,1], p=[0.75,0.25])
    alcohol = np.random.choice([0,1], p=[0.65,0.35])

    # ---------------- FAMILY HISTORY ----------------
    family_diabetes = np.random.choice([0,1], p=[0.70,0.30])
    family_heart = np.random.choice([0,1], p=[0.72,0.28])

    # ---------------- RISK SCORES ----------------
    diabetes_score = (
        0.55 * bmi +
        2.2 * sugar -
        2.0 * exercise -
        1.6 * fiber +
        2.0 * family_diabetes +
        0.03 * age +
        np.random.normal(0, 3)
    )

    hypertension_score = (
        0.05 * age +
        2.0 * stress +
        1.5 * sitting +
        1.0 * bmi -
        1.2 * fiber +
        np.random.normal(0, 3)
    )

    obesity_score = (
        0.9 * bmi +
        1.6 * fast_food -
        2.0 * exercise -
        1.2 * fiber +
        np.random.normal(0, 2)
    )

    heart_score = (
        0.06 * age +
        2.5 * smoking +
        2.0 * alcohol +
        2.0 * family_heart -
        1.2 * fiber +
        np.random.normal(0, 3)
    )

    # ---------------- PROBABILITIES (CALIBRATED) ----------------
    diabetes_prob = sigmoid((diabetes_score - 25) / 6)

    hypertension_prob = sigmoid((hypertension_score - 36) / 6)

    obesity_prob = sigmoid((obesity_score - 30) / 5)
    """
    heart_prob = sigmoid(
        (heart_score +
        3.0 * diabetes_prob +
        3.0 * hypertension_prob - 26) / 6
    )
    """
    heart_prob = sigmoid(
        (heart_score +
        3.5 * diabetes_prob +
        3.5 * hypertension_prob - 25) / 6
    )

    # ---------------- LABELS ----------------
    diabetes = int(np.random.rand() < diabetes_prob)
    hypertension = int(np.random.rand() < hypertension_prob)
    obesity = int(np.random.rand() < obesity_prob)
    heart = int(np.random.rand() < heart_prob)

    data.append([
        age, gender, bmi,
        fruit, vegetables, fiber,
        sugar, fast_food,
        exercise, sitting, sleep, stress,
        smoking, alcohol,
        family_diabetes, family_heart,
        diabetes, hypertension, heart, obesity
    ])

# ---------------- DATAFRAME ----------------
columns = [
    "age","gender","bmi",
    "fruit_intake","vegetable_intake","fiber_intake",
    "sugar_intake","fast_food_intake",
    "exercise_minutes_per_day","sitting_hours_per_day",
    "sleep_hours","stress_level",
    "smoking_status","alcohol_consumption",
    "family_history_diabetes","family_history_heart_disease",
    "diabetes","hypertension","heart_disease","obesity"
]

df = pd.DataFrame(data, columns=columns)
df.to_csv("lifestyle_health_dataset_v2.csv", index=False)

print("Dataset shape:", df.shape)
print(df[["diabetes","hypertension","heart_disease","obesity"]].mean())
