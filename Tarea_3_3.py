from openai import OpenAI
import base64
import os
import json

client = OpenAI()

# Funcion para describir una imagen usando Vision API
def describe_image(image):
    encoded_string = ""
    with open(image, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode("utf-8")

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text", 
                        "text": "Indicame una descripción de la imagen adjunta."
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{encoded_string}"}
                    },
                ],
            }
        ],
    )
    descripcion = response.choices[0].message.content.strip()
    tokens = response.usage
    return descripcion, tokens

# Funcion para generar una imagen desde una descripción usando DALL-E 3
def generar_imagen_dalle3(prompt):
    response = client.images.generate(
        model="dall-e-3",
        prompt=f"Genera una imagen de lo siguiente: {prompt}",
        size="1024x1024",
        response_format="b64_json",
        quality="standard",

    )
    return response

# Funcion para generar variantes de una imagen usando DALL-E 2
def generar_variacion_dall2(image):
    response = client.images.create_variation(
        model="dall-e-2",
        image=open(image, "rb"),
        n=1,
        size="1024x1024",
        response_format="b64_json",
    )
    return response

# Main function
def main():

    # Preguntar por el nombre de la imagen del logo
    logo = input("Indica el nombre de la imagen que se modificará (Ej: logo.png): ")

    # Describir el logo usando Vision API
    descripcion, token = describe_image(logo)

    #Guardar los tokens usados
    tokens_entrada = token.prompt_tokens
    tokens_salida = token.completion_tokens

    # Crear las carpetas si no existen
    os.makedirs("Tarea3-Grupo2/cod3/", exist_ok=True)

    #Guardar la descripción en un archivo
    with open("Tarea3-Grupo2/cod3/descripcion_logo.txt", "w") as f:
        f.write(descripcion)
    print(f"Descripción del logo guardada en Tarea3-Grupo2/cod3/descripcion_logo.txt")

    # Crear un prompt para un text to image a partir de la descripción
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": """Créame un prompt para un text to image de la descripción que te voy a dar,
                          este prompt no debe tener palabras prohibidas o nombres de empresa directamente. 
                          DESCRIPCION:
                          """ + descripcion
                    }
                ]
            }
        ]
    )

    prompt_imagen = response.choices[0].message.content.strip()
    tokens_entrada += response.usage.prompt_tokens
    tokens_salida += response.usage.completion_tokens


    #Generar variación del logo usando DALL-E 2
    variacion_dalle2 = generar_variacion_dall2(logo)

    #Guardar la variación en un archivo
    with open("Tarea3-Grupo2/cod3/variacion_dalle2.png", "wb") as f:
        f.write(base64.b64decode(variacion_dalle2.data[0].b64_json))
    print(f"Variacion de la imagen generada con DALL-E 2 y guardada en Tarea3-Grupo2/cod3/variacion_dalle2.png")


    # Generar variacion del logo usando DALL-E 3 y la descripción de la imagen de Vision
    variacion_dalle3 = generar_imagen_dalle3(prompt_imagen)

    #Guardar la variación en un archivo
    with open("Tarea3-Grupo2/cod3/variacion_dalle3.png", "wb") as f:
        f.write(base64.b64decode(variacion_dalle3.data[0].b64_json))
    print(f"Variacion de la imagen generada con DALL-E 3 guardada en Tarea3-Grupo2/cod3/variacion_dalle3.png")

    # Calcular los costos
    costo_tokens_entrada_completions = tokens_entrada * 0.00000125
    costo_tokens_salida_completions = tokens_salida * 0.000005
    costo_imagen_dall_e_2 = 0.02
    costo_imagen_dall_e_3 = 0.04

    costo_total = (
        costo_tokens_entrada_completions +
        costo_tokens_salida_completions +
        costo_imagen_dall_e_2 +
        costo_imagen_dall_e_3
    )

    # Crear un diccionario con la información
    costos = {
        "Tokens_entrada_completions": costo_tokens_entrada_completions,
        "Tokens_salida_completions": costo_tokens_salida_completions,
        "Costo_imagen_dall_e_2": costo_imagen_dall_e_2,
        "Costo_imagen_dall_e_3": costo_imagen_dall_e_3,
        "Costo_Total": costo_total
    }

    # Guardar la información en un archivo JSON
    with open("Tarea3-Grupo2/cod3/costos.json", "w") as f:
        json.dump(costos, f, indent=4)
    print(f"Costos guardados en Tarea3-Grupo2/cod3/costos.json")

if __name__ == "__main__":
    main()
