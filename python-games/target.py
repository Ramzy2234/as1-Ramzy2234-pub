import pygame
import sys
import random
import math
import time

pygame.init()

# ─── Constants ──────────────────────────────────────────────
WIDTH, HEIGHT = 700, 700
GRID_SIZE     = 10
CELL          = 48
GRID_X        = (WIDTH - GRID_SIZE * CELL) // 2
GRID_Y        = 160
MAX_SHOTS     = 7
FPS           = 60

# ─── Colours ────────────────────────────────────────────────
BLACK       = (0,    0,    0)
BG          = (5,    8,    20)
GRID_LINE   = (20,   40,   80)
WATER       = (10,   20,   50)
WATER_LIGHT = (15,   30,   70)
HIT_COL     = (255,  80,   80)
NEAR_COL    = (255,  200,  50)
MISS_COL    = (80,   120,  200)
TARGET_COL  = (255,  60,   60)
CYAN        = (0,    220,  255)
WHITE       = (255,  255,  255)
GREEN       = (80,   255,  140)
GOLD        = (255,  215,  0)
RED         = (255,  60,   60)
DIM         = (60,   70,   90)
RADAR_GREEN = (0,    255,  100)

# ─── Fonts ──────────────────────────────────────────────────
FONT_TITLE = pygame.font.SysFont("consolas", 32, bold=True)
FONT_MID   = pygame.font.SysFont("consolas", 20, bold=True)
FONT_SM    = pygame.font.SysFont("consolas", 15)
FONT_COORD = pygame.font.SysFont("consolas", 13)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("RAMZ — Naval Strike")
clock  = pygame.time.Clock()

# ─── Particle system ────────────────────────────────────────
class Particle:
    def __init__(self, x, y, col):
        angle  = random.uniform(0, math.tau)
        speed  = random.uniform(1, 5)
        self.x = x
        self.y = y
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.life   = random.randint(20, 50)
        self.maxlife = self.life
        self.col = col
        self.r   = random.randint(2, 5)

    def update(self):
        self.x  += self.vx
        self.y  += self.vy
        self.vy += 0.15   # gravity
        self.life -= 1

    def draw(self, surface):
        alpha = int(255 * self.life / self.maxlife)
        s = pygame.Surface((self.r * 2, self.r * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*self.col, alpha), (self.r, self.r), self.r)
        surface.blit(s, (int(self.x) - self.r, int(self.y) - self.r))

particles = []

def spawn_explosion(cx, cy, col, count=40):
    for _ in range(count):
        particles.append(Particle(cx, cy, col))

# ─── Ripple system ──────────────────────────────────────────
class Ripple:
    def __init__(self, x, y, col):
        self.x = x; self.y = y
        self.r = 5; self.max_r = 40
        self.col = col
        self.alpha = 200

    def update(self):
        self.r     += 2
        self.alpha -= 10

    def alive(self):
        return self.alpha > 0

    def draw(self, surface):
        s = pygame.Surface((self.max_r * 2 + 4, self.max_r * 2 + 4), pygame.SRCALPHA)
        pygame.draw.circle(s, (*self.col, max(0, self.alpha)),
                           (self.max_r + 2, self.max_r + 2), self.r, 2)
        surface.blit(s, (self.x - self.max_r - 2, self.y - self.max_r - 2))

ripples = []

# ─── Radar sweep ────────────────────────────────────────────
radar_angle = 0

