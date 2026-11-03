import pygame
import sys
from math import cos, sin, pi, sqrt
from random import uniform

# ==========================================
# 1. CÁLCULO DE PUNTOS DE LA PARED (ORIGINAL)
# ==========================================
puntosa = []
for i in range(11):
    puntosa.append((i, 0))
    puntosa.append((i, -1))
    puntosa.append((i, +1))

puntosb = []
for i in range(11):
    coorda = (10, 0)
    coordb = (cos(2 * pi / 3), sin(2 * pi / 3))
    coordb = tuple(x * i for x in coordb)
    coordc = (cos(2 * pi / 3 + pi / 2), sin(2 * pi / 3 + pi / 2))
    
    scoorda = tuple(sum(x) for x in zip(coorda, coordb))
    scoordb = tuple(a + b for a, b in zip(scoorda, coordc))
    scoordc = tuple(a - b for a, b in zip(scoorda, coordc))
    
    puntosb.append(scoorda)
    puntosb.append(scoordb)
    puntosb.append(scoordc)

puntosc = []
for i in range(11):
    coorda = (5, 8.66)
    coordb = (cos(4 * pi / 3), sin(4 * pi / 3))
    coordb = tuple(x * i for x in coordb)
    coordc = (cos(4 * pi / 3 + pi / 2), sin(4 * pi / 3 + pi / 2))
    
    scoorda = tuple(sum(x) for x in zip(coorda, coordb))
    scoordb = tuple(a + b for a, b in zip(scoorda, coordc))
    scoordc = tuple(a - b for a, b in zip(scoorda, coordc))
    
    puntosc.append(scoorda)
    puntosc.append(scoordb)
    puntosc.append(scoordc)

puntos = puntosa + puntosb + puntosc

# ==========================================
# 2. CONFIGURACIÓN DE PYGAME
# ==========================================
pygame.init()
pygame.font.init()

ANCHO, ALTO = 800, 650
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Punto Atraviesa Pared - Pygame")

# Colores
BLANCO = (255, 255, 255)
NEGRO = (20, 20, 20)
ROJO = (220, 50, 50)
AZUL = (30, 144, 255)
VERDE = (46, 204, 113)
GRIS = (120, 120, 120)

# Fuentes
fuente_mensaje = pygame.font.SysFont("Arial", 24, bold=True)
fuente_info = pygame.font.SysFont("Arial", 16)

# Escala y traslación para transformar coordenadas matemáticas a píxeles
ESCALA = 42          # Píxeles por unidad matemática
ORIGEN_X = 180      # Desplazamiento horizontal
ORIGEN_Y = 520      # Desplazamiento vertical (Y crece hacia abajo en Pygame)

def a_pantalla(x, y):
    """Convierte coordenadas matemáticas (x, y) a coordenadas de píxeles."""
    px = int(ORIGEN_X + x * ESCALA)
    py = int(ORIGEN_Y - y * ESCALA)
    return px, py

# ==========================================
# 3. ESTADO INICIAL DEL PUNTO AZUL
# ==========================================
# Coordenadas matemáticas iniciales
pos_x = uniform(2, 8)
pos_y = uniform(2, 6)
velocidad = 5.0  # Unidades matemáticas por segundo

reloj = pygame.time.Clock()

# ==========================================
# 4. BUCLE PRINCIPAL
# ==========================================
ejecutando = True
while ejecutando:
    dt = reloj.tick(60) / 1000.0  # Tiempo transcurrido en segundos por cuadro

    # Eventos
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            ejecutando = False

    # Controles por teclado (Flechas)
    teclas = pygame.key.get_pressed()
    if teclas[pygame.K_LEFT]:
        pos_x -= velocidad * dt
    if teclas[pygame.K_RIGHT]:
        pos_x += velocidad * dt
    if teclas[pygame.K_UP]:
        pos_y += velocidad * dt
    if teclas[pygame.K_DOWN]:
        pos_y -= velocidad * dt

    # Detección de colisión (distancia < 1 con cualquier punto de la pared)
    hay_choque = False
    for p in puntos:
        dx = p[0] - pos_x
        dy = p[1] - pos_y
        distancia = sqrt(dx**2 + dy**2)
        if distancia < 1.0:
            hay_choque = True
            break

    # ==========================================
    # 5. DIBUJADO EN PANTALLA
    # ==========================================
    pantalla.fill(BLANCO)

    # Dibujar puntos rojos de la pared
    for p in puntos:
        cx, cy = a_pantalla(p[0], p[1])
        pygame.draw.circle(pantalla, ROJO, (cx, cy), 6)

    # Dibujar punto azul (controlado por el usuario)
    bx, by = a_pantalla(pos_x, pos_y)
    pygame.draw.circle(pantalla, AZUL, (bx, by), 8)

    # Mensaje de estado (en la parte superior)
    if hay_choque:
        texto_estado = "¡Punto choca con pared dura!"
        color_texto = ROJO
    else:
        texto_estado = "Punto atraviesa pared (libre)"
        color_texto = VERDE

    superficie_mensaje = fuente_mensaje.render(texto_estado, True, color_texto)
    pantalla.blit(superficie_mensaje, (20, 20))

    # Información de controles y coordenadas
    texto_ayuda = fuente_info.render("Usa las FLECHAS del teclado para mover el punto azul", True, NEGRO)
    texto_coords = fuente_info.render(f"Posición matemática: X={pos_x:.2f}, Y={pos_y:.2f}", True, GRIS)
    
    pantalla.blit(texto_ayuda, (20, 55))
    pantalla.blit(texto_coords, (20, 75))

    pygame.display.flip()

pygame.quit()
sys.exit()