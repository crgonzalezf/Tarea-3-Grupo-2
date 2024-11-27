from openai import OpenAI
import base64
from pydantic import BaseModel
import os
import json

client = OpenAI()

class Boleta(BaseModel):
    class Producto(BaseModel):
        nombre: str
        cantidad: int
        precio: int
    productos: list[Producto]
    total: int

# Funcion para describir una boleta usando Vision API y obtener el JSON de los productos y el total
def ocr_boleta(image):
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
                        "text": """
                            Te voy a entregar una foto de una boleta o un recibo. 
                            Necesito que identifiques cada producto, su cantidad y su precio.
                            Tambien debes identificar el total de la boleta.
                            Esta información me la debes entregar como un JSON con la siguiente estructura:
                            {
                                "productos": [
                                    {
                                        "nombre": "Nombre del producto",
                                        "cantidad": Cantidad del producto,
                                        "precio": Precio del producto
                                    },
                                    ...
                                ],
                                "total": Total de la boleta
                            }
                            """
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

# Funcion para crear una imagen de un producto de una boleta
def crear_imagen_producto(producto):
    response = client.images.generate(
        model="dall-e-3",
        prompt=f"Genera una imagen de lo siguiente: {producto}",
        size="1024x1024",
        response_format="b64_json",
        quality="standard",
    )
    return response

# Main function
def main():

    # Crear las carpetas si no existen
    os.makedirs("Tarea3-Grupo12/Script1/", exist_ok=True)

    # Preguntar por el nombre de la imagen de la boleta
    imagen = input("Ingresa el nombre de la imagen de la boleta (Ej: boleta.png): ")
    descripcion, tokens = ocr_boleta(imagen)
    
    # Guardar los tokens usados
    tokens_entrada = tokens.prompt_tokens
    tokens_salida = tokens.completion_tokens

    # Guardar la descripcion de Vision de la boleta en un archivo de texto
    with open("Tarea3-Grupo12/Script1/descripcion_boleta.txt", "w") as f:
        f.write(descripcion)
    print(f"Descripción entregada por Vision de la boleta guardada en Tarea3-Grupo12/Script1/descripcion_boleta.txt")

    # Pide a la API de OPENAI que entregue el JSON de la descripcion de la boleta
    completion = client.beta.chat.completions.parse(
        model="gpt-4o-2024-08-06",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Entregame un JSON de lo siguiente: " + descripcion
                    }
                ]
            }
        ],
        response_format=Boleta,
    )

    JSON_boleta = completion.choices[0].message.parsed

    # Guardar los tokens usados
    tokens_json_entrada = completion.usage.prompt_tokens
    tokens_json_salida = completion.usage.completion_tokens
    
    # Convertir el objeto JSON_boleta a una cadena JSON
    json_string = JSON_boleta.model_dump_json()

    # Convertir la cadena JSON a un diccionario
    json_dict = json.loads(json_string)

    # JSON formateado
    formatted_json = json.dumps(json_dict, indent=4)

    # Guardar el JSON en un archivo
    with open("Tarea3-Grupo12/Script1/boleta.json", "w") as f:
        f.write(formatted_json)
    print(f"JSON de la boleta guardado en Tarea3-Grupo12/Script1/boleta.json")

    # Para cada producto en la boleta, crear una imagen y guardarla.
    for producto in JSON_boleta.productos:
        response = crear_imagen_producto(producto.nombre)
        with open(f"Tarea3-Grupo12/Script1/{producto.nombre}.png", "wb") as f:
            f.write(base64.b64decode(response.data[0].b64_json))
        print(f"Imagen del producto {producto.nombre} guardada en Tarea3-Grupo12/Script1/{producto.nombre}.png")

    # Calcular los costos de los tokens
    token_totales_entrada = (tokens_entrada + tokens_json_entrada) * 0.00000125
    token_totales_salida = (tokens_salida + tokens_json_salida) * 0.000005
    token_totales_imagenes = len(JSON_boleta.productos) * 0.04
    # Sumar todos los costos de los tokens
    costo_total = token_totales_entrada + token_totales_salida + token_totales_imagenes

    # Crear un diccionario con los costos
    costos = {
        "token_totales_entrada": token_totales_entrada,
        "token_totales_salida": token_totales_salida,
        "token_totales_imagenes": token_totales_imagenes,
        "costo_total": costo_total
    }

    # Guardar los costos en un archivo JSON
    with open("Tarea3-Grupo12/Script1/costos.json", "w") as f:
        json.dump(costos, f, indent=4)
    print(f"Costos guardados en Tarea3-Grupo12/Script1/costos.json")

if __name__ == "__main__":
    main()
