from openai import OpenAI
import base64
import os
import json
from PIL import Image

client = OpenAI()

# Funcion que pide una imagen, la mascara, la descripcion y usa la API de OpenAI para generar una imagen modificada
def generate_image(image: str, mask: str, description: str):
    response = client.images.edit(
        model="dall-e-2",
        image=open(image, "rb"),
        mask=open(mask, "rb"),
        prompt="Genera una imagen agregando lo siguiente:" +description,
        n=1,
        size="1024x1024",
        response_format="b64_json"
    )
    return response

# Funcion que crea una trasparencia en una imagen
def create_transparency(image: str, section: str):
    img = Image.open(image).convert("RGBA")
    width, height = img.size
    transparent_area = None

    if section == "superior derecha":
        transparent_area = (width // 2, 0, width, height // 2)
    elif section == "superior izquierda":
        transparent_area = (0, 0, width // 2, height // 2)
    elif section == "inferior derecha":
        transparent_area = (width // 2, height // 2, width, height)
    elif section == "inferior izquierda":
        transparent_area = (0, height // 2, width // 2, height)
    else:
        raise ValueError("Sección no válida. Las opciones son: 'superior derecha', 'superior izquierda', 'inferior derecha', 'inferior izquierda'.")

    for x in range(transparent_area[0], transparent_area[2]):
        for y in range(transparent_area[1], transparent_area[3]):
            img.putpixel((x, y), (255, 255, 255, 0))
    img.save(image.replace(".png", "_mask.png"))
    print(f"Imagen con transparencia guardada en {image.replace('.png', '_mask.png')}")


# Funcion Main
def main():

    # Crear las carpetas si no existen
    os.makedirs("Tarea3-Grupo2/cod2/", exist_ok=True)

    # Se pide la imagen, la mascara y lo que se desea agregar
    image = input("Ingrese la imagen del interior de una casa para modificar (Ej: living.png): ")

    # Se pide la sección a transparentar
    section = input("Ingrese la sección a transparentar (superior derecha, superior izquierda, inferior derecha, inferior izquierda): ")
    create_transparency(image, section)

    mask = image.replace(".png", "_mask.png")
    description = input("Ingrese lo que quiere agregar a la imagen: ")

    # Se llama a la funcion generate_image
    response = generate_image(image, mask, description)
    
    # Se guarda la imagen generada
    with open("Tarea3-Grupo2/cod2/imagen_generada.png", "wb") as f:
        f.write(base64.b64decode(response.data[0].b64_json))
    
    print("Imagen generada guardada en Tarea3-Grupo2/cod2/imagen_generada.png")

    # Crear un archivo JSON con la informacion del costo total
    data = {
        "Costo_total": "0,02"
    }
    with open("Tarea3-Grupo2/cod2/costo.json", "w") as f:
        json.dump(data, f)
    print("Archivo costo.json creado.")

if __name__ == "__main__":
    main()   
