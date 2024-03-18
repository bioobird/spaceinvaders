import pygame
import random
import time

# Initialize Pygame
pygame.init()

# Game window parameters
WINDOW_WIDTH, WINDOW_HEIGHT = 800, 600
window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Space Invaders")

# Define colors
BLACK, WHITE, GREEN, RED, BLUE, ORANGE = (0, 0, 0), (255, 255, 255), (0, 255, 0), (255, 0, 0), (0, 0, 255), (255, 165, 0)

# Player properties adjusted for width
SPACESHIP_WIDTH, SPACESHIP_HEIGHT = 25, 30
spaceship_x = (WINDOW_WIDTH - SPACESHIP_WIDTH) // 2
spaceship_y = WINDOW_HEIGHT - SPACESHIP_HEIGHT - 10
spaceship_speed = 5

# Bullet properties - Adjusted player bullet fire rate for fairness
player_bullets = []
player_bullet_speed = -10
player_bullet_fire_rate = 150  # More frequent firing
last_player_shot_time = pygame.time.get_ticks()

enemy_bullets = []
enemy_bullet_speed = 3

# Enemies
enemies = []
enemy_fire_rate = 2000
current_stage = 1
boss_health = 10

# Explosions
explosions = []

# Score and font
score = 0
font = pygame.font.SysFont(None, 36)

def generate_enemies(stage):
    global enemies
    enemies.clear()
    enemy_size = SPACESHIP_WIDTH if stage < 3 else SPACESHIP_WIDTH * 6
    enemy_speed = 2
    enemy_count = 10 if stage < 3 else 1
    
    for _ in range(enemy_count):
        enemies.append({
            'x': random.randint(0, WINDOW_WIDTH - enemy_size),
            'y': random.randint(50, 150) if stage < 3 else 50,
            'width': enemy_size,
            'height': enemy_size,
            'speed': random.choice([-1, 1]) * enemy_speed,
            'health': 1 if stage < 3 else boss_health,
            'is_boss': stage == 3,
            'last_shot': pygame.time.get_ticks()
        })

def explode(x, y, size):
    explosions.append({'x': x, 'y': y, 'size': size, 'timer': 10})

def fire_bullet(rect, speed, is_enemy):
    (enemy_bullets if is_enemy else player_bullets).append({
        'rect': rect,
        'speed': speed,
        'is_enemy': is_enemy
    })

def check_stage_progression():
    global current_stage
    if not enemies:
        current_stage += 1
        if current_stage <= 3:
            generate_enemies(current_stage)
        else:
            display_end_game_message("You Win! Your Score: " + str(score))

def display_end_game_message(message):
    window.fill(BLACK)
    text = font.render(message, True, WHITE)
    window.blit(text, (WINDOW_WIDTH // 2 - text.get_width() // 2, WINDOW_HEIGHT // 2 - text.get_height() // 2))
    pygame.display.update()
    pygame.time.delay(3000)
    global running
    running = False

def update_display():
    window.fill(BLACK)
    pygame.draw.rect(window, WHITE, (spaceship_x, spaceship_y, SPACESHIP_WIDTH, SPACESHIP_HEIGHT))
    for enemy in enemies:
        pygame.draw.rect(window, RED if not enemy['is_boss'] else BLUE, (enemy['x'], enemy['y'], enemy['width'], enemy['height']))
        if enemy['is_boss']:
            health_bar_width = 200 * enemy['health'] / boss_health
            pygame.draw.rect(window, GREEN, (WINDOW_WIDTH - 210, 20, health_bar_width, 20))
    for bullet in player_bullets + enemy_bullets:
        color = GREEN if not bullet['is_enemy'] else RED
        pygame.draw.ellipse(window, color, bullet['rect'])
    for explosion in explosions[:]:
        pygame.draw.circle(window, ORANGE, (explosion['x'], explosion['y']), explosion['size'])
        explosion['timer'] -= 1
        if explosion['timer'] <= 0:
            explosions.remove(explosion)
    pygame.display.flip()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and pygame.time.get_ticks() - last_player_shot_time > player_bullet_fire_rate:
                bullet_rect = pygame.Rect(spaceship_x + SPACESHIP_WIDTH // 2 - 2, spaceship_y, 4, 4)
                fire_bullet(bullet_rect, player_bullet_speed, False)
                last_player_shot_time = pygame.time.get_ticks()

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and spaceship_x > 0:
        spaceship_x -= spaceship_speed
    if keys[pygame.K_RIGHT] and spaceship_x < WINDOW_WIDTH - SPACESHIP_WIDTH:
        spaceship_x += spaceship_speed

    # Enemy shooting logic
    now = pygame.time.get_ticks()
    for enemy in enemies[:]:
        enemy['x'] += enemy['speed']
        if enemy['x'] <= 0 or enemy['x'] + enemy['width'] >= WINDOW_WIDTH:
            enemy['speed'] *= -1
        if now - enemy['last_shot'] > enemy_fire_rate and random.random() > 0.5:  # Random chance to fire
            bullet_size = 60 if enemy['is_boss'] else 20
            bullet_rect = pygame.Rect(enemy['x'] + enemy['width'] // 2 - bullet_size // 2, enemy['y'] + enemy['height'], bullet_size, bullet_size)
            fire_bullet(bullet_rect, enemy_bullet_speed, True)
            enemy['last_shot'] = now

    # Bullet movement and collision
    for bullet in player_bullets + enemy_bullets[:]:
        bullet['rect'].y += bullet['speed']
        if bullet['rect'].y < 0 or bullet['rect'].y > WINDOW_HEIGHT:
            (enemy_bullets if bullet['is_enemy'] else player_bullets).remove(bullet)
            continue
        if bullet['is_enemy']:
            if bullet['rect'].colliderect(pygame.Rect(spaceship_x, spaceship_y, SPACESHIP_WIDTH, SPACESHIP_HEIGHT)):
                display_end_game_message("Game Over! Your Score: " + str(score))
        else:
            for enemy in enemies[:]:
                if bullet['rect'].colliderect(pygame.Rect(enemy['x'], enemy['y'], enemy['width'], enemy['height'])):
                    player_bullets.remove(bullet)
                    explode(enemy['x'] + enemy['width'] // 2, enemy['y'] + enemy['height'] // 2, enemy['width']/2)
                    enemy['health'] -= 1
                    if enemy['health'] <= 0:
                        enemies.remove(enemy)
                        score += 500 if enemy['is_boss'] else 100
                    break

    if not enemies:
        check_stage_progression()

    update_display()
    pygame.time.delay(10)

pygame.quit()
