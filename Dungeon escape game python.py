import pygame
import sys
import random

pygame.init()

# Fenstergröße
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dungeon Escape")

# Farben
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
WHITE = (255, 255, 255)
DARK_BLUE = (10, 10, 60)
GRAY = (100, 100, 100)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)

# Musik
pygame.mixer.music.load("musik.mp3")
pygame.mixer.music.play(-1)
volume_level = 10  # 1 bis 20
pygame.mixer.music.set_volume(volume_level / 20)

# Spieler
player = pygame.Rect(0, 0, 40, 40)
player_speed = 5

# Ziel
goal = pygame.Rect(700, 500, 50, 50)
try:
    goal_image = pygame.image.load("exit.png").convert_alpha()
    goal_image = pygame.transform.scale(goal_image, (goal.width, goal.height))
except:
    goal_image = None

# Gegner (früher "Fallen")
enemy1 = pygame.Rect(300, 200, 100, 50)
enemy1_speed = 3
enemy2 = pygame.Rect(400, 300, 100, 50)
enemy2_speed = 4
enemy3 = pygame.Rect(500, 400, 100, 50)
enemy3_speed = 5
enemy4 = pygame.Rect(200, 150, 100, 50)
enemy4_speed = 2

# Neue Fallen
trap_ground = pygame.Rect(350, 350, 60, 60)  # Bodenfalle in Level 2
trap_laser = pygame.Rect(200, 250, 400, 10)  # Laserfalle in Level 3
trap_laser_active = True
trap_laser_timer = 90

# Spielzustand
game_state = "playing"
game_level = 1
show_intro = True
intro_timer = 120

# Todesnachrichten
death_messages = [
    "Bruder kann nicht mal ausweichen",
    "Oh hell NAW twin",
    "damn.",
    "passiert",
    "was machen sie",
    "Du bist gestorben",
    "Quit einfach real talk"
]
death_text = ""

# Bilder
try:
    background = pygame.image.load("background_13.jpg").convert()
    background = pygame.transform.scale(background, (WIDTH, HEIGHT))

    player_image = pygame.image.load("player_1.png").convert_alpha()
    player_image = pygame.transform.scale(player_image, (player.width, player.height))

    trap_image = pygame.image.load("enemy_1.png").convert_alpha()
    trap_image = pygame.transform.scale(trap_image, (enemy1.width, enemy1.height))

    trap2_image = pygame.image.load("gegner_3.png").convert_alpha()
    trap2_image = pygame.transform.scale(trap2_image, (enemy4.width, enemy4.height))
except pygame.error as e:
    print("Fehler beim Laden der Bilder:", e)
    pygame.quit()
    sys.exit()

clock = pygame.time.Clock()
running = True

def draw_button(text, x, y, w, h, color, hover_color, action=None):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    rect = pygame.Rect(x, y, w, h)
    if rect.collidepoint(mouse):
        pygame.draw.rect(screen, hover_color, rect)
        if click[0] == 1 and action:
            action()
    else:
        pygame.draw.rect(screen, color, rect)
    font = pygame.font.SysFont(None, 40)
    text_surf = font.render(text, True, WHITE)
    text_rect = text_surf.get_rect(center=rect.center)
    screen.blit(text_surf, text_rect)

def restart_game():
    global player, game_state, death_text, show_intro, intro_timer
    player.x, player.y = 0, 0
    enemy1.x, enemy1.y = 300, 200
    enemy2.x, enemy2.y = 400, 300
    enemy3.x, enemy3.y = 500, 400
    enemy4.x, enemy4.y = 200, 150
    death_text = ""
    game_state = "playing"
    show_intro = True
    intro_timer = 120
    pygame.display.set_caption(f"Dungeon Escape - Level {game_level}")

def resume_game():
    global game_state
    game_state = "playing"

def set_game_state(state):
    global game_state
    game_state = state

def change_volume(change):
    global volume_level
    volume_level = max(1, min(20, volume_level + change))
    pygame.mixer.music.set_volume(volume_level / 20)

