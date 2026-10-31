import pygame
import math
import random
import sys

# Inicialización
pygame.init()
pygame.font.init()

WIDTH, HEIGHT = 500, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Lámpara de Lava - Simulación Realista")
clock = pygame.time.Clock()
FONT = pygame.font.SysHYPERLINK if hasattr(pygame.font, "SysHYPERLINK") else pygame.font.SysFont("Arial", 14, bold=True)
TITLE_FONT = pygame.font.SysFont("Arial", 11, bold=True)

# Paletas de color: (Color base, Núcleo brillante, Resplandor suave)
COLOR_PALETTES = {
    "Rojo Lava": {
        "base": (230, 35, 45),
        "core": (255, 200, 160),
        "glow": (255, 40, 20, 45)
    },
    "Verde Alien": {
        "base": (40, 230, 70),
        "core": (210, 255, 180),
        "glow": (30, 255, 60, 45)
    },
    "Azul Neón": {
        "base": (0, 170, 255),
        "core": (190, 240, 255),
        "glow": (0, 150, 255, 45)
    },
    "Púrpura Mágico": {
        "base": (195, 30, 245),
        "core": (245, 195, 255),
        "glow": (180, 20, 240, 45)
    },
    "Ámbar / Fuego": {
        "base": (255, 130, 0),
        "core": (255, 230, 140),
        "glow": (255, 120, 0, 45)
    }
}

# --- Geometría de la Lámpara ---
LAMP_X = 140
LAMP_Y = 120
LAMP_W = 220
LAMP_H = 460
LAMP_RECT = pygame.Rect(LAMP_X, LAMP_Y, LAMP_W, LAMP_H)


class LavaBlob:
    """Gotas con termodinámica, deformación elástica y oscilación."""

    def __init__(self):
        self.radius = random.randint(24, 46)
        self.x = random.uniform(LAMP_X + self.radius + 15, LAMP_X + LAMP_W - self.radius - 15)
        self.y = random.uniform(LAMP_Y + 50, LAMP_Y + LAMP_H - 50)
        self.temp = random.uniform(0.0, 1.0)  # 1.0 = caliente (sube), 0.0 = frío (baja)
        self.vy = 0
        self.vx = 0
        self.phase = random.uniform(0, math.pi * 2)

    def update(self):
        # La temperatura cambia según la cercanía a la base (fuente de calor) o al tope
        depth = (self.y - LAMP_Y) / LAMP_H  # 0 arriba, 1 abajo
        if depth > 0.75:
            self.temp = min(1.0, self.temp + 0.006)  # Calentamiento
        elif depth < 0.25:
            self.temp = max(0.0, self.temp - 0.005)  # Enfriamiento

        # Flotabilidad: caliente sube, frío baja
        target_vy = -2.2 if self.temp > 0.5 else 1.8
        self.vy += (target_vy - self.vy) * 0.04

        # Oscilación horizontal orgánica
        self.phase += 0.03
        self.vx = math.sin(self.phase) * 0.6

        self.y += self.vy
        self.x += self.vx

        # Confinamiento dentro del cristal
        margin = self.radius + 12
        if self.x < LAMP_X + margin:
            self.x = LAMP_X + margin
            self.phase += math.pi
        elif self.x > LAMP_X + LAMP_W - margin:
            self.x = LAMP_X + LAMP_W - margin
            self.phase += math.pi

        top_limit = LAMP_Y + margin - 5
        bot_limit = LAMP_Y + LAMP_H - margin + 5
        if self.y < top_limit:
            self.y = top_limit
            self.temp = 0.0  # Se enfría al chocar arriba
        elif self.y > bot_limit:
            self.y = bot_limit
            self.temp = 1.0  # Se calienta abajo


