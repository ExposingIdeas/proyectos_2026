import pygame
import sys
import time
import threading
import tkinter as tk
from tkinter import messagebox

# Inicializar Pygame
pygame.init()
pygame.font.init()

# Dimensiones de la ventana
ANCHO, ALTO = 600, 720
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Simulador de Reloj de Arena 2D")
reloj = pygame.time.Clock()

# Colores
COLOR_FONDO = (30, 32, 40)
COLOR_CRISTAL = (220, 230, 242)
COLOR_ARENA = (235, 185, 52)
COLOR_ARENA_CAYENDO = (210, 160, 40)
COLOR_BOTON = (60, 64, 80)
COLOR_BOTON_HOVER = (80, 85, 110)
COLOR_TEXTO = (240, 240, 240)
COLOR_DROPDOWN_BG = (45, 48, 60)
COLOR_DROPDOWN_SEL = (70, 75, 95)

# Fuentes
fuente_ui = pygame.font.SysFont("Segoe UI", 16, bold=True)
fuente_timer = pygame.font.SysFont("Consolas", 24, bold=True)

# Opciones de tiempo (Texto: Segundos)
OPCIONES_TIEMPO = [
    ("5 Minutos", 5 * 60),
    ("10 Minutos", 10 * 60),
    ("30 Minutos", 30 * 60),
    ("1 Hora", 60 * 60)
]


# Función para disparar notificación en un hilo secundario
def mostrar_notificacion(mensaje):
    def _popup():
        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        messagebox.showinfo("¡Tiempo Finalizado!", mensaje)
        root.destroy()

    threading.Thread(target=_popup, daemon=True).start()


# --- Clases de UI ---
class Boton:
    def __init__(self, x, y, ancho, alto, texto, callback):
        self.rect = pygame.Rect(x, y, ancho, alto)
        self.texto = texto
        self.callback = callback
        self.hover = False

    def dibujar(self, superficie):
        color = COLOR_BOTON_HOVER if self.hover else COLOR_BOTON
        pygame.draw.rect(superficie, color, self.rect, border_radius=8)
        pygame.draw.rect(superficie, COLOR_CRISTAL, self.rect, 2, border_radius=8)

        texto_surf = fuente_ui.render(self.texto, True, COLOR_TEXTO)
        superficie.blit(texto_surf, texto_surf.get_rect(center=self.rect.center))

    def manejar_evento(self, evento):
        if evento.type == pygame.MOUSEMOTION:
            self.hover = self.rect.collidepoint(evento.pos)
        elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            if self.hover:
                self.callback()


class Dropdown:
    def __init__(self, x, y, ancho, alto, opciones, al_seleccionar):
        self.rect = pygame.Rect(x, y, ancho, alto)
        self.opciones = opciones
        self.al_seleccionar = al_seleccionar
        self.seleccionado = 0
        self.abierto = False

    def dibujar(self, superficie):
        # Caja principal
        pygame.draw.rect(superficie, COLOR_DROPDOWN_BG, self.rect, border_radius=6)
        pygame.draw.rect(superficie, COLOR_CRISTAL, self.rect, 2, border_radius=6)

        texto = fuente_ui.render(self.opciones[self.seleccionado][0] + " ▼", True, COLOR_TEXTO)
        superficie.blit(texto, (self.rect.x + 10, self.rect.y + 10))

        # Opciones desplegadas
        if self.abierto:
            for i, (nombre, _) in enumerate(self.opciones):
                rect_opc = pygame.Rect(self.rect.x, self.rect.y + (i + 1) * self.rect.height, self.rect.width,
                                       self.rect.height)
                color = COLOR_DROPDOWN_SEL if rect_opc.collidepoint(pygame.mouse.get_pos()) else COLOR_DROPDOWN_BG
                pygame.draw.rect(superficie, color, rect_opc)
                pygame.draw.rect(superficie, (80, 80, 80), rect_opc, 1)

                texto_opc = fuente_ui.render(nombre, True, COLOR_TEXTO)
                superficie.blit(texto_opc, (rect_opc.x + 10, rect_opc.y + 10))

    def manejar_evento(self, evento):
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            if self.rect.collidepoint(evento.pos):
                self.abierto = not self.abierto
                return True
            elif self.abierto:
                for i in range(len(self.opciones)):
                    rect_opc = pygame.Rect(self.rect.x, self.rect.y + (i + 1) * self.rect.height, self.rect.width,
                                           self.rect.height)
                    if rect_opc.collidepoint(evento.pos):
                        self.seleccionado = i
                        self.al_seleccionar(self.opciones[i][1])
                        self.abierto = False
                        return True
                self.abierto = False
        return False


