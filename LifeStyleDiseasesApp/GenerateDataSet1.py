import random
import pandas as pd
import numpy as np

# Reproducibility
random.seed(42)
np.random.seed(42)

NUM_SAMPLES = 20000   # good size

# ---------- LEVEL DEFINITIONS ----------
INTAKE_LEVELS = [0, 1, 2, 3, 4]
EXERCISE_LEVELS = [0, 1, 2, 3, 4]
SITTING_LEVELS = [0, 1, 2, 3]
STRESS_LEVELS = [0, 1, 2, 3, 4]

data = []

for _ in range(NUM_SAMPLES):

    # ---------- DEMOGRAPHICS ----------
    age = random.randint(18, 75)
    gender = random.choice([0, 1])
    bmi = round(np.clip(np.random.normal(26, 5), 18, 40), 1)

    # ---------- LIFESTYLE ----------
    fruit_intake = random.choice(INTAKE_LEVELS)
    vegetable_intake = random.choice(INTAKE_LEVELS)
    fiber_intake = random.choice(INTAKE_LEVELS)
    sugar_intake = random.choice(INTAKE_LEVELS)
    fast_food = random.choice(INTAKE_LEVELS)

    exercise_minutes = random.choice(EXERCISE_LEVELS)
    sitting_hours = random.choice(SITTING_LEVELS)
    sleep_hours = random.randint(4, 9)
    stress_level = random.choice(STRESS_LEVELS)

    smoking = random.choice([0, 1])
    alcohol = random.choice([0, 1])

    family_diabetes = random.choice([0, 1])
    family_heart = random.choice([0, 1])

    # ---------- RISK SCORES (CONTINUOUS) ----------
    diabetes_risk = (
        0.03 * age +
        0.6 * bmi +
        3.5 * sugar_intake -
        2.0 * exercise_minutes +
        3.0 * family_diabetes +
        np.random.normal(0, 8)
    )

    hypertension_risk = (
        0.04 * age +
        2.5 * stress_level +
        2.0 * sitting_hours +
        2.0 * bmi +
        np.random.normal(0, 7)
    )

    heart_risk = (
        3.0 * smoking +
        2.5 * alcohol +
        2.5 * family_heart +
        0.04 * age +
        np.random.normal(0, 6)
    )

    obesity_risk = (
        3.5 * bmi -
        2.0 * exercise_minutes +
        1.5 * fast_food +
        np.random.normal(0, 6)
    )

    # ---------- PROBABILITIES (SIGMOID) ----------
    diabetes_prob = 1 / (1 + np.exp(-(diabetes_risk - 45) / 10))
    hypertension_prob = 1 / (1 + np.exp(-(hypertension_risk - 50) / 10))
    obesity_prob = 1 / (1 + np.exp(-(obesity_risk - 55) / 10))

    # heart disease depends on hypertension + diabetes
    heart_prob = (
        0.4 * diabetes_prob +
        0.4 * hypertension_prob +
        0.2 * (1 / (1 + np.exp(-(heart_risk - 40) / 10)))
    )

    # ---------- FINAL LABELS ----------
    diabetes = int(np.random.rand() < diabetes_prob)
    hypertension = int(np.random.rand() < hypertension_prob)
    obesity = int(np.random.rand() < obesity_prob)
    heart_disease = int(np.random.rand() < heart_prob)

    data.append([
        age, gender, bmi,
        fruit_intake, vegetable_intake, fiber_intake,
        sugar_intake, fast_food,
        exercise_minutes, sitting_hours,
        sleep_hours, stress_level,
        smoking, alcohol,
        family_diabetes, family_heart,
        diabetes, hypertension, heart_disease, obesity
    ])

# ---------- DATAFRAME ----------
columns = [
    "age", "gender", "bmi",
    "fruit_intake", "vegetable_intake", "fiber_intake",
    "sugar_intake", "fast_food_intake",
    "exercise_minutes_per_day", "sitting_hours_per_day",
    "sleep_hours", "stress_level",
    "smoking_status", "alcohol_consumption",
    "family_history_diabetes", "family_history_heart_disease",
    "diabetes", "hypertension", "heart_disease", "obesity"
]

df = pd.DataFrame(data, columns=columns)

df.to_csv("lifestyle_health_dataset.csv", index=False)

print("  Realistic dataset generated:", df.shape)
print(df[["diabetes", "hypertension", "heart_disease", "obesity"]].mean())
print(df.head())
