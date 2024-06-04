# Pixel art refiner by Hipnos
# V 1.0
# Liberado bajo licencia Creative Commons reconocimiento (by)

from PIL import Image, ImageEnhance, ImageDraw, ImageFilter
import numpy as np
from collections import Counter

# Parámetros
ruta_imagen = "imagenes/1.jpg"
filtrado_previo = False # Si queremos pasar un filtro mediano previo a la imagen original, elimina ruido y algunos detalles. Reduce colores.
eliminacion_ruido = 0 # Número de pasadas del filtro de la mediana al resultado final
factor_contraste = 1.2 # Mejora el contraste de la imagen, útil para discriminar mejor los colores en imagenes complicadas.
distancia_minima_agrupar_colores = 20 # Este parámetro limita el tamaño de la paleta final. Se recomienda elegir un valor entre 20 y 80. Un valor muy bajo puede ralentizar el cálculo, y un valor muy alto puede binarizar la imagen.

imagen = Image.open(ruta_imagen)
tamano_imagen_salida = (int(imagen.width/6),int(imagen.height/5))

def calcular_distancia_rgb(color1, color2):
    # Calcula la distancia RGB entre dos colores
    r1, g1, b1 = color1
    r2, g2, b2 = color2
    return ((r1 - r2) ** 2 + (g1 - g2) ** 2 + (b1 - b2) ** 2) ** 0.5

def procesar_imagen(imagen):
    # Crea una copia de la imagen original
    imagen_procesada = imagen.copy()

    # Obtiene los píxeles de la imagen procesada
    pixeles = imagen_procesada.load()

    # Crea un diccionario para almacenar los colores
    colores = {}

    # Recorre cada píxel
    for x in range(imagen_procesada.width):
        for y in range(imagen_procesada.height):
            pixel = pixeles[x, y]
            # Compara con los colores existentes en el diccionario
            for color_existente in colores:
                distancia = calcular_distancia_rgb(pixel, color_existente)
                if distancia < distancia_minima_agrupar_colores:
                    # Convierte el pixel al color más cercano
                    pixeles[x, y] = colores[color_existente]
                    break
            else:
                # Si no se encuentra un color cercano, agrega el color al diccionario
                colores[pixel] = pixel
    return imagen_procesada

def contar_colores_unicos(imagen):
    # Convierte la imagen a un arreglo numpy
    arreglo_imagen = np.array(imagen)

    # Obtiene los colores únicos
    colores_unicos = np.unique(arreglo_imagen.reshape(-1, arreglo_imagen.shape[2]), axis=0)

    return len(colores_unicos)

# Ajusta el contraste
imagen = ImageEnhance.Contrast(imagen).enhance(factor_contraste)

# Aplicamos un filtro de la mediana
if filtrado_previo:
    imagen = imagen.filter(ImageFilter.MedianFilter(size=3))

# Simplifica los colores de la imagen
imagen_procesada = procesar_imagen(imagen)
imagen_procesada.save('simplificada.gif')
original=imagen
original.save('original.gif')
imagen=imagen_procesada

# Ajusta el tamaño a pixel 1:1
imagen = imagen.resize(tamano_imagen_salida, Image.NEAREST)

# Aplicamos uno o varios filtros de la mediana según el valor de eliminacion_ruido
for j in range(eliminacion_ruido):
    imagen = imagen.filter(ImageFilter.MedianFilter(size=3))

# Obtener los colores más utilizados de la imagen RGB
## Obtener los valores de píxeles de la imagen
pixels = list(imagen.getdata())

## Contar la frecuencia de cada color
frecuencia_colores = Counter(pixels)

## Ordenar los colores por frecuencia (de mayor a menor)
colores_ordenados = frecuencia_colores.most_common()

## Extraer los colores más utilizados
colores_mas_utilizados = [color for color, _ in colores_ordenados]

# Añade un margen derecho de 20 píxeles en blanco
margen_derecho = Image.new("RGB", (20, imagen.height), color="white")
imagen_con_margen = Image.new("RGB", (imagen.width + 20, imagen.height))
imagen_con_margen.paste(imagen, (0, 0))
imagen_con_margen.paste(margen_derecho, (imagen.width, 0))

# Pon una muestra de cada color de la paleta detectada en el margen, como un cuadrado de 20x5 pixeles
# Crea un objeto ImageDraw para dibujar en la imagen
draw = ImageDraw.Draw(imagen_con_margen)

# Tamaño del cuadrado de muestra
ancho_muestra = 18
alto_muestra = imagen.height / len(colores_mas_utilizados)

# Coordenadas iniciales para el primer cuadrado
x = 1+imagen.width
y = 0

# Itera a través de los colores de la paleta
for color in colores_mas_utilizados:
    # Dibuja un rectángulo del color actual
    draw.rectangle([x, y, x + ancho_muestra, y + alto_muestra], fill=color)
    # Actualiza las coordenadas para el siguiente cuadrado
    y += alto_muestra

# Ajusta el tamaño a pixel 1:5
imagen_con_margen = imagen_con_margen.resize((original.width+100, original.height), Image.NEAREST)

# Guarda la imagen con las muestras de color
ruta_salida_muestras = "final.gif"
imagen_con_margen.save(ruta_salida_muestras)

# Calcula el número de colores únicos
num_colores = contar_colores_unicos(original)
print(f"Número de colores únicos en la imagen original: {num_colores}") #Ojo que si aplicas filtrado previo este número se reduce.
num_colores = contar_colores_unicos(imagen_procesada)
print(f"Número de colores únicos en la imagen simplificada: {num_colores}")
num_colores = contar_colores_unicos(imagen)
print(f"Número de colores únicos en la imagen simplificada y resized: {num_colores}")
