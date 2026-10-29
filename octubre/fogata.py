import pygame
import random
import sys

# Inicialización
pygame.init()
pygame.font.init()

# Dimensiones de la ventana (Alta resolución)
VENTANA_ANCHO = 800
VENTANA_ALTO = 600

# Dimensiones internas (Pixel Art) -> Relación 4:3
CANVAS_ANCHO = 200
CANVAS_ALTO = 150
ESCALA = VENTANA_ANCHO // CANVAS_ANCHO

pantalla = pygame.display.set_mode((VENTANA_ANCHO, VENTANA_ALTO))
pygame.display.set_caption("Simulador de Fogata Pixel Art")
reloj = pygame.time.Clock()

# Lienzo de baja resolución
lienzo_pixel = pygame.Surface((CANVAS_ANCHO, CANVAS_ALTO))

# Colores del fuego según su vida
COLORES_FUEGO = [
    (255, 255, 220), # Núcleo blanco/amarillo brillante
    (255, 210, 60),  # Amarillo
    (255, 120, 20),  # Naranja
    (210, 40, 20),   # Rojo
    (90, 30, 30),    # Rojo oscuro / brasa
    (40, 35, 40)     # Humo gris
]

class ParticulaFuego:
    def __init__(self, x, y):
        self.x = x + random.uniform(-6, 6)
        self.y = y + random.uniform(-2, 2)
        self.vx = random.uniform(-0.35, 0.35)
        self.vy = random.uniform(-1.4, -0.6)
        self.vida = 1.0  # 1.0 = recién nacida, 0.0 = desaparece
        self.velocidad_decaimiento = random.uniform(0.015, 0.035)
        self.tamano_inicial = random.randint(3, 5)

    def actualizar(self):
        self.x += self.vx
        self.y += self.vy
        self.vida -= self.velocidad_decaimiento

    def dibujar(self, superficie):
        if self.vida > 0:
            # Calcular tamaño decreciente
            tam = max(1, int(self.tamano_inicial * self.vida))
            
            # Elegir color según la vida restante
            idx = int((1.0 - self.vida) * (len(COLORES_FUEGO) - 1))
            color = COLORES_FUEGO[min(idx, len(COLORES_FUEGO) - 1)]
            
            # Dibujar píxel cuadrado
            pygame.draw.rect(superficie, color, (int(self.x - tam / 2), int(self.y - tam / 2), tam, tam))

class Chispa:
    def __init__(self, x, y):
        self.x = x + random.uniform(-8, 8)
        self.y = y
        self.vx = random.uniform(-0.6, 0.6)
        self.vy = random.uniform(-1.8, -1.0)
        self.vida = random.randint(20, 45)

    def actualizar(self):
        self.x += self.vx + random.uniform(-0.1, 0.1)
        self.y += self.vy
        self.vida -= 1

    def dibujar(self, superficie):
        if self.vida > 0:
            color = (255, random.randint(180, 240), 50)
            superficie.set_at((int(self.x), int(self.y)), color)

def dibujar_madera_y_piedras(surf, cx, cy):
    # Piedras alrededor
    piedras = [(-14, 2), (-10, 4), (-4, 5), (4, 5), (10, 4), (14, 2), (0, 6)]
    for px, py in piedras:
        pygame.draw.circle(surf, (60, 60, 70), (cx + px, cy + py), 3)
        surf.set_at((cx + px - 1, cy + py - 1), (90, 90, 105)) # Brillo piedra

    # Troncos cruzados
    # Tronco 1
    pygame.draw.line(surf, (80, 45, 20), (cx - 12, cy + 2), (cx + 12, cy - 3), 3)
    # Tronco 2
    pygame.draw.line(surf, (100, 55, 25), (cx - 10, cy - 3), (cx + 10, cy + 2), 3)
    # Carbón en el centro
    pygame.draw.rect(surf, (30, 20, 20), (cx - 5, cy - 2, 10, 4))