def draw_volume_bar(x, y, w, h):
    for i in range(20):
        bar_rect = pygame.Rect(x + i * (w // 20), y, (w // 20) - 2, h)
        color = YELLOW if i < volume_level else GRAY
        pygame.draw.rect(screen, color, bar_rect)

while running:
    screen.blit(background, (0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if game_state == "playing" and event.key == pygame.K_ESCAPE:
                game_state = "paused"
            elif game_state == "paused" and event.key == pygame.K_ESCAPE:
                game_state = "playing"

    if game_state == "playing":
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player.left > 0:
            player.x -= player_speed
        if keys[pygame.K_RIGHT] and player.right < WIDTH:
            player.x += player_speed
        if keys[pygame.K_UP] and player.top > 0:
            player.y -= player_speed
        if keys[pygame.K_DOWN] and player.bottom < HEIGHT:
            player.y += player_speed

        # Gegnerbewegung
        enemy1.x += enemy1_speed
        if enemy1.left <= 100 or enemy1.right >= 700:
            enemy1_speed *= -1

        if game_level >= 2:
            enemy2.x += enemy2_speed
            if enemy2.left <= 100 or enemy2.right >= 700:
                enemy2_speed *= -1

        if game_level == 3:
            enemy3.x += enemy3_speed
            if enemy3.left <= 100 or enemy3.right >= 700:
                enemy3_speed *= -1
            enemy4.y += enemy4_speed
            if enemy4.top <= 50 or enemy4.bottom >= 550:
                enemy4_speed *= -1

        # Laserfalle steuern
        if game_level == 3:
            trap_laser_timer -= 1
            if trap_laser_timer <= 0:
                trap_laser_active = not trap_laser_active
                trap_laser_timer = 90

        # Kollisionserkennung
        if (
            player.colliderect(enemy1) or
            (game_level >= 2 and player.colliderect(enemy2)) or
            (game_level == 3 and (player.colliderect(enemy3) or player.colliderect(enemy4))) or
            (game_level == 2 and player.colliderect(trap_ground)) or
            (game_level == 3 and trap_laser_active and player.colliderect(trap_laser))
        ):
            death_text = random.choice(death_messages)
            game_state = "dead"

        if player.colliderect(goal):
            if game_level < 3:
                game_level += 1
                restart_game()
            else:
                game_state = "win"

        # Zeichnen
        screen.blit(player_image, (player.x, player.y))
        screen.blit(trap_image, (enemy1.x, enemy1.y))
        if game_level >= 2:
            screen.blit(trap_image, (enemy2.x, enemy2.y))
        if game_level == 3:
            screen.blit(trap_image, (enemy3.x, enemy3.y))
            screen.blit(trap2_image, (enemy4.x, enemy4.y))

        if game_level == 2:
            pygame.draw.rect(screen, (120, 0, 0), trap_ground)
        if game_level == 3 and trap_laser_active:
            pygame.draw.rect(screen, (255, 0, 255), trap_laser)

        if goal_image:
            screen.blit(goal_image, (goal.x, goal.y))
        else:
            pygame.draw.rect(screen, GREEN, goal)

        if show_intro:
            pygame.draw.rect(screen, DARK_BLUE, (WIDTH//2 - 200, 10, 400, 60))
            font = pygame.font.SysFont("comicsansms", 32)
            text = font.render("Du musst hier schnell raus!", True, WHITE)
            screen.blit(text, (WIDTH // 2 - text.get_width() // 2, 25))
            intro_timer -= 1
            if intro_timer <= 0:
                show_intro = False

    elif game_state == "paused":
        screen.fill(DARK_BLUE)
        font = pygame.font.SysFont(None, 70)
        text = font.render("Pause", True, WHITE)
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, 150))
        draw_button("Weiterspielen (ESC)", WIDTH // 2 - 150, 280, 300, 60, (0, 100, 200), (0, 150, 250), resume_game)
        draw_button("Neustarten", WIDTH // 2 - 150, 360, 300, 60, (100, 0, 0), (150, 0, 0), restart_game)
        draw_button("Optionen", WIDTH // 2 - 150, 440, 300, 60, (120, 120, 0), (170, 170, 0), lambda: set_game_state("options"))

    elif game_state == "options":
        screen.fill(DARK_BLUE)
        font = pygame.font.SysFont(None, 70)
        text = font.render("Optionen", True, WHITE)
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, 120))

        font_small = pygame.font.SysFont(None, 40)
        vol_text = font_small.render(f"Lautstärke: {volume_level}/20", True, WHITE)
        screen.blit(vol_text, (WIDTH // 2 - 80, 200))
        draw_volume_bar(WIDTH // 2 - 100, 240, 200, 30)
        draw_button("+", WIDTH // 2 + 120, 240, 40, 30, (0, 150, 0), (0, 200, 0), lambda: change_volume(1))
        draw_button("-", WIDTH // 2 - 160, 240, 40, 30, (150, 0, 0), (200, 0, 0), lambda: change_volume(-1))
        draw_button("Zurück", WIDTH // 2 - 100, 320, 200, 60, (0, 100, 200), (0, 150, 250), resume_game)

    elif game_state == "dead":
        font = pygame.font.SysFont(None, 60)
        text = font.render(death_text, True, RED)
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, 200))
        draw_button("Neustarten", WIDTH // 2 - 100, 350, 200, 60, (0, 100, 200), (0, 150, 250), restart_game)

    elif game_state == "win":
        screen.fill((0, 180, 0))
        font = pygame.font.SysFont(None, 80)
        text = font.render("Du hast gewonnen!", True, WHITE)
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, 250))
        draw_button("Nochmal spielen", WIDTH // 2 - 120, 350, 240, 60, (0, 100, 200), (0, 150, 250), restart_game)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
