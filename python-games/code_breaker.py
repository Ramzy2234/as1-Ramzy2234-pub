import pygame
import sys
import random
import math

pygame.init()

# ─── Window ─────────────────────────────────────────────────
WIDTH, HEIGHT = 720, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("RAMZ — Code Breaker")
clock = pygame.time.Clock()
FPS   = 60

# ─── Colours ────────────────────────────────────────────────
BG          = (8,   8,   18)
PANEL       = (14,  14,  30)
BORDER      = (40,  40,  80)
BORDER_GLOW = (80,  80,  180)
WHITE       = (230, 235, 255)
DIM         = (70,  75,  100)
CYAN        = (0,   210, 255)
GREEN       = (60,  220, 120)
RED         = (220, 60,  80)
ORANGE      = (255, 150, 40)
YELLOW      = (240, 210, 60)
GOLD        = (255, 200, 40)
PURPLE      = (160, 80,  255)
PINK        = (255, 80,  180)

DIGIT_COLS = [
    (255, 80,  80),   # 0
    (255, 150, 40),   # 1
    (240, 220, 50),   # 2
    (80,  220, 100),  # 3
    (50,  210, 255),  # 4
    (130, 100, 255),  # 5
    (255, 80,  180),  # 6
    (200, 255, 100),  # 7
    (255, 180, 60),   # 8
    (80,  255, 220),  # 9
]

# ─── Fonts ──────────────────────────────────────────────────
F_TITLE = pygame.font.SysFont("consolas", 32, bold=True)
F_BIG   = pygame.font.SysFont("consolas", 24, bold=True)
F_MID   = pygame.font.SysFont("consolas", 18, bold=True)
F_SM    = pygame.font.SysFont("consolas", 14)
F_DIGIT = pygame.font.SysFont("consolas", 36, bold=True)
F_TINY  = pygame.font.SysFont("consolas", 12)

# ─── Constants ───────────────────────────────────────────────
CODE_LEN    = 4
MAX_GUESSES = 10
CELL_W      = 60
CELL_H      = 60
CELL_GAP    = 14
GRID_X      = (WIDTH - (CODE_LEN * (CELL_W + CELL_GAP) - CELL_GAP)) // 2
GRID_Y      = 200
ROW_H       = 72

# ─── Particle system ─────────────────────────────────────────
class Particle:
    def __init__(self, x, y, col):
        angle = random.uniform(0, math.tau)
        speed = random.uniform(1.5, 5)
        self.x    = x
        self.y    = y
        self.vx   = math.cos(angle) * speed
        self.vy   = math.sin(angle) * speed
        self.life = random.randint(30, 70)
        self.ml   = self.life
        self.col  = col
        self.r    = random.randint(2, 5)

    def update(self):
        self.x   += self.vx
        self.y   += self.vy
        self.vy  += 0.1
        self.life -= 1

    def draw(self, surf):
        a = int(255 * self.life / self.ml)
        s = pygame.Surface((self.r*2, self.r*2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*self.col, a), (self.r, self.r), self.r)
        surf.blit(s, (int(self.x)-self.r, int(self.y)-self.r))

particles = []

def explode(x, y, col, n=40):
    for _ in range(n):
        particles.append(Particle(x, y, col))

# ─── Shake system ────────────────────────────────────────────
shake_frames = 0
shake_mag    = 0

def trigger_shake(mag=8, frames=18):
    global shake_frames, shake_mag
    shake_frames = frames
    shake_mag    = mag

def get_shake():
    if shake_frames <= 0:
        return 0, 0
    return (random.randint(-shake_mag, shake_mag),
            random.randint(-shake_mag, shake_mag))

# ─── Peg drawing ─────────────────────────────────────────────
def draw_peg(surf, x, y, kind):
    """kind: 'hit' (green), 'near' (yellow), 'miss' (dim)"""
    col = GREEN if kind == "hit" else YELLOW if kind == "near" else (30, 30, 50)
    pygame.draw.circle(surf, col, (x, y), 7)
    if kind != "miss":
        pygame.draw.circle(surf, WHITE, (x-2, y-2), 2)

