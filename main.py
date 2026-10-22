
import math
import random
import sys
import json
import os
import pygame

# CHEVALIER DU VOLCAN - Python 3.13 / Pygame 2.6.1
pygame.init()

WIDTH, HEIGHT = 1000, 650
FPS = 60
WORLD_WIDTH = 3900
GRAVITY = 0.65

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Chevalier du Volcan — Edition Mobile")
clock = pygame.time.Clock()

FONT = pygame.font.SysFont("georgia", 22, bold=True)
SMALL = pygame.font.SysFont("arial", 16)
BIG = pygame.font.SysFont("georgia", 43, bold=True)
TITLE_FONT = pygame.font.SysFont("georgia", 46, bold=True)

WHITE = (248, 245, 235)
GOLD = (255, 202, 70)
ORANGE = (255, 111, 45)
RED = (220, 55, 47)
DARK = (35, 35, 49)
SKY = (23, 30, 61)
SKY2 = (54, 54, 93)
STONE = (91, 94, 117)
STONE_LIGHT = (133, 136, 157)
GREEN = (91, 190, 115)

WORLD_NAMES = [
    "Puys ardents",
    "Grottes de glace",
    "Forêt des dragons",
    "Citadelle gargouille",
    "Temple des étoiles",
]
LEVELS_PER_WORLD = 3
TOTAL_LEVELS = len(WORLD_NAMES) * LEVELS_PER_WORLD
# Les sauvegardes sont rangées dans le profil Windows de l'utilisateur,
# pas à côté du jeu ni sur le Bureau.
if os.name == "nt":
    SAVE_ROOT = os.environ.get("APPDATA", os.path.expanduser("~"))
else:
    SAVE_ROOT = os.path.expanduser("~/.local/share")
SAVE_DIR = os.path.join(SAVE_ROOT, "ChevalierDuVolcan", "sauvegardes")
os.makedirs(SAVE_DIR, exist_ok=True)
SAVE_FILE = os.path.join(SAVE_DIR, "chevalier_volcan_sauvegarde.json")

# Couleurs propres a chaque monde : ciel, relief, pierre, sommet, danger, lumiere.
THEMES = [
    {"sky": (23, 30, 61), "far": (54, 54, 93), "stone": (61, 58, 77),
     "top": (133, 136, 157), "danger": (255, 111, 45), "glow": (255, 202, 70)},
    {"sky": (17, 43, 72), "far": (45, 91, 130), "stone": (55, 87, 112),
     "top": (156, 218, 238), "danger": (88, 211, 245), "glow": (210, 249, 255)},
    {"sky": (19, 55, 48), "far": (38, 102, 76), "stone": (57, 83, 65),
     "top": (125, 181, 112), "danger": (195, 83, 56), "glow": (255, 205, 92)},
    {"sky": (32, 25, 52), "far": (76, 51, 86), "stone": (66, 59, 79),
     "top": (154, 128, 167), "danger": (225, 70, 105), "glow": (255, 182, 109)},
    {"sky": (12, 21, 59), "far": (42, 55, 112), "stone": (54, 64, 105),
     "top": (133, 157, 218), "danger": (151, 95, 255), "glow": (255, 239, 152)},
]

CHARACTERS = [
    # 3 chevaliers
    ("Chevalier de feu", (220, 55, 47), (197, 205, 217)),
    ("Chevalier noir", (45, 42, 57), (135, 135, 157)),
    ("Chevalier royal", (175, 125, 25), (255, 224, 120)),
    # 3 dragons
    ("Dragon rouge", (180, 45, 35), (255, 150, 75)),
    ("Dragon de glace", (50, 150, 210), (195, 240, 255)),
    ("Dragon des ombres", (75, 45, 105), (185, 100, 225)),
    # 4 Valkyries
    ("Valkyrie solaire", (205, 150, 35), (255, 235, 155)),
    ("Valkyrie des glaces", (95, 175, 220), (225, 250, 255)),
    ("Valkyrie des tempetes", (95, 105, 145), (210, 220, 255)),
    ("Valkyrie des flammes", (200, 65, 50), (255, 175, 95)),
    # Personnage ultime
    ("Roi demon", (80, 20, 35), (185, 45, 70)),
]
BUTTONS = {}
# Commandes tactiles : maintenues tant que le doigt reste appuye.
mobile_buttons = {"left": False, "right": False}
TOUCH_CONTROLS = {
    "left": pygame.Rect(28, HEIGHT - 112, 72, 72),
    "right": pygame.Rect(112, HEIGHT - 112, 72, 72),
    "shoot": pygame.Rect(WIDTH - 174, HEIGHT - 122, 78, 78),
    "jump": pygame.Rect(WIDTH - 88, HEIGHT - 112, 72, 72),
}
selected_character = 0
weapon_mode = 0  # Arme fixe : les ameliorations se font automatiquement.
total_coins = 0
weapon_level = 0
unlocked_characters = 1


def calculate_weapon_level(coins):
    """Seuils : 10, 20, 30, puis 50, 70, 90, etc."""
    if coins < 10:
        return 0
    if coins < 20:
        return 1
    if coins < 30:
        return 2
    if coins < 50:
        return 3
    return 4 + (coins - 50) // 20


def load_progress():
    global selected_character, weapon_mode, total_coins, weapon_level, unlocked_characters
    try:
        with open(SAVE_FILE, "r", encoding="utf-8") as save:
            data = json.load(save)
        completed = max(0, min(TOTAL_LEVELS, int(data.get("completed_levels", 0))))
        total_coins = max(0, int(data.get("total_coins", 0)))
        weapon_level = calculate_weapon_level(total_coins)
        saved_unlocked = max(1, int(data.get("unlocked_characters", 1)))
        unlocked_characters = max(1, min(len(CHARACTERS), max(saved_unlocked, completed + 1)))
        selected_character = max(0, min(unlocked_characters - 1,
                                        int(data.get("character", 0))))
        weapon_mode = 0
        return completed
    except (OSError, ValueError, TypeError, json.JSONDecodeError):
        total_coins = 0
        weapon_level = 0
        unlocked_characters = 1
        selected_character = 0
        weapon_mode = 0
        return 0


def save_progress(completed):
    try:
        with open(SAVE_FILE, "w", encoding="utf-8") as save:
            json.dump({
                "completed_levels": completed,
                "character": selected_character,
                "total_coins": total_coins,
                "unlocked_characters": unlocked_characters
            }, save, indent=2)
    except OSError:
        # Le jeu reste jouable meme si Windows bloque l'ecriture du fichier.
        pass


