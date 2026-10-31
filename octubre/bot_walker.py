import pygame
import random
from collections import deque

# ================= CONFIGURACIÓN Y CONSTANTES =================
SCREEN_WIDTH = 850
SCREEN_HEIGHT = 600
GRID_SIZE = 25  # 25x25 celdas
CELL_SIZE = 20  # 20x20 píxeles por celda
MAZE_SIZE = GRID_SIZE * CELL_SIZE  # 500x500 píxeles
OFFSET_X = 40
OFFSET_Y = 50

# Paleta de colores (Estilo Pixel / Retro)
COLOR_BG = (22, 22, 30)
COLOR_FLOOR = (35, 35, 50)
COLOR_WALL = (80, 80, 110)
COLOR_WALL_BORDER = (110, 110, 150)
COLOR_BOT = (50, 255, 120)
COLOR_BOT_EYE = (10, 50, 20)
COLOR_TARGET = (255, 90, 90)
COLOR_BTN = (60, 60, 90)
COLOR_BTN_HOVER = (90, 90, 130)
COLOR_TEXT = (240, 240, 250)


# ================= CLASE BOTÓN =================
class Button:
    def __init__(self, x, y, w, h, text):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.hovered = False

    def draw(self, surface, font):
        color = COLOR_BTN_HOVER if self.hovered else COLOR_BTN
        pygame.draw.rect(surface, color, self.rect, border_radius=6)
        pygame.draw.rect(surface, COLOR_TEXT, self.rect, 2, border_radius=6)

        txt_surf = font.render(self.text, True, COLOR_TEXT)
        txt_rect = txt_surf.get_rect(center=self.rect.center)
        surface.blit(txt_surf, txt_rect)

    def check_hover(self, mouse_pos):
        self.hovered = self.rect.collidepoint(mouse_pos)

    def is_clicked(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)


# ================= GENERACIÓN DE MAZMORRA =================
def generate_dungeon(size):
    """Crea una mazmorra con bordes y obstáculos distribuidos aleatoriamente."""
    grid = [[0 for _ in range(size)] for _ in range(size)]

    # 1. Bordes exteriores
    for i in range(size):
        grid[0][i] = 1
        grid[size - 1][i] = 1
        grid[i][0] = 1
        grid[i][size - 1] = 1

    # 2. Paredes internas (tipo bloques y pasillos)
    for y in range(2, size - 2, 2):
        for x in range(2, size - 2, 2):
            if random.random() < 0.65:
                grid[y][x] = 1
                # Crear ramas de obstáculos
                dirs = [(0, 1), (1, 0), (0, -1), (-1, 0)]
                dx, dy = random.choice(dirs)
                grid[y + dy][x + dx] = 1

    return grid


# ================= PATHFINDING (BFS) =================
def get_reachable_cells(grid, start):
    """Devuelve todas las celdas piso transitables conectadas al inicio."""
    queue = deque([start])
    visited = {start}
    reachable = []

    while queue:
        cx, cy = queue.popleft()
        reachable.append((cx, cy))
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            nx, ny = cx + dx, cy + dy
            if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE:
                if grid[ny][nx] == 0 and (nx, ny) not in visited:
                    visited.add((nx, ny))
                    queue.append((nx, ny))
    return reachable


def find_path(grid, start, goal):
    """Algoritmo BFS para encontrar la ruta más corta evitando obstáculos."""
    queue = deque([(start, [start])])
    visited = {start}

    while queue:
        (cx, cy), path = queue.popleft()
        if (cx, cy) == goal:
            return path

        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            nx, ny = cx + dx, cy + dy
            if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE:
                if grid[ny][nx] == 0 and (nx, ny) not in visited:
                    visited.add((nx, ny))
                    queue.append(((nx, ny), path + [(nx, ny)]))
    return []


