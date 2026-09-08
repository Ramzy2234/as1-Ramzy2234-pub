import pygame
import sys
import random
import time

pygame.init()

# ─── Constants ──────────────────────────────────────────────
TILE      = 40
COLS      = 15
ROWS      = 13
WIDTH     = COLS * TILE
HEIGHT    = ROWS * TILE + 80
FPS       = 60

# ─── Colours ────────────────────────────────────────────────
BLACK      = (0,   0,   0)
WHITE      = (255, 255, 255)
WALL       = (30,  30,  60)
WALL_EDGE  = (60,  60,  120)
FLOOR      = (15,  15,  35)
PLAYER_COL = (80,  200, 255)
EXIT_COL   = (255, 215, 0)
GEM_COL    = (255, 80,  180)
KEY_COL    = (255, 200, 50)
FOG        = (0,   0,   0)
HUD_BG     = (10,  10,  25)
CYAN       = (0,   255, 220)
RED        = (255, 60,  60)
GREEN      = (60,  255, 120)

# ─── Fonts ──────────────────────────────────────────────────
pygame.font.init()
FONT_BIG  = pygame.font.SysFont("consolas", 28, bold=True)
FONT_MID  = pygame.font.SysFont("consolas", 20)
FONT_SM   = pygame.font.SysFont("consolas", 15)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("RAMZ — Maze Escape")
clock  = pygame.time.Clock()

