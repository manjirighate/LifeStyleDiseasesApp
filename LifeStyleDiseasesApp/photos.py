import requests

for i in range(70 ,76):
    url = "https://thispersondoesnotexist.com/"
    img = requests.get(url).content

    with open(f"../static/doctors/cardio{i}.jpg", "wb") as f:
        f.write(img)

    print(f"Saved cardio{i}.jpg")
