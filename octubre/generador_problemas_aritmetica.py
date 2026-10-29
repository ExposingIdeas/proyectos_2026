import math
import random
from datetime import datetime
import tkinter as tk
from tkinter import messagebox, ttk

# ==========================================
# FUNCIONES AUXILIARES MATEMÁTICAS
# ==========================================


def es_primo(n):
    if n < 2:
        return False
    for i in range(2, int(math.isqrt(n)) + 1):
        if n % i == 0:
            return False
    return True


# ==========================================
# GENERADORES DE PROBLEMAS POR TEMA
# ==========================================


def problema_primos():
    a = random.randint(10, 80)
    b = a + random.randint(20, 60)
    # Contar primos estrictamente entre a y b
    cantidad = sum(1 for x in range(a + 1, b) if es_primo(x))
    enunciado = f"¿Cuántos números primos existen entre {a} y {b}?"
    respuesta = f"Existen {cantidad} números primos entre {a} y {b}."
    return enunciado, respuesta


def problema_mcm_mcd():
    tipo = random.choice(["MCD", "MCM"])
    n1 = random.randint(12, 100)
    n2 = random.randint(12, 100)
    if tipo == "MCD":
        ans = math.gcd(n1, n2)
        enunciado = (
            f"Calcula el Máximo Común Divisor (MCD) de {n1} y {n2}."
        )
        respuesta = f"El MCD({n1}, {n2}) es {ans}."
    else:
        ans = math.lcm(n1, n2)
        enunciado = (
            f"Calcula el Mínimo Común Múltiplo (MCM) de {n1} y {n2}."
        )
        respuesta = f"El MCM({n1}, {n2}) es {ans}."
    return enunciado, respuesta


def problema_divisores():
    # Escoger un número con variedad de divisores
    n = random.randint(30, 200)
    divisores = [i for i in range(1, n + 1) if n % i == 0]
    enunciado = f"¿Cuántos divisores positivos tiene el número {n}?"
    respuesta = f"El número {n} tiene {len(divisores)} divisores positivos: {divisores}."
    return enunciado, respuesta


def problema_porcentajes():
    total = random.choice([50, 80, 120, 150, 200, 250, 300, 400, 500])
    pct = random.choice([5, 10, 15, 20, 25, 30, 40, 50, 75])
    resultado = int((pct / 100) * total)
    enunciado = (
        f"En una tienda, un artículo cuesta ${total}. Si se le aplica un descuento del "
        f"{pct}%, ¿cuál es el precio final a pagar?"
    )
    respuesta = f"El descuento es de ${resultado}, por lo que el precio final es ${total - resultado}."
    return enunciado, respuesta


def problema_fracciones():
    # Suma de fracciones con respuesta simplificada
    d1 = random.randint(2, 8)
    d2 = random.randint(2, 8)
    n1 = random.randint(1, d1 - 1)
    n2 = random.randint(1, d2 - 1)

    num_total = n1 * d2 + n2 * d1
    den_total = d1 * d2
    divisor_comun = math.gcd(num_total, den_total)

    num_simpl = num_total // divisor_comun
    den_simpl = den_total // divisor_comun

    enunciado = f"Calcula el resultado irreducible de la suma: ({n1}/{d1}) + ({n2}/{d2})."
    if den_simpl == 1:
        respuesta = f"El resultado es {num_simpl}."
    else:
        respuesta = f"El resultado es {num_simpl}/{den_simpl}."
    return enunciado, respuesta


def problema_progresion_aritmetica():
    a1 = random.randint(3, 20)
    d = random.randint(2, 7)
    n = random.randint(10, 25)
    an = a1 + (n - 1) * d
    suma = n * (a1 + an) // 2

    opcion = random.choice(["termino", "suma"])
    if opcion == "termino":
        enunciado = (
            f"En una progresión aritmética cuyo primer término es {a1} y la diferencia común es {d}, "
            f"¿cuál es el valor del término número {n}?"
        )
        respuesta = f"El término a_{n} es {an}."
    else:
        enunciado = (
            f"En una progresión aritmética con primer término {a1} y diferencia {d}, "
            f"¿cuál es la suma de los primeros {n} términos?"
        )
        respuesta = f"La suma de los primeros {n} términos es {suma}."
    return enunciado, respuesta


CATEGORIAS = [
    problema_primos,
    problema_mcm_mcd,
    problema_divisores,
    problema_porcentajes,
    problema_fracciones,
    problema_progresion_aritmetica,
]