# ─── Maze generator (recursive backtracker) ─────────────────
def generate_maze(cols, rows):
    # Start all walls
    grid = [["#"] * cols for _ in range(rows)]

    def carve(x, y):
        grid[y][x] = "."
        directions = [(0, -2), (0, 2), (-2, 0), (2, 0)]
        random.shuffle(directions)
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < cols and 0 <= ny < rows and grid[ny][nx] == "#":
                grid[y + dy // 2][x + dx // 2] = "."
                carve(nx, ny)

    carve(1, 1)
    grid[1][1]           = "S"
    grid[rows - 2][cols - 2] = "E"
    return grid

# ─── Place collectibles ─────────────────────────────────────
def place_items(grid, rows, cols, count, symbol):
    placed = 0
    attempts = 0
    while placed < count and attempts < 1000:
        x = random.randint(1, cols - 2)
        y = random.randint(1, rows - 2)
        if grid[y][x] == ".":
            grid[y][x] = symbol
            placed += 1
        attempts += 1

# ─── Fog of war: visible tiles ──────────────────────────────
VISION = 3   # radius in tiles

def get_visible(px, py):
    visible = set()
    for dy in range(-VISION, VISION + 1):
        for dx in range(-VISION, VISION + 1):
            if dx * dx + dy * dy <= VISION * VISION:
                visible.add((px + dx, py + dy))
    return visible

# ─── Draw tile ──────────────────────────────────────────────
def draw_tile(surface, x, y, cell, lit):
    rx, ry = x * TILE, y * TILE + 80

    if not lit:
        pygame.draw.rect(surface, FOG, (rx, ry, TILE, TILE))
        return

    if cell == "#":
        pygame.draw.rect(surface, WALL, (rx, ry, TILE, TILE))
        pygame.draw.rect(surface, WALL_EDGE, (rx, ry, TILE, TILE), 2)
    else:
        pygame.draw.rect(surface, FLOOR, (rx, ry, TILE, TILE))

    if cell == "E":
        # Glowing exit
        pygame.draw.rect(surface, (40, 30, 0), (rx, ry, TILE, TILE))
        glow = pygame.Surface((TILE, TILE), pygame.SRCALPHA)
        pygame.draw.rect(glow, (*EXIT_COL, 60), (0, 0, TILE, TILE))
        surface.blit(glow, (rx, ry))
        label = FONT_SM.render("EXIT", True, EXIT_COL)
        surface.blit(label, (rx + TILE // 2 - label.get_width() // 2,
                              ry + TILE // 2 - label.get_height() // 2))

    elif cell == "G":
        cx, cy = rx + TILE // 2, ry + TILE // 2
        pygame.draw.circle(surface, GEM_COL, (cx, cy), 8)
        pygame.draw.circle(surface, WHITE,   (cx - 3, cy - 3), 3)

    elif cell == "K":
        cx, cy = rx + TILE // 2, ry + TILE // 2
        pygame.draw.circle(surface, KEY_COL, (cx, cy), 7)
        pygame.draw.rect(surface, KEY_COL, (cx, cy, 8, 4))
        pygame.draw.circle(surface, BLACK, (cx + 4, cy + 2), 2)

# ─── Draw player ────────────────────────────────────────────
def draw_player(surface, px, py, bob):
    rx = px * TILE + TILE // 2
    ry = py * TILE + TILE // 2 + 80 + int(bob)
    # Glow
    glow = pygame.Surface((TILE, TILE), pygame.SRCALPHA)
    pygame.draw.circle(glow, (*PLAYER_COL, 50), (TILE // 2, TILE // 2), 18)
    surface.blit(glow, (rx - TILE // 2, ry - TILE // 2))
    # Body
    pygame.draw.circle(surface, PLAYER_COL, (rx, ry), 12)
    pygame.draw.circle(surface, WHITE,      (rx, ry), 12, 2)
    # Eyes
    pygame.draw.circle(surface, WHITE, (rx - 4, ry - 3), 3)
    pygame.draw.circle(surface, WHITE, (rx + 4, ry - 3), 3)
    pygame.draw.circle(surface, BLACK, (rx - 4, ry - 3), 1)
    pygame.draw.circle(surface, BLACK, (rx + 4, ry - 3), 1)

# ─── HUD ────────────────────────────────────────────────────
def draw_hud(surface, gems, keys, steps, level, has_key, total_gems):
    pygame.draw.rect(surface, HUD_BG, (0, 0, WIDTH, 80))
    pygame.draw.line(surface, CYAN, (0, 79), (WIDTH, 79), 2)

    title = FONT_BIG.render(f"RAMZ — Level {level}", True, CYAN)
    surface.blit(title, (10, 10))

    gem_t  = FONT_MID.render(f"💎 {gems}/{total_gems}", True, GEM_COL)
    key_t  = FONT_MID.render(f"🔑 {'YES' if has_key else 'NO'}", True,
                               GREEN if has_key else RED)
    step_t = FONT_MID.render(f"Steps: {steps}", True, WHITE)

    surface.blit(gem_t,  (10,  50))
    surface.blit(key_t,  (130, 50))
    surface.blit(step_t, (260, 50))

    hint = FONT_SM.render("WASD / Arrow keys to move", True, (80, 80, 100))
    surface.blit(hint, (WIDTH - hint.get_width() - 10, 60))

# ─── Splash screen ──────────────────────────────────────────
def splash_screen(level):
    for alpha in range(0, 256, 4):
        screen.fill(BLACK)
        t1 = FONT_BIG.render(f"LEVEL  {level}", True, CYAN)
        t2 = FONT_MID.render("Find the KEY then reach the EXIT", True, WHITE)
        t3 = FONT_SM.render("Press any key to start", True, (100, 100, 100))
        t1.set_alpha(alpha); t2.set_alpha(alpha); t3.set_alpha(alpha)
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
            if e.type == pygame.KEYDOWN:
                waiting = False

# ─── Win screen ─────────────────────────────────────────────
def win_screen(steps, gems, total_gems, level):
    for alpha in range(0, 256, 3):
        screen.fill(BLACK)
        t1 = FONT_BIG.render("ESCAPED!", True, EXIT_COL)
        t2 = FONT_MID.render(f"Steps: {steps}   Gems: {gems}/{total_gems}", True, WHITE)
        t3 = FONT_SM.render("Press any key to continue...", True, (100, 100, 100))
        t1.set_alpha(alpha); t2.set_alpha(alpha); t3.set_alpha(alpha)
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
            if e.type == pygame.KEYDOWN:
                waiting = False

# ─── Final screen ───────────────────────────────────────────
def final_screen(total_steps, total_gems, max_gems):
    screen.fill(BLACK)
    lines = [
        (FONT_BIG, "🏆  YOU WIN, RAMZ!",        EXIT_COL),
        (FONT_MID, f"Total steps : {total_steps}", WHITE),
        (FONT_MID, f"Gems found  : {total_gems}/{max_gems}", GEM_COL),
        (FONT_SM,  "Press Escape to quit",        (80, 80, 80)),
    ]
    for i, (f, txt, col) in enumerate(lines):
        s = f.render(txt, True, col)
        screen.blit(s, (WIDTH // 2 - s.get_width() // 2, 180 + i * 60))
    pygame.display.flip()

    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT or (
               e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE):
                pygame.quit(); sys.exit()

# ─── Play one level ─────────────────────────────────────────
def play_level(level_num):
    grid       = generate_maze(COLS, ROWS)
    total_gems = 5
    place_items(grid, ROWS, COLS, total_gems, "G")
    place_items(grid, ROWS, COLS, 1,          "K")

    px, py    = 1, 1
    gems      = 0
    has_key   = False
    steps     = 0
    bob_tick  = 0
    visited   = set()
    visited.add((px, py))

    splash_screen(level_num)

    move_keys = {
        pygame.K_w: (0, -1), pygame.K_UP:    (0, -1),
        pygame.K_s: (0,  1), pygame.K_DOWN:  (0,  1),
        pygame.K_a: (-1, 0), pygame.K_LEFT:  (-1, 0),
        pygame.K_d: (1,  0), pygame.K_RIGHT: (1,  0),
    }

    running = True
    while running:
        dt = clock.tick(FPS)
        bob_tick += 0.08
        bob = 2 * pygame.math.Vector2(0, 1).rotate(bob_tick * 30).y

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key in move_keys:
                    dx, dy = move_keys[e.key]
                    nx, ny = px + dx, py + dy
                    if 0 <= nx < COLS and 0 <= ny < ROWS:
                        if grid[ny][nx] != "#":
                            px, py = nx, ny
                            steps += 1
                            visited.add((px, py))
                            cell = grid[py][px]

                            if cell == "G":
                                gems += 1
                                grid[py][px] = "."

                            elif cell == "K":
                                has_key = True
                                grid[py][px] = "."

                            elif cell == "E":
                                if has_key:
                                    running = False   # level complete

        # ── Draw ────────────────────────────────────
        screen.fill(BLACK)
        visible = get_visible(px, py)

        for y in range(ROWS):
            for x in range(COLS):
                lit = (x, y) in visible or (x, y) in visited
                draw_tile(screen, x, y, grid[y][x], lit)

        draw_player(screen, px, py, bob)
        draw_hud(screen, gems, 0, steps, level_num, has_key, total_gems)
        pygame.display.flip()

    win_screen(steps, gems, total_gems, level_num)
    return steps, gems, total_gems

# ─── Main ───────────────────────────────────────────────────
def main():
    LEVELS     = 3
    tot_steps  = 0
    tot_gems   = 0
    max_gems   = 0

    for lvl in range(1, LEVELS + 1):
        s, g, mg = play_level(lvl)
        tot_steps += s
        tot_gems  += g
        max_gems  += mg

    final_screen(tot_steps, tot_gems, max_gems)

main()