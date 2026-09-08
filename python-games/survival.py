import pygame
import sys
import random
import math

pygame.init()

# ─── Window ─────────────────────────────────────────────────
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("RAMZ — Survive")
clock = pygame.time.Clock()
FPS   = 60

# ─── Colours ────────────────────────────────────────────────
BG_TOP      = (10,  18,  10)
BG_BOT      = (5,   10,  5)
PANEL       = (12,  22,  12)
BORDER      = (40,  80,  40)
GREEN       = (80,  200, 80)
DARK_GREEN  = (30,  90,  30)
RED         = (220, 60,  60)
ORANGE      = (230, 140, 30)
YELLOW      = (240, 210, 60)
BROWN       = (140, 90,  40)
LIGHT_BROWN = (190, 140, 80)
WHITE       = (230, 240, 230)
DIM         = (80,  100, 80)
CYAN        = (80,  220, 160)
NIGHT       = (5,   10,  30)
GOLD        = (255, 200, 50)
SKY_DAY     = (80,  160, 220)
SKY_NIGHT   = (10,  15,  50)
SUN_COL     = (255, 230, 80)
MOON_COL    = (200, 210, 240)

# ─── Fonts ──────────────────────────────────────────────────
F_TITLE = pygame.font.SysFont("consolas", 34, bold=True)
F_BIG   = pygame.font.SysFont("consolas", 22, bold=True)
F_MID   = pygame.font.SysFont("consolas", 17)
F_SM    = pygame.font.SysFont("consolas", 13)

