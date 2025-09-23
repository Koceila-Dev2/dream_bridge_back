from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO
import os
import dotenv
from dotenv import load_dotenv

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

client = genai.Client(api_key=GOOGLE_API_KEY)

response = client.models.generate_images(
    model='imagen-4.0-generate-001',
    prompt='Un rêve poétique de Paris avec la Tour Eiffel flottant dans un ciel nocturne violet pastel, entourée de nuages doux et lumineux. La scène est onirique et surréaliste : des étoiles scintillent, la Seine brille comme un miroir, et des formes floues évoquent des souvenirs de cafés parisiens et de lampadaires. L’ambiance est mystérieuse et paisible, avec une palette de violet sombre et pastel, sans texte ni écritures.',
    config=types.GenerateImagesConfig(
        number_of_images= 1,
    )
)
for generated_image in response.generated_images:
  generated_image.image.show()
  print(type(generated_image.image))

   # PIL Image object