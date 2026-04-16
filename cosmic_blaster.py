import pygame
import random
import math
import sys

# --- Constants ---
WIDTH, HEIGHT = 800, 600
FPS = 60
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 50, 50)
GREEN = (50, 255, 50)
BLUE = (80, 140, 255)
YELLOW = (255, 255, 50)
ORANGE = (255, 160, 40)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 200)
PURPLE = (160, 50, 255)
GREY = (150, 150, 150)
DARK_GREY = (60, 60, 60)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Cosmic Blaster")
clock = pygame.time.Clock()
font_sm = pygame.font.SysFont("consolas", 16)
font_md = pygame.font.SysFont("consolas", 24)
font_lg = pygame.font.SysFont("consolas", 48)


# --- Helper functions ---

def draw_pixel_rect(surface, color, x, y, w, h, pixel=4):
    """Draw a rectangle made of pixel blocks."""
    for px in range(0, w, pixel):
        for py in range(0, h, pixel):
            pygame.draw.rect(surface, color, (x + px, y + py, pixel, pixel))


def draw_pixel_circle(surface, color, cx, cy, radius, pixel=4):
    """Draw a circle made of pixel blocks."""
    for px in range(-radius, radius + 1, pixel):
        for py in range(-radius, radius + 1, pixel):
            if px * px + py * py <= radius * radius:
                pygame.draw.rect(surface, color, (cx + px, cy + py, pixel, pixel))


def draw_stars(surface, stars):
    """Draw scrolling starfield background."""
    for star in stars:
        brightness = star[2]
        color = (brightness, brightness, brightness)
        pygame.draw.rect(surface, color, (star[0], star[1], 2, 2))


def update_stars(stars):
    """Scroll stars downward."""
    for i, star in enumerate(stars):
        speed = star[2] // 80 + 1
        stars[i] = (star[0], (star[1] + speed) % HEIGHT, star[2])


def create_stars(count=120):
    return [(random.randint(0, WIDTH), random.randint(0, HEIGHT), random.randint(80, 255))
            for _ in range(count)]


# --- Bullet ---

class Bullet:
    def __init__(self, x, y, speed=-8, color=CYAN, damage=1, friendly=True):
        self.x = x
        self.y = y
        self.speed = speed
        self.color = color
        self.damage = damage
        self.friendly = friendly
        self.alive = True
        self.width = 4
        self.height = 10

    def update(self):
        self.y += self.speed
        if self.y < -20 or self.y > HEIGHT + 20:
            self.alive = False

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, (self.x - 2, self.y - 5, self.width, self.height))
        pygame.draw.rect(surface, WHITE, (self.x - 1, self.y - 3, 2, 6))

    def get_rect(self):
        return pygame.Rect(self.x - 2, self.y - 5, self.width, self.height)


# --- Ship (Player) ---

class Ship:
    def __init__(self):
        self.x = WIDTH // 2
        self.y = HEIGHT - 80
        self.speed = 5
        self.hp = 5
        self.max_hp = 5
        self.shoot_cooldown = 0
        self.shoot_delay = 10
        self.alive = True
        self.invincible = 0
        self.power_level = 1
        self.score = 0

    def update(self, keys):
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.x = max(20, self.x - self.speed)
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.x = min(WIDTH - 20, self.x + self.speed)
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.y = max(20, self.y - self.speed)
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.y = min(HEIGHT - 20, self.y + self.speed)
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
        if self.invincible > 0:
            self.invincible -= 1

    def shoot(self):
        bullets = []
        if self.shoot_cooldown <= 0:
            self.shoot_cooldown = self.shoot_delay
            bullets.append(Bullet(self.x, self.y - 16))
            if self.power_level >= 2:
                bullets.append(Bullet(self.x - 12, self.y - 10))
                bullets.append(Bullet(self.x + 12, self.y - 10))
            if self.power_level >= 3:
                bullets.append(Bullet(self.x - 8, self.y - 8, speed=-9, color=YELLOW, damage=2))
                bullets.append(Bullet(self.x + 8, self.y - 8, speed=-9, color=YELLOW, damage=2))
        return bullets

    def take_damage(self, amount=1):
        if self.invincible > 0:
            return
        self.hp -= amount
        self.invincible = 60
        if self.hp <= 0:
            self.alive = False

    def draw(self, surface):
        if self.invincible > 0 and self.invincible % 6 < 3:
            return
        # Ship body
        draw_pixel_rect(surface, BLUE, self.x - 4, self.y - 16, 8, 32, 4)
        # Wings
        draw_pixel_rect(surface, BLUE, self.x - 16, self.y - 4, 32, 12, 4)
        # Cockpit
        draw_pixel_rect(surface, CYAN, self.x - 4, self.y - 12, 8, 8, 4)
        # Engine glow
        if random.random() > 0.3:
            draw_pixel_rect(surface, ORANGE, self.x - 4, self.y + 16, 8, 4, 4)
            draw_pixel_rect(surface, YELLOW, self.x - 4, self.y + 12, 8, 4, 2)

    def get_rect(self):
        return pygame.Rect(self.x - 16, self.y - 16, 32, 32)