# ─── Game state ─────────────────────────────────────────────
class Game:
    def __init__(self):
        self.reset()

    def reset(self):
        self.health    = 100
        self.max_health= 100
        self.food      = 50
        self.max_food  = 100
        self.water     = 60
        self.max_water = 100
        self.warmth    = 70
        self.max_warmth= 100
        self.wood      = 0
        self.day       = 1
        self.hour      = 6        # start at 6am
        self.alive     = True
        self.log       = []
        self.weather   = self.roll_weather()
        self.events    = []       # active timed events
        self.score     = 0
        self.anim_tick = 0
        self.fire_lit  = False
        self.fire_turns= 0
        self.add_log(f"Day 1. You wake up alone in the wilderness.")

    def roll_weather(self):
        return random.choice(["clear", "clear", "cloudy", "rainy", "stormy"])

    def add_log(self, msg, col=None):
        self.log.insert(0, (msg, col or WHITE))
        if len(self.log) > 8:
            self.log.pop()

    def is_night(self):
        return self.hour < 6 or self.hour >= 20

    # ── Actions ─────────────────────────────────────────────
    def action_forage(self):
        cost_health = 8
        cost_water  = 10
        if self.weather == "stormy":
            cost_health += 5
            self.add_log("Storm makes foraging brutal.", RED)
        found_food  = random.randint(8, 25)
        found_water = random.randint(0, 15) if self.weather in ("rainy","stormy") else 0
        self.food   = min(self.max_food,  self.food  + found_food)
        self.water  = min(self.max_water, self.water + found_water)
        self.health = max(0, self.health - cost_health)
        self.water  = max(0, self.water  - cost_water)
        self.advance_hour(3)
        self.score += 5
        msg = f"Foraged {found_food} food"
        if found_water:
            msg += f" + {found_water} water"
        self.add_log(msg + ".", CYAN)

    def action_rest(self):
        if self.food < 10:
            self.add_log("Too hungry to rest properly.", RED)
            self.advance_hour(2)
            return
        heal = 20 if self.fire_lit else 12
        self.food   = max(0, self.food   - 10)
        self.water  = max(0, self.water  - 5)
        self.health = min(self.max_health, self.health + heal)
        self.advance_hour(6)
        self.score += 3
        self.add_log(f"Rested. Recovered {heal} health.", GREEN)

    def action_collect_wood(self):
        amt = random.randint(5, 15)
        self.wood  += amt
        self.water  = max(0, self.water - 8)
        self.health = max(0, self.health - 5)
        self.advance_hour(2)
        self.score += 2
        self.add_log(f"Collected {amt} wood. Total: {self.wood}.", LIGHT_BROWN)

    def action_light_fire(self):
        if self.wood < 10:
            self.add_log("Need at least 10 wood to light a fire.", RED)
            return
        self.wood      -= 10
        self.fire_lit   = True
        self.fire_turns = 3
        self.warmth     = min(self.max_warmth, self.warmth + 30)
        self.advance_hour(1)
        self.add_log("Fire lit! Warmth restored.", ORANGE)

    def action_drink(self):
        if self.water < 5:
            self.add_log("No water to drink!", RED)
            return
        self.water  = max(0, self.water - 20)
        self.health = min(self.max_health, self.health + 10)
        self.advance_hour(1)
        self.add_log("Drank water. Feeling better.", CYAN)

    def advance_hour(self, hours):
        self.hour += hours
        while self.hour >= 24:
            self.hour -= 24
            self.end_of_day()

    def end_of_day(self):
        self.day    += 1
        self.score  += 10
        self.weather = self.roll_weather()

        # Daily decay
        self.food   = max(0, self.food   - 12)
        self.water  = max(0, self.water  - 15)
        self.warmth = max(0, self.warmth - (20 if self.is_night() else 5))

        if self.fire_lit:
            self.fire_turns -= 1
            if self.fire_turns <= 0:
                self.fire_lit = False
                self.add_log("Fire has gone out.", DIM)

        if self.food <= 0:
            self.health = max(0, self.health - 20)
            self.add_log("Starving! Health dropping.", RED)
        if self.water <= 0:
            self.health = max(0, self.health - 20)
            self.add_log("Dehydrated! Health dropping.", RED)
        if self.warmth <= 0:
            self.health = max(0, self.health - 15)
            self.add_log("Freezing! Health dropping.", (100, 180, 255))

        # Random events
        event = random.random()
        if event < 0.12:
            self.food = max(0, self.food - 15)
            self.add_log("Animals raided your supplies!", RED)
        elif event < 0.20:
            bonus = random.randint(10, 25)
            self.food = min(self.max_food, self.food + bonus)
            self.add_log(f"Found a wild berry bush! +{bonus} food.", GREEN)
        elif event < 0.27:
            self.water = min(self.max_water, self.water + 20)
            self.add_log("Rain collected fresh water. +20 water.", CYAN)
        elif event < 0.32:
            dmg = random.randint(10, 25)
            self.health = max(0, self.health - dmg)
            self.add_log(f"Injured by a wild animal! -{dmg} health.", RED)

        self.add_log(f"Day {self.day}. Weather: {self.weather.title()}.",
                     YELLOW if self.weather == "clear" else DIM)

        if self.health <= 0:
            self.alive = False


# ─── Particle system ─────────────────────────────────────────
class Particle:
    def __init__(self, x, y):
        self.x  = x + random.uniform(-4, 4)
        self.y  = y
        self.vx = random.uniform(-0.5, 0.5)
        self.vy = random.uniform(-2.5, -0.8)
        self.life = random.randint(30, 60)
        self.ml   = self.life
        self.r    = random.randint(2, 5)
        self.col  = random.choice([(255,120,0),(255,200,50),(255,60,0),(255,180,30)])

    def update(self):
        self.x   += self.vx
        self.y   += self.vy
        self.vy  += 0.04
        self.life -= 1

    def draw(self, surf):
        a = int(255 * self.life / self.ml)
        s = pygame.Surface((self.r*2, self.r*2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*self.col, a), (self.r, self.r), self.r)
        surf.blit(s, (int(self.x)-self.r, int(self.y)-self.r))

particles = []