def main():
    particulas = []
    chispas = []
    encendido = True
    
    # Coordenadas de la fogata en el lienzo pixel
    fuego_x = CANVAS_ANCHO // 2
    fuego_y = CANVAS_ALTO // 2 + 30

    # Configuración del botón (definido en coordenadas de ventana para nitidez del texto)
    boton_rect = pygame.Rect(VENTANA_ANCHO // 2 - 80, VENTANA_ALTO - 70, 160, 45)
    fuente = pygame.font.SysFont("Arial", 18, bold=True)

    corriendo = True
    while corriendo:
        reloj.tick(60)

        # --- EVENTOS ---
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                corriendo = False
            elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                if boton_rect.collidepoint(evento.pos):
                    encendido = not encendido

        # --- GENERACIÓN DE PARTÍCULAS ---
        if encendido:
            # Generar partículas de llama
            for _ in range(4):
                particulas.append(ParticulaFuego(fuego_x, fuego_y))
            # Generar chispas ocasionales
            if random.random() < 0.25:
                chispas.append(Chispa(fuego_x, fuego_y - 2))

        # --- ACTUALIZACIÓN ---
        for p in particulas[:]:
            p.actualizar()
            if p.vida <= 0:
                particulas.remove(p)

        for c in chispas[:]:
            c.actualizar()
            if c.vida <= 0:
                chispas.remove(c)

        # --- RENDERIZADO EN LIENZO PIXEL (200x150) ---
        lienzo_pixel.fill((12, 12, 20)) # Cielo nocturno

        # Suelo oscuro
        pygame.draw.rect(lienzo_pixel, (18, 18, 26), (0, fuego_y + 4, CANVAS_ANCHO, CANVAS_ALTO - fuego_y))

        # Resplandor cálido en el suelo si hay fuego
        if len(particulas) > 10:
            resplandor = pygame.Surface((80, 40), pygame.SRCALPHA)
            alpha_glow = min(50, len(particulas) * 2)
            pygame.draw.ellipse(resplandor, (255, 100, 20, alpha_glow), (0, 0, 80, 40))
            lienzo_pixel.blit(resplandor, (fuego_x - 40, fuego_y - 12))

        # Dibujar fogata base (leña y piedras)
        dibujar_madera_y_piedras(lienzo_pixel, fuego_x, fuego_y)

        # Brasas ardientes si está encendido
        if encendido or len(particulas) > 5:
            color_brasa = (255, random.randint(60, 120), 0)
            lienzo_pixel.set_at((fuego_x + random.randint(-4, 4), fuego_y + random.randint(-2, 1)), color_brasa)

        # Dibujar partículas y chispas
        for p in particulas:
            p.dibujar(lienzo_pixel)
        for c in chispas:
            c.dibujar(lienzo_pixel)

        # --- ESCALADO A ALTA DEFINICIÓN ---
        # Escala sin suavizado (mantiene los bordes de los píxeles afilados y perfectos)
        superficie_escalada = pygame.transform.scale(lienzo_pixel, (VENTANA_ANCHO, VENTANA_ALTO))
        pantalla.blit(superficie_escalada, (0, 0))

        # --- INTERFAZ DE USUARIO (DIBUJADA EN ALTA DEFINICIÓN) ---
        # Botón estilo moderno
        color_btn = (200, 50, 50) if encendido else (40, 160, 60)
        color_borde = (255, 100, 100) if encendido else (80, 220, 100)
        
        # Efecto hover
        if boton_rect.collidepoint(pygame.mouse.get_pos()):
            color_btn = tuple(min(c + 25, 255) for c in color_btn)

        pygame.draw.rect(pantalla, color_btn, boton_rect, border_radius=8)
        pygame.draw.rect(pantalla, color_borde, boton_rect, width=2, border_radius=8)

        texto_str = "APAGAR" if encendido else "ENCENDER"
        texto = fuente.render(texto_str, True, (255, 255, 255))
        pantalla.blit(texto, texto.get_rect(center=boton_rect.center))

        # Actualizar pantalla
        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()