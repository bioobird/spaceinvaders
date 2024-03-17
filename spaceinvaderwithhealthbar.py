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
SPACESHIP_WIDTH, SPACESHIP_HEIGHT = 50, 30
spaceship_x = (WINDOW_WIDTH - SPACESHIP_WIDTH) // 2
spaceship_y = WINDOW_HEIGHT - SPACESHIP_HEIGHT - 10
spaceship_speed = 5

# Bullet properties
bullets = []
player_bullet_speed = -10  # Negative for bullets moving upwards
enemy_bullet_speed = 3  # Positive for enemy bullets moving downwards
bullet_fire_rate = 300  # Milliseconds between shots
last_shot_time = pygame.time.get_ticks()

# Enemies
enemies = []
enemy_fire_rate = 1000  # Milliseconds between enemy shots
current_stage = 1
boss_health = 10  # Number of hits the boss can take

# Explosions
explosions = []

# Score and font
score = 0
font = pygame.font.SysFont(None, 36)

def generate_enemies(stage):
    global enemies
    enemies.clear()
    enemy_size = SPACESHIP_WIDTH // 2 if stage < 3 else SPACESHIP_WIDTH * 3
    enemy_speed = 2
    enemy_count = 10 if stage < 3 else 1  # Boss in stage 3
    
    for _ in range(enemy_count):
        enemies.append({
            'x': random.randint(0, WINDOW_WIDTH - enemy_size),
            'y': random.randint(50, 150) if stage < 3 else 50,  # Higher for the boss
            'width': enemy_size,
            'height': enemy_size,
            'speed': random.choice([-1, 1]) * enemy_speed,
            'health': 1 if stage < 3 else boss_health,
            'is_boss': stage == 3,
            'last_shot': pygame.time.get_ticks()
        })

def explode(x, y, size):
    '''Create an explosion at the given location with the given size'''
    explosions.append({'x': x, 'y': y, 'size': size, 'timer': 10})  # timer for explosion duration

def fire_enemy_bullet(enemy):
    '''Fires a bullet from the enemy'''
    bullets.append({
        'x': enemy['x'] + enemy['width'] // 2,
        'y': enemy['y'] + enemy['height'],
        'speed': enemy_bullet_speed,
        'is_enemy': True
    })

generate_enemies(current_stage)

def check_stage_progression():
    global current_stage
    if not enemies:
        if current_stage < 3:
            current_stage += 1
            generate_enemies(current_stage)
        else:
            display_end_game_message("You Win! Your Score: " + str(score))

def display_end_game_message(message):
    for _ in range(50):  # Dramatic finale for the boss
        explode(random.randint(100, WINDOW_WIDTH - 100), random.randint(100, WINDOW_HEIGHT - 100), random.randint(20, 50))
    update_display()  # Show all explosions
    pygame.time.delay(3000)
    window.fill(BLACK)
    text = font.render(message, True, WHITE)
    window.blit(text, (WINDOW_WIDTH // 2 - text.get_width() // 2, WINDOW_HEIGHT // 2 - text.get_height() // 2))
    pygame.display.update()
    pygame.time.delay(3000)
    global running
    running = False

def update_display():
    '''Handles drawing everything including explosions and the boss health bar'''
    window.fill(BLACK)
    pygame.draw.rect(window, WHITE, (spaceship_x, spaceship_y, SPACESHIP_WIDTH, SPACESHIP_HEIGHT))
    for enemy in enemies:
        pygame.draw.rect(window, RED if not enemy['is_boss'] else BLUE, (enemy['x'], enemy['y'], enemy['width'], enemy['height']))
        if enemy['is_boss']:  # Draw boss health bar
            health_bar_width = 200 * enemy['health'] / boss_health
            pygame.draw.rect(window, GREEN, (WINDOW_WIDTH - 210, 20, health_bar_width, 20))
    for bullet in bullets:
        color = GREEN if not bullet['is_enemy'] else RED
        pygame.draw.rect(window, color, (bullet['x'], bullet['y'], 2, 5))
    for explosion in explosions[:]:
        pygame.draw.circle(window, ORANGE, (explosion['x'], explosion['y']), explosion['size'])
        explosion['timer'] -= 1
        if explosion['timer'] <= 0:
            explosions.remove(explosion)
    pygame.display.flip()

running = True
# Main game loop
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and pygame.time.get_ticks() - last_shot_time > bullet_fire_rate:
                bullets.append({'x': spaceship_x + SPACESHIP_WIDTH // 2, 'y': spaceship_y, 'speed': player_bullet_speed, 'is_enemy': False})
                last_shot_time = pygame.time.get_ticks()

    # Player movement
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and spaceship_x > 0:
        spaceship_x -= spaceship_speed
    elif keys[pygame.K_RIGHT] and spaceship_x < WINDOW_WIDTH - SPACESHIP_WIDTH:
        spaceship_x += spaceship_speed

    current_time = pygame.time.get_ticks()
    for enemy in enemies[:]:
        if current_time - enemy['last_shot'] > enemy_fire_rate:
            fire_enemy_bullet(enemy)
            enemy['last_shot'] = current_time
        enemy['x'] += enemy['speed']
        if enemy['x'] <= 0 or enemy['x'] + enemy['width'] >= WINDOW_WIDTH:
            enemy['speed'] *= -1

    for bullet in bullets[:]:
        bullet['y'] += bullet['speed']
        if bullet['y'] < 0 or bullet['y'] > WINDOW_HEIGHT:
            bullets.remove(bullet)
            continue
        if bullet['is_enemy']:
            if spaceship_x < bullet['x'] < spaceship_x + SPACESHIP_WIDTH and spaceship_y < bullet['y'] < spaceship_y + SPACESHIP_HEIGHT:
                display_end_game_message("Game Over! Your Score: " + str(score))
        else:
            for enemy in enemies[:]:
                if enemy['x'] < bullet['x'] < enemy['x'] + enemy['width'] and enemy['y'] < bullet['y'] < enemy['y'] + enemy['height']:
                    bullets.remove(bullet)
                    explode(enemy['x'] + enemy['width'] // 2, enemy['y'] + enemy['height'] // 2, enemy['width'])  # Show explosion
                    enemy['health'] -= 1
                    if enemy['health'] <= 0:
                        enemies.remove(enemy)
                        score += 500 if enemy['is_boss'] else 100
                        check_stage_progression()
                    break
    
    update_display()  # Update and draw everything each frame

    pygame.time.delay(10)

pygame.quit()