class Dropdown:
    """Menú desplegable estilizado para Pygame."""

    def __init__(self, x, y, w, h, options):
        self.rect = pygame.Rect(x, y, w, h)
        self.options = options
        self.selected_index = 0
        self.is_open = False

    def draw(self, surface):
        # Botón principal
        pygame.draw.rect(surface, (35, 35, 45), self.rect, border_radius=6)
        pygame.draw.rect(surface, (70, 70, 90), self.rect, 1, border_radius=6)

        txt = FONT.render(self.options[self.selected_index], True, (240, 240, 240))
        surface.blit(txt, (self.rect.x + 10, self.rect.y + 7))

        arrow = "▲" if self.is_open else "▼"
        arrow_txt = TITLE_FONT.render(arrow, True, (170, 170, 190))
        surface.blit(arrow_txt, (self.rect.right - 18, self.rect.y + 8))

        # Lista expandida
        if self.is_open:
            for i, opt in enumerate(self.options):
                opt_rect = pygame.Rect(self.rect.x, self.rect.bottom + i * self.rect.h, self.rect.w, self.rect.h)
                bg_col = (45, 45, 60) if opt_rect.collidepoint(pygame.mouse.get_pos()) else (28, 28, 38)
                pygame.draw.rect(surface, bg_col, opt_rect)
                pygame.draw.rect(surface, (60, 60, 80), opt_rect, 1)
                t = FONT.render(opt, True, (220, 220, 230))
                surface.blit(t, (opt_rect.x + 10, opt_rect.y + 7))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.is_open = not self.is_open
                return None

            if self.is_open:
                for i in range(len(self.options)):
                    opt_rect = pygame.Rect(self.rect.x, self.rect.bottom + i * self.rect.h, self.rect.w, self.rect.h)
                    if opt_rect.collidepoint(event.pos):
                        self.selected_index = i
                        self.is_open = False
                        return self.options[i]
                self.is_open = False
        return None

    def get_selected(self):
        return self.options[self.selected_index]


def draw_lamp_hardware(surface):
    """Dibuja la base y la tapa metálica con sombreado degradado."""
    # Tapa superior
    cap_points = [
        (LAMP_X + 25, LAMP_Y),
        (LAMP_X + LAMP_W - 25, LAMP_Y),
        (LAMP_X + LAMP_W - 40, LAMP_Y - 45),
        (LAMP_X + 40, LAMP_Y - 45)
    ]
    pygame.draw.polygon(surface, (90, 92, 105), cap_points)
    pygame.draw.polygon(surface, (130, 134, 150), cap_points, 2)

    # Base inferior
    base_points = [
        (LAMP_X + 15, LAMP_Y + LAMP_H),
        (LAMP_X + LAMP_W - 15, LAMP_Y + LAMP_H),
        (LAMP_X + LAMP_W + 20, LAMP_Y + LAMP_H + 55),
        (LAMP_X - 20, LAMP_Y + LAMP_H + 55)
    ]
    pygame.draw.polygon(surface, (80, 82, 95), base_points)
    pygame.draw.polygon(surface, (120, 124, 140), base_points, 2)


def render_viscous_fluid(surface, blobs, palette):
    """Renderiza gotas estiradas, resplandores y uniones viscosas entre ellas."""
    glow_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    base_color = palette["base"]
    core_color = palette["core"]
    glow_color = palette["glow"]

    # 1. Conexiones viscosas (ligamentos elásticos entre gotas cercanas)
    for i in range(len(blobs)):
        for j in range(i + 1, len(blobs)):
            b1, b2 = blobs[i], blobs[j]
            dx = b2.x - b1.x
            dy = b2.y - b1.y
            dist = math.hypot(dx, dy)
            connect_range = (b1.radius + b2.radius) * 1.35

            if dist < connect_range and dist > 0:
                width = int((1.0 - dist / connect_range) * min(b1.radius, b2.radius) * 1.2)
                if width > 3:
                    pygame.draw.line(surface, base_color, (b1.x, b1.y), (b2.x, b2.y), width)
                    pygame.draw.line(glow_surf, glow_color, (b1.x, b1.y), (b2.x, b2.y), width + 18)

    # 2. Gotas individuales con estiramiento elástico
    for b in blobs:
        # Deformación según velocidad vertical (efecto squash & stretch)
        stretch = max(-0.25, min(0.35, abs(b.vy) * 0.12))
        rx = int(b.radius * (1.0 - stretch * 0.5))
        ry = int(b.radius * (1.0 + stretch))

        rect_blob = pygame.Rect(b.x - rx, b.y - ry, rx * 2, ry * 2)

        # Capa de Aura/Resplandor (Glow)
        glow_rx, glow_ry = rx + 18, ry + 18
        glow_rect = pygame.Rect(b.x - glow_rx, b.y - glow_ry, glow_rx * 2, glow_ry * 2)
        pygame.draw.ellipse(glow_surf, glow_color, glow_rect)

        # Capa de Cuerpo Principal
        pygame.draw.ellipse(surface, base_color, rect_blob)

        # Capa de Núcleo Luminoso (centro caliente)
        core_rx = int(rx * 0.55)
        core_ry = int(ry * 0.55)
        core_rect = pygame.Rect(b.x - core_rx, b.y - core_ry + (1 if b.vy > 0 else -1), core_rx * 2, core_ry * 2)
        pygame.draw.ellipse(surface, core_color, core_rect)

    # Combinar el resplandor con la pantalla
    surface.blit(glow_surf, (0, 0))