def current_level_name(level_index):
    world = min(level_index // LEVELS_PER_WORLD, len(WORLD_NAMES) - 1)
    level = level_index % LEVELS_PER_WORLD + 1
    return WORLD_NAMES[world], level


def clamp(value, low, high):
    return max(low, min(high, value))


def draw_text(surface, text, font, color, x, y, center=False):
    image = font.render(text, True, color)
    rect = image.get_rect()
    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    surface.blit(image, rect)


def draw_button(surface, key, label, rect, mouse_pos, enabled=True):
    """Bouton cinematique : ombre profonde, bordure doree et survol lumineux."""
    BUTTONS[key] = pygame.Rect(rect)
    button = BUTTONS[key]
    hovered = button.collidepoint(mouse_pos) and enabled
    fill = (76, 39, 36) if hovered else (27, 29, 45)
    edge = (255, 190, 91) if hovered else (111, 91, 79)
    text_color = (255, 246, 224) if enabled else (117, 116, 126)
    if not enabled:
        fill, edge = (25, 26, 35), (61, 59, 68)
    pygame.draw.rect(surface, (4, 5, 12), button.move(0, 5), border_radius=9)
    pygame.draw.rect(surface, fill, button, border_radius=9)
    # Subtle upper highlight and a small glowing accent on the left.
    pygame.draw.line(surface, tuple(min(255, c + 22) for c in fill),
                     (button.x + 10, button.y + 2), (button.right - 10, button.y + 2), 1)
    pygame.draw.line(surface, edge, (button.x + 10, button.y + 8),
                     (button.x + 10, button.bottom - 8), 2)
    pygame.draw.rect(surface, edge, button, 1 if not hovered else 2, border_radius=9)
    if hovered:
        draw_glow(surface, (button.x + 12, button.centery), (255, 130, 54), 7)
    draw_text(surface, label, SMALL, text_color, button.centerx + 1, button.centery, True)


def draw_panel(surface, rect, alpha=232):
    """Panneau obsidienne translucide, double contour et accents en cuivre."""
    panel = pygame.Rect(rect)
    pygame.draw.rect(surface, (3, 4, 11), panel.move(0, 8), border_radius=18)
    layer = pygame.Surface(panel.size, pygame.SRCALPHA)
    layer.fill((10, 12, 24, alpha))
    surface.blit(layer, panel.topleft)
    pygame.draw.rect(surface, (120, 77, 57), panel, 2, border_radius=18)
    inner = panel.inflate(-10, -10)
    pygame.draw.rect(surface, (54, 45, 53), inner, 1, border_radius=14)
    # Four short corner accents give the panel a crafted, premium feel.
    accent = (222, 151, 83)
    for x, direction in ((panel.left + 13, 1), (panel.right - 13, -1)):
        pygame.draw.line(surface, accent, (x, panel.top + 12), (x + 13 * direction, panel.top + 12), 2)
        pygame.draw.line(surface, accent, (x, panel.bottom - 12), (x + 13 * direction, panel.bottom - 12), 2)


def draw_glow(surface, center, color, radius=8):
    radius = max(2, int(radius))
    size = radius * 4 + 4
    halo = pygame.Surface((size, size), pygame.SRCALPHA)
    c = size // 2
    pygame.draw.circle(halo, (*color, 24), (c, c), radius * 2)
    pygame.draw.circle(halo, (*color, 42), (c, c), int(radius * 1.25))
    surface.blit(halo, (int(center[0] - c), int(center[1] - c)))


def menu_background():
    """Voile sombre, braises animees et cadre cinematographique pour les menus."""
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((4, 5, 14, 178))
    screen.blit(overlay, (0, 0))
    # Lueurs de braises, plus visibles dans la partie basse de l'image.
    for i in range(34):
        x = (i * 83 + int(math.sin(frame * 0.018 + i) * 24)) % WIDTH
        y = (HEIGHT - ((frame * (1 + i % 3) + i * 59) % (HEIGHT + 50)))
        radius = 1 + (i % 3 == 0)
        color = (255, 112 + (i % 4) * 20, 48)
        if i % 4 == 0:
            draw_glow(screen, (x, y), color, 4)
        pygame.draw.circle(screen, color, (x, y), radius)
    # Barres noires discretes de cinema et filets dores.
    pygame.draw.rect(screen, (3, 4, 10), (0, 0, WIDTH, 13))
    pygame.draw.rect(screen, (3, 4, 10), (0, HEIGHT - 13, WIDTH, 13))
    pygame.draw.line(screen, (113, 65, 43), (22, 22), (WIDTH - 22, 22), 1)
    pygame.draw.line(screen, (113, 65, 43), (22, HEIGHT - 23), (WIDTH - 22, HEIGHT - 23), 1)


class Player:
    def __init__(self):
        self.rect = pygame.Rect(80, 400, 24, 30)
        self.x = float(self.rect.x)
        self.y = float(self.rect.y)
        self.vx = 0
        self.vy = 0
        self.on_ground = False
        self.jumps_used = 0
        self.max_jumps = 2
        self.facing = 1
        self.cooldown = 0
        self.invincible = 0
        self.lives = 3
        self.coins = 0
        self.weapon_flash = 0
        self.attack_flash = 0
        self.was_on_ground = False
        self.run_phase = 0.0
        self.special_cooldown = 0
        self.special_flash = 0

    def respawn(self):
        self.x = 80.0
        self.y = 400.0
        self.vx = 0
        self.vy = 0
        self.rect.topleft = (80, 400)
        self.invincible = 100

    def update(self, keys, platforms):
        self.was_on_ground = self.on_ground
        self.vx = 0
        if self.attack_flash > 0:
            self.attack_flash -= 1
        if self.special_cooldown > 0:
            self.special_cooldown -= 1
        if self.special_flash > 0:
            self.special_flash -= 1

        # Statistiques legerement differentes selon le personnage.
        character_speed = 4.2
        if selected_character in (3, 4, 5):
            character_speed = 4.45
        elif selected_character in (6, 7, 8, 9):
            character_speed = 4.35
        elif selected_character == 10:
            character_speed = 3.9
        if keys[pygame.K_LEFT] or mobile_buttons["left"]:
            self.vx = -character_speed
            self.facing = -1

        if keys[pygame.K_RIGHT] or mobile_buttons["right"]:
            self.vx = character_speed
            self.facing = 1

        # Animation de course synchronisee au deplacement.
        if self.vx:
            self.run_phase += 0.24
        else:
            self.run_phase *= 0.72

        # Deplacement horizontal et collisions
        self.x += self.vx
        self.rect.x = round(self.x)

        for platform in platforms:
            if self.rect.colliderect(platform):
                if self.vx > 0:
                    self.rect.right = platform.left
                elif self.vx < 0:
                    self.rect.left = platform.right
                self.x = float(self.rect.x)

        # Gravite et collisions verticales
        self.vy = min(self.vy + GRAVITY, 12)
        self.y += self.vy
        self.rect.y = round(self.y)
        self.on_ground = False

        for platform in platforms:
            if self.rect.colliderect(platform):
                if self.vy > 0:
                    self.rect.bottom = platform.top
                    self.on_ground = True
                    self.jumps_used = 0
                elif self.vy < 0:
                    self.rect.top = platform.bottom

                self.y = float(self.rect.y)
                self.vy = 0

        self.x = clamp(self.x, 0, WORLD_WIDTH - self.rect.width)
        self.rect.x = round(self.x)


        if self.cooldown > 0:
            self.cooldown -= 1
        if self.invincible > 0:
            self.invincible -= 1

    
    def jump(self):
        if self.jumps_used < self.max_jumps:
            jump_power = 12.2
            if selected_character in (6, 7, 8, 9):  # Valkyries : saut plus haut
                jump_power = 13.3
            elif selected_character in (3, 4, 5):   # Dragons : saut un peu plus bas
                jump_power = 11.7
            self.vy = -jump_power
            self.on_ground = False
            self.jumps_used += 1
            burst(self.rect.centerx, self.rect.bottom, (185, 190, 205), 7 if self.jumps_used == 1 else 11)


    def shoot(self, bullets):
        if self.cooldown > 0:
            return

        # Le niveau est recalcule depuis les pieces cumulees a chaque tir :
        # le systeme ne depend donc pas d'un choix de menu ou d'une variable oubliee.
        level = calculate_weapon_level(total_coins)
        speed = 10.0 + min(level, 10) * 1.15
        damage = 1 + level // 2 + (1 if selected_character == 10 else 0)
        size = 6 + min(level, 8) * 2
        if level >= 5:
            color = (255, 70, 220)  # energie violette : tir avance
        elif level >= 3:
            color = (255, 155, 55)  # energie enflammee
        elif level >= 1:
            color = (80, 237, 255)  # energie amelioree
        else:
            color = (210, 220, 230)  # tir de base

        # Nombre de projectiles : 1 au depart, 2 des le niveau 2, 3 des le niveau 3.
        if level >= 3:
            offsets = [-10, 0, 10]
        elif level >= 2:
            offsets = [-6, 6]
        else:
            offsets = [0]

        bx = self.rect.centerx + self.facing * 15
        by = self.rect.centery - 2
        for offset in offsets:
            rect = pygame.Rect(bx - size, by + offset - max(2, size // 4),
                               size * 2, max(5, size // 2))
            bullets.append({
                "rect": rect, "vx": self.facing * speed, "damage": damage,
                "color": color, "pierce": level >= 5
            })
        character_bonus = 3 if selected_character in (5, 9, 10) else (1 if selected_character in (2, 3, 8) else 0)
        self.cooldown = max(5, 18 - min(level, 12) - character_bonus)
        self.attack_flash = 7

    def special_attack(self, enemies, bosses):
        """Onde de choc. Chaque famille de heros a une portee et une puissance differentes."""
        if self.special_cooldown > 0:
            return False
        radius = 150 if selected_character in (3, 5, 9, 10) else (175 if selected_character in (6, 7, 8) else 125)
        damage = 3 if selected_character == 10 else (2 if selected_character in (3, 5, 9) else 1)
        center = self.rect.center
        for enemy in enemies:
            if enemy.alive and math.hypot(enemy.rect.centerx-center[0], enemy.rect.centery-center[1]) <= radius:
                enemy.health -= damage
                enemy.hit_flash = 8
                burst(enemy.rect.centerx, enemy.rect.centery, (255, 185, 95), 12)
                if enemy.health <= 0:
                    enemy.alive = False
                    burst(enemy.rect.centerx, enemy.rect.centery, (255, 100, 65), 22)
        for boss in bosses:
            if boss.alive and math.hypot(boss.rect.centerx-center[0], boss.rect.centery-center[1]) <= radius + 35:
                boss.health -= damage
                boss.hit_flash = 9
                burst(boss.rect.centerx, boss.rect.centery, boss.color, 16)
                if boss.health <= 0:
                    boss.alive = False
                    burst(boss.rect.centerx, boss.rect.centery, (255, 215, 125), 42)
        self.special_cooldown = 300 if selected_character == 10 else (260 if selected_character in (3, 5, 9) else 330)
        self.special_flash = 24
        burst(center[0], center[1], (255, 175, 80), 34)
        return True

    def draw(self, surface, camera):
        if self.invincible and (self.invincible // 5) % 2 == 0:
            return

        r = self.rect.move(-camera, 0)

        char_name, cape_color, armor_color = CHARACTERS[selected_character]
        # Ombre au sol et aura coloree propre a chaque famille de heros.
        pygame.draw.ellipse(surface, (12, 13, 24), (r.x - 3, r.bottom - 2, r.w + 7, 6))
        aura = armor_color
        if selected_character in (3, 9):
            aura = (255, 95, 42)
        elif selected_character in (4, 7):
            aura = (105, 215, 255)
        elif selected_character in (5, 10):
            aura = (195, 80, 245)
        elif selected_character == 6:
            aura = (255, 220, 105)
        if state == "playing" and frame % 8 < 6:
            draw_glow(surface, (r.centerx, r.centery), aura, 10 if selected_character != 10 else 15)
        # Cape et armure selon le personnage choisi
        pygame.draw.polygon(surface, cape_color, [
            (r.centerx - 4, r.y + 12),
            (r.centerx + 6, r.y + 13),
            (r.centerx + 10, r.bottom - 1),
            (r.centerx - 8, r.bottom - 1)
        ])

        # Bottes et armure
        leg_swing = int(math.sin(self.run_phase) * 3) if self.vx and self.on_ground else 0
        pygame.draw.rect(surface, DARK, (r.x + 4, r.y + 23, 6, 7 + max(0, leg_swing)), border_radius=2)
        pygame.draw.rect(surface, DARK, (r.x + 14, r.y + 23, 6, 7 + max(0, -leg_swing)), border_radius=2)
        pygame.draw.rect(
            surface, armor_color,
            (r.x + 4, r.y + 10, 16, 14), border_radius=4
        )
        pygame.draw.rect(
            surface, (109, 133, 157),
            (r.x + 6, r.y + 15, 12, 3), border_radius=1
        )

        # Tete et casque
        pygame.draw.ellipse(
            surface, (238, 194, 151),
            (r.x + 6, r.y + 3, 13, 12)
        )
        pygame.draw.arc(
            surface, GOLD,
            (r.x + 4, r.y, 17, 14), math.pi, math.tau, 4
        )
        pygame.draw.rect(
            surface, (197, 205, 217),
            (r.x + 4, r.y + 4, 17, 6), border_radius=3
        )

        eye_x = r.x + (15 if self.facing > 0 else 8)
        pygame.draw.circle(surface, DARK, (eye_x, r.y + 8), 2)

        # Silhouette differenciee : ailes pour les dragons, casque aile pour les Valkyries,
        # cornes plus grandes pour le Roi demon.
        if selected_character in (3, 4, 5):
            wing = tuple(max(0, c - 28) for c in cape_color)
            pygame.draw.polygon(surface, wing, [(r.x+5,r.y+14),(r.x-5,r.y+9),(r.x+1,r.y+23)])
            pygame.draw.polygon(surface, wing, [(r.right-5,r.y+14),(r.right+5,r.y+9),(r.right-1,r.y+23)])
        elif selected_character in (6, 7, 8, 9):
            pygame.draw.polygon(surface, armor_color, [(r.x+5,r.y+5),(r.x-1,r.y-2),(r.x+9,r.y+2)])
            pygame.draw.polygon(surface, armor_color, [(r.right-5,r.y+5),(r.right+1,r.y-2),(r.right-9,r.y+2)])
        horn_size = 8 if selected_character == 10 else 4
        pygame.draw.polygon(surface, GOLD if selected_character != 10 else RED, [
            (r.x + 8, r.y + 3),
            (r.x + 8 - horn_size//2, r.y - horn_size),
            (r.x + 12, r.y + 2)
        ])
        pygame.draw.line(surface, tuple(min(255, c + 45) for c in armor_color),
                         (r.x+7, r.y+12), (r.x+7, r.y+21), 2)
        # Plaques d'armure, ceinture, reflets metalliques et arme visible.
        highlight = tuple(min(255, c + 60) for c in armor_color)
        shadow = tuple(max(0, c - 55) for c in armor_color)
        pygame.draw.polygon(surface, highlight,
                            [(r.x+7, r.y+11), (r.x+12, r.y+13), (r.x+17, r.y+11),
                             (r.x+16, r.y+17), (r.x+8, r.y+17)])
        pygame.draw.line(surface, shadow, (r.x+5, r.y+21), (r.x+18, r.y+21), 2)
        pygame.draw.line(surface, GOLD, (r.x+5, r.y+23), (r.x+18, r.y+23), 1)
        pygame.draw.circle(surface, GOLD, (r.centerx, r.y+19), 2)
        # Cape animee par le vent, et epee orientee selon la direction.
        cape_wave = int(math.sin(frame * 0.18 + r.x * 0.03) * 3)
        pygame.draw.polygon(surface, tuple(max(0, c-30) for c in cape_color),
                            [(r.centerx-4, r.y+13), (r.centerx+5, r.y+14),
                             (r.centerx+8+cape_wave, r.bottom-2), (r.centerx-7, r.bottom-2)])
        hand_x = r.centerx + self.facing * 9
        hand_y = r.y + 17
        blade_end = (hand_x + self.facing * 12, hand_y - 10)
        pygame.draw.line(surface, (68, 43, 31), (hand_x, hand_y),
                         (hand_x + self.facing * 5, hand_y - 4), 3)
        pygame.draw.line(surface, (246, 239, 215), (hand_x + self.facing*3, hand_y-3), blade_end, 2)
        pygame.draw.line(surface, highlight, (hand_x + self.facing*4, hand_y-4),
                         (blade_end[0], blade_end[1]+1), 1)
        if self.attack_flash > 0:
            slash_color = (255, 245, 190) if self.attack_flash > 3 else (255, 150, 75)
            slash_rect = pygame.Rect(r.centerx + self.facing * 5 - 17, r.y + 5, 34, 30)
            pygame.draw.arc(surface, slash_color, slash_rect, -0.9 if self.facing > 0 else 3.9, 1.0 if self.facing > 0 else 5.8, 3)

class Enemy:
    def __init__(self, x, y, left, right, kind=0, difficulty=1):
        self.kind = kind
        # La difficulte commence des le niveau 1 : les ennemis encaissent
        # plusieurs coups et accelerent progressivement au fil des niveaux.
        self.health = 2 + (difficulty // 3) + (1 if kind else 0)
        self.max_health = self.health
        self.rect = pygame.Rect(x, y, 27 + (5 if kind else 0), 22 + (4 if kind else 0))
        self.left = left
        self.right = right
        self.base_speed = (1.55 + min(difficulty, 15) * 0.12) * (1.18 if kind else 1.0)
        self.vx = random.choice([-1, 1]) * self.base_speed
        self.alive = True
        self.attack_clock = random.randint(0, 75)
        self.lunge = 0
        self.hit_flash = 0

    def update(self, player=None):
        if not self.alive:
            return
        if self.hit_flash > 0:
            self.hit_flash -= 1
        self.attack_clock = (self.attack_clock + 1) % 110
        # Quand le joueur s'approche, certains monstres bondissent vers lui.
        if player is not None and abs(player.rect.centerx - self.rect.centerx) < 185:
            if self.attack_clock == 0:
                self.lunge = 16
                self.vx = self.base_speed * (1 if player.rect.centerx > self.rect.centerx else -1) * 1.65
        if self.lunge > 0:
            self.lunge -= 1
        elif abs(self.vx) > self.base_speed:
            self.vx *= 0.92
        self.rect.x += round(self.vx)
        if self.rect.left < self.left or self.rect.right > self.right:
            self.vx *= -1
            self.rect.left = max(self.left, min(self.rect.left, self.right - self.rect.width))

    def draw(self, surface, camera):
        if not self.alive:
            return

        r = self.rect.move(-camera, 0)
        body = (104, 208, 122) if self.kind == 0 else ((210, 85, 72) if self.kind == 1 else (155, 100, 220))
        if self.hit_flash > 0:
            body = (255, 245, 225)
        # Ombre, aura et carapace en plusieurs couches pour un monstre plus lisible.
        pygame.draw.ellipse(surface, (8, 10, 18), r.inflate(6, 5).move(0, 4))
        draw_glow(surface, r.center, body, 8 if self.kind == 0 else 11)
        pygame.draw.ellipse(surface, tuple(max(0, c - 38) for c in body), r.inflate(2, 2))
        pygame.draw.ellipse(surface, body, r)
        belly = (65, 145, 88) if self.kind == 0 else tuple(min(255, c + 25) for c in body)
        pygame.draw.ellipse(surface, belly, (r.x + 2, r.y + 11, r.w - 4, 10))
        spike_color = tuple(min(255, c + 30) for c in body)
        pygame.draw.polygon(surface, spike_color, [(r.x+5,r.y+4),(r.x+8,r.y-5),(r.x+12,r.y+5)])
        pygame.draw.polygon(surface, spike_color, [(r.right-12,r.y+5),(r.right-8,r.y-5),(r.right-5,r.y+4)])

        pygame.draw.circle(surface, WHITE, (r.x + 8, r.y + 8), 4)
        pygame.draw.circle(surface, WHITE, (r.x + 19, r.y + 8), 4)
        pygame.draw.circle(surface, DARK, (r.x + 9, r.y + 8), 2)
        pygame.draw.circle(surface, DARK, (r.x + 18, r.y + 8), 2)
        # Reflets durs et petite barre de vie pour les monstres renforces.
        pygame.draw.arc(surface, tuple(min(255, c + 55) for c in body),
                        r.inflate(-4, -4), math.pi * 1.05, math.pi * 1.9, 2)
        if self.max_health > 2:
            bar = pygame.Rect(r.x, r.y - 7, r.w, 3)
            pygame.draw.rect(surface, (28, 18, 26), bar)
            pygame.draw.rect(surface, (232, 73, 65),
                             (bar.x, bar.y, max(1, int(bar.w * self.health / self.max_health)), bar.h))



class Boss:
    """Boss de fin de monde : patrouille, change de rythme et possede une barre de vie."""
    NAMES = ["Golem de lave", "Dragon de glace", "Dragon des ronces", "Gargouille royale", "Sentinelle astrale"]
    COLORS = [(221, 75, 43), (105, 205, 245), (74, 170, 92), (154, 105, 185), (110, 135, 255)]

    def __init__(self, world, difficulty):
        self.world = world
        self.name = self.NAMES[world]
        self.color = self.COLORS[world]
        self.max_health = 14 + difficulty * 2
        self.health = self.max_health
        self.rect = pygame.Rect(WORLD_WIDTH - 360, 465, 76, 70)
        self.left = WORLD_WIDTH - 470
        self.right = WORLD_WIDTH - 190
        self.vx = -2.0 if world % 2 == 0 else 2.0
        self.alive = True
        self.attack_clock = 0
        self.phase = 1
        self.hit_flash = 0

    def update(self):
        if not self.alive:
            return
        if self.hit_flash > 0:
            self.hit_flash -= 1
        ratio = self.health / max(1, self.max_health)
        self.phase = 3 if ratio <= 0.25 else (2 if ratio <= 0.60 else 1)
        self.rect.x += round(self.vx * (1.0 + 0.25 * (self.phase - 1)))
        if self.rect.left <= self.left or self.rect.right >= self.right:
            self.vx *= -1
        self.attack_clock = (self.attack_clock + 1) % 120
        # Le boss accelere et signale visuellement son attaque dans ses phases avancees.
        if self.attack_clock == 0 and self.phase >= 2:
            self.vx *= 1.08

    def draw(self, surface, camera):
        if not self.alive:
            return
        r = self.rect.move(-camera, 0)
        # Aura et silhouette distincte. L'aura pulse davantage a faible sante.
        pulse = 3 + (self.attack_clock // 12) % 5
        aura_color = tuple(min(255, c + 35) for c in self.color)
        pygame.draw.ellipse(surface, (7, 9, 18), r.inflate(12, 8).move(0, 6))
        draw_glow(surface, r.center, aura_color, 22 if self.phase >= 2 else 14)
        pygame.draw.ellipse(surface, aura_color, r.inflate(pulse * 2, pulse * 2), 3)
        pygame.draw.ellipse(surface, tuple(max(0, c * 0.58) for c in self.color), r.inflate(-8, -5))
        pygame.draw.ellipse(surface, (255, 245, 225) if self.hit_flash > 0 else self.color, r)
        pygame.draw.ellipse(surface, tuple(min(255, c + 35) for c in self.color),
                            (r.x + 13, r.y + 10, r.w - 26, 22))
        pygame.draw.polygon(surface, self.color, [(r.x+10,r.y+10),(r.x+3,r.y-12),(r.x+25,r.y+5)])
        pygame.draw.polygon(surface, self.color, [(r.right-10,r.y+10),(r.right-3,r.y-12),(r.right-25,r.y+5)])
        pygame.draw.ellipse(surface, (55, 35, 48), (r.x+12,r.y+22,13,11))
        pygame.draw.ellipse(surface, (55, 35, 48), (r.right-25,r.y+22,13,11))
        pygame.draw.circle(surface, GOLD, (r.x+19,r.y+27), 4)
        pygame.draw.circle(surface, GOLD, (r.right-19,r.y+27), 4)
        # Barre de vie et indication de phase au-dessus du boss.
        bar = pygame.Rect(r.x-5, r.y-25, r.w+10, 9)
        pygame.draw.rect(surface, (35, 25, 35), bar, border_radius=4)
        fill = pygame.Rect(bar.x+1, bar.y+1, int((bar.w-2)*max(0,self.health)/self.max_health), bar.h-2)
        phase_color = (GREEN, ORANGE, RED)[self.phase - 1]
        pygame.draw.rect(surface, phase_color, fill, border_radius=3)
        pygame.draw.rect(surface, (245, 235, 225), bar, 1, border_radius=4)
        if self.phase >= 2 and self.attack_clock > 85:
            pygame.draw.circle(surface, GOLD, (r.centerx, r.bottom + 8), 5 + self.phase, 2)


def build_level(world_index=0, level_index=0):
    platforms = [
        pygame.Rect(0, 535, 430, 115),
        pygame.Rect(500, 535, 350, 115),
        pygame.Rect(930, 535, 420, 115),
        pygame.Rect(1430, 535, 370, 115),
        pygame.Rect(1880, 535, 460, 115),
        pygame.Rect(2420, 535, 420, 115),
        pygame.Rect(2920, 535, 400, 115),
        pygame.Rect(3400, 535, 500, 115),

        pygame.Rect(220, 430, 130, 22),
        pygame.Rect(590, 425, 130, 22),
        pygame.Rect(790, 355, 110, 22),
        pygame.Rect(1060, 430, 150, 22),
        pygame.Rect(1280, 355, 110, 22),
        pygame.Rect(1530, 420, 130, 22),
        pygame.Rect(1730, 345, 130, 22),
        pygame.Rect(2050, 430, 150, 22),
        pygame.Rect(2290, 360, 120, 22),
        pygame.Rect(2530, 425, 140, 22),
        pygame.Rect(2760, 350, 120, 22),
        pygame.Rect(3000, 425, 140, 22),
        pygame.Rect(3230, 355, 130, 22),
        pygame.Rect(3540, 430, 150, 22)
    ]

    lava = [
        pygame.Rect(430, 575, 70, 75),
        pygame.Rect(850, 575, 80, 75),
        pygame.Rect(1350, 575, 80, 75),
        pygame.Rect(1800, 575, 80, 75),
        pygame.Rect(2340, 575, 80, 75),
        pygame.Rect(2840, 575, 80, 75),
        pygame.Rect(3320, 575, 80, 75)
    ]

    coin_positions = [
        (270, 390), (630, 385), (830, 315),
        (1110, 390), (1320, 315), (1570, 380),
        (1770, 305), (2100, 390), (2340, 320),
        (2580, 385), (2800, 310), (3050, 385),
        (3270, 315), (3590, 390), (3700, 480)
    ]
    coins = [pygame.Rect(x, y, 16, 16) for x, y in coin_positions]

    enemies = [
        Enemy(300, 508, 180, 410),
        Enemy(640, 508, 520, 830),
        Enemy(1120, 508, 960, 1320),
        Enemy(1600, 508, 1460, 1780),
        Enemy(2110, 508, 1900, 2320),
        Enemy(2600, 508, 2440, 2820),
        Enemy(3070, 508, 2940, 3300),
        Enemy(3600, 508, 3420, 3870),
        Enemy(610, 403, 590, 720),
        Enemy(2560, 403, 2530, 2670)
    ]

    # Les 15 niveaux partagent une base lisible, avec une hauteur et des pieges
    # qui varient progressivement d'un niveau a l'autre.
    height_shift = ((level_index % LEVELS_PER_WORLD) - 1) * 12
    for platform in platforms[8:]:
        platform.y -= height_shift

    # Quelques plateformes signature selon le monde, pour varier les trajectoires.
    # Elles sont placees au-dessus des couloirs principaux et restent accessibles au double saut.
    if world_index == 0:  # ponts de roche volcanique
        platforms.extend([pygame.Rect(870, 455, 72, 18), pygame.Rect(1845, 445, 72, 18)])
    elif world_index == 1:  # corniches de glace
        platforms.extend([pygame.Rect(870, 395, 82, 18), pygame.Rect(2350, 395, 82, 18)])
    elif world_index == 2:  # branches de la foret
        platforms.extend([pygame.Rect(430, 385, 85, 18), pygame.Rect(1885, 385, 85, 18)])
    elif world_index == 3:  # plateformes de la citadelle
        platforms.extend([pygame.Rect(870, 375, 90, 18), pygame.Rect(2845, 385, 90, 18)])
    else:  # marches magiques du temple
        platforms.extend([pygame.Rect(430, 390, 90, 18), pygame.Rect(2345, 385, 90, 18)])

    # Les pieces suivent les plateformes flottantes.
    coins = [pygame.Rect(c.x, c.y - height_shift, c.w, c.h) for c in coins]

    # Les mondes plus avances ajoutent quelques pieces et ennemis.
    if level_index % LEVELS_PER_WORLD >= 1:
        for x, y in [(970, 470), (1900, 470), (2880, 470)]:
            coins.append(pygame.Rect(x, y, 16, 16))
    difficulty = level_index + 1
    # Une menace supplementaire est presente des le debut pour rendre
    # le premier niveau plus engageant, sans bloquer les sauts d'apprentissage.
    enemies.extend([
        Enemy(430, 508, 365, 495, kind=1, difficulty=difficulty),
        Enemy(1875, 508, 1810, 1870, kind=1, difficulty=difficulty),
        Enemy(2760, 323, 2760, 2880, kind=2 if world_index >= 2 else 1, difficulty=difficulty)
    ])
    if level_index % LEVELS_PER_WORLD == 2:
        enemies.append(Enemy(870, 508, 860, 920, kind=1, difficulty=difficulty))
        enemies.append(Enemy(2370, 508, 2350, 2410, kind=1, difficulty=difficulty))
    # De nouveaux types arrivent au fil des niveaux et les ennemis accelerent.
    if level_index >= 3:
        enemies.append(Enemy(1450, 508, 1440, 1790, kind=1, difficulty=difficulty))
    if level_index >= 6:
        enemies.append(Enemy(2020, 403, 1900, 2290, kind=2, difficulty=difficulty))
    if level_index >= 9:
        enemies.append(Enemy(3000, 508, 2940, 3300, kind=2, difficulty=difficulty))
    for enemy in enemies:
        enemy.vx *= (1 + difficulty * 0.035)
        enemy.base_speed *= (1 + difficulty * 0.025)

    # Petites variantes de parcours selon le monde pour eviter les 15 parcours identiques.
    if world_index == 1:  # plateformes de glace plus hautes
        platforms.extend([pygame.Rect(960, 300, 95, 18), pygame.Rect(1935, 315, 105, 18),
                          pygame.Rect(2860, 300, 95, 18)])
    elif world_index == 2:  # plateformes forestieres en escalier
        platforms.extend([pygame.Rect(720, 465, 90, 18), pygame.Rect(1640, 465, 95, 18),
                          pygame.Rect(2700, 465, 90, 18)])
    elif world_index == 3:  # citadelle : plateformes plus etroites
        platforms.extend([pygame.Rect(990, 325, 75, 18), pygame.Rect(2180, 310, 75, 18),
                          pygame.Rect(3140, 325, 75, 18)])
    elif world_index == 4:  # temple : chemin de plateformes astrales
        platforms.extend([pygame.Rect(880, 390, 100, 18), pygame.Rect(1885, 380, 100, 18),
                          pygame.Rect(2885, 390, 100, 18)])

    # Plateformes mobiles : elles traversent les fosses et facilitent les passages
    # au debut, puis leur trajectoire devient plus longue dans les niveaux avances.
    moving_platforms = []
    for x, y, left, right in [(445, 475, 430, 485), (1365, 470, 1350, 1415), (2355, 465, 2340, 2405), (3335, 475, 3320, 3385)]:
        rect = pygame.Rect(x, y - min(level_index, 8), 76, 16)
        platforms.append(rect)
        moving_platforms.append({"rect": rect, "left": left, "right": right,
                                "speed": 0.8 + min(level_index, 14) * 0.045,
                                "direction": random.choice([-1, 1])})

    # Pieges lisibles : pics fixes et geysers qui se chargent avant de jaillir.
    traps = []
    spike_positions = [] if level_index == 0 else [650, 1190]
    if level_index >= 3:
        spike_positions += [2115, 3060]
    if level_index >= 7:
        spike_positions += [1575, 2600]
    if level_index >= 10:
        spike_positions += [980, 2870]
    for x in spike_positions:
        traps.append({"kind": "spikes", "rect": pygame.Rect(x, 505, 42, 30),
                      "phase": random.randint(0, 100), "active": True})
    geyser_positions = [780, 1660, 2710]
    if level_index >= 5:
        geyser_positions += [1030, 3190]
    for x in geyser_positions:
        traps.append({"kind": "geyser", "rect": pygame.Rect(x, 445, 34, 90),
                      "phase": random.randint(0, 150), "active": False})

    # Recoloration thematique de la lave/danger (glace, ronces, magie...).
    bosses = [Boss(world_index, level_index + 1)] if level_index % LEVELS_PER_WORLD == LEVELS_PER_WORLD - 1 else []
    return platforms, lava, coins, enemies, bosses, moving_platforms, traps


def draw_vertical_gradient(surface, top_color, bottom_color):
    """Ciel en degrade pour un fond moins plat et plus cinematographique."""
    for y in range(0, HEIGHT, 4):
        t = y / max(1, HEIGHT - 1)
        color = tuple(int(top_color[i] * (1 - t) + bottom_color[i] * t) for i in range(3))
        pygame.draw.rect(surface, color, (0, y, WIDTH, 4))


def draw_background(surface, camera):
    theme = THEMES[world_index]
    lower_sky = tuple(max(0, int(c * 0.48)) for c in theme["sky"])
    draw_vertical_gradient(surface, theme["sky"], lower_sky)

    # Halo atmospherique doux derriere le soleil/lune.
    celestial_x = 760 - int(camera * 0.035) % 180
    halo = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    halo_color = theme["glow"]
    for radius, alpha in ((150, 9), (105, 13), (68, 18)):
        pygame.draw.circle(halo, (*halo_color, alpha), (celestial_x, 145), radius)
    surface.blit(halo, (0, 0))

    # Astre et reliefs varies selon le monde.
    if world_index == 0:
        pygame.draw.circle(surface, (104, 57, 83), (760, 145), 95)
        pygame.draw.circle(surface, (245, 131, 83), (760, 145), 58)
    elif world_index == 1:
        pygame.draw.circle(surface, (193, 235, 255), (760, 125), 47)
        for i in range(7):
            sx = (i * 151 - int(camera * 0.16)) % (WIDTH + 80)
            pygame.draw.polygon(surface, (129, 185, 218),
                                [(sx, 535), (sx + 45, 365), (sx + 92, 535)])
    elif world_index == 2:
        pygame.draw.circle(surface, (255, 220, 125), (760, 130), 36)
        for i in range(9):
            sx = (i * 137 - int(camera * 0.18)) % (WIDTH + 70)
            pygame.draw.circle(surface, (61, 139, 91), (sx, 355), 38)
            pygame.draw.rect(surface, (77, 83, 59), (sx - 7, 355, 14, 180))
    elif world_index == 3:
        pygame.draw.circle(surface, (221, 204, 241), (760, 125), 32)
        for i in range(5):
            sx = (i * 230 - int(camera * 0.18)) % (WIDTH + 100)
            pygame.draw.polygon(surface, (57, 43, 72),
                                [(sx, 535), (sx + 50, 240), (sx + 100, 535)])
    else:
        pygame.draw.circle(surface, (255, 239, 152), (760, 125), 42)
        for i in range(45):
            sx = (i * 97 + 31) % WIDTH
            sy = (i * 53 + 17) % 430
            pygame.draw.circle(surface, (226, 232, 255), (sx, sy), 2)

    # Reliefs en couches avec parallaxe : effet de profondeur 2.5D.
    for layer, (parallax, base_y, step, peak_h, shade) in enumerate((
            (0.10, 505, 190, 150, 0.72), (0.22, 535, 245, 255, 1.0),
            (0.34, 545, 205, 185, 0.62))):
        for i in range(-2, 9):
            x = i * step - int(camera * parallax) % step
            c = tuple(max(0, min(255, int(v * shade))) for v in (theme["far"] if layer != 1 else theme["stone"]))
            peak = base_y - peak_h - ((i * 29) % 75)
            pygame.draw.polygon(surface, c, [
                (x - 45, base_y), (x + 22, peak + 75), (x + 65, peak),
                (x + 104, peak + 54), (x + 160, base_y)
            ])
            # Facettes rocheuses : ombres et aretes eclairees.
            light = tuple(min(255, int(v * 1.22 + 8)) for v in c)
            dark = tuple(max(0, int(v * 0.68)) for v in c)
            pygame.draw.polygon(surface, light, [(x + 22, peak + 75), (x + 65, peak), (x + 70, peak + 88)])
            pygame.draw.polygon(surface, dark, [(x + 70, peak + 88), (x + 104, peak + 54), (x + 160, base_y)])

    # Piliers, ruines et silhouettes du monde pour une echelle plus realiste.
    structure_color = tuple(max(0, int(c * 0.58)) for c in theme["stone"])
    for i in range(-1, 7):
        x = i * 310 - int(camera * 0.43) % 310
        height = 80 + (i * 37 % 95)
        pygame.draw.polygon(surface, structure_color,
                            [(x, 535), (x + 8, 535-height), (x + 28, 535-height-12),
                             (x + 42, 535-height), (x + 53, 535)])
        pygame.draw.line(surface, tuple(min(255, c + 25) for c in structure_color),
                         (x + 28, 535-height-8), (x + 31, 535-height+28), 2)

    # Brume en bandes et particules au premier plan pour renforcer la profondeur.
    mist = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    for band in range(4):
        y = 395 + band * 43
        pygame.draw.ellipse(mist, (*theme["far"], 24),
                            ((band * 170 - int(camera * (0.08 + band*0.02))) % (WIDTH + 260) - 130,
                             y, 430, 72))
    surface.blit(mist, (0, 0))
    for i in range(42):
        x = (i * 83 - int(camera * (0.12 + (i % 3) * 0.04))) % WIDTH
        y = 55 + (i * 47 + frame * (1 + i % 2)) % 440
        radius = 1 + (i % 3 == 0)
        pygame.draw.circle(surface, theme["glow"], (x, y), radius)

    # Brume volumetrique au niveau du sol et silhouettes au premier plan.
    fog = pygame.Surface((WIDTH, 150), pygame.SRCALPHA)
    for band in range(5):
        alpha = 9 + band * 2
        pygame.draw.ellipse(fog, (*theme["far"], alpha),
                            ((band * 190 - int(camera * 0.5)) % (WIDTH + 280) - 140,
                             30 + band * 13, 360, 75))
    surface.blit(fog, (0, 450))
    foreground = tuple(max(0, int(c * 0.32)) for c in theme["stone"])
    for i in range(8):
        x = (i * 157 - int(camera * 0.62)) % (WIDTH + 90) - 45
        y = 616 + (i % 3) * 8
        pygame.draw.polygon(surface, foreground,
                            [(x-32, HEIGHT), (x-8, y-22), (x+7, y-5), (x+22, y-27), (x+43, HEIGHT)])


def draw_platform(surface, platform, camera):
    r = platform.move(-camera, 0)

    if r.right < 0 or r.left > WIDTH:
        return

    theme = THEMES[world_index]
    # Ombre portee et face laterale pour un faux volume 2.5D.
    pygame.draw.rect(surface, (8, 10, 21), r.move(0, 7), border_radius=6)
    pygame.draw.rect(surface, theme["stone"], r, border_radius=5)
    side_color = tuple(max(0, c - 22) for c in theme["stone"])
    pygame.draw.polygon(surface, side_color, [(r.x, r.y+7), (r.right, r.y+7),
                                               (r.right, r.bottom), (r.x+5, r.bottom)])
    # Face avant en plans successifs pour simuler une roche epaisse en 2.5D.
    lower_shade = tuple(max(0, c - 15) for c in side_color)
    pygame.draw.polygon(surface, lower_shade,
                        [(r.x+5, r.y+27), (r.right, r.y+22), (r.right, r.bottom), (r.x+5, r.bottom)])
    pygame.draw.line(surface, tuple(min(255, c + 22) for c in theme["stone"]),
                     (r.x+4, r.y+10), (r.x+4, r.bottom-5), 1)
    top = pygame.Rect(r.x, r.y, r.w, min(9, r.h))
    pygame.draw.rect(surface, theme["top"], top, border_radius=4)
    highlight = tuple(min(255, c + 30) for c in theme["top"])
    pygame.draw.line(surface, highlight, (r.x+7, r.y+2), (r.right-8, r.y+2), 2)
    for x in range(r.x + 12, r.right - 8, 38):
        pygame.draw.line(surface, theme["far"], (x, r.y + 14),
                         (x + 11, min(r.bottom, r.y + 30)), 2)


def draw_lava(surface, rect, camera, frame):
    r = rect.move(-camera, 0)

    if r.right < 0 or r.left > WIDTH:
        return

    theme = THEMES[world_index]
    danger_color = theme["danger"]
    glow_color = theme["glow"]
    pygame.draw.rect(surface, tuple(max(0, c * 0.48) for c in danger_color), r)
    pygame.draw.rect(surface, danger_color, (r.x, r.y, r.w, 10))

    for x in range(r.x + 4, r.right, 18):
        yy = r.y + 4 + int(math.sin(frame * 0.12 + x) * 3)
        pygame.draw.circle(surface, glow_color, (x, yy), 3)


def reset_game():
    player = Player()
    platforms, lava, coins, enemies, bosses, moving_platforms, traps = build_level(world_index, level_index)
    bullets = []
    return player, platforms, lava, coins, enemies, bosses, bullets, moving_platforms, traps


def start_level(index):
    """Charge proprement un niveau et son monde correspondant."""
    global level_index, world_index, player, platforms, lava, coins, enemies, bosses, bullets, moving_platforms, traps
    level_index = max(0, min(TOTAL_LEVELS - 1, index))
    world_index = level_index // LEVELS_PER_WORLD
    player, platforms, lava, coins, enemies, bosses, bullets, moving_platforms, traps = reset_game()
    boss_projectiles.clear()
    particles.clear()
    return 0


completed_levels = load_progress()
level_index = min(completed_levels, TOTAL_LEVELS - 1)
world_index = level_index // LEVELS_PER_WORLD
player, platforms, lava, coins, enemies, bosses, bullets, moving_platforms, traps = reset_game()

state = "title"
previous_state = "playing"
camera = 0
frame = 0
particles = []
boss_projectiles = []


def burst(x, y, color, count=8):
    # Limite le nombre d'elements visuels pour garder 60 FPS.
    if len(particles) > 350:
        del particles[:100]
    for _ in range(count):
        angle = random.random() * math.tau
        speed = random.uniform(1.0, 3.2)
        particles.append({
            "x": float(x), "y": float(y),
            "vx": math.cos(angle) * speed, "vy": math.sin(angle) * speed,
            "life": random.randint(14, 27), "color": color,
            "size": random.randint(2, 4)
        })


def draw_touch_controls():
    """Dessine les commandes tactiles au-dessus du jeu pendant une partie."""
    specs = [
        ("left", "◀", (58, 72, 96)),
        ("right", "▶", (58, 72, 96)),
        ("shoot", "A", (168, 57, 48)),
        ("jump", "B", (43, 102, 173)),
    ]
    for key, label, color in specs:
        rect = TOUCH_CONTROLS[key]
        pressed = mobile_buttons.get(key, False)
        fill = tuple(min(255, c + 28) for c in color) if pressed else color
        surface = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
        pygame.draw.rect(surface, (*fill, 205), surface.get_rect(), border_radius=18)
        pygame.draw.rect(surface, (235, 225, 210, 235), surface.get_rect(), 2, border_radius=18)
        screen.blit(surface, rect.topleft)
        font = pygame.font.SysFont("arial", 32, bold=True)
        txt = font.render(label, True, (255, 255, 255))
        screen.blit(txt, txt.get_rect(center=(rect.centerx, rect.centery - 7)))
        if key == "shoot":
            sub = SMALL.render("TIR", True, (255, 230, 210))
            screen.blit(sub, sub.get_rect(center=(rect.centerx, rect.bottom - 17)))
        elif key == "jump":
            sub = SMALL.render("SAUT", True, (225, 240, 255))
            screen.blit(sub, sub.get_rect(center=(rect.centerx, rect.bottom - 17)))


def handle_touch_down(pos):
    """Retourne True si l'appui est consomme par une commande de jeu."""
    if state != "playing":
        return False
    if TOUCH_CONTROLS["left"].collidepoint(pos):
        mobile_buttons["left"] = True
        return True
    if TOUCH_CONTROLS["right"].collidepoint(pos):
        mobile_buttons["right"] = True
        return True
    if TOUCH_CONTROLS["shoot"].collidepoint(pos):
        player.shoot(bullets)
        mobile_buttons["shoot"] = True
        return True
    if TOUCH_CONTROLS["jump"].collidepoint(pos):
        player.jump()
        mobile_buttons["jump"] = True
        return True
    return False


def clear_touch_controls():
    for key in mobile_buttons:
        mobile_buttons[key] = False
    mobile_buttons["shoot"] = False
    mobile_buttons["jump"] = False


while True:
    clock.tick(FPS)
    frame += 1

    # Evenements clavier et fenetre
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos
            if handle_touch_down(pos):
                continue
            if state == "playing" and BUTTONS.get("pause_button", pygame.Rect(0,0,0,0)).collidepoint(pos):
                state = "paused"
            elif state == "title":
                if BUTTONS.get("start", pygame.Rect(0,0,0,0)).collidepoint(pos):
                    start_level(level_index if completed_levels < TOTAL_LEVELS else 0)
                    camera = 0
                    state = "playing"
                elif BUTTONS.get("levels", pygame.Rect(0,0,0,0)).collidepoint(pos):
                    state = "level_select"
                elif BUTTONS.get("characters", pygame.Rect(0,0,0,0)).collidepoint(pos):
                    state = "character_select"
            elif state == "level_select":
                if BUTTONS.get("back", pygame.Rect(0,0,0,0)).collidepoint(pos):
                    state = "title"
                else:
                    for i in range(TOTAL_LEVELS):
                        if (i <= completed_levels or i == level_index) and BUTTONS.get(
                                f"level_{i}", pygame.Rect(0,0,0,0)).collidepoint(pos):
                            start_level(i)
                            camera = 0
                            state = "playing"
                            break
            elif state == "character_select":
                if (BUTTONS.get("back", pygame.Rect(0,0,0,0)).collidepoint(pos) or
                        BUTTONS.get("back_pause", pygame.Rect(0,0,0,0)).collidepoint(pos)):
                    save_progress(completed_levels)
                    state = "title"
                else:
                    for i in range(len(CHARACTERS)):
                        if (i < unlocked_characters and
                                (BUTTONS.get(f"char_{i}", pygame.Rect(0,0,0,0)).collidepoint(pos) or
                                 BUTTONS.get(f"pausechar_{i}", pygame.Rect(0,0,0,0)).collidepoint(pos))):
                            selected_character = i
                            save_progress(completed_levels)
                            break
            elif state == "paused":
                if BUTTONS.get("resume", pygame.Rect(0,0,0,0)).collidepoint(pos):
                    state = "playing"
                elif BUTTONS.get("pause_char", pygame.Rect(0,0,0,0)).collidepoint(pos):
                    state = "character_select_pause"
                elif BUTTONS.get("main_menu", pygame.Rect(0,0,0,0)).collidepoint(pos):
                    save_progress(completed_levels)
                    state = "title"
            elif state == "character_select_pause":
                if BUTTONS.get("back_pause", pygame.Rect(0,0,0,0)).collidepoint(pos):
                    state = "paused"
                else:
                    for i in range(len(CHARACTERS)):
                        if (i < unlocked_characters and
                                BUTTONS.get(f"pausechar_{i}", pygame.Rect(0,0,0,0)).collidepoint(pos)):
                            selected_character = i
                            save_progress(completed_levels)
                            state = "paused"
                            break
            elif state == "gameover":
                if BUTTONS.get("retry", pygame.Rect(0,0,0,0)).collidepoint(pos):
                    start_level(level_index); camera = 0; state = "playing"
                elif BUTTONS.get("game_menu", pygame.Rect(0,0,0,0)).collidepoint(pos):
                    state = "title"
            elif state == "victory":
                if BUTTONS.get("next", pygame.Rect(0,0,0,0)).collidepoint(pos):
                    if level_index < TOTAL_LEVELS - 1:
                        camera = start_level(level_index + 1); state = "playing"
                    else:
                        start_level(0); camera = 0; state = "title"

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            clear_touch_controls()

        # Les evenements FINGER sont emis sur les appareils tactiles Android.
        elif event.type == pygame.FINGERDOWN:
            touch_pos = (int(event.x * WIDTH), int(event.y * HEIGHT))
            handle_touch_down(touch_pos)
        elif event.type in (pygame.FINGERUP, pygame.FINGERCANCEL):
            clear_touch_controls()

        if event.type == pygame.KEYDOWN:
            if state == "title":
                if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    start_level(level_index if completed_levels < TOTAL_LEVELS else 0)
                    camera = 0; state = "playing"
                elif event.key == pygame.K_l:
                    state = "level_select"
                elif event.key == pygame.K_c:
                    state = "character_select"
            elif state == "level_select" and event.key == pygame.K_ESCAPE:
                state = "title"
            elif state == "character_select" and event.key == pygame.K_ESCAPE:
                state = "title"
            elif state == "character_select_pause" and event.key == pygame.K_ESCAPE:
                state = "paused"
            elif state == "paused" and event.key in (pygame.K_ESCAPE, pygame.K_RETURN):
                state = "playing"
            elif state == "gameover":
                if event.key == pygame.K_RETURN:
                    start_level(level_index); camera = 0; state = "playing"
                elif event.key == pygame.K_ESCAPE:
                    state = "title"
            elif state == "victory":
                if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    if level_index < TOTAL_LEVELS - 1:
                        camera = start_level(level_index + 1); state = "playing"
                    else:
                        start_level(0); camera = 0; state = "title"
            elif state == "playing":
                if event.key == pygame.K_SPACE:
                    player.jump()
                elif event.key == pygame.K_x:
                    player.shoot(bullets)
                elif event.key == pygame.K_c:
                    player.special_attack(enemies, bosses)
                elif event.key in (pygame.K_ESCAPE, pygame.K_p):
                    state = "paused"
            elif state == "paused":
                if event.key in (pygame.K_ESCAPE, pygame.K_RETURN):
                    state = "playing"
                elif event.key == pygame.K_c:
                    previous_state = "paused"; state = "character_select_pause"
            elif state == "character_select_pause" and event.key == pygame.K_ESCAPE:
                state = "paused"

    # Mise a jour du jeu
    if state == "playing":
        keys = pygame.key.get_pressed()
        # Mouvement des plateformes avant la physique du joueur.
        for moving in moving_platforms:
            rect = moving["rect"]
            rect.x += round(moving["speed"] * moving["direction"])
            if rect.left <= moving["left"] or rect.right >= moving["right"] + rect.width:
                moving["direction"] *= -1
        # Les geysers ont une phase de charge, puis une eruption dangereuse.
        for trap in traps:
            trap["phase"] = (trap["phase"] + 1) % 180
            if trap["kind"] == "geyser":
                trap["active"] = 78 <= trap["phase"] <= 119
                trap["rect"].y = 535 - (92 if trap["active"] else (18 if 55 <= trap["phase"] < 78 else 0))
                trap["rect"].height = 535 - trap["rect"].y
        player.update(keys, platforms)
        if not player.was_on_ground and player.on_ground:
            burst(player.rect.centerx, player.rect.bottom, (155, 157, 174), 12)
        if player.weapon_flash > 0:
            player.weapon_flash -= 1

        for enemy in enemies:
            enemy.update(player)
        for boss in bosses:
            boss.update()
            attack_ticks = (1, 2) if boss.phase == 1 else ((1, 2, 48, 49) if boss.phase == 2 else (1, 2, 28, 29, 68, 69))
            if boss.alive and boss.attack_clock in attack_ticks and abs(player.rect.centerx - boss.rect.centerx) < 900:
                direction = -1 if player.rect.centerx < boss.rect.centerx else 1
                shot_speed = 4.0 if boss.phase == 1 else (5.0 if boss.phase == 2 else 6.2)
                shot_y = boss.rect.y + 25 + (10 if boss.phase == 3 and boss.attack_clock > 30 else 0)
                boss_projectiles.append({
                    "rect": pygame.Rect(boss.rect.centerx, shot_y, 18, 12),
                    "vx": direction * shot_speed, "color": boss.color
                })

        for shot in boss_projectiles[:]:
            shot["rect"].x += round(shot["vx"])
            if shot["rect"].right < 0 or shot["rect"].left > WORLD_WIDTH:
                boss_projectiles.remove(shot)
            elif player.rect.colliderect(shot["rect"]) and player.invincible <= 0:
                boss_projectiles.remove(shot)
                burst(player.rect.centerx, player.rect.centery, (255, 90, 75), 16)
                player.lives -= 1
                if player.lives <= 0:
                    state = "gameover"
                else:
                    player.respawn()

        # Projectiles laser
        for bullet in bullets[:]:
            rect = bullet["rect"]
            rect.x += round(bullet["vx"])
            if rect.right < 0 or rect.left > WORLD_WIDTH:
                bullets.remove(bullet)
                continue
            hit_target = False
            for enemy in enemies:
                if enemy.alive and rect.colliderect(enemy.rect):
                    enemy.health -= bullet["damage"]
                    enemy.hit_flash = 5
                    burst(enemy.rect.centerx, enemy.rect.centery, (255, 190, 110), 5)
                    if enemy.health <= 0:
                        enemy.alive = False
                        burst(enemy.rect.centerx, enemy.rect.centery, (255, 115, 70), 18)
                    hit_target = True
                    if not bullet["pierce"]:
                        if bullet in bullets: bullets.remove(bullet)
                        break
            if not hit_target or bullet in bullets:
                for boss in bosses:
                    if boss.alive and rect.colliderect(boss.rect):
                        boss.health -= bullet["damage"]
                        boss.hit_flash = 6
                        burst(boss.rect.centerx, boss.rect.centery, boss.color, 10)
                        if boss.health <= 0:
                            boss.alive = False
                            burst(boss.rect.centerx, boss.rect.centery, (255, 210, 110), 38)
                        if not bullet["pierce"] and bullet in bullets:
                            bullets.remove(bullet)
                        break

        # Ramassage des pieces
        for coin in coins[:]:
            if player.rect.colliderect(coin):
                coins.remove(coin)
                player.coins += 1
                old_weapon_level = calculate_weapon_level(total_coins)
                total_coins += 1
                weapon_level = calculate_weapon_level(total_coins)
                burst(coin.centerx, coin.centery, GOLD, 10)
                if weapon_level > old_weapon_level:
                    player.weapon_flash = 150
                    burst(player.rect.centerx, player.rect.centery, (80, 237, 255), 22)
                save_progress(completed_levels)

        # Dangers : lave, ennemis et chute
        hit = any(player.rect.colliderect(hazard) for hazard in lava)
        hit = hit or any(trap["active"] and player.rect.colliderect(trap["rect"])
                         for trap in traps)
        hit = hit or any(
            enemy.alive and player.rect.colliderect(enemy.rect)
            for enemy in enemies
        )
        hit = hit or any(boss.alive and player.rect.colliderect(boss.rect) for boss in bosses)

        if player.rect.top > HEIGHT + 80:
            hit = True

        if hit and player.invincible <= 0:
            player.lives -= 1

            if player.lives <= 0:
                state = "gameover"
            else:
                player.respawn()

        # Arrivee du niveau : detecter le bord droit du chevalier
        # plutot que son bord gauche, pour rendre la sortie plus facile a atteindre.
        exit_zone = pygame.Rect(WORLD_WIDTH - 150, 400, 150, 150)
        reached_exit = player.rect.colliderect(exit_zone) or player.rect.right >= WORLD_WIDTH - 90
        boss_blocking_exit = any(boss.alive for boss in bosses)
        if reached_exit and state == "playing" and not boss_blocking_exit:
            state = "victory"
            previous_completed = completed_levels
            completed_levels = max(completed_levels, level_index + 1)
            if completed_levels > previous_completed:
                unlocked_characters = min(len(CHARACTERS),
                                          max(unlocked_characters, completed_levels + 1))
            save_progress(completed_levels)

        camera = clamp(
            player.rect.centerx - WIDTH // 2,
            0, WORLD_WIDTH - WIDTH
        )

    # Mise a jour des particules de pieces et d'amelioration.
    if state == "playing":
        for particle in particles[:]:
            particle["x"] += particle["vx"]
            particle["y"] += particle["vy"]
            particle["vy"] += 0.07
            particle["life"] -= 1
            if particle["life"] <= 0:
                particles.remove(particle)

    # Dessin du monde
    draw_background(screen, camera)

    for platform in platforms:
        draw_platform(screen, platform, camera)
    # Les plateformes mobiles sont marquees par des runes lumineuses sur leurs bords.
    for moving in moving_platforms:
        mr = moving["rect"].move(-camera, 0)
        if -100 < mr.x < WIDTH + 100:
            rune = THEMES[world_index]["glow"]
            pygame.draw.line(screen, rune, (mr.x + 7, mr.y + 3), (mr.x + 22, mr.y + 3), 2)
            pygame.draw.line(screen, rune, (mr.right - 22, mr.y + 3), (mr.right - 7, mr.y + 3), 2)
            draw_glow(screen, (mr.centerx, mr.y + 2), rune, 5)

    for hazard in lava:
        draw_lava(screen, hazard, camera, frame)

    # Pieges fantasy : pics d'obsidienne et geysers avec avertissement lumineux.
    for trap in traps:
        tr = trap["rect"].move(-camera, 0)
        if tr.right < 0 or tr.left > WIDTH:
            continue
        danger = THEMES[world_index]["danger"]
        if trap["kind"] == "spikes":
            for sx in range(tr.left, tr.right, 10):
                pygame.draw.polygon(screen, (22, 20, 34), [(sx, tr.bottom), (sx+5, tr.top), (sx+10, tr.bottom)])
                pygame.draw.line(screen, danger, (sx+5, tr.top+5), (sx+5, tr.bottom-2), 2)
        else:
            charging = 55 <= trap["phase"] < 78
            if charging:
                draw_glow(screen, (tr.centerx, 525), danger, 13)
                pygame.draw.ellipse(screen, (255, 220, 150), (tr.x-5, 526, tr.w+10, 6), 2)
            elif trap["active"]:
                draw_glow(screen, (tr.centerx, tr.y+tr.h//2), danger, 18)
                for sy in range(tr.y, tr.bottom, 13):
                    wobble = int(math.sin(frame * 0.28 + sy) * 5)
                    pygame.draw.polygon(screen, danger, [(tr.centerx-7+wobble, sy+12), (tr.centerx+wobble, sy), (tr.centerx+8+wobble, sy+12)])
                pygame.draw.rect(screen, (255, 225, 175), (tr.centerx-3, tr.y+5, 6, max(5, tr.h-10)), border_radius=3)

    # Pieces dorees
    for coin in coins:
        r = coin.move(-camera, 0)

        if -30 < r.x < WIDTH + 30:
            draw_glow(screen, r.center, GOLD, 9)
            pygame.draw.ellipse(screen, (7, 8, 15), (r.x + 2, r.y + 4, 17, 17))
            pygame.draw.ellipse(screen, (125, 78, 20), (r.x - 1, r.y + 1, 18, 17))
            pygame.draw.ellipse(screen, (190, 125, 28), (r.x, r.y, 16, 16))
            pygame.draw.ellipse(screen, GOLD, (r.x + 2, r.y, 12, 14))
            shine_x = r.centerx + int(math.sin(frame * 0.09 + coin.x) * 3)
            pygame.draw.line(screen, (255, 250, 195),
                             (shine_x, r.y + 3), (shine_x, r.bottom - 3), 2)

    for enemy in enemies:
        enemy.draw(screen, camera)
    for boss in bosses:
        boss.draw(screen, camera)

    # Dessin des lasers
    for bullet in bullets:
        r = bullet["rect"].move(-camera, 0)
        glow = tuple(min(255, c + 45) for c in bullet["color"])
        draw_glow(screen, r.center, bullet["color"], max(5, r.h))
        pygame.draw.ellipse(screen, (*glow, 90), r.inflate(10, 8))
        pygame.draw.rect(screen, bullet["color"], r, border_radius=max(3, r.h // 2))
        pygame.draw.ellipse(screen, WHITE, (r.x + 2, r.y + 1, max(3, r.w - 4), max(2, r.h - 2)))

    for particle in particles:
        px = int(particle["x"] - camera)
        if -16 <= px <= WIDTH + 16:
            pygame.draw.circle(screen, particle["color"], (px, int(particle["y"])),
                               max(1, particle["size"] * max(1, particle["life"]) // 18))

    # Projectiles hostiles des boss, colores selon le monde.
    for shot in boss_projectiles:
        r = shot["rect"].move(-camera, 0)
        draw_glow(screen, r.center, shot["color"], 9)
        pygame.draw.ellipse(screen, shot["color"], r)
        pygame.draw.ellipse(screen, (255, 245, 220), r.inflate(-8, -5))

    player.draw(screen, camera)

    # Porte de sortie
    gate_x = WORLD_WIDTH - 72 - camera
    pygame.draw.rect(
        screen, (49, 37, 65),
        (gate_x, 435, 44, 100), border_radius=8
    )
    pygame.draw.rect(
        screen, GOLD,
        (gate_x + 7, 442, 30, 93),
        width=3, border_radius=6
    )
    pygame.draw.circle(screen, GOLD, (gate_x + 22, 470), 8)

    # Vignettage discret : contraste plus cinematographique sans masquer l'action.
    if state in ("playing", "paused", "gameover", "victory"):
        vignette = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        pygame.draw.rect(vignette, (0, 0, 8, 32), (0, 0, WIDTH, HEIGHT), 22)
        pygame.draw.rect(vignette, (0, 0, 8, 22), (0, 0, WIDTH, HEIGHT), 48)
        screen.blit(vignette, (0, 0))

    # Interface de jeu
    draw_panel(screen, (12, 12, 570, 104), alpha=220)
    world_name, level_number = current_level_name(level_index)
    draw_text(screen, f"Vies : {player.lives}", FONT, WHITE, 26, 18)
    draw_text(screen, f"Pieces totales : {total_coins}", FONT, GOLD, 150, 18)
    draw_text(screen, f"{world_name}  -  Niveau {level_number}/3",
              SMALL, WHITE, 260, 23)
    thresholds = [10, 20, 30] + list(range(50, 1001, 20))
    next_upgrade = next((n for n in thresholds if n > total_coins), None)
    upgrade_text = f"Arme niv. {weapon_level}"
    if next_upgrade is not None:
        upgrade_text += f" | prochaine amelioration : {next_upgrade} pieces"
    draw_text(screen, f"Pieces : {total_coins} | {upgrade_text}", SMALL, WHITE, 25, 57)
    draw_text(screen, "Fleches : bouger   Espace : double saut   X : tirer   C : pouvoir", SMALL,
              (190, 198, 220), 25, 82)
    difficulty_label = "DANGER I" if level_index < 3 else ("DANGER II" if level_index < 6 else ("DANGER III" if level_index < 9 else ("DANGER IV" if level_index < 12 else "DANGER V")))
    draw_text(screen, difficulty_label, SMALL, THEMES[world_index]["glow"], 500, 82)
    special_label = "POUVOIR PRET [C]" if player.special_cooldown <= 0 else f"POUVOIR : {player.special_cooldown // FPS + 1}s"
    draw_text(screen, special_label, SMALL, (255, 180, 100) if player.special_cooldown <= 0 else (175, 175, 195), 620, 82)
    # Barre de progression du niveau : donne un repere clair dans chaque monde.
    progress_rect = pygame.Rect(24, 111, 360, 5)
    pygame.draw.rect(screen, (24, 25, 39), progress_rect, border_radius=3)
    progress_width = int(progress_rect.w * clamp(player.rect.centerx / max(1, WORLD_WIDTH - 70), 0, 1))
    if progress_width > 0:
        pygame.draw.rect(screen, THEMES[world_index]["glow"],
                         (progress_rect.x, progress_rect.y, progress_width, progress_rect.h), border_radius=3)
    draw_button(screen, "pause_button", "PAUSE", (872, 14, 112, 38), pygame.mouse.get_pos())
    if player.weapon_flash > 0 and state == "playing":
        banner_alpha = min(230, player.weapon_flash * 3)
        banner = pygame.Surface((360, 44), pygame.SRCALPHA)
        banner.fill((20, 18, 38, banner_alpha))
        screen.blit(banner, (WIDTH//2 - 180, 150))
        pygame.draw.rect(screen, (100, 220, 255), (WIDTH//2 - 180, 150, 360, 44), 2, border_radius=10)
        draw_text(screen, f"ARME AMELIOREE ! NIVEAU {weapon_level}", FONT, GOLD,
                  WIDTH//2, 172, True)
    active_boss = next((boss for boss in bosses if boss.alive), None)
    if active_boss and state == "playing":
        draw_text(screen, f"BOSS : {active_boss.name} - phases et salves ! detruis-le pour ouvrir la sortie", SMALL, GOLD, WIDTH//2, 125, True)
    elif bosses and state == "playing":
        draw_text(screen, "Boss vaincu ! Rejoins la porte doree.", SMALL, GOLD, WIDTH//2, 125, True)

    # Menus interactifs
    mouse_pos = pygame.mouse.get_pos()
    if state in ("title", "level_select", "character_select", "character_select_pause", "paused", "gameover", "victory"):
        menu_background()

    if state == "title":
        draw_panel(screen, (175, 92, 650, 475), alpha=247)
        draw_text(screen, "UNE AVENTURE FANTASTIQUE", SMALL, (208, 143, 104), WIDTH//2, 126, True)
        draw_glow(screen, (WIDTH//2, 163), (255, 105, 45), 27)
        draw_text(screen, "CHEVALIER DU VOLCAN", TITLE_FONT, (70, 35, 29), WIDTH//2 + 2, 164, True)
        draw_text(screen, "CHEVALIER DU VOLCAN", TITLE_FONT, GOLD, WIDTH//2, 161, True)
        pygame.draw.line(screen, (155, 92, 57), (330, 193), (670, 193), 1)
        draw_text(screen, "15 NIVEAUX  •  5 MONDES  •  11 HEROS  •  PIEGES ET POUVOIRS", SMALL, WHITE, WIDTH//2, 215, True)
        draw_text(screen, f"HEROS DEBLOQUES : {unlocked_characters}/{len(CHARACTERS)}",
                  SMALL, GOLD, WIDTH//2, 242, True)
        world_name, level_number = current_level_name(level_index)
        draw_text(screen, f"PROGRESSION  /  {world_name.upper()}  /  NIVEAU {level_number}/3", SMALL, (218, 190, 162), WIDTH//2, 264, True)
        draw_button(screen, "start", "▶   JOUER", (350, 292, 300, 48), mouse_pos)
        draw_button(screen, "levels", "CHOISIR UN MONDE / NIVEAU", (300, 352, 400, 48), mouse_pos)
        draw_button(screen, "characters", "CHOISIR MON PERSONNAGE", (300, 412, 400, 48), mouse_pos)
        draw_text(screen, "FLECHES : BOUGER   ESPACE : DOUBLE SAUT   X : TIRER   C : POUVOIR   ECHAP : PAUSE", SMALL, (177, 182, 199), WIDTH//2, 505, True)
        draw_text(screen, "DIFFICULTE PROGRESSIVE  •  BOSS A PHASES MULTIPLES", SMALL, (255, 164, 111), WIDTH//2, 525, True)
        draw_text(screen, "PROGRESSION SAUVEGARDEE AUTOMATIQUEMENT", SMALL, (150, 132, 119), WIDTH//2, 548, True)

    elif state == "level_select":
        draw_panel(screen, (22, 40, 956, 570), alpha=235)
        draw_text(screen, "CHOISIR UN NIVEAU", BIG, GOLD, WIDTH//2, 78, True)
        draw_text(screen, "LES PORTES DE CHAQUE MONDE SE DEVERROUILLENT AU FIL DE TON AVENTURE", SMALL, (190, 181, 175), WIDTH//2, 111, True)
        for i in range(TOTAL_LEVELS):
            col, row = i % 5, i // 5
            world_name, number = current_level_name(i)
            unlocked = i <= completed_levels or i == level_index
            label = f"{i+1}. {world_name[:10]} {number}/3" if unlocked else f"{i+1}. VERROUILLE"
            draw_button(screen, f"level_{i}", label, (35 + col*190, 145 + row*92, 175, 58), mouse_pos, unlocked)
        draw_text(screen, "Termine un niveau pour debloquer le suivant.", SMALL, WHITE, WIDTH//2, 455, True)
        draw_button(screen, "back", "RETOUR", (400, 520, 200, 48), mouse_pos)

    elif state in ("character_select", "character_select_pause"):
        draw_panel(screen, (35, 35, 930, 580), alpha=238)
        heading = "CHOISIS TON PERSONNAGE" if state == "character_select" else "PERSONNAGE - PAUSE"
        draw_text(screen, heading, BIG, GOLD, WIDTH//2, 75, True)
        draw_text(screen, f"Debloques : {unlocked_characters}/{len(CHARACTERS)}  |  Termine des niveaux pour en obtenir d'autres",
                  SMALL, (205, 210, 230), WIDTH//2, 101, True)
        for i, (name, cape, armor) in enumerate(CHARACTERS):
            col, row = i % 4, i // 4
            x, y = 65 + col*225, 125 + row*132
            rect = pygame.Rect(x, y, 190, 108)
            button_prefix = "pausechar" if state == "character_select_pause" else "char"
            BUTTONS[f"{button_prefix}_{i}"] = rect
            unlocked = i < unlocked_characters
            fill = (67, 62, 96) if i == selected_character else (42, 42, 66)
            if not unlocked:
                fill = (32, 32, 42)
            pygame.draw.rect(screen, fill, rect, border_radius=10)
            pygame.draw.rect(screen, GOLD if i == selected_character else (120,120,150),
                             rect, 2, border_radius=10)
            if unlocked:
                draw_glow(screen, (x+92, y+43), armor, 11 if i == selected_character else 6)
            pygame.draw.polygon(screen, cape, [(x+78,y+24),(x+105,y+24),(x+115,y+61),(x+68,y+61)])
            pygame.draw.rect(screen, armor, (x+79,y+29,26,28), border_radius=6)
            pygame.draw.circle(screen, (238,194,151), (x+92,y+20), 12)
            label = name if unlocked else "VERROUILLE"
            draw_text(screen, label, SMALL, WHITE if unlocked else (145,145,155),
                      rect.centerx, y+78, True)
        if state == "character_select_pause":
            draw_button(screen, "back_pause", "RETOUR A LA PAUSE", (365, 535, 270, 45), mouse_pos)
        else:
            draw_button(screen, "back", "RETOUR AU MENU", (365, 535, 270, 45), mouse_pos)

    elif state == "paused":
        draw_panel(screen, (245, 92, 510, 480), alpha=248)
        draw_text(screen, "PAUSE", BIG, GOLD, WIDTH//2, 145, True)
        draw_text(screen, f"Personnage : {CHARACTERS[selected_character][0]}", FONT, WHITE, WIDTH//2, 205, True)
        draw_text(screen, f"Pieces cumulees : {total_coins}", SMALL, GOLD, WIDTH//2, 242, True)
        draw_text(screen, f"Niveau de l'arme : {weapon_level}", SMALL, (120, 225, 255), WIDTH//2, 268, True)
        draw_button(screen, "resume", "REPRENDRE LA PARTIE", (350, 300, 300, 44), mouse_pos)
        draw_button(screen, "pause_char", "CHANGER DE PERSONNAGE", (350, 358, 300, 44), mouse_pos)
        draw_button(screen, "main_menu", "MENU D'ACCUEIL", (350, 416, 300, 44), mouse_pos)
        draw_text(screen, "Ameliorations auto : 10, 20, 30, puis 50, 70, 90...", SMALL, (205, 210, 230), WIDTH//2, 484, True)
        draw_text(screen, "Echap / Entree : reprendre", SMALL, (165, 175, 200), WIDTH//2, 518, True)

    elif state == "gameover":
        draw_text(screen, "GAME OVER", BIG, RED, WIDTH//2, 245, True)
        draw_text(screen, f"Pieces ramassees : {player.coins}", FONT, WHITE, WIDTH//2, 305, True)
        draw_button(screen, "retry", "RECOMMENCER LE NIVEAU", (320, 365, 360, 48), mouse_pos)
        draw_button(screen, "game_menu", "MENU D'ACCUEIL", (370, 425, 260, 48), mouse_pos)

    elif state == "victory":
        draw_text(screen, "VICTOIRE !", BIG, GOLD, WIDTH//2, 220, True)
        world_name, level_number = current_level_name(level_index)
        draw_text(screen, f"{world_name} - niveau {level_number} termine !", FONT, WHITE, WIDTH//2, 285, True)
        draw_text(screen, f"Pieces totales : {total_coins} | Amelioration : {weapon_level}", FONT, GOLD, WIDTH//2, 330, True)
        draw_button(screen, "next", "NIVEAU SUIVANT", (350, 385, 300, 50), mouse_pos)

    # Commandes tactiles : visibles uniquement pendant le gameplay.
    if state == "playing":
        draw_touch_controls()

    # Finition d'image : bordure fine et repere lumineux discret.
    pygame.draw.rect(screen, (5, 6, 13), (0, 0, WIDTH, HEIGHT), 2)
    pygame.display.flip()
