import os
import sys
import random
import math

# --- CONTROL DE TECLADO MULTIPLATAFORMA (CON FLECHAS) ---
try:
    import msvcrt
    def get_key():
        ch = msvcrt.getch()
        if ch in (b'\x00', b'\xe0'):
            # Teclas especiales en Windows (Flechas)
            code = msvcrt.getch()
            arrows = {b'H': 'up', b'P': 'down', b'K': 'left', b'M': 'right'}
            return arrows.get(code, '')
        return ch.decode('latin1', errors='ignore').lower()
except ImportError:
    import tty, termios
    def get_key():
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
            if ch == '\x1b':
                # Teclas especiales en Linux/Mac (Secuencias ANSI para flechas)
                ch2 = sys.stdin.read(1)
                if ch2 == '[':
                    ch3 = sys.stdin.read(1)
                    arrows = {'A': 'up', 'B': 'down', 'D': 'left', 'C': 'right'}
                    return arrows.get(ch3, '')
        finally:
            termios.tcsetattr(fd, old_settings)
        return ch.lower()

# --- DEFINICIÓN DE CLASES ---
CLASSES = {
    'Constructor': {'emoji': '👷', 'hp': 100, 'def': 3, 'atk': 12, 'desc': 'Espacio: Construir/Picar bloque'},
    'Tirador':     {'emoji': '🏹', 'hp': 85,  'def': 2, 'atk': 18, 'desc': 'Espacio: Disparo a distancia'},
    'Portalero':   {'emoji': '🌀', 'hp': 90,  'def': 2, 'atk': 14, 'desc': 'Espacio: Crear portal a otra mazmorra'},
    'Tanque':      {'emoji': '🛡️', 'hp': 160, 'def': 8, 'atk': 10, 'desc': 'Espacio: Onda de choque defensiva'},
    'Espadachin':  {'emoji': '⚔️', 'hp': 110, 'def': 4, 'atk': 22, 'desc': 'Espacio: Tajo giratorio 360°'},
    'Mago':        {'emoji': '🧙', 'hp': 75,  'def': 1, 'atk': 28, 'desc': 'Espacio: Bola de fuego a distancia'},
    'Soporte':     {'emoji': '💚', 'hp': 95,  'def': 3, 'atk': 10, 'desc': 'Espacio: Curación mayor instantánea'},
    # --- INSERTAR AQUÍ ---
    'Corredor':    {'emoji': '👟', 'hp': 90,  'def': 2, 'atk': 14, 'desc': 'Pasiva: Avanza 2 casillas al moverte | Espacio: Patada sprint'}
}
CLASS_KEYS = list(CLASSES.keys())

MAP_W, MAP_H = 30, 15

class Entity:
    def __init__(self, x, y, class_name, is_player=False, is_friendly=True):
        self.x = x
        self.y = y
        self.class_name = class_name
        self.is_player = is_player
        self.is_friendly = is_friendly
        
        info = CLASSES[class_name]
        self.emoji = info['emoji']
        scale = 1.0 if is_player else 0.55  # Los mobs son versiones más débiles
        self.max_hp = int(info['hp'] * scale)
        self.hp = self.max_hp
        self.defense = int(info['def'] * scale)
        self.atk = int(info['atk'] * scale)