def main():
    blobs = [LavaBlob() for _ in range(9)]
    is_running = True

    # Interfaz
    btn_rect = pygame.Rect(30, 35, 120, 36)
    dropdown = Dropdown(260, 35, 180, 36, list(COLOR_PALETTES.keys()))
    current_palette = COLOR_PALETTES[dropdown.get_selected()]

    while True:
        # Eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Eventos del menú desplegable
            new_color = dropdown.handle_event(event)
            if new_color:
                current_palette = COLOR_PALETTES[new_color]

            # Botón Iniciar/Pausar
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if btn_rect.collidepoint(event.pos) and not dropdown.is_open:
                    is_running = not is_running

        # Actualizar física
        if is_running:
            for b in blobs:
                b.update()

        # --- DIBUJADO ---
        screen.fill((16, 17, 24))  # Fondo oscuro de habitación

        # 1. Cristal de la lámpara (Fondo interno oscuro/líquido)
        pygame.draw.rect(screen, (10, 10, 18), LAMP_RECT, border_radius=16)

        # 2. Resplandor difuso ambiental dentro del cristal
        ambient_surf = pygame.Surface((LAMP_W, LAMP_H), pygame.SRCALPHA)
        col_with_alpha = (*current_palette["base"][:3], 18)
        pygame.draw.rect(ambient_surf, col_with_alpha, (0, 0, LAMP_W, LAMP_H), border_radius=16)
        screen.blit(ambient_surf, (LAMP_X, LAMP_Y))

        # 3. Gotas de lava (con clip para no salirse del tubo de vidrio)
        screen.set_clip(LAMP_RECT)
        render_viscous_fluid(screen, blobs, current_palette)
        screen.set_clip(None)

        # 4. Reflejo del cristal y borde 3D
        pygame.draw.rect(screen, (60, 65, 85), LAMP_RECT, 3, border_radius=16)
        reflection_surf = pygame.Surface((18, LAMP_H - 30), pygame.SRCALPHA)
        reflection_surf.fill((255, 255, 255, 22))
        screen.blit(reflection_surf, (LAMP_X + 16, LAMP_Y + 15))

        # 5. Base y Tapa metálicas
        draw_lamp_hardware(screen)

        # 6. Barra superior de Controles
        # Botón Play/Pausa
        btn_col = (180, 40, 50) if is_running else (35, 140, 65)
        btn_hover = btn_rect.collidepoint(pygame.mouse.get_pos())
        if btn_hover and not dropdown.is_open:
            btn_col = tuple(min(255, c + 25) for c in btn_col)

        pygame.draw.rect(screen, btn_col, btn_rect, border_radius=6)
        btn_text = FONT.render("PAUSAR" if is_running else "INICIAR", True, (255, 255, 255))
        screen.blit(btn_text, btn_text.get_rect(center=btn_rect.center))

        # Menú desplegable (se dibuja al final para quedar sobre todo)
        dropdown.draw(screen)

        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()