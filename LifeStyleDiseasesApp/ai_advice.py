import openai

openai.api_key = "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"

def get_health_advice(disease, probability, lifestyle):
    prompt = f"""
    User has:
    - Hypertension risk: {result['hypertension_risk']['level']}
    - Diabetes risk: {result['diabetes_risk']['level']}

    Suggest:
    1. Diet
    2. Yoga
    3. Physical activity
    4. Lifestyle habits

    Give response in bullet points, simple language.
    """
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role":"user","content":prompt}],
        temperature=0.5
    )

    return response.choices[0].message.content
