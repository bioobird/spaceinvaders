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

# Player properties
SPACESHIP_WIDTH, SPACESHIP_HEIGHT = 25, 30
spaceship_x = (WINDOW_WIDTH - SPACESHIP_WIDTH) // 2
spaceship_y = WINDOW_HEIGHT - SPACESHIP_HEIGHT - 10
spaceship_speed = 5

# Bullet properties
player_bullets = []
player_bullet_speed = -10
player_bullet_fire_rate = 150  # milliseconds
last_player_shot_time = pygame.time.get_ticks()

enemy_bullets = []
enemy_bullet_speed = 3

# Enemies
enemies = []
enemy_fire_rate = 2000  # milliseconds
current_stage = 1
boss_health = 10  # Stage 3 boss health
stage_4_boss_health = 40  # Stage 4 boss health

# Explosions
explosions = []

# Score and font
score = 0
font = pygame.font.SysFont(None, 36)

def next_stage():
    global current_stage
    current_stage += 1
    generate_enemies(current_stage)

def check_all_enemies_defeated():
    if not enemies:
        next_stage()

def generate_enemies(stage):
    global enemies
    enemies.clear()
    if stage in [1, 2]:
        enemy_count = 10
        enemy_type = 'enemy1' if stage == 1 else 'enemy2'
        enemy_size = SPACESHIP_WIDTH
        enemy_health = 1
    elif stage == 3:
        enemy_count = 1
        enemy_type = 'boss3'
        enemy_size = SPACESHIP_WIDTH * 6
        enemy_health = boss_health
    else:  # Stage 4
        enemy_count = 1
        enemy_type = 'boss4'
        enemy_size = SPACESHIP_WIDTH * 6
        enemy_health = stage_4_boss_health
        
    for _ in range(enemy_count):
        enemies.append({
            'x': random.randint(0, WINDOW_WIDTH - enemy_size),
            'y': 50 if stage >= 3 else random.randint(50, 150),
            'width': enemy_size,
            'height': enemy_size,
            'speed': random.choice([-1, 1]) * 2,
            'health': enemy_health,
            'is_boss': stage >= 3,
            'enemy_type': enemy_type,
            'last_shot': pygame.time.get_ticks()
        })

def explode(x, y, size):
    explosions.append({'x': x, 'y': y, 'size': size, 'timer': 10})

def fire_bullet(rect, speed, is_enemy, size=(20, 20)):
    bullet = {
        'rect': pygame.Rect(rect.x, rect.y, size[0], size[1]),
        'speed': speed,
        'is_enemy': is_enemy
    }
    (enemy_bullets if is_enemy else player_bullets).append(bullet)

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
            health_bar_width = 200 * enemy['health'] / (boss_health if enemy['enemy_type'] == 'boss3' else stage_4_boss_health)
            pygame.draw.rect(window, GREEN, (WINDOW_WIDTH - 210, 20, health_bar_width, 20))
    for bullet in player_bullets + enemy_bullets:
        color = GREEN if not bullet['is_enemy'] else RED
        pygame.draw.rect(window, color, bullet['rect'])
    for explosion in explosions[:]:
        pygame.draw.circle(window, ORANGE, (explosion['x'], explosion['y']), explosion['size'])
        explosion['timer'] -= 1
        if explosion['timer'] <= 0:
            explosions.remove(explosion)
    pygame.display.flip()

generate_enemies(current_stage)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and pygame.time.get_ticks() - last_player_shot_time > player_bullet_fire_rate:
                fire_bullet(pygame.Rect(spaceship_x + SPACESHIP_WIDTH // 2 - 10, spaceship_y, 20, 20), player_bullet_speed, False)

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and spaceship_x > 0:
        spaceship_x -= spaceship_speed
    if keys[pygame.K_RIGHT] and spaceship_x < WINDOW_WIDTH - SPACESHIP_WIDTH:
        spaceship_x += spaceship_speed

    now = pygame.time.get_ticks()
    for enemy in enemies[:]:
        enemy['x'] += enemy['speed']
        if enemy['x'] <= 0 or enemy['x'] + enemy['width'] >= WINDOW_WIDTH:
            enemy['speed'] *= -1
        if now - enemy['last_shot'] > enemy_fire_rate:
            bullet_size = (20, 20) if enemy['enemy_type'] == 'enemy1' else (30, 30) if enemy['enemy_type'] == 'enemy2' else (60, 60) if enemy['enemy_type'] == 'boss3' else (100, 100)
            fire_bullet(pygame.Rect(enemy['x'] + enemy['width'] // 2 - bullet_size[0] // 2, enemy['y'] + enemy['height'], *bullet_size), enemy_bullet_speed, True, size=bullet_size)
            enemy['last_shot'] = now

    for bullet in player_bullets + enemy_bullets[:]:
        bullet['rect'].y += bullet['speed']
        if bullet['rect'].y < 0 or bullet['rect'].y > WINDOW_HEIGHT:
            (enemy_bullets if bullet['is_enemy'] else player_bullets).remove(bullet)
        else:
            if bullet['is_enemy']:
                if bullet['rect'].colliderect(pygame.Rect(spaceship_x, spaceship_y, SPACESHIP_WIDTH, SPACESHIP_HEIGHT)):
                    display_end_game_message("Game Over! Your Score: " + str(score))
            else:
                for enemy in enemies[:]:
                    if bullet['rect'].colliderect(pygame.Rect(enemy['x'], enemy['y'], enemy['width'], enemy['height'])):
                        player_bullets.remove(bullet)
                        explode(enemy['x'] + enemy['width'] // 2, enemy['y'] + enemy['height'] // 2, 20)
                        enemy['health'] -= 1
                        if enemy['health'] <= 0:
                            enemies.remove(enemy)
                            score += 1000 if enemy['is_boss'] else 500
                        break

    check_all_enemies_defeated()

    if current_stage > 4 and not enemies:  # Condition for winning the game after Stage 4 boss
        display_end_game_message("You Win! Your Score: " + str(score))

    update_display()
    pygame.time.delay(10)

pygame.quit()