def draw_radar(surface, shots_left):
    cx, cy, rad = 90, HEIGHT - 100, 65
    # Background
    pygame.draw.circle(surface, (5, 15, 5), (cx, cy), rad)
    pygame.draw.circle(surface, (0, 80, 0), (cx, cy), rad, 2)
    for r in [rad // 3, 2 * rad // 3]:
        pygame.draw.circle(surface, (0, 50, 0), (cx, cy), r, 1)
    pygame.draw.line(surface, (0, 50, 0), (cx - rad, cy), (cx + rad, cy), 1)
    pygame.draw.line(surface, (0, 50, 0), (cx, cy - rad), (cx, cy + rad), 1)

    # Sweep
    sweep_surf = pygame.Surface((rad * 2, rad * 2), pygame.SRCALPHA)
    for i in range(30):
        a = math.radians(radar_angle - i * 3)
        alpha = max(0, 120 - i * 4)
        end_x = rad + int(math.cos(a) * rad)
        end_y = rad + int(math.sin(a) * rad)
        pygame.draw.line(sweep_surf, (0, 255, 100, alpha),
                         (rad, rad), (end_x, end_y), 2)
    surface.blit(sweep_surf, (cx - rad, cy - rad))

    # Shots indicator dots
    for i in range(MAX_SHOTS):
        dot_col = GREEN if i < shots_left else RED
        dx = cx - (MAX_SHOTS // 2) * 10 + i * 10
        pygame.draw.circle(surface, dot_col, (dx, cy + rad + 12), 4)

    label = FONT_SM.render("RADAR", True, RADAR_GREEN)
    surface.blit(label, (cx - label.get_width() // 2, cy - rad - 20))

# ─── Draw water grid ────────────────────────────────────────
wave_tick = 0

def draw_grid(surface, shots_fired, target_x, target_y, revealed):
    global wave_tick
    wave_tick += 0.05

    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            rx = GRID_X + col * CELL
            ry = GRID_Y + row * CELL
            wave = int(math.sin(wave_tick + col * 0.5 + row * 0.3) * 3)
            base = WATER_LIGHT if (col + row) % 2 == 0 else WATER
            pygame.draw.rect(surface, base, (rx, ry + wave, CELL, CELL))
            pygame.draw.rect(surface, GRID_LINE, (rx, ry, CELL, CELL), 1)

    # Column labels (A–J)
    for col in range(GRID_SIZE):
        lbl = FONT_COORD.render(chr(65 + col), True, DIM)
        surface.blit(lbl, (GRID_X + col * CELL + CELL // 2 - lbl.get_width() // 2,
                           GRID_Y - 18))
    # Row labels (1–10)
    for row in range(GRID_SIZE):
        lbl = FONT_COORD.render(str(row + 1), True, DIM)
        surface.blit(lbl, (GRID_X - 20, GRID_Y + row * CELL + CELL // 2 - lbl.get_height() // 2))

    # Draw shot results
    for sx, sy, result in shots_fired:
        cx = GRID_X + sx * CELL + CELL // 2
        cy = GRID_Y + sy * CELL + CELL // 2
        if result == "hit":
            pygame.draw.rect(surface, HIT_COL,
                             (GRID_X + sx * CELL + 4, GRID_Y + sy * CELL + 4,
                              CELL - 8, CELL - 8))
            pygame.draw.line(surface, WHITE,
                             (GRID_X + sx * CELL + 4, GRID_Y + sy * CELL + 4),
                             (GRID_X + sx * CELL + CELL - 4, GRID_Y + sy * CELL + CELL - 4), 3)
            pygame.draw.line(surface, WHITE,
                             (GRID_X + sx * CELL + CELL - 4, GRID_Y + sy * CELL + 4),
                             (GRID_X + sx * CELL + 4, GRID_Y + sy * CELL + CELL - 4), 3)
        elif result == "near":
            pygame.draw.circle(surface, NEAR_COL, (cx, cy), CELL // 2 - 4, 3)
            pygame.draw.circle(surface, NEAR_COL, (cx, cy), 5)
        elif result == "miss":
            pygame.draw.circle(surface, MISS_COL, (cx, cy), 6, 2)

    # Reveal target after game over
    if revealed:
        tx = GRID_X + target_x * CELL + CELL // 2
        ty = GRID_Y + target_y * CELL + CELL // 2
        pulse = int(abs(math.sin(wave_tick * 3)) * 8)
        pygame.draw.circle(surface, TARGET_COL, (tx, ty), 10 + pulse, 3)
        lbl = FONT_SM.render("TARGET", True, TARGET_COL)
        surface.blit(lbl, (tx - lbl.get_width() // 2, ty - 24))

# ─── HUD ────────────────────────────────────────────────────
def draw_hud(surface, shots_left, score, message, message_col, level):
    # Top bar
    pygame.draw.rect(surface, (8, 12, 30), (0, 0, WIDTH, 140))
    pygame.draw.line(surface, CYAN, (0, 139), (WIDTH, 139), 2)

    title = FONT_TITLE.render("⚓  NAVAL STRIKE", True, CYAN)
    surface.blit(title, (WIDTH // 2 - title.get_width() // 2, 10))

    lvl_t = FONT_MID.render(f"MISSION {level}", True, GOLD)
    surface.blit(lvl_t, (WIDTH // 2 - lvl_t.get_width() // 2, 48))

    score_t = FONT_MID.render(f"SCORE: {score}", True, WHITE)
    surface.blit(score_t, (WIDTH - score_t.get_width() - 20, 10))

    shots_t = FONT_SM.render(f"TORPEDOES: {shots_left}", True,
                               GREEN if shots_left > 2 else RED)
    surface.blit(shots_t, (WIDTH - shots_t.get_width() - 20, 42))

    if message:
        msg_t = FONT_MID.render(message, True, message_col)
        surface.blit(msg_t, (WIDTH // 2 - msg_t.get_width() // 2, 100))

    # Bottom bar
    pygame.draw.rect(surface, (8, 12, 30), (0, HEIGHT - 50, WIDTH, 50))
    pygame.draw.line(surface, CYAN, (0, HEIGHT - 50), (WIDTH, HEIGHT - 50), 2)
    hint = FONT_SM.render("Click a grid cell to fire  •  ESC to quit", True, DIM)
    surface.blit(hint, (WIDTH // 2 - hint.get_width() // 2, HEIGHT - 30))

# ─── Hover highlight ────────────────────────────────────────
def draw_hover(surface, mx, my):
    col = (mx - GRID_X) // CELL
    row = (my - GRID_Y) // CELL
    if 0 <= col < GRID_SIZE and 0 <= row < GRID_SIZE:
        rx = GRID_X + col * CELL
        ry = GRID_Y + row * CELL
        s = pygame.Surface((CELL, CELL), pygame.SRCALPHA)
        pygame.draw.rect(s, (0, 220, 255, 40), (0, 0, CELL, CELL))
        pygame.draw.rect(s, (0, 220, 255, 120), (0, 0, CELL, CELL), 2)
        surface.blit(s, (rx, ry))
        coord = f"{chr(65 + col)}{row + 1}"
        lbl = FONT_SM.render(coord, True, CYAN)
        surface.blit(lbl, (rx + CELL // 2 - lbl.get_width() // 2,
                           ry + CELL // 2 - lbl.get_height() // 2))
        return col, row
    return None, None

# ─── Splash ─────────────────────────────────────────────────
def splash(mission):
    for alpha in range(0, 256, 5):
        screen.fill(BG)
        t1 = FONT_TITLE.render(f"MISSION  {mission}", True, CYAN)
        t2 = FONT_MID.render("Locate and destroy the enemy vessel", True, WHITE)
        t3 = FONT_SM.render("Click the grid to fire torpedoes", True, DIM)
        for t in [t1, t2, t3]:
            t.set_alpha(alpha)
        screen.blit(t1, (WIDTH // 2 - t1.get_width() // 2, HEIGHT // 3))
        screen.blit(t2, (WIDTH // 2 - t2.get_width() // 2, HEIGHT // 2))
        screen.blit(t3, (WIDTH // 2 - t3.get_width() // 2, HEIGHT * 2 // 3))
        pygame.display.flip()
        clock.tick(60)
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()

    waiting = True
    while waiting:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if e.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                waiting = False

# ─── Game over ──────────────────────────────────────────────
def game_over_screen(won, score, mission):
    msg  = "TARGET DESTROYED!" if won else "MISSION FAILED"
    col  = GOLD if won else RED
    for alpha in range(0, 256, 4):
        screen.fill(BG)
        t1 = FONT_TITLE.render(msg, True, col)
        t2 = FONT_MID.render(f"Score: {score}", True, WHITE)
        t3 = FONT_SM.render("Press any key to continue", True, DIM)
        for t in [t1, t2, t3]:
            t.set_alpha(alpha)
        screen.blit(t1, (WIDTH // 2 - t1.get_width() // 2, HEIGHT // 3))
        screen.blit(t2, (WIDTH // 2 - t2.get_width() // 2, HEIGHT // 2))
        screen.blit(t3, (WIDTH // 2 - t3.get_width() // 2, HEIGHT * 2 // 3))
        pygame.display.flip()
        clock.tick(60)
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()

    waiting = True
    while waiting:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if e.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                waiting = False

# ─── Final screen ───────────────────────────────────────────
def final_screen(total_score, missions):
    screen.fill(BG)
    lines = [
        (FONT_TITLE, "⚓  CAMPAIGN COMPLETE", GOLD),
        (FONT_MID,   f"Missions cleared : {missions}", WHITE),
        (FONT_MID,   f"Total score      : {total_score}", CYAN),
        (FONT_SM,    "Press ESC to exit", DIM),
    ]
    for i, (f, txt, col) in enumerate(lines):
        s = f.render(txt, True, col)
        screen.blit(s, (WIDTH // 2 - s.get_width() // 2, 200 + i * 70))
    pygame.display.flip()
    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT or (
               e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE):
                pygame.quit(); sys.exit()

# ─── Play one mission ────────────────────────────────────────
def play_mission(mission_num, total_score):
    global radar_angle

    target_x = random.randint(0, GRID_SIZE - 1)
    target_y = random.randint(0, GRID_SIZE - 1)

    # Multiple targets for later missions
    extra_targets = []
    if mission_num >= 2:
        while len(extra_targets) < mission_num - 1:
            ex = random.randint(0, GRID_SIZE - 1)
            ey = random.randint(0, GRID_SIZE - 1)
            if (ex, ey) != (target_x, target_y) and (ex, ey) not in extra_targets:
                extra_targets.append((ex, ey))

    all_targets = [(target_x, target_y)] + extra_targets
    destroyed   = []

    shots_left  = MAX_SHOTS + mission_num - 1   # more shots for harder missions
    score       = 0
    shots_fired = []   # (col, row, result)
    message     = ""
    message_col = WHITE
    revealed    = False
    game_done   = False
    won         = False

    splash(mission_num)

    while True:
        clock.tick(FPS)
        radar_angle = (radar_angle + 1.5) % 360
        mx, my = pygame.mouse.get_pos()

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                pygame.quit(); sys.exit()

            if e.type == pygame.MOUSEBUTTONDOWN and not game_done:
                col = (mx - GRID_X) // CELL
                row = (my - GRID_Y) // CELL
                if 0 <= col < GRID_SIZE and 0 <= row < GRID_SIZE:
                    already = any(s[0] == col and s[1] == row for s in shots_fired)
                    if not already and shots_left > 0:
                        shots_left -= 1
                        cx = GRID_X + col * CELL + CELL // 2
                        cy = GRID_Y + row * CELL + CELL // 2

                        # Check against all targets
                        min_dist = min(
                            abs(tx - col) + abs(ty - row)
                            for tx, ty in all_targets
                        )

                        if min_dist == 0:
                            shots_fired.append((col, row, "hit"))
                            score += 100
                            message = "💥  DIRECT HIT!"
                            message_col = HIT_COL
                            spawn_explosion(cx, cy, (255, 100, 0), 60)
                            ripples.append(Ripple(cx, cy, HIT_COL))
                            destroyed.append((col, row))

                            if len(destroyed) == len(all_targets):
                                won = True
                                game_done = True
                                revealed = True

                        elif min_dist <= 2:
                            shots_fired.append((col, row, "near"))
                            score += 30
                            message = "🌊  NEAR MISS!"
                            message_col = NEAR_COL
                            spawn_explosion(cx, cy, (80, 150, 255), 20)
                            ripples.append(Ripple(cx, cy, NEAR_COL))

                        else:
                            shots_fired.append((col, row, "miss"))
                            message = "❌  MISS"
                            message_col = MISS_COL
                            ripples.append(Ripple(cx, cy, MISS_COL))

                        if shots_left == 0 and not game_done:
                            game_done = True
                            revealed  = True

        # ── Render ──────────────────────────────────
        screen.fill(BG)
        draw_grid(screen, shots_fired, target_x, target_y, revealed)
        draw_hover(screen, mx, my)
        draw_hud(screen, shots_left, total_score + score, message, message_col, mission_num)
        draw_radar(screen, shots_left)

        # Particles & ripples
        for p in particles[:]:
            p.update()
            p.draw(screen)
            if p.life <= 0:
                particles.remove(p)

        for r in ripples[:]:
            r.update()
            r.draw(screen)
            if not r.alive():
                ripples.remove(r)

        pygame.display.flip()

        if game_done:
            pygame.time.delay(1000)
            game_over_screen(won, total_score + score, mission_num)
            return score, won

# ─── Main ───────────────────────────────────────────────────
def main():
    MISSIONS    = 3
    total_score = 0
    cleared     = 0

    for m in range(1, MISSIONS + 1):
        score, won = play_mission(m, total_score)
        total_score += score
        if won:
            cleared += 1

    final_screen(total_score, cleared)

main()