# ─── Draw digit cell ─────────────────────────────────────────
def draw_cell(surf, x, y, digit, active=False, pulse=0, locked=False):
    col = DIGIT_COLS[digit] if digit is not None else (25, 25, 50)
    border_col = col if digit is not None else BORDER

    if active:
        # Glow border
        glow = pygame.Surface((CELL_W+12, CELL_H+12), pygame.SRCALPHA)
        a = int(120 + 80*math.sin(pulse))
        pygame.draw.rect(glow, (*CYAN, a), (0, 0, CELL_W+12, CELL_H+12),
                         border_radius=12)
        surf.blit(glow, (x-6, y-6))

    pygame.draw.rect(surf, PANEL, (x, y, CELL_W, CELL_H), border_radius=8)
    pygame.draw.rect(surf, border_col, (x, y, CELL_W, CELL_H), 2, border_radius=8)

    if digit is not None:
        t = F_DIGIT.render(str(digit), True, col)
        surf.blit(t, (x + CELL_W//2 - t.get_width()//2,
                      y + CELL_H//2 - t.get_height()//2))
        if locked:
            lock = F_TINY.render("✓", True, GREEN)
            surf.blit(lock, (x + CELL_W - 14, y + 4))

# ─── Draw history row ────────────────────────────────────────
def draw_row(surf, row_idx, guess, correct, misplaced, is_latest=False):
    y  = GRID_Y + row_idx * ROW_H
    rx = GRID_X - 50

    # Row number
    num = F_SM.render(f"{row_idx+1:02d}", True, DIM)
    surf.blit(num, (rx - 30, y + CELL_H//2 - num.get_height()//2))

    # Digit cells
    for i, d in enumerate(guess):
        cx = GRID_X + i * (CELL_W + CELL_GAP)
        draw_cell(surf, cx, y, d, locked=True)

    # Pegs (2x2 grid)
    peg_x = GRID_X + CODE_LEN * (CELL_W + CELL_GAP) + 10
    peg_positions = [(0,0),(1,0),(0,1),(1,1)]
    pegs = ["hit"]*correct + ["near"]*misplaced + ["miss"]*(CODE_LEN - correct - misplaced)
    for idx, (px, py) in enumerate(peg_positions):
        draw_peg(surf, peg_x + px*20, y + 15 + py*20, pegs[idx])

    # Feedback text
    fx = peg_x + 50
    ht = F_SM.render(f"● {correct}", True, GREEN)
    nt = F_SM.render(f"◌ {misplaced}", True, YELLOW)
    surf.blit(ht, (fx, y + 12))
    surf.blit(nt, (fx, y + 32))

# ─── Draw input row ──────────────────────────────────────────
def draw_input_row(surf, current_guess, selected_col, pulse, attempt_num):
    y = GRID_Y + attempt_num * ROW_H

    # Highlight row bg
    bg = pygame.Surface((WIDTH, ROW_H - 4), pygame.SRCALPHA)
    bg.fill((30, 30, 80, 60))
    surf.blit(bg, (0, y + 2))

    num = F_SM.render(f"{attempt_num+1:02d}", True, CYAN)
    surf.blit(num, (GRID_X - 60, y + CELL_H//2 - num.get_height()//2))

    for i in range(CODE_LEN):
        cx = GRID_X + i * (CELL_W + CELL_GAP)
        active = (i == selected_col)
        draw_cell(surf, cx, y, current_guess[i], active=active, pulse=pulse)

    hint = F_SM.render("← → navigate   0–9 enter digit   ENTER confirm   DEL clear", True, DIM)
    surf.blit(hint, (WIDTH//2 - hint.get_width()//2, y + CELL_H + 8))

# ─── HUD ─────────────────────────────────────────────────────
def draw_hud(surf, attempts_left, score, streak):
    pygame.draw.rect(surf, PANEL, (0, 0, WIDTH, 160))
    pygame.draw.line(surf, BORDER_GLOW, (0, 159), (WIDTH, 159), 2)

    t = F_TITLE.render("🔐  CODE  BREAKER", True, CYAN)
    surf.blit(t, (WIDTH//2 - t.get_width()//2, 12))

    # Attempts bar
    for i in range(MAX_GUESSES):
        col = GREEN if i < attempts_left else (30, 30, 50)
        pygame.draw.rect(surf, col, (GRID_X + i * 52, 58, 44, 14), border_radius=4)

    al = F_SM.render(f"Attempts left: {attempts_left}", True,
                      GREEN if attempts_left > 4 else ORANGE if attempts_left > 2 else RED)
    surf.blit(al, (GRID_X, 78))

    sc = F_SM.render(f"Score: {score}", True, GOLD)
    surf.blit(sc, (GRID_X + 300, 78))

    stk = F_SM.render(f"Streak: {streak}🔥", True, ORANGE)
    surf.blit(stk, (GRID_X + 300, 100))

    # Difficulty label
    diff = "EASY" if CODE_LEN == 3 else "NORMAL" if CODE_LEN == 4 else "HARD"
    dt = F_SM.render(f"Mode: {diff}", True, PURPLE)
    surf.blit(dt, (GRID_X, 100))

    # Column labels
    for i in range(CODE_LEN):
        cx = GRID_X + i * (CELL_W + CELL_GAP) + CELL_W//2
        lbl = F_SM.render(f"[{i+1}]", True, DIM)
        surf.blit(lbl, (cx - lbl.get_width()//2, 130))

# ─── Scrolling background grid ───────────────────────────────
scroll_y = 0

def draw_bg(surf, tick):
    global scroll_y
    surf.fill(BG)
    scroll_y = (scroll_y + 0.3) % 40
    for gx in range(0, WIDTH, 40):
        for gy_base in range(-40, HEIGHT + 40, 40):
            gy = gy_base + int(scroll_y)
            pygame.draw.rect(surf, (14, 14, 28), (gx, gy, 39, 39))

    # Scanlines
    for ly in range(0, HEIGHT, 4):
        s = pygame.Surface((WIDTH, 1), pygame.SRCALPHA)
        s.fill((0, 0, 0, 30))
        surf.blit(s, (0, ly))

# ─── Splash ──────────────────────────────────────────────────
def splash():
    for alpha in range(0, 256, 4):
        screen.fill(BG)
        t1 = F_TITLE.render("🔐  CODE BREAKER", True, CYAN)
        t2 = F_MID.render("Crack the 4-digit secret code", True, WHITE)
        t3 = F_SM.render("● = right digit, right place", True, GREEN)
        t4 = F_SM.render("◌ = right digit, wrong place", True, YELLOW)
        t5 = F_SM.render("Press any key to start", True, DIM)
        for i, t in enumerate([t1,t2,t3,t4,t5]):
            t.set_alpha(alpha)
            screen.blit(t, (WIDTH//2 - t.get_width()//2, 180 + i*60))
        pygame.display.flip()
        clock.tick(60)
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()

    waiting = True
    while waiting:
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN: waiting = False

# ─── Win / Lose overlay ──────────────────────────────────────
def result_screen(surf, won, code, score, streak, tick):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 190))
    surf.blit(overlay, (0, 0))

    if won:
        t1 = F_TITLE.render("✅  CODE CRACKED!", True, GREEN)
        t2 = F_MID.render(f"Score: {score}   Streak: {streak}🔥", True, GOLD)
    else:
        t1 = F_TITLE.render("💀  SYSTEM LOCKED", True, RED)
        code_str = "".join(str(d) for d in code)
        t2 = F_MID.render(f"Code was: {code_str}", True, ORANGE)

    t3 = F_SM.render("R = play again   ESC = quit", True, DIM)

    for i, t in enumerate([t1, t2, t3]):
        surf.blit(t, (WIDTH//2 - t.get_width()//2, HEIGHT//3 + i*65))

# ─── Game class ──────────────────────────────────────────────
class CodeBreaker:
    def __init__(self):
        self.code          = [random.randint(0, 9) for _ in range(CODE_LEN)]
        self.history       = []   # list of (guess, correct, misplaced)
        self.current_guess = [None] * CODE_LEN
        self.selected_col  = 0
        self.attempts_left = MAX_GUESSES
        self.done          = False
        self.won           = False
        self.score         = 0
        self.streak        = 0
        self.pulse         = 0
        self.tick          = 0
        self.invalid_flash = 0

    def submit(self):
        if any(d is None for d in self.current_guess):
            self.invalid_flash = 30
            trigger_shake(6, 15)
            return

        guess   = list(self.current_guess)
        correct = sum(1 for i in range(CODE_LEN) if guess[i] == self.code[i])
        misplaced = (sum(min(guess.count(d), self.code.count(d))
                        for d in set(guess)) - correct)

        self.history.append((guess, correct, misplaced))
        self.attempts_left -= 1

        # Particles on correct digits
        for i in range(CODE_LEN):
            if guess[i] == self.code[i]:
                cx = GRID_X + i*(CELL_W+CELL_GAP) + CELL_W//2
                cy = GRID_Y + (len(self.history)-1)*ROW_H + CELL_H//2
                explode(cx, cy, DIGIT_COLS[guess[i]], 15)

        if correct == CODE_LEN:
            self.won   = True
            self.done  = True
            self.score += 100 + self.attempts_left * 20
            self.streak += 1
            # Big celebration
            for _ in range(6):
                explode(random.randint(100, WIDTH-100),
                        random.randint(100, HEIGHT-100),
                        random.choice(list(DIGIT_COLS)), 20)
        elif self.attempts_left <= 0:
            self.done   = True
            self.streak = 0
            trigger_shake(10, 25)

        self.current_guess = [None] * CODE_LEN
        self.selected_col  = 0

    def handle_key(self, key):
        if self.done:
            return
        if key == pygame.K_RIGHT or key == pygame.K_TAB:
            self.selected_col = (self.selected_col + 1) % CODE_LEN
        elif key == pygame.K_LEFT:
            self.selected_col = (self.selected_col - 1) % CODE_LEN
        elif key == pygame.K_RETURN or key == pygame.K_KP_ENTER:
            self.submit()
        elif key == pygame.K_DELETE or key == pygame.K_BACKSPACE:
            self.current_guess[self.selected_col] = None
        elif pygame.K_0 <= key <= pygame.K_9:
            digit = key - pygame.K_0
            self.current_guess[self.selected_col] = digit
            self.selected_col = min(self.selected_col + 1, CODE_LEN - 1)
        elif pygame.K_KP0 <= key <= pygame.K_KP9:
            digit = key - pygame.K_KP0
            self.current_guess[self.selected_col] = digit
            self.selected_col = min(self.selected_col + 1, CODE_LEN - 1)
        # Number row 1-4 to select column
        elif pygame.K_F1 <= key <= pygame.K_F4:
            self.selected_col = key - pygame.K_F1

    def draw(self, surf):
        global shake_frames, shake_mag
        self.pulse += 0.08
        self.tick  += 1

        sx, sy = get_shake()
        if shake_frames > 0:
            shake_frames -= 1

        draw_bg(surf, self.tick)

        # Apply shake offset via a temp surface
        game_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

        draw_hud(game_surf, self.attempts_left, self.score, self.streak)

        # History rows
        for i, (guess, correct, misplaced) in enumerate(self.history):
            draw_row(game_surf, i, guess, correct, misplaced)

        # Input row
        if not self.done:
            draw_input_row(game_surf, self.current_guess,
                           self.selected_col, self.pulse,
                           len(self.history))

        # Invalid flash
        if self.invalid_flash > 0:
            self.invalid_flash -= 1
            flash = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            a = int(80 * self.invalid_flash / 30)
            flash.fill((255, 0, 0, a))
            game_surf.blit(flash, (0, 0))
            msg = F_MID.render("Fill all digits first!", True, RED)
            game_surf.blit(msg, (WIDTH//2 - msg.get_width()//2, HEIGHT - 60))

        # Particles
        for p in particles[:]:
            p.update()
            p.draw(game_surf)
            if p.life <= 0:
                particles.remove(p)

        surf.blit(game_surf, (sx, sy))

        if self.done:
            result_screen(surf, self.won, self.code,
                          self.score, self.streak, self.tick)

# ─── Main ─────────────────────────────────────────────────────
def main():
    splash()
    game = CodeBreaker()

    while True:
        clock.tick(FPS)

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()
                if game.done and e.key == pygame.K_r:
                    particles.clear()
                    game = CodeBreaker()
                else:
                    game.handle_key(e.key)

        game.draw(screen)
        pygame.display.flip()

for e in pygame.event.get():
    if e.type == pygame.QUIT:
        pygame.quit(); sys.exit()
    
    if e.type == pygame.VIDEORESIZE:          # ← add this
        WIDTH, HEIGHT = e.w, e.h
        screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)

    if e.type == pygame.KEYDOWN:
        if e.key == pygame.K_ESCAPE:
            pygame.quit(); sys.exit()
        if e.key == pygame.K_F11:             # ← add this for true fullscreen toggle
            pygame.display.toggle_fullscreen()
main()