# ================= CLASE BOT =================
class Bot:
    def __init__(self, x, y):
        self.grid_x = x
        self.grid_y = y
        self.pixel_x = OFFSET_X + x * CELL_SIZE
        self.pixel_y = OFFSET_Y + y * CELL_SIZE
        self.target_pixel_x = self.pixel_x
        self.target_pixel_y = self.pixel_y
        self.speed = 3  # Velocidad de movimiento en píxeles
        self.path = []
        self.current_goal = None

    def set_new_objective(self, grid):
        reachable = get_reachable_cells(grid, (self.grid_x, self.grid_y))
        if reachable:
            # Elegir un punto piso lejano para avanzar
            self.current_goal = random.choice(reachable)
            self.path = find_path(grid, (self.grid_x, self.grid_y), self.current_goal)
            if self.path and len(self.path) > 1:
                self.path.pop(0)  # Quitar celda actual

    def update(self, grid, running):
        if not running:
            return

        # Movimiento fluido hacia la siguiente celda en píxeles
        if self.pixel_x < self.target_pixel_x:
            self.pixel_x = min(self.pixel_x + self.speed, self.target_pixel_x)
        elif self.pixel_x > self.target_pixel_x:
            self.pixel_x = max(self.pixel_x - self.speed, self.target_pixel_x)

        if self.pixel_y < self.target_pixel_y:
            self.pixel_y = min(self.pixel_y + self.speed, self.target_pixel_y)
        elif self.pixel_y > self.target_pixel_y:
            self.pixel_y = max(self.pixel_y - self.speed, self.target_pixel_y)

        # Cuando llega a la celda objetivo del path
        if self.pixel_x == self.target_pixel_x and self.pixel_y == self.target_pixel_y:
            if self.path:
                next_cell = self.path.pop(0)
                self.grid_x, self.grid_y = next_cell
                self.target_pixel_x = OFFSET_X + self.grid_x * CELL_SIZE
                self.target_pixel_y = OFFSET_Y + self.grid_y * CELL_SIZE
            else:
                # Si llegó a su objetivo, buscar otro punto para seguir explorando
                self.set_new_objective(grid)

    def draw(self, surface):
        # Dibujar Bot (pequeño y verde)
        bot_rect = pygame.Rect(self.pixel_x + 3, self.pixel_y + 3, CELL_SIZE - 6, CELL_SIZE - 6)
        pygame.draw.rect(surface, COLOR_BOT, bot_rect, border_radius=3)

        # Ojos tipo pixel
        eye_size = 3
        pygame.draw.rect(surface, COLOR_BOT_EYE, (self.pixel_x + 6, self.pixel_y + 6, eye_size, eye_size))
        pygame.draw.rect(surface, COLOR_BOT_EYE, (self.pixel_x + 11, self.pixel_y + 6, eye_size, eye_size))


# ================= FUNCIÓN PRINCIPAL =================
def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Simulación de Bot en Mazmorra")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("consolas", 14, bold=True)
    title_font = pygame.font.SysFont("consolas", 18, bold=True)

    # Botones
    btn_toggle = Button(580, 100, 220, 45, "INICIAR")
    btn_regenerate = Button(580, 170, 220, 45, "REGENERAR MAPA")

    # Inicializar Mazmorra y Bot
    grid = generate_dungeon(GRID_SIZE)
    bot = Bot(1, 1)
    grid[1][1] = 0  # Asegurar punto de partida libre
    bot.set_new_objective(grid)

    is_running = False

    # Bucle Principal
    loop = True
    while loop:
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                loop = False

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Click en Iniciar / Detener
                if btn_toggle.is_clicked(mouse_pos):
                    is_running = not is_running
                    btn_toggle.text = "DETENER" if is_running else "INICIAR"

                # Click en Regenerar
                elif btn_regenerate.is_clicked(mouse_pos):
                    grid = generate_dungeon(GRID_SIZE)
                    # Colocar bot en un espacio libre
                    grid[1][1] = 0
                    bot = Bot(1, 1)
                    bot.set_new_objective(grid)

        # Actualizar estados de botones
        btn_toggle.check_hover(mouse_pos)
        btn_regenerate.check_hover(mouse_pos)

        # Actualizar física y pathfinding del bot
        bot.update(grid, is_running)

        # ================= RENDERIZADO =================
        screen.fill(COLOR_BG)

        # 1. Dibujar Cuadrícula de la Mazmorra
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                rect = pygame.Rect(OFFSET_X + c * CELL_SIZE, OFFSET_Y + r * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                if grid[r][c] == 1:
                    # Paredes (con textura pixelada interior)
                    pygame.draw.rect(screen, COLOR_WALL, rect)
                    pygame.draw.rect(screen, COLOR_WALL_BORDER, rect, 1)
                else:
                    # Suelo transitable
                    pygame.draw.rect(screen, COLOR_FLOOR, rect)
                    pygame.draw.rect(screen, (30, 30, 42), rect, 1)

        # 2. Dibujar Marcador del Objetivo actual del Bot
        if bot.current_goal:
            gx, gy = bot.current_goal
            target_rect = pygame.Rect(OFFSET_X + gx * CELL_SIZE + 6, OFFSET_Y + gy * CELL_SIZE + 6, 8, 8)
            pygame.draw.rect(screen, COLOR_TARGET, target_rect)

        # 3. Dibujar Bot
        bot.draw(screen)

        # 4. Dibujar Interfaz y Botones
        btn_toggle.draw(screen, font)
        btn_regenerate.draw(screen, font)

        # Textos informativos
        title = title_font.render("SIMULADOR MAZMORRA", True, COLOR_TEXT)
        screen.blit(title, (580, 50))

        status_text = f"Estado: {'AVANZANDO' if is_running else 'PAUSADO'}"
        status_surf = font.render(status_text, True, (100, 255, 100) if is_running else (255, 100, 100))
        screen.blit(status_surf, (580, 240))

        info1 = font.render("- Verde: Bot de navegación", True, (180, 180, 200))
        info2 = font.render("- Rojo: Punto destino", True, (180, 180, 200))
        info3 = font.render("- Gris: Muros intransitables", True, (180, 180, 200))
        screen.blit(info1, (580, 280))
        screen.blit(info2, (580, 305))
        screen.blit(info3, (580, 330))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()