# ==========================================
# INTERFAZ GRÁFICA (TKINTER)
# ==========================================


class GeneradorApp:

    def __init__(self, root):
        self.root = root
        self.root.title("Generador de Problemas Aritméticos")
        self.root.geometry("640x480")
        self.root.resizable(False, False)

        self.enunciado_actual = ""
        self.respuesta_actual = ""
        self.mostrando_respuesta = False

        self.configurar_ui()
        self.generar_nuevo_problema()

    def configurar_ui(self):
        # Marco superior (Título)
        header = ttk.Label(
            self.root,
            text="Generador de Problemas de Aritmética",
            font=("Helvetica", 16, "bold"),
        )
        header.pack(pady=15)

        # Contenedor del enunciado
        marco_problema = ttk.LabelFrame(
            self.root, text=" Enunciado del Problema "
        )
        marco_problema.pack(padx=20, pady=10, fill="both", expand=True)

        self.lbl_enunciado = tk.Label(
            marco_problema,
            text="",
            font=("Arial", 12),
            wraplength=560,
            justify="center",
            bg="#f8f9fa",
            relief="solid",
            bd=1,
        )
        self.lbl_enunciado.pack(padx=15, pady=15, fill="both", expand=True)

        # Contenedor de la respuesta
        marco_respuesta = ttk.LabelFrame(self.root, text=" Respuesta ")
        marco_respuesta.pack(padx=20, pady=5, fill="x")

        self.lbl_respuesta = tk.Label(
            marco_respuesta,
            text="[Oculta]",
            font=("Arial", 11, "italic"),
            fg="#2b580c",
            wraplength=560,
            height=2,
        )
        self.lbl_respuesta.pack(padx=10, pady=10)

        # Botones de acción
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(pady=15)

        self.btn_nuevo = ttk.Button(
            btn_frame,
            text="🎲 Generar Nuevo Problema",
            command=self.generar_nuevo_problema,
        )
        self.btn_nuevo.grid(row=0, column=0, padx=8)

        self.btn_toggle = ttk.Button(
            btn_frame,
            text="👁 Mostrar Respuesta",
            command=self.alternar_respuesta,
        )
        self.btn_toggle.grid(row=0, column=1, padx=8)

        self.btn_exportar = ttk.Button(
            btn_frame,
            text="💾 Exportar como TXT",
            command=self.exportar_txt,
        )
        self.btn_exportar.grid(row=0, column=2, padx=8)

    def generar_nuevo_problema(self):
        # Elegir un generador al azar
        generador = random.choice(CATEGORIAS)
        self.enunciado_actual, self.respuesta_actual = generador()

        # Actualizar UI
        self.lbl_enunciado.config(text=self.enunciado_actual)
        self.mostrando_respuesta = False
        self.lbl_respuesta.config(text="[Oculta]")
        self.btn_toggle.config(text="👁 Mostrar Respuesta")

    def alternar_respuesta(self):
        if not self.enunciado_actual:
            return

        self.mostrando_respuesta = not self.mostrando_respuesta
        if self.mostrando_respuesta:
            self.lbl_respuesta.config(text=self.respuesta_actual)
            self.btn_toggle.config(text="🙈 Ocultar Respuesta")
        else:
            self.lbl_respuesta.config(text="[Oculta]")
            self.btn_toggle.config(text="👁 Mostrar Respuesta")

    def exportar_txt(self):
        if not self.enunciado_actual:
            messagebox.showwarning(
                "Aviso", "No hay ningún problema para exportar."
            )
            return

        # Generar nombre único con timestamp al milisegundo
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        nombre_archivo = f"problema_{timestamp}.txt"

        contenido = (
            "=========================================\n"
            "       PROBLEMA DE ARITMÉTICA            \n"
            "=========================================\n\n"
            f"ENUNCIADO:\n{self.enunciado_actual}\n\n"
            f"RESPUESTA:\n{self.respuesta_actual}\n\n"
            f"Generado el: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        )

        try:
            with open(nombre_archivo, "w", encoding="utf-8") as f:
                f.write(contenido)
            messagebox.showinfo(
                "Exportado con éxito",
                f"El problema fue guardado como:\n{nombre_archivo}",
            )
        except Exception as e:
            messagebox.showerror(
                "Error", f"No se pudo guardar el archivo:\n{e}"
            )


# ==========================================
# EJECUCIÓN
# ==========================================
if __name__ == "__main__":
    ventana = tk.Tk()
    app = GeneradorApp(ventana)
    ventana.mainloop()