# --- Lógica del Reloj de Arena ---
class RelojArena:
    def __init__(self):
        self.tiempo_total = OPCIONES_TIEMPO[0][1]
        self.tiempo_inicio = time.time()
        self.progreso = 0.0  # 0.0 a 1.0
        self.notificado = False

        # Geometría del reloj (centro: x=300)
        self.cx = 300
        self.tope_y = 100
        self.cuello_y = 310
        self.base_y = 520
        self.ancho_bombilla = 130
        self.ancho_cuello = 8

        # Polígonos de cristal
        self.poly_superior = [
            (self.cx - self.ancho_bombilla, self.tope_y),
            (self.cx + self.ancho_bombilla, self.tope_y),
            (self.cx + self.ancho_cuello, self.cuello_y),
            (self.cx - self.ancho_cuello, self.cuello_y)
        ]

        self.poly_inferior = [
            (self.cx - self.ancho_cuello, self.cuello_y),
            (self.cx + self.ancho_cuello, self.cuello_y),
            (self.cx + self.ancho_bombilla, self.base_y),
            (self.cx - self.ancho_bombilla, self.base_y)
        ]

    def reiniciar(self, nuevo_tiempo=None):
        if nuevo_tiempo:
            self.tiempo_total = nuevo_tiempo
        self.tiempo_inicio = time.time()
        self.progreso = 0.0
        self.notificado = False

    def actualizar(self):
        tiempo_transcurrido = time.time() - self.tiempo_inicio
        self.progreso = min(1.0, tiempo_transcurrido / self.tiempo_total)

        if self.progreso >= 1.0 and not self.notificado:
            self.notificado = True
            mostrar_notificacion("El reloj de arena ha completado su tiempo programado.")

    def dibujar(self, superficie):
        # 1. Arena Superior (se vacía hacia abajo)
        h_sup = (self.cuello_y - self.tope_y) * (1.0 - self.progreso)
        y_corte_sup = self.cuello_y - h_sup

        # Rectángulo de recorte para la arena superior
        clip_anterior = superficie.get_clip()
        superficie.set_clip(pygame.Rect(self.cx - self.ancho_bombilla, y_corte_sup, self.ancho_bombilla * 2, h_sup + 2))
        pygame.draw.polygon(superficie, COLOR_ARENA, self.poly_superior)
        superficie.set_clip(clip_anterior)

        # 2. Arena Inferior (se llena hacia arriba)
        h_inf = (self.base_y - self.cuello_y) * self.progreso
        y_corte_inf = self.base_y - h_inf

        # Rectángulo de recorte para la arena inferior
        superficie.set_clip(pygame.Rect(self.cx - self.ancho_bombilla, y_corte_inf, self.ancho_bombilla * 2, h_inf + 2))
        pygame.draw.polygon(superficie, COLOR_ARENA, self.poly_inferior)
        superficie.set_clip(clip_anterior)

        # 3. Chorro de arena cayendo
        if 0.0 < self.progreso < 1.0:
            pygame.draw.line(superficie, COLOR_ARENA_CAYENDO, (self.cx, self.cuello_y), (self.cx, self.base_y - 2), 4)

        # 4. Bordes de cristal y soporte
        pygame.draw.polygon(superficie, COLOR_CRISTAL, self.poly_superior, 4)
        pygame.draw.polygon(superficie, COLOR_CRISTAL, self.poly_inferior, 4)

        # Tapas de madera/soporte
        pygame.draw.rect(superficie, (110, 60, 30),
                         (self.cx - self.ancho_bombilla - 15, self.tope_y - 12, (self.ancho_bombilla + 15) * 2, 14),
                         border_radius=3)
        pygame.draw.rect(superficie, (110, 60, 30),
                         (self.cx - self.ancho_bombilla - 15, self.base_y, (self.ancho_bombilla + 15) * 2, 14),
                         border_radius=3)

        # 5. Texto de tiempo restante digital
        restante = max(0, int(self.tiempo_total - (time.time() - self.tiempo_inicio)))
        mins, segs = divmod(restante, 60)
        horas, mins = divmod(mins, 60)
        tiempo_str = f"{horas:02d}:{mins:02d}:{segs:02d}"

        txt_render = fuente_timer.render(tiempo_str, True, COLOR_TEXTO)
        superficie.blit(txt_render, txt_render.get_rect(center=(self.cx, self.base_y + 40)))


# --- Instancias y Bucle Principal ---
simulador = RelojArena()


def al_cambiar_tiempo(segundos):
    simulador.reiniciar(segundos)


dropdown = Dropdown(80, 620, 180, 42, OPCIONES_TIEMPO, al_cambiar_tiempo)
boton_reset = Boton(340, 620, 180, 42, "Poner a Cero", lambda: simulador.reiniciar())

ejecutando = True
while ejecutando:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            ejecutando = False

        # Eventos de UI (El dropdown tiene prioridad para capturar clics flotantes)
        bloqueado = dropdown.manejar_evento(evento)
        if not bloqueado and not dropdown.abierto:
            boton_reset.manejar_evento(evento)

    simulador.actualizar()

    # Dibujado
    pantalla.fill(COLOR_FONDO)

    simulador.dibujar(pantalla)
    boton_reset.dibujar(pantalla)
    dropdown.dibujar(pantalla)  # Se dibuja al final para superponerse a otros elementos

    pygame.display.flip()
    reloj.tick(60)

pygame.quit()
sys.exit()