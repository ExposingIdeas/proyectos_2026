import pygame
import sys
from math import cos, sin, pi, sqrt
from random import uniform

# ==========================================
# 1. CÁLCULO DE PUNTOS ORIGINALES DE LA PARED
# ==========================================
puntosa = []
for i in range(11):
    puntosa.append([float(i), 0.0])
    puntosa.append([float(i), -1.0])
    puntosa.append([float(i), 1.0])

puntosb = []
for i in range(11):
    coorda = (10, 0)
    coordb = (cos(2 * pi / 3) * i, sin(2 * pi / 3) * i)
    coordc = (cos(2 * pi / 3 + pi / 2), sin(2 * pi / 3 + pi / 2))
    
    scoorda = [coorda[0] + coordb[0], coorda[1] + coordb[1]]
    scoordb = [scoorda[0] + coordc[0], scoorda[1] + coordc[1]]
    scoordc = [scoorda[0] - coordc[0], scoorda[1] - coordc[1]]
    
    puntosb.extend([scoorda, scoordb, scoordc])

puntosc = []
for i in range(11):
    coorda = (5, 8.66)
    coordb = (cos(4 * pi / 3) * i, sin(4 * pi / 3) * i)
    coordc = (cos(4 * pi / 3 + pi / 2), sin(4 * pi / 3 + pi / 2))
    
    scoorda = [coorda[0] + coordb[0], coorda[1] + coordb[1]]
    scoordb = [scoorda[0] + coordc[0], scoorda[1] + coordc[1]]
    scoordc = [scoorda[0] - coordc[0], scoorda[1] - coordc[1]]
    
    puntosc.extend([scoorda, scoordb, scoordc])

# Posiciones fijas de base y posiciones editables actuales
puntos_base = [list(p) for p in (puntosa + puntosb + puntosc)]
puntos = [list(p) for p in puntos_base]

# ==========================================
# 2. CONFIGURACIÓN DE PYGAME
# ==========================================
pygame.init()
pygame.font.init()

ANCHO, ALTO = 800, 650
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Punto Atraviesa Pared - Modo Elástico")

# Colores
BLANCO = (255, 255, 255)
NEGRO = (20, 20, 20)
ROJO = (220, 50, 50)
NARANJA = (255, 140, 0)
AZUL = (30, 144, 255)
VERDE = (46, 204, 113)
GRIS = (120, 120, 120)

fuente_info = pygame.font.SysFont("Arial", 16)
fuente_estado = pygame.font.SysFont("Arial", 18, bold=True)

# Escala matemática -> píxeles
ESCALA = 42
ORIGEN_X = 180
ORIGEN_Y = 520

def a_pantalla(x, y):
    return int(ORIGEN_X + x * ESCALA), int(ORIGEN_Y - y * ESCALA)

# Estado del punto azul
pos_x = uniform(2, 8)
pos_y = uniform(2, 6)
velocidad = 5.0

# Variable de autorestauración (elástico)
modo_elastico = True
VELOCIDAD_RECUPERACION = 6.0

reloj = pygame.time.Clock()

# ==========================================
# 3. BUCLE PRINCIPAL
# ==========================================
ejecutando = True
while ejecutando:
    dt = reloj.tick(60) / 1000.0
    dt = min(dt, 0.1)

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            ejecutando = False
        elif evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_e:
                modo_elastico = not modo_elastico
            elif evento.key == pygame.K_r:
                puntos = [list(p) for p in puntos_base]

    # Movimiento con flechas del teclado
    teclas = pygame.key.get_pressed()
    if teclas[pygame.K_LEFT]:
        pos_x -= velocidad * dt
    if teclas[pygame.K_RIGHT]:
        pos_x += velocidad * dt
    if teclas[pygame.K_UP]:
        pos_y += velocidad * dt
    if teclas[pygame.K_DOWN]:
        pos_y -= velocidad * dt

    # Retorno elástico si el modo está activo
    if modo_elastico:
        for p, base in zip(puntos, puntos_base):
            p[0] += (base[0] - p[0]) * VELOCIDAD_RECUPERACION * dt
            p[1] += (base[1] - p[1]) * VELOCIDAD_RECUPERACION * dt

    # Alejar puntos rojos si están a distancia < 1.0
    puntos_afectados = set()
    for idx, p in enumerate(puntos):
        dx = p[0] - pos_x
        dy = p[1] - pos_y
        distancia = sqrt(dx**2 + dy**2)

        if distancia < 1.0:
            puntos_afectados.add(idx)

            if distancia > 0.0001:
                ux = dx / distancia
                uy = dy / distancia
            else:
                ux, uy = 1.0, 0.0

            p[0] += ux * 0.5
            p[1] += uy * 0.5

    # ==========================================
    # 4. RENDERIZADO
    # ==========================================
    pantalla.fill(BLANCO)

    # Dibujar puntos rojos (naranja mientras interactúan)
    for idx, p in enumerate(puntos):
        cx, cy = a_pantalla(p[0], p[1])
        color_punto = NARANJA if idx in puntos_afectados else ROJO
        radio = 8 if idx in puntos_afectados else 6
        pygame.draw.circle(pantalla, color_punto, (cx, cy), radio)

    # Dibujar punto azul
    bx, by = a_pantalla(pos_x, pos_y)
    pygame.draw.circle(pantalla, AZUL, (bx, by), 8)

    # Indicador del modo elástico
    estado_elastico = "ACTIVADO (Elástico)" if modo_elastico else "DESACTIVADO (Plástico)"
    color_elastico = VERDE if modo_elastico else ROJO
    texto_modo = fuente_estado.render(f"Autorestaurar [Tecla E]: {estado_elastico}", True, color_elastico)
    pantalla.blit(texto_modo, (20, 20))

    # Información de controles y posición
    ayuda = fuente_info.render("Flechas: Moverse  |  'E': Alternar Elástico  |  'R': Reiniciar", True, NEGRO)
    coords = fuente_info.render(f"Posición Azul: X={pos_x:.2f}, Y={pos_y:.2f}", True, GRIS)

    pantalla.blit(ayuda, (20, 48))
    pantalla.blit(coords, (20, 70))

    pygame.display.flip()

pygame.quit()
sys.exit()