# ─── Bar drawing ─────────────────────────────────────────────
def draw_bar(surf, x, y, w, h, val, mx, fill_col, label):
    pygame.draw.rect(surf, (20, 30, 20), (x, y, w, h))
    filled = int((max(0, val) / mx) * w)
    pygame.draw.rect(surf, fill_col, (x, y, filled, h))
    pygame.draw.rect(surf, BORDER, (x, y, w, h), 1)
    lbl = F_SM.render(f"{label}: {int(val)}/{mx}", True, WHITE)
    surf.blit(lbl, (x + 4, y + h // 2 - lbl.get_height() // 2))

# ─── Sky background ──────────────────────────────────────────
def draw_sky(surf, hour, weather, tick):
    t = hour / 24
    # Blend day/night
    night_blend = 0.0
    if hour < 5:   night_blend = 1.0
    elif hour < 7: night_blend = 1 - (hour - 5) / 2
    elif hour < 18: night_blend = 0.0
    elif hour < 20: night_blend = (hour - 18) / 2
    else:          night_blend = 1.0

    def lerp_col(a, b, t):
        return tuple(int(a[i] + (b[i]-a[i])*t) for i in range(3))

    sky = lerp_col(SKY_DAY, SKY_NIGHT, night_blend)
    if weather == "stormy":
        sky = lerp_col(sky, (30, 30, 50), 0.7)
    elif weather == "rainy":
        sky = lerp_col(sky, (60, 70, 90), 0.4)
    elif weather == "cloudy":
        sky = lerp_col(sky, (120, 130, 140), 0.3)

    surf.fill(sky)

    # Sun / Moon
    sun_x = int(WIDTH * (hour / 24))
    sun_y = int(HEIGHT * 0.25 - math.sin(math.pi * hour / 24) * 100)
    if night_blend < 0.5:
        pygame.draw.circle(surf, SUN_COL, (sun_x, sun_y), 22)
        pygame.draw.circle(surf, (255,255,200), (sun_x, sun_y), 18)
    else:
        pygame.draw.circle(surf, MOON_COL, (sun_x, sun_y), 15)
        pygame.draw.circle(surf, (160,170,200), (sun_x+5, sun_y-4), 10)

    # Stars at night
    if night_blend > 0.3:
        rng = random.Random(42)
        for _ in range(60):
            sx = rng.randint(0, WIDTH)
            sy = rng.randint(0, HEIGHT // 3)
            a  = int(night_blend * 220)
            twinkle = abs(math.sin(tick * 0.03 + sx)) * 80
            s = pygame.Surface((3,3), pygame.SRCALPHA)
            pygame.draw.circle(s, (255,255,255, int(a - twinkle)), (1,1), 1)
            surf.blit(s, (sx, sy))

    # Clouds
    if weather in ("cloudy","rainy","stormy"):
        cloud_col = (180,180,190) if weather == "cloudy" else (90,90,110)
        for i in range(4):
            cx = (int(tick * 0.3 + i * 200) % (WIDTH + 100)) - 50
            cy = 60 + i * 20
            pygame.draw.ellipse(surf, cloud_col, (cx, cy, 120, 40))
            pygame.draw.ellipse(surf, cloud_col, (cx+30, cy-15, 80, 40))

    # Rain
    if weather in ("rainy","stormy"):
        rng2 = random.Random(int(tick // 3))
        for _ in range(60 if weather=="stormy" else 30):
            rx = rng2.randint(0, WIDTH)
            ry = rng2.randint(0, HEIGHT // 2)
            pygame.draw.line(surf, (100,140,200,160), (rx, ry), (rx-2, ry+10), 1)

# ─── Ground / scene ──────────────────────────────────────────
def draw_scene(surf, fire_lit, tick):
    # Ground
    pygame.draw.rect(surf, (20, 50, 15), (0, HEIGHT//2, WIDTH, HEIGHT//2))

    # Trees
    for tx, th in [(80,90),(160,70),(650,100),(730,75),(600,85)]:
        pygame.draw.rect(surf, BROWN, (tx-6, HEIGHT//2 + th//2 - th, 12, th))
        pygame.draw.polygon(surf, DARK_GREEN, [
            (tx, HEIGHT//2 - th),
            (tx - 30, HEIGHT//2 + th//2 - th//3),
            (tx + 30, HEIGHT//2 + th//2 - th//3),
        ])
        pygame.draw.polygon(surf, GREEN, [
            (tx, HEIGHT//2 - th - 20),
            (tx - 22, HEIGHT//2 - th + 10),
            (tx + 22, HEIGHT//2 - th + 10),
        ])

    # Campfire
    fx, fy = WIDTH//2, HEIGHT//2 + 30
    pygame.draw.polygon(surf, BROWN, [
        (fx-20, fy), (fx+20, fy), (fx+8, fy-18), (fx-8, fy-18)
    ])

    if fire_lit:
        for _ in range(3):
            particles.append(Particle(fx, fy - 15))
        # Glow
        glow = pygame.Surface((120,120), pygame.SRCALPHA)
        alpha = int(120 + 40*math.sin(tick*0.1))
        pygame.draw.circle(glow, (255, 140, 0, alpha), (60,60), 50)
        surf.blit(glow, (fx-60, fy-60))

    # Shelter hint
    pygame.draw.polygon(surf, BROWN, [
        (WIDTH-120, HEIGHT//2),
        (WIDTH-40,  HEIGHT//2),
        (WIDTH-80,  HEIGHT//2 - 50),
    ])
    pygame.draw.rect(surf, (60,40,20), (WIDTH-115, HEIGHT//2-30, 70, 30))

# ─── HUD panel ───────────────────────────────────────────────
def draw_hud(surf, g):
    # Left panel
    pw, ph = 220, HEIGHT
    panel = pygame.Surface((pw, ph), pygame.SRCALPHA)
    panel.fill((8, 18, 8, 210))
    surf.blit(panel, (0, 0))
    pygame.draw.line(surf, BORDER, (pw, 0), (pw, HEIGHT), 2)

    # Title
    t = F_BIG.render("⛺ SURVIVE", True, GREEN)
    surf.blit(t, (pw//2 - t.get_width()//2, 10))

    day_t = F_MID.render(f"Day {g.day}  {g.hour:02d}:00", True, YELLOW)
    surf.blit(day_t, (pw//2 - day_t.get_width()//2, 38))

    wx_col = YELLOW if g.weather=="clear" else (100,140,255) if g.weather in ("rainy","stormy") else DIM
    wx_t = F_SM.render(f"☁ {g.weather.title()}", True, wx_col)
    surf.blit(wx_t, (pw//2 - wx_t.get_width()//2, 60))

    # Bars
    by = 90
    draw_bar(surf, 10, by,      200, 22, g.health, g.max_health, RED,   "❤ HP")
    draw_bar(surf, 10, by+28,   200, 22, g.food,   g.max_food,   ORANGE,"🍖 Food")
    draw_bar(surf, 10, by+56,   200, 22, g.water,  g.max_water,  CYAN,  "💧 Water")
    draw_bar(surf, 10, by+84,   200, 22, g.warmth, g.max_warmth, YELLOW,"🔥 Warmth")

    # Resources
    ry = by + 120
    wood_t = F_MID.render(f"🪵 Wood: {g.wood}", True, LIGHT_BROWN)
    surf.blit(wood_t, (10, ry))
    fire_t = F_SM.render("🔥 Fire: ON" if g.fire_lit else "🔥 Fire: OFF",
                          True, ORANGE if g.fire_lit else DIM)
    surf.blit(fire_t, (10, ry+24))
    score_t = F_SM.render(f"⭐ Score: {g.score}", True, GOLD)
    surf.blit(score_t, (10, ry+44))

    # Buttons
    buttons = [
        ("1  Forage",       (10,200,10)),
        ("2  Rest",         (10,150,80)),
        ("3  Collect Wood", (120,80,20)),
        ("4  Light Fire",   (200,100,10)),
        ("5  Drink Water",  (20,150,200)),
    ]
    bx, bstart = 10, ry + 80
    for i, (label, col) in enumerate(buttons):
        by2 = bstart + i * 42
        pygame.draw.rect(surf, (20,35,20), (bx, by2, 200, 34), border_radius=6)
        pygame.draw.rect(surf, col, (bx, by2, 200, 34), 2, border_radius=6)
        bt = F_SM.render(label, True, WHITE)
        surf.blit(bt, (bx + 10, by2 + 9))

    # Log
    log_y = bstart + len(buttons)*42 + 10
    pygame.draw.line(surf, BORDER, (5, log_y), (215, log_y), 1)
    log_y += 6
    for msg, col in g.log[:6]:
        lt = F_SM.render(msg[:28], True, col)
        surf.blit(lt, (5, log_y))
        log_y += 17

# ─── Death / Win screen ──────────────────────────────────────
def end_screen(surf, g):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    surf.blit(overlay, (0, 0))

    t1 = F_TITLE.render("YOU PERISHED", True, RED)
    t2 = F_BIG.render(f"Survived {g.day} days", True, WHITE)
    t3 = F_MID.render(f"Final score: {g.score}", True, GOLD)
    t4 = F_SM.render("Press R to restart  |  ESC to quit", True, DIM)

    for i, t in enumerate([t1, t2, t3, t4]):
        surf.blit(t, (WIDTH//2 - t.get_width()//2, HEIGHT//3 + i*55))

# ─── Splash ──────────────────────────────────────────────────
def splash(surf):
    for alpha in range(0, 256, 4):
        surf.fill((5, 12, 5))
        t1 = F_TITLE.render("⛺  RAMZ — SURVIVE", True, GREEN)
        t2 = F_MID.render("Manage health, food, water & warmth", True, WHITE)
        t3 = F_SM.render("Press any key to begin", True, DIM)
        for t in [t1,t2,t3]:
            t.set_alpha(alpha)
        surf.blit(t1, (WIDTH//2 - t1.get_width()//2, HEIGHT//3))
        surf.blit(t2, (WIDTH//2 - t2.get_width()//2, HEIGHT//2))
        surf.blit(t3, (WIDTH//2 - t3.get_width()//2, HEIGHT*2//3))
        pygame.display.flip()
        clock.tick(60)
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()

    waiting = True
    while waiting:
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN: waiting = False

# ─── Main ────────────────────────────────────────────────────
def main():
    g    = Game()
    tick = 0
    splash(screen)

    while True:
        clock.tick(FPS)
        tick += 1

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if not g.alive:
                    if e.key == pygame.K_r:
                        g = Game()
                        particles.clear()
                    elif e.key == pygame.K_ESCAPE:
                        pygame.quit(); sys.exit()
                else:
                    if e.key == pygame.K_1: g.action_forage()
                    elif e.key == pygame.K_2: g.action_rest()
                    elif e.key == pygame.K_3: g.action_collect_wood()
                    elif e.key == pygame.K_4: g.action_light_fire()
                    elif e.key == pygame.K_5: g.action_drink()
                    elif e.key == pygame.K_ESCAPE:
                        pygame.quit(); sys.exit()

        # ── Draw ────────────────────────────────────
        draw_sky(screen, g.hour, g.weather, tick)
        draw_scene(screen, g.fire_lit, tick)

        # Particles
        for p in particles[:]:
            p.update()
            p.draw(screen)
            if p.life <= 0:
                particles.remove(p)

        draw_hud(screen, g)

        if not g.alive:
            end_screen(screen, g)

        pygame.display.flip()

main()