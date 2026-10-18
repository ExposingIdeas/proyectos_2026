import tkinter as tk
from tkinter import messagebox
import linecache
import random

RUTA_ARCHIVO = r"0_palabras_todas_no_conjugaciones.txt"

FILAS = 10
COLUMNAS = 3
TOTAL_PALABRAS = FILAS * COLUMNAS  # 30 palabras


def contar_lineas(ruta):
    try:
        with open(ruta, "r", encoding="utf-8") as f:
            return sum(1 for _ in f)
    except FileNotFoundError:
        return 0


def generar_matriz():
    total_lineas = contar_lineas(RUTA_ARCHIVO)

    if total_lineas < TOTAL_PALABRAS:
        messagebox.showerror(
            "Error",
            f"El archivo debe tener al menos {TOTAL_PALABRAS} líneas (tiene {total_lineas})."
        )
        return

    # 1. Seleccionar 30 números de línea únicos al azar
    numeros = random.sample(range(1, total_lineas + 1), TOTAL_PALABRAS)

    # 2. Obtener las palabras limpias
    palabras = [linecache.getline(RUTA_ARCHIVO, num).strip() for num in numeros]
    palabrasb=sorted(palabras)
    # 3. Construir la matriz de 10x3 con columnas alineadas
    ancho_columna = 18  # Espacio reservado para cada columna
    texto_matriz = ""

    for i in range(FILAS):
        fila_palabras = palabrasb[i * COLUMNAS: (i + 1) * COLUMNAS] #palabras!!!
        # Formatea cada palabra con un ancho fijo para alinear las columnas
        linea_formateada = "".join(palabra.ljust(ancho_columna) for palabra in fila_palabras)
        texto_matriz += linea_formateada + "\n"

    # 4. Actualizar la caja de texto
    area_texto.config(state="normal")
    area_texto.delete("1.0", tk.END)
    area_texto.insert(tk.END, texto_matriz)
    area_texto.config(state="disabled")


# Interfaz gráfica
ventana = tk.Tk()
ventana.title("Matriz de Palabras (10x3)")
ventana.geometry("520x360")
ventana.resizable(False, False)

titulo = tk.Label(ventana, text="Matriz de 10x3 Palabras Aleatorias", font=("Arial", 12, "bold"))
titulo.pack(pady=8)

# Importante: Usar fuente monoespaciada ("Consolas") para que las columnas cuadren perfecto
area_texto = tk.Text(
    ventana,
    height=11,
    width=55,
    font=("Consolas", 10),
    state="disabled",
    bg="#f4f4f4",
    padx=10,
    pady=10
)
area_texto.pack(pady=5)

btn_generar = tk.Button(
    ventana,
    text="🎲 Generar Nuevas 30 Palabras",
    command=generar_matriz,
    font=("Arial", 10, "bold"),
    bg="#2196F3",
    fg="white",
    padx=10,
    pady=5
)
btn_generar.pack(pady=10)

# Cargar la primera matriz al iniciar
generar_matriz()

ventana.mainloop()