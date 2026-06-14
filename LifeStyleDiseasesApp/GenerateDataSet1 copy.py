import random
import pandas as pd
import numpy as np

# Reproducibility
random.seed(42)
np.random.seed(42)

NUM_SAMPLES = 20000   # MINIMUM 2000 as guide instructed

# ---------- MAPPINGS ----------
# 0 = Almost None / Very Little
# 1 = A Small Amount / A Little
# 2 = Moderate
# 3 = A Good Amount
# 4 = A Lot / Too Much

INTAKE_LEVELS = [0, 1, 2, 3, 4]
FAST_FOOD_LEVELS = [0, 1, 2, 3, 4]
EXERCISE_LEVELS = [0, 1, 2, 3, 4]
SITTING_LEVELS = [0, 1, 2, 3]
STRESS_LEVELS = [0, 1, 2, 3, 4]

data = []

for _ in range(NUM_SAMPLES):
    age = random.randint(18, 75)
    gender = random.choice([0, 1])   # 0 = Female, 1 = Male
    bmi = round(random.uniform(18, 38), 1)

    fruit_intake = random.choice(INTAKE_LEVELS)
    vegetable_intake = random.choice(INTAKE_LEVELS)
    fiber_intake = random.choice(INTAKE_LEVELS)
    sugar_intake = random.choice(INTAKE_LEVELS)
    fast_food = random.choice(FAST_FOOD_LEVELS)

    exercise_minutes = random.choice(EXERCISE_LEVELS)
    sitting_hours = random.choice(SITTING_LEVELS)

    sleep_hours = random.randint(4, 9)
    stress_level = random.choice(STRESS_LEVELS)

    smoking = random.choice([0, 1])    # 0 = No, 1 = Yes
    alcohol = random.choice([0, 1])    # 0 = No, 1 = Yes

    family_diabetes = random.choice([0, 1])
    family_heart = random.choice([0, 1])

    # ---------- DISEASE LOGIC ----------
    diabetes = 1 if (bmi > 27 and sugar_intake >= 3 and exercise_minutes <= 1) else 0
    hypertension = 1 if (age > 45 and stress_level >= 3 and sitting_hours >= 2) else 0
    heart_disease = 1 if (hypertension == 1 and smoking == 1) else 0
    obesity = 1 if bmi >= 30 else 0

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

# ---------- COLUMNS ----------
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

# Save dataset
df.to_csv("lifestyle_health_dataset.csv", index=False)

print("Dataset generated successfully with 2000 records!")
print(df.head())
