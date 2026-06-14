import random
import pandas as pd
import numpy as np

# Set random seed for reproducibility
random.seed(42)
np.random.seed(42)

NUM_SAMPLES = 10000

def random_choice(options):
    return random.choice(options)

data = []

for _ in range(NUM_SAMPLES):
    age = random.randint(18, 75)
    gender = random_choice(["Male", "Female"])
    bmi = round(random.uniform(18, 38), 1)

    fruit_intake = random.randint(0, 5)
    veg_intake = random.randint(0, 5)
    fast_food = random_choice(["Rare", "Occasional", "Often"])
    sugary_drinks = random.randint(0, 10)

    exercise_days = random.randint(0, 7)
    sedentary_hours = random.randint(2, 12)

    sleep_hours = round(random.uniform(4, 9), 1)
    stress_level = random_choice(["Low", "Medium", "High"])

    smoking = random_choice(["Never", "Former", "Current"])
    alcohol = random_choice(["None", "Moderate", "Heavy"])

    family_diabetes = random_choice([0, 1])
    family_heart = random_choice([0, 1])

    # Disease logic (rule-based for realistic labels)
    diabetes = 1 if (bmi > 27 and exercise_days < 3 and sugary_drinks > 4) else 0
    hypertension = 1 if (age > 45 and stress_level == "High" and bmi > 26) else 0
    heart_disease = 1 if (smoking == "Current" and hypertension == 1) else 0
    obesity = 1 if bmi >= 30 else 0

    data.append([
        age, gender, bmi,
        fruit_intake, veg_intake, fast_food, sugary_drinks,
        exercise_days, sedentary_hours,
        sleep_hours, stress_level,
        smoking, alcohol,
        family_diabetes, family_heart,
        diabetes, hypertension, heart_disease, obesity
    ])

columns = [
    "age", "gender", "bmi",
    "fruit_intake", "vegetable_intake", "fast_food_frequency", "sugary_drinks_per_week",
    "exercise_days_per_week", "sedentary_hours_per_day",
    "sleep_hours", "stress_level",
    "smoking_status", "alcohol_consumption",
    "family_history_diabetes", "family_history_heart_disease",
    "diabetes", "hypertension", "heart_disease", "obesity"
]

df = pd.DataFrame(data, columns=columns)

# Save dataset
df.to_csv("lifestyle_disease_dataset.csv", index=False)

print("Dataset generated successfully!")
print(df.head())