# --- Asteroid ---

class Asteroid:
    def __init__(self):
        self.x = random.randint(30, WIDTH - 30)
        self.y = -40
        self.speed = random.uniform(1.5, 3.5)
        self.size = random.choice([12, 16, 20])
        self.hp = self.size // 4
        self.alive = True
        self.rotation = random.uniform(0, 360)
        self.rot_speed = random.uniform(-2, 2)
        self.color = random.choice([GREY, DARK_GREY, (120, 100, 80)])

    def update(self):
        self.y += self.speed
        self.rotation += self.rot_speed
        if self.y > HEIGHT + 40:
            self.alive = False

    def take_hit(self, damage=1):
        self.hp -= damage
        if self.hp <= 0:
            self.alive = False
            return True
        return False

    def draw(self, surface):
        draw_pixel_circle(surface, self.color, int(self.x), int(self.y), self.size, 4)
        draw_pixel_circle(surface, DARK_GREY, int(self.x) - 4, int(self.y) - 4, self.size // 3, 4)

    def get_rect(self):
        return pygame.Rect(self.x - self.size, self.y - self.size, self.size * 2, self.size * 2)

    def get_score(self):
        return self.size * 5


# --- Quasar ---

class Quasar:
    def __init__(self):
        self.x = random.randint(60, WIDTH - 60)
        self.y = -30
        self.speed = 2.0
        self.hp = 3
        self.alive = True
        self.shoot_timer = random.randint(40, 80)
        self.pulse = 0

    def update(self):
        self.y += self.speed
        self.pulse = (self.pulse + 4) % 360
        self.shoot_timer -= 1
        if self.y > HEIGHT + 30:
            self.alive = False

    def should_shoot(self):
        if self.shoot_timer <= 0:
            self.shoot_timer = random.randint(60, 100)
            return True
        return False

    def get_bullets(self):
        bullets = []
        for angle in [80, 90, 100]:
            rad = math.radians(angle)
            bx = math.cos(rad) * 5
            by = math.sin(rad) * 5
            bullets.append(Bullet(self.x, self.y + 10, speed=by, color=MAGENTA, damage=1, friendly=False))
        return bullets

    def take_hit(self, damage=1):
        self.hp -= damage
        if self.hp <= 0:
            self.alive = False
            return True
        return False

    def draw(self, surface):
        glow = int(abs(math.sin(math.radians(self.pulse))) * 80)
        color = (160 + glow, 50, 255)
        draw_pixel_circle(surface, color, int(self.x), int(self.y), 14, 4)
        draw_pixel_circle(surface, WHITE, int(self.x), int(self.y), 6, 4)
        # Energy ring
        ring_r = 18 + int(math.sin(math.radians(self.pulse)) * 4)
        pygame.draw.circle(surface, MAGENTA, (int(self.x), int(self.y)), ring_r, 2)

    def get_rect(self):
        return pygame.Rect(self.x - 14, self.y - 14, 28, 28)

    def get_score(self):
        return 150


# --- Comet ---

class Comet:
    def __init__(self):
        self.x = random.randint(40, WIDTH - 40)
        self.y = -30
        self.speed = random.uniform(4.0, 6.0)
        self.hp = 2
        self.alive = True
        self.trail = []

    def update(self):
        self.trail.append((self.x, self.y))
        if len(self.trail) > 12:
            self.trail.pop(0)
        self.y += self.speed
        self.x += math.sin(self.y * 0.03) * 2
        if self.y > HEIGHT + 30:
            self.alive = False

    def take_hit(self, damage=1):
        self.hp -= damage
        if self.hp <= 0:
            self.alive = False
            return True
        return False

    def draw(self, surface):
        # Trail
        for i, pos in enumerate(self.trail):
            alpha = int((i / len(self.trail)) * 200) if self.trail else 0
            size = max(2, int((i / max(len(self.trail), 1)) * 8))
            color = (255, 160 + min(alpha // 3, 80), alpha // 4)
            draw_pixel_circle(surface, color, int(pos[0]), int(pos[1]), size // 2, 2)
        # Head
        draw_pixel_circle(surface, ORANGE, int(self.x), int(self.y), 8, 4)
        draw_pixel_circle(surface, YELLOW, int(self.x), int(self.y), 4, 2)

    def get_rect(self):
        return pygame.Rect(self.x - 8, self.y - 8, 16, 16)

    def get_score(self):
        return 100


# --- BlackHole ---

class BlackHole:
    def __init__(self):
        self.x = random.randint(80, WIDTH - 80)
        self.y = -50
        self.speed = 0.8
        self.radius = 36
        self.pull_radius = 140
        self.hp = 10
        self.alive = True
        self.angle = 0
        self.lifetime = 600

    def update(self):
        self.y += self.speed
        self.angle = (self.angle + 3) % 360
        self.lifetime -= 1
        if self.y > HEIGHT + 60 or self.lifetime <= 0:
            self.alive = False

    def pull_entity(self, entity):
        """Apply gravitational pull toward the black hole."""
        dx = self.x - entity.x
        dy = self.y - entity.y
        dist = math.sqrt(dx * dx + dy * dy)
        if dist < self.pull_radius and dist > 5:
            force = 2.0 / (dist / 40)
            entity.x += dx / dist * force
            entity.y += dy / dist * force

    def take_hit(self, damage=1):
        self.hp -= damage
        if self.hp <= 0:
            self.alive = False
            return True
        return False

    def draw(self, surface):
        # Accretion disk
        for i in range(8):
            a = math.radians(self.angle + i * 45)
            rx = int(self.x + math.cos(a) * (self.radius + 8))
            ry = int(self.y + math.sin(a) * (self.radius + 8))
            color = PURPLE if i % 2 == 0 else MAGENTA
            draw_pixel_circle(surface, color, rx, ry, 4, 2)
        # Outer ring
        pygame.draw.circle(surface, PURPLE, (int(self.x), int(self.y)), self.radius, 3)
        # Core
        draw_pixel_circle(surface, (20, 0, 40), int(self.x), int(self.y), self.radius - 8, 4)
        draw_pixel_circle(surface, BLACK, int(self.x), int(self.y), self.radius - 16, 4)
        # Pull radius indicator
        pygame.draw.circle(surface, (40, 20, 60), (int(self.x), int(self.y)), self.pull_radius, 1)

    def get_rect(self):
        return pygame.Rect(self.x - self.radius, self.y - self.radius,
                           self.radius * 2, self.radius * 2)

    def get_score(self):
        return 500


# --- Station (pickup) ---

class Station:
    def __init__(self, kind="heal"):
        self.x = random.randint(40, WIDTH - 40)
        self.y = -20
        self.speed = 1.5
        self.kind = kind  # "heal", "power", "shield"
        self.alive = True
        self.bob = 0

    def update(self):
        self.y += self.speed
        self.bob = (self.bob + 3) % 360
        if self.y > HEIGHT + 20:
            self.alive = False

    def apply(self, ship):
        if self.kind == "heal":
            ship.hp = min(ship.hp + 2, ship.max_hp)
        elif self.kind == "power":
            ship.power_level = min(ship.power_level + 1, 3)
        elif self.kind == "shield":
            ship.invincible = 180

    def draw(self, surface):
        bob_offset = int(math.sin(math.radians(self.bob)) * 3)
        y = int(self.y) + bob_offset
        if self.kind == "heal":
            color = GREEN
            # Cross shape
            draw_pixel_rect(surface, color, self.x - 2, y - 8, 4, 16, 4)
            draw_pixel_rect(surface, color, self.x - 8, y - 2, 16, 4, 4)
        elif self.kind == "power":
            color = YELLOW
            # Arrow up shape
            draw_pixel_rect(surface, color, self.x - 2, y - 8, 4, 16, 4)
            draw_pixel_rect(surface, color, self.x - 8, y - 8, 4, 4, 4)
            draw_pixel_rect(surface, color, self.x + 4, y - 8, 4, 4, 4)
        elif self.kind == "shield":
            color = CYAN
            draw_pixel_circle(surface, color, self.x, y, 10, 4)
            draw_pixel_circle(surface, BLACK, self.x, y, 6, 4)
        # Border box
        pygame.draw.rect(surface, WHITE, (self.x - 12, y - 12, 24, 24), 1)

    def get_rect(self):
        return pygame.Rect(self.x - 12, self.y - 12, 24, 24)


# --- Boss ---

class Boss:
    def __init__(self, level=1):
        self.x = WIDTH // 2
        self.y = -60
        self.target_y = 80
        self.speed = 1.0
        self.hp = 20 + level * 10
        self.max_hp = self.hp
        self.alive = True
        self.phase = 0
        self.timer = 0
        self.shoot_timer = 0
        self.direction = 1
        self.move_speed = 2
        self.entering = True
        self.level = level

    def update(self):
        if self.entering:
            self.y += 1
            if self.y >= self.target_y:
                self.entering = False
            return

        self.timer += 1
        self.shoot_timer -= 1

        # Move side to side
        self.x += self.move_speed * self.direction
        if self.x > WIDTH - 60:
            self.direction = -1
        elif self.x < 60:
            self.direction = 1

        # Phase changes based on HP
        if self.hp < self.max_hp * 0.3:
            self.phase = 2
            self.move_speed = 3.5
        elif self.hp < self.max_hp * 0.6:
            self.phase = 1
            self.move_speed = 2.5

    def should_shoot(self):
        if self.entering:
            return False
        if self.shoot_timer <= 0:
            self.shoot_timer = max(15, 40 - self.phase * 10)
            return True
        return False

    def get_bullets(self):
        bullets = []
        if self.phase == 0:
            bullets.append(Bullet(self.x, self.y + 30, speed=4, color=RED, damage=1, friendly=False))
        elif self.phase == 1:
            for offset in [-20, 0, 20]:
                bullets.append(Bullet(self.x + offset, self.y + 30, speed=4.5, color=RED, damage=1, friendly=False))
        else:
            for angle in range(60, 121, 15):
                rad = math.radians(angle)
                spd_x = math.cos(rad) * 3
                spd_y = math.sin(rad) * 3
                b = Bullet(self.x, self.y + 30, speed=spd_y, color=ORANGE, damage=1, friendly=False)
                b.speed_x = spd_x
                bullets.append(b)
        return bullets

    def take_hit(self, damage=1):
        self.hp -= damage
        if self.hp <= 0:
            self.alive = False
            return True
        return False

    def draw(self, surface):
        # Main body
        draw_pixel_rect(surface, RED, self.x - 32, self.y - 20, 64, 40, 4)
        # Wings
        draw_pixel_rect(surface, (180, 30, 30), self.x - 48, self.y - 8, 16, 24, 4)
        draw_pixel_rect(surface, (180, 30, 30), self.x + 32, self.y - 8, 16, 24, 4)
        # Cockpit
        draw_pixel_rect(surface, DARK_GREY, self.x - 12, self.y - 16, 24, 16, 4)
        draw_pixel_rect(surface, YELLOW, self.x - 8, self.y - 12, 16, 8, 4)
        # Cannons
        draw_pixel_rect(surface, DARK_GREY, self.x - 24, self.y + 16, 8, 12, 4)
        draw_pixel_rect(surface, DARK_GREY, self.x + 16, self.y + 16, 8, 12, 4)
        # Engine glow on phase 2
        if self.phase == 2 and random.random() > 0.4:
            draw_pixel_rect(surface, ORANGE, self.x - 20, self.y - 24, 8, 4, 2)
            draw_pixel_rect(surface, ORANGE, self.x + 12, self.y - 24, 8, 4, 2)

        # HP bar
        bar_width = 80
        bar_x = self.x - bar_width // 2
        bar_y = self.y - 32
        hp_ratio = self.hp / self.max_hp
        pygame.draw.rect(surface, DARK_GREY, (bar_x, bar_y, bar_width, 6))
        bar_color = GREEN if hp_ratio > 0.5 else YELLOW if hp_ratio > 0.25 else RED
        pygame.draw.rect(surface, bar_color, (bar_x, bar_y, int(bar_width * hp_ratio), 6))
        pygame.draw.rect(surface, WHITE, (bar_x, bar_y, bar_width, 6), 1)

    def get_rect(self):
        return pygame.Rect(self.x - 48, self.y - 20, 96, 48)

    def get_score(self):
        return 1000 * self.level


# --- Explosion effect ---

class Explosion:
    def __init__(self, x, y, size=12):
        self.x = x
        self.y = y
        self.size = size
        self.frame = 0
        self.max_frames = 15
        self.alive = True

    def update(self):
        self.frame += 1
        if self.frame >= self.max_frames:
            self.alive = False

    def draw(self, surface):
        progress = self.frame / self.max_frames
        radius = int(self.size * (1 + progress))
        alpha = 1.0 - progress
        if progress < 0.4:
            color = (255, 255, int(200 * alpha))
        elif progress < 0.7:
            color = (255, int(160 * alpha), 0)
        else:
            color = (int(200 * alpha), int(50 * alpha), 0)
        draw_pixel_circle(surface, color, int(self.x), int(self.y), radius, 4)


# --- HUD ---

def draw_hud(surface, ship, wave):
    # HP bar
    bar_w = 120
    pygame.draw.rect(surface, DARK_GREY, (10, 10, bar_w, 12))
    hp_ratio = ship.hp / ship.max_hp
    bar_color = GREEN if hp_ratio > 0.5 else YELLOW if hp_ratio > 0.25 else RED
    pygame.draw.rect(surface, bar_color, (10, 10, int(bar_w * hp_ratio), 12))
    pygame.draw.rect(surface, WHITE, (10, 10, bar_w, 12), 1)

    hp_text = font_sm.render(f"HP {ship.hp}/{ship.max_hp}", True, WHITE)
    surface.blit(hp_text, (140, 8))

    # Score
    score_text = font_sm.render(f"SCORE: {ship.score}", True, WHITE)
    surface.blit(score_text, (WIDTH - 180, 10))

    # Wave
    wave_text = font_sm.render(f"WAVE {wave}", True, YELLOW)
    surface.blit(wave_text, (WIDTH // 2 - 30, 10))

    # Power level
    power_text = font_sm.render(f"PWR: {'|' * ship.power_level}", True, CYAN)
    surface.blit(power_text, (10, 28))


# --- Game states ---

def title_screen():
    stars = create_stars()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    return
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

        update_stars(stars)
        screen.fill(BLACK)
        draw_stars(screen, stars)

        title = font_lg.render("COSMIC BLASTER", True, CYAN)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 180))

        sub = font_md.render("A Pixel Space Shooter", True, PURPLE)
        screen.blit(sub, (WIDTH // 2 - sub.get_width() // 2, 240))

        prompt = font_sm.render("Press ENTER or SPACE to start", True, WHITE)
        screen.blit(prompt, (WIDTH // 2 - prompt.get_width() // 2, 340))

        controls = [
            "WASD / Arrow Keys — Move",
            "SPACE — Shoot",
            "ESC — Quit",
        ]
        for i, line in enumerate(controls):
            text = font_sm.render(line, True, GREY)
            screen.blit(text, (WIDTH // 2 - text.get_width() // 2, 400 + i * 22))

        pygame.display.flip()
        clock.tick(FPS)


def game_over_screen(score):
    stars = create_stars()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    return True
                if event.key == pygame.K_ESCAPE:
                    return False

        update_stars(stars)
        screen.fill(BLACK)
        draw_stars(screen, stars)

        go_text = font_lg.render("GAME OVER", True, RED)
        screen.blit(go_text, (WIDTH // 2 - go_text.get_width() // 2, 200))

        score_text = font_md.render(f"Final Score: {score}", True, YELLOW)
        screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 270))

        prompt = font_sm.render("ENTER to retry | ESC to quit", True, WHITE)
        screen.blit(prompt, (WIDTH // 2 - prompt.get_width() // 2, 340))

        pygame.display.flip()
        clock.tick(FPS)


# --- Main game loop ---

def game_loop():
    ship = Ship()
    stars = create_stars()
    bullets = []
    enemies = []
    stations = []
    explosions = []
    boss = None

    wave = 1
    wave_timer = 0
    spawn_timer = 0
    enemies_spawned = 0
    enemies_per_wave = 8
    boss_wave = False
    wave_complete = False
    wave_message_timer = 0

    running = True
    while running:
        # --- Events ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return ship.score

        keys = pygame.key.get_pressed()

        # --- Update ---
        update_stars(stars)
        ship.update(keys)

        # Shooting
        if keys[pygame.K_SPACE]:
            new_bullets = ship.shoot()
            bullets.extend(new_bullets)

        # Wave management
        if wave_message_timer > 0:
            wave_message_timer -= 1

        boss_wave = (wave % 5 == 0)

        if boss_wave and boss is None and not wave_complete:
            if enemies_spawned == 0:
                boss = Boss(level=wave // 5)
                enemies_spawned = 1
                wave_message_timer = 120
        elif not boss_wave and not wave_complete:
            spawn_timer -= 1
            if spawn_timer <= 0 and enemies_spawned < enemies_per_wave:
                spawn_timer = max(20, 60 - wave * 3)
                enemies_spawned += 1

                roll = random.random()
                if roll < 0.35:
                    enemies.append(Asteroid())
                elif roll < 0.55:
                    enemies.append(Comet())
                elif roll < 0.75:
                    enemies.append(Quasar())
                elif roll < 0.85 and wave >= 3:
                    enemies.append(BlackHole())
                else:
                    enemies.append(Asteroid())

                # Occasional station drop
                if random.random() < 0.08:
                    kind = random.choice(["heal", "power", "shield"])
                    stations.append(Station(kind))

        # Check if wave is done
        if not boss_wave and enemies_spawned >= enemies_per_wave and len(enemies) == 0:
            wave_complete = True
        if boss_wave and boss is not None and not boss.alive:
            wave_complete = True
            boss = None

        if wave_complete:
            wave_timer += 1
            if wave_timer > 90:
                wave += 1
                wave_timer = 0
                enemies_spawned = 0
                enemies_per_wave = 8 + wave * 2
                wave_complete = False
                wave_message_timer = 120

        # Update bullets
        for b in bullets:
            b.update()
            if hasattr(b, 'speed_x'):
                b.x += b.speed_x
        bullets = [b for b in bullets if b.alive]

        # Update enemies
        for e in enemies:
            e.update()
            # Quasar shooting
            if isinstance(e, Quasar) and e.should_shoot():
                bullets.extend(e.get_bullets())
        enemies = [e for e in enemies if e.alive]

        # Update boss
        if boss:
            boss.update()
            if boss.should_shoot():
                bullets.extend(boss.get_bullets())

        # Update stations
        for s in stations:
            s.update()
        stations = [s for s in stations if s.alive]

        # Update explosions
        for ex in explosions:
            ex.update()
        explosions = [ex for ex in explosions if ex.alive]

        # Black hole gravity
        for e in enemies:
            if isinstance(e, BlackHole):
                e.pull_entity(ship)

        # --- Collisions ---

        # Player bullets vs enemies
        for b in bullets:
            if not b.friendly:
                continue
            for e in enemies:
                if b.alive and e.alive and b.get_rect().colliderect(e.get_rect()):
                    b.alive = False
                    if e.take_hit(b.damage):
                        ship.score += e.get_score()
                        explosions.append(Explosion(e.x, e.y, getattr(e, 'size', 14)))
            # Bullets vs boss
            if boss and boss.alive and b.alive and b.get_rect().colliderect(boss.get_rect()):
                b.alive = False
                if boss.take_hit(b.damage):
                    ship.score += boss.get_score()
                    explosions.append(Explosion(boss.x, boss.y, 40))

        # Enemy bullets vs player
        for b in bullets:
            if b.friendly:
                continue
            if b.alive and b.get_rect().colliderect(ship.get_rect()):
                b.alive = False
                ship.take_damage(b.damage)

        # Enemy collision with player
        for e in enemies:
            if e.alive and e.get_rect().colliderect(ship.get_rect()):
                ship.take_damage(1)
                if isinstance(e, (Asteroid, Comet)):
                    e.alive = False
                    explosions.append(Explosion(e.x, e.y))

        # Boss collision with player
        if boss and boss.alive and boss.get_rect().colliderect(ship.get_rect()):
            ship.take_damage(2)

        # Station pickup
        for s in stations:
            if s.alive and s.get_rect().colliderect(ship.get_rect()):
                s.apply(ship)
                s.alive = False
                ship.score += 50

        # Check player death
        if not ship.alive:
            explosions.append(Explosion(ship.x, ship.y, 24))
            return ship.score

        # --- Draw ---
        screen.fill(BLACK)
        draw_stars(screen, stars)

        for s in stations:
            s.draw(screen)
        for e in enemies:
            e.draw(screen)
        if boss:
            boss.draw(screen)
        for b in bullets:
            b.draw(screen)
        ship.draw(screen)
        for ex in explosions:
            ex.draw(screen)

        draw_hud(screen, ship, wave)

        # Wave announcement
        if wave_message_timer > 60:
            if boss_wave:
                text = font_md.render(f"BOSS INCOMING!", True, RED)
            else:
                text = font_md.render(f"WAVE {wave}", True, YELLOW)
            screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 3))

        pygame.display.flip()
        clock.tick(FPS)

    return ship.score


# --- Entry point ---

def main():
    while True:
        title_screen()
        score = game_loop()
        if not game_over_screen(score):
            break
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
