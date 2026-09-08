import pygame
import sys

pygame.init()

WIDTH, HEIGHT = 600, 400
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GOLD = (255, 215, 0)
CYAN = (0, 255, 255)
BALL_SPEED = 5
WIN_SCORE = 5

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("PONG")

clock = pygame.time.Clock()

# --- Fonts ---
title_font = pygame.font.Font(None, 100)
large_font = pygame.font.Font(None, 72)
mid_font = pygame.font.Font(None, 60)
font = pygame.font.Font(None, 36)
small_font = pygame.font.Font(None, 28)


# ─────────────────────────────────────────────
#  HELPER: draw the court (centre line + scores)
# ─────────────────────────────────────────────
def draw_court(score_left, score_right):
    # Dashed centre line
    for y in range(0, HEIGHT, 20):
        if (y // 10) % 2 == 0:
            pygame.draw.rect(screen, (60, 60, 60), (WIDTH // 2 - 2, y, 4, 10))

    score_surf = font.render(f"{score_left}   {score_right}", True, WHITE)
    screen.blit(score_surf, (WIDTH // 2 - score_surf.get_width() // 2, 14))


# ─────────────────────────────────────────────
#  GLOW BALL
# ─────────────────────────────────────────────
def draw_glow_ball(x, y):
    for radius, alpha in [(22, 30), (16, 70), (11, 140)]:
        glow_surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        pygame.draw.ellipse(glow_surf, (255, 255, 255, alpha),
                            (0, 0, radius * 2, radius * 2))
        screen.blit(glow_surf, (x - radius, y - radius))
    pygame.draw.ellipse(screen, WHITE, (x - 8, y - 8, 16, 16))


# ─────────────────────────────────────────────
#  TITLE SCREEN  (fade in)
# ─────────────────────────────────────────────
def title_screen():
    alpha = 0
    tick = 0
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                return

        screen.fill(BLACK)

        # Subtle animated background dots
        tick += 1
        for i in range(8):
            r = abs(int(30 * pygame.math.Vector2(1, 0)
                        .rotate(tick * 0.5 + i * 45).x)) + 5
            cx = int(WIDTH * (i % 4) / 3.5 + 20)
            cy = int(HEIGHT * (i // 4) / 1.5 + 60)
            pygame.draw.circle(screen, (20, 20, 20), (cx, cy), r)

        if alpha < 255:
            alpha = min(255, alpha + 2)

        # "PONG" title
        title_surf = title_font.render("PONG", True, WHITE)
        title_surf.set_alpha(alpha)
        screen.blit(title_surf,
                    (WIDTH // 2 - title_surf.get_width() // 2, HEIGHT // 4))

        # Controls info
        controls = [
            "Player 1:  W / S",
            "Player 2:  ↑ / ↓",
            f"First to {WIN_SCORE} wins!",
        ]
        for i, line in enumerate(controls):
            s = small_font.render(line, True, (160, 160, 160))
            s.set_alpha(alpha)
            screen.blit(s, (WIDTH // 2 - s.get_width() // 2,
                            HEIGHT // 2 + i * 28))

        blink_surf = font.render("Press any key to start", True, GOLD)
        if (tick // 40) % 2 == 0:          # blink every ~0.6 s
            blink_surf.set_alpha(alpha)
            screen.blit(blink_surf,
                        (WIDTH // 2 - blink_surf.get_width() // 2,
                         HEIGHT - 60))

        pygame.display.flip()
        clock.tick(60)


# ─────────────────────────────────────────────
#  COUNTDOWN
# ─────────────────────────────────────────────
def countdown(score_left, score_right,
              left_paddle_y, right_paddle_y,
              paddle_width, paddle_height,
              left_paddle_x, right_paddle_x):
    for label in ["3", "2", "1", "GO!"]:
        start = pygame.time.get_ticks()
        while pygame.time.get_ticks() - start < 800:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()

            screen.fill(BLACK)
            draw_court(score_left, score_right)
            pygame.draw.rect(screen, WHITE,
                             (left_paddle_x, left_paddle_y,
                              paddle_width, paddle_height))
            pygame.draw.rect(screen, WHITE,
                             (right_paddle_x, right_paddle_y,
                              paddle_width, paddle_height))

            colour = GOLD if label == "GO!" else WHITE
            s = mid_font.render(label, True, colour)
            screen.blit(s, (WIDTH // 2 - s.get_width() // 2,
                            HEIGHT // 2 - s.get_height() // 2))
            pygame.display.flip()
            clock.tick(60)


# ─────────────────────────────────────────────
#  SCORE FLASH
# ─────────────────────────────────────────────
def score_flash(message,
                score_left, score_right,
                left_paddle_y, right_paddle_y,
                paddle_width, paddle_height,
                left_paddle_x, right_paddle_x):
    start = pygame.time.get_ticks()
    while pygame.time.get_ticks() - start < 1400:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

        screen.fill(BLACK)
        draw_court(score_left, score_right)
        pygame.draw.rect(screen, WHITE,
                         (left_paddle_x, left_paddle_y,
                          paddle_width, paddle_height))
        pygame.draw.rect(screen, WHITE,
                         (right_paddle_x, right_paddle_y,
                          paddle_width, paddle_height))

        s = mid_font.render(message, True, GOLD)
        screen.blit(s, (WIDTH // 2 - s.get_width() // 2,
                        HEIGHT // 2 - s.get_height() // 2))
        pygame.display.flip()
        clock.tick(60)


# ─────────────────────────────────────────────
#  GAME OVER SCREEN
# ─────────────────────────────────────────────
def game_over_screen(winner):
    alpha = 0
    tick = 0
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                return

        screen.fill(BLACK)
        tick += 1
        if alpha < 255:
            alpha = min(255, alpha + 3)

        win_surf = large_font.render(f"{winner} Wins!", True, GOLD)
        win_surf.set_alpha(alpha)
        screen.blit(win_surf,
                    (WIDTH // 2 - win_surf.get_width() // 2, HEIGHT // 3))

        restart_surf = font.render("Press any key to play again", True, WHITE)
        restart_surf.set_alpha(alpha)
        screen.blit(restart_surf,
                    (WIDTH // 2 - restart_surf.get_width() // 2, HEIGHT // 2))

        pygame.display.flip()
        clock.tick(60)


# ─────────────────────────────────────────────
#  BALL RESET
# ─────────────────────────────────────────────
def reset_ball():
    return WIDTH // 2, HEIGHT // 2, BALL_SPEED, BALL_SPEED


# ═════════════════════════════════════════════
#  MAIN GAME LOOP  (wrapped so we can restart)
# ═════════════════════════════════════════════
def run_game():
    ball_x, ball_y = WIDTH // 2, HEIGHT // 2
    ball_speed_x, ball_speed_y = BALL_SPEED, BALL_SPEED

    paddle_width, paddle_height = 15, 60
    left_paddle_x  = 10
    right_paddle_x = WIDTH - 25
    left_paddle_y  = HEIGHT // 2 - paddle_height // 2
    right_paddle_y = HEIGHT // 2 - paddle_height // 2
    paddle_speed   = 7

    score_left, score_right = 0, 0

    # Opening countdown
    countdown(score_left, score_right,
              left_paddle_y, right_paddle_y,
              paddle_width, paddle_height,
              left_paddle_x, right_paddle_x)

    while True:
        # ── Events ──────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

        # ── Paddle movement ──────────────────────
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w] and left_paddle_y > 0:
            left_paddle_y -= paddle_speed
        if keys[pygame.K_s] and left_paddle_y < HEIGHT - paddle_height:
            left_paddle_y += paddle_speed
        if keys[pygame.K_UP] and right_paddle_y > 0:
            right_paddle_y -= paddle_speed
        if keys[pygame.K_DOWN] and right_paddle_y < HEIGHT - paddle_height:
            right_paddle_y += paddle_speed

        # ── Ball movement ────────────────────────
        ball_x += ball_speed_x
        ball_y += ball_speed_y

        # ── Paddle collision ─────────────────────
        if (
            left_paddle_x < ball_x < left_paddle_x + paddle_width
            and left_paddle_y < ball_y < left_paddle_y + paddle_height
        ) or (
            right_paddle_x < ball_x < right_paddle_x + paddle_width
            and right_paddle_y < ball_y < right_paddle_y + paddle_height
        ):
            ball_speed_x = -ball_speed_x

        # ── Top / bottom wall ────────────────────
        if ball_y <= 0 or ball_y >= HEIGHT:
            ball_speed_y = -ball_speed_y

        # ── Scoring ──────────────────────────────
        if ball_x <= 0:
            score_right += 1
            if score_right >= WIN_SCORE:
                game_over_screen("Player 2")
                return
            score_flash("Player 2 Scores!",
                        score_left, score_right,
                        left_paddle_y, right_paddle_y,
                        paddle_width, paddle_height,
                        left_paddle_x, right_paddle_x)
            ball_x, ball_y, ball_speed_x, ball_speed_y = reset_ball()
            countdown(score_left, score_right,
                      left_paddle_y, right_paddle_y,
                      paddle_width, paddle_height,
                      left_paddle_x, right_paddle_x)

        if ball_x >= WIDTH:
            score_left += 1
            if score_left >= WIN_SCORE:
                game_over_screen("Player 1")
                return
            score_flash("Player 1 Scores!",
                        score_left, score_right,
                        left_paddle_y, right_paddle_y,
                        paddle_width, paddle_height,
                        left_paddle_x, right_paddle_x)
            ball_x, ball_y, ball_speed_x, ball_speed_y = reset_ball()
            countdown(score_left, score_right,
                      left_paddle_y, right_paddle_y,
                      paddle_width, paddle_height,
                      left_paddle_x, right_paddle_x)

        # ── Draw ─────────────────────────────────
        screen.fill(BLACK)
        draw_court(score_left, score_right)

        pygame.draw.rect(screen, WHITE,
                         (left_paddle_x, left_paddle_y,
                          paddle_width, paddle_height))
        pygame.draw.rect(screen, WHITE,
                         (right_paddle_x, right_paddle_y,
                          paddle_width, paddle_height))

        draw_glow_ball(ball_x, ball_y)

        pygame.display.flip()
        clock.tick(60)


# ═════════════════════════════════════════════
#  ENTRY POINT
# ═════════════════════════════════════════════
title_screen()

while True:          # allows restart after game over
    run_game()
    title_screen()