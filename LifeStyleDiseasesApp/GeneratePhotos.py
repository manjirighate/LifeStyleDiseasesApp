from diffusers import StableDiffusionPipeline
import torch, os

pipe = StableDiffusionPipeline.from_pretrained(
    "runwayml/stable-diffusion-v1-5",
    torch_dtype=torch.float16
)
pipe = pipe.to("cpu")   # use "cpu" if no GPU

os.makedirs("static/doctors", exist_ok=True)

specialities = {
    "cardio": "indian male cardiologist, hospital background",
    "dent": "indian dentist, dental clinic portrait",
    "derma": "indian female dermatologist, studio lighting",
    "ent": "indian ent specialist, professional photo",
    "gp": "indian general physician, stethoscope",
    "neuro": "indian neurologist, hospital portrait",
    "pedia": "indian pediatrician, friendly smile",
    "psych": "indian psychiatrist, calm professional portrait",
    "ortho": "indian orthopedic doctor, white coat"
}

count = 1
for key, prompt in specialities.items():
    for i in range(1, 11):
        image = pipe(
            f"high quality professional portrait of {prompt}, ultra realistic, soft lighting"
        ).images[0]

        image.save(f"../static/doctors/{key}{i}.jpg")
        print(f"Generated {key}{i}.jpg")
        count += 1