class Game:
    def __init__(self):
        self.dungeon_level = 1
        self.class_idx = 0
        self.player_class = CLASS_KEYS[self.class_idx]
        self.player = Entity(0, 0, self.player_class, is_player=True)
        self.facing = (0, 1)  # Dirección a la que mira el jugador (dx, dy)
        self.logs = ["¡Bienvenido a la mazmorra! Presiona [C] para cambiar de clase."]
        self.portal_pos = None
        self.init_dungeon()

    def add_log(self, msg):
        self.logs.append(msg)
        if len(self.logs) > 4:
            self.logs.pop(0)

    def init_dungeon(self):
        # Generar mapa con bordes y pilares aleatorios
        self.grid = [['▪️ ' for _ in range(MAP_W)] for _ in range(MAP_H)]
        for x in range(MAP_W):
            self.grid[0][x] = '🧱'
            self.grid[MAP_H - 1][x] = '🧱'
        for y in range(MAP_H):
            self.grid[y][0] = '🧱'
            self.grid[y][MAP_W - 1] = '🧱'

        # Obstáculos interiores
        for _ in range(int(MAP_W * MAP_H * 0.12)):
            rx, ry = random.randint(1, MAP_W - 2), random.randint(1, MAP_H - 2)
            self.grid[ry][rx] = '🧱'

        # Ubicar jugador
        self.player.x, self.player.y = 2, 2
        self.grid[2][2] = '▪️ '

        # Generar mobs (50% amigos, 50% enemigos)
        self.mobs = []
        num_mobs = random.randint(5, 8)
        for _ in range(num_mobs):
            mx, my = random.randint(2, MAP_W - 3), random.randint(2, MAP_H - 3)
            if self.grid[my][mx] == '▪️ ' and (mx, my) != (self.player.x, self.player.y):
                mob_class = random.choice(CLASS_KEYS)
                is_friendly = random.random() < 0.50
                mob = Entity(mx, my, mob_class, is_player=False, is_friendly=is_friendly)
                self.mobs.append(mob)
        self.portal_pos = None

    def switch_player_class(self):
        prev_pct = self.player.hp / self.player.max_hp
        self.class_idx = (self.class_idx + 1) % len(CLASS_KEYS)
        self.player_class = CLASS_KEYS[self.class_idx]
        
        info = CLASSES[self.player_class]
        self.player.class_name = self.player_class
        self.player.emoji = info['emoji']
        self.player.max_hp = info['hp']
        self.player.hp = max(1, int(self.player.max_hp * prev_pct))
        self.player.defense = info['def']
        self.player.atk = info['atk']
        self.add_log(f"Cambiaste a clase: {self.player.emoji} {self.player_class}!")

    def get_mob_at(self, x, y):
        for m in self.mobs:
            if m.x == x and m.y == y:
                return m
        return None

    def attack(self, attacker, defender):
        dmg = max(1, attacker.atk - defender.defense)
        defender.hp -= dmg
        if defender.is_player:
            self.add_log(f"¡{attacker.emoji} te infligió {dmg} de daño!")
        else:
            tag = "Amigo" if defender.is_friendly else "Enemigo"
            self.add_log(f"Atacas a {defender.emoji} ({tag}) por {dmg} de daño.")
            if defender.is_friendly:
                defender.is_friendly = False
                self.add_log(f"¡El {defender.emoji} se ha vuelto HOSTIL!")

        if defender.hp <= 0:
            if defender.is_player:
                self.add_log("💀 ¡HAS MUERTO!")
            else:
                self.add_log(f"¡{defender.emoji} fue eliminado!")
                self.mobs.remove(defender)

    def use_ability(self):
        p = self.player
        c = self.player_class
        dx, dy = self.facing

        if c == 'Constructor':
            fx, fy = p.x + dx, p.y + dy
            if 0 < fx < MAP_W - 1 and 0 < fy < MAP_H - 1:
                if self.grid[fy][fx] == '🧱':
                    self.grid[fy][fx] = '▪️ '
                    self.add_log("🔨 Picaste un muro.")
                elif self.grid[fy][fx] == '▪️ ' and not self.get_mob_at(fx, fy):
                    self.grid[fy][fx] = '🧱'
                    self.add_log("🧱 Construiste un muro.")

        elif c == 'Tirador':
            self.add_log("🏹 Disparaste un proyectil.")
            for dist in range(1, 8):
                tx, ty = p.x + dx * dist, p.y + dy * dist
                if self.grid[ty][tx] == '🧱':
                    break
                target = self.get_mob_at(tx, ty)
                if target:
                    self.attack(p, target)
                    break

        elif c == 'Portalero':
            fx, fy = p.x + dx, p.y + dy
            if self.grid[fy][fx] == '▪️ ':
                self.portal_pos = (fx, fy)
                self.add_log("🌀 ¡Abriste un portal dimensional!")

        elif c == 'Tanque':
            self.add_log("🛡️ ¡Impacto soplido defensivo!")
            for mob in list(self.mobs):
                if abs(mob.x - p.x) <= 1 and abs(mob.y - p.y) <= 1:
                    self.attack(p, mob)

        elif c == 'Espadachin':
            self.add_log("⚔️ ¡Giro cortante!")
            for mob in list(self.mobs):
                if abs(mob.x - p.x) <= 1 and abs(mob.y - p.y) <= 1:
                    self.attack(p, mob)

        elif c == 'Mago':
            tx, ty = p.x + dx * 2, p.y + dy * 2
            self.add_log("🧙 ¡Explosión de bola de fuego!")
            for mob in list(self.mobs):
                if math.hypot(mob.x - tx, mob.y - ty) <= 1.8:
                    self.attack(p, mob)

        elif c == 'Soporte':
            heal = 25
            p.hp = min(p.max_hp, p.hp + heal)
            self.add_log(f"💚 Te has curado +{heal} HP.")

        # --- INSERTAR AQUÍ ---
        elif c == 'Corredor':
            # Patada frontal veloz que empuja o golpea
            fx, fy = p.x + dx, p.y + dy
            target = self.get_mob_at(fx, fy)
            if target:
                self.attack(p, target)
                self.add_log("👟 ¡Patada sprint en carrera!")
            else:
                self.add_log("👟 ¡Estás listo para correr!")


    def update_mobs(self):
        for mob in list(self.mobs):
            # Curación pasiva del soporte
            if mob.class_name == 'Soporte' and random.random() < 0.2:
                mob.hp = min(mob.max_hp, mob.hp + 5)

            dist_p = math.hypot(self.player.x - mob.x, self.player.y - mob.y)

            if not mob.is_friendly:
                # Comportamiento agresivo: persigue al jugador
                if dist_p <= 1.5:
                    self.attack(mob, self.player)
                    continue
                step_x = 1 if self.player.x > mob.x else (-1 if self.player.x < mob.x else 0)
                step_y = 1 if self.player.y > mob.y else (-1 if self.player.y < mob.y else 0)
                nx, ny = mob.x + step_x, mob.y + step_y
            else:
                # Comportamiento pacífico: deambular
                nx = mob.x + random.choice([-1, 0, 1])
                ny = mob.y + random.choice([-1, 0, 1])

            # Mover si la casilla destino está vacía
            if (0 < nx < MAP_W - 1 and 0 < ny < MAP_H - 1 and 
                self.grid[ny][nx] == '▪️ ' and 
                not (nx == self.player.x and ny == self.player.y) and 
                not self.get_mob_at(nx, ny)):
                mob.x, mob.y = nx, ny

    def render(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        view = [row[:] for row in self.grid]

        # Colocar Portal si existe
        if self.portal_pos:
            px, py = self.portal_pos
            view[py][px] = '🌀'

        # Colocar Mobs
        for m in self.mobs:
            view[m.y][m.x] = m.emoji

        # Colocar Jugador
        view[self.player.y][self.player.x] = self.player.emoji

        print(f"=== ROGUELITE CLI - NIVEL {self.dungeon_level} ===")
        print("".join(f"[{k}:{v['emoji']}] " for k, v in CLASSES.items()))
        print("-" * (MAP_W * 2))

        # Dibujar tablero (cada celda mide exactamente 2 espacios visuales)
        for row in view:
            line = ""
            for cell in row:
                # Si el carácter es un emoji con selector de variación, asegura tamaño estándar
                if cell in ['🛡️', '⚔️']:
                    line += cell + " " # Ya ocupan 2 columnas
                elif len(cell) == 1:
                    line += cell + " "
                else:
                    line += cell
            print(line)

        print("-" * (MAP_W * 2))
        info = CLASSES[self.player_class]
        print(f"Jugador: {self.player.emoji} {self.player_class} | HP: {self.player.hp}/{self.player.max_hp} | ATK: {self.player.atk} | DEF: {self.player.defense}")
        print(f"Habilidad: {info['desc']}")
        print(f"Controles: [FLECHAS] Mover/Mirar | [ESPACIO] Habilidad | [C] Cambiar Clase | [Q] Salir")
        print("\nRegistro:")
        for log in self.logs:
            print(" ▸ " + log)

    def run(self):
        while True:
            self.render()

            # --- PANTALLA DE MUERTE Y REINICIO ---
            if self.player.hp <= 0:
                print("\n❌ FIN DEL JUEGO: Has caído en la mazmorra.")
                print("👉 Presiona [ESPACIO] para reiniciar o [Q] para salir...")
                while True:
                    k = get_key()
                    if k == ' ':
                        # Reiniciar partida desde nivel 1
                        self.dungeon_level = 1
                        self.class_idx = 0
                        self.player_class = CLASS_KEYS[self.class_idx]
                        self.player = Entity(0, 0, self.player_class, is_player=True)
                        self.logs = ["¡Partida reiniciada! Buena suerte."]
                        self.init_dungeon()
                        break
                    elif k == 'q':
                        print("\n¡Gracias por jugar!")
                        return
                continue

            # Revisar si se entra a un portal
            if self.portal_pos and (self.player.x, self.player.y) == self.portal_pos:
                self.dungeon_level += 1
                self.add_log(f"¡Has descendido a la mazmorra nivel {self.dungeon_level}!")
                self.init_dungeon()
                continue

            key = get_key()

            if key == 'q':
                print("\n¡Gracias por jugar!")
                break
            elif key == 'c':
                self.switch_player_class()
                continue
            elif key == ' ':
                self.use_ability()
                self.update_mobs()

            # --- MOVIMIENTO CON FLECHAS (Y WASD COMO ALTERNATIVA) ---
            elif key in ['up', 'down', 'left', 'right', 'w', 's', 'a', 'd']:
                moves = {
                    'up': (0, -1), 'down': (0, 1), 'left': (-1, 0), 'right': (1, 0),
                    'w': (0, -1),  's': (0, 1),    'a': (-1, 0),    'd': (1, 0)
                }
                dx, dy = moves[key]
                self.facing = (dx, dy)

                pasos = 2 if self.player_class == 'Corredor' else 1

                for _ in range(pasos):
                    nx, ny = self.player.x + dx, self.player.y + dy
                    target_mob = self.get_mob_at(nx, ny)

                    if target_mob:
                        if target_mob.is_friendly:
                            target_mob.x, target_mob.y = self.player.x, self.player.y
                            self.player.x, self.player.y = nx, ny
                            self.add_log(f"Te cruzaste con el aliado {target_mob.emoji}.")
                            if target_mob.class_name == 'Soporte':
                                self.player.hp = min(self.player.max_hp, self.player.hp + 10)
                                self.add_log(f"{target_mob.emoji} te bendijo con +10 HP.")
                            break
                        else:
                            self.attack(self.player, target_mob)
                            break
                    elif self.grid[ny][nx] == '▪️ ':
                        self.player.x, self.player.y = nx, ny
                    else:
                        break

                if self.player_class == 'Soporte':
                    self.player.hp = min(self.player.max_hp, self.player.hp + 2)

                self.update_mobs()

if __name__ == '__main__':
    Game().run()