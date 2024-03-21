import pygame
import random
import time
import math

# Initialize Pygame and its mixer
pygame.init()
pygame.mixer.init()

# Global Oscillation Variables
tail_angle = 0
oscillation_amplitude = 10  # Feel free to adjust
oscillation_speed = 0.05  # Feel free to adjust
particles = []

# Load the sound
player_hit_sound = pygame.mixer.Sound("pacman_dies_y.wav")
blaster_sound = pygame.mixer.Sound("blaster.wav")  # Loading the blaster sound
enemy_hit_sound = pygame.mixer.Sound("a-team_shut_up_fool_x.wav")

# Game window parameters
WINDOW_WIDTH, WINDOW_HEIGHT = 800, 600
window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Space Invaders")

# Define colors
BLACK, WHITE, GREEN, RED, BLUE, ORANGE, YELLOW = (0, 0, 0), (255, 255, 255), (0, 255, 0), (255, 0, 0), (0, 0, 255), (255, 165, 0), (255, 255, 0)

# Particle class definition
class Particle:
    def __init__(self, x, y, color, size, velocity_x, velocity_y, lifetime):
        self.x = x
        self.y = y
        self.color = color
        self.size = size
        self.velocity_x = velocity_x
        self.velocity_y = velocity_y
        self.lifetime = lifetime

    def update(self):
        self.x += self.velocity_x
        self.y += self.velocity_y
        self.lifetime -= 1

    def draw(self, window):
        pygame.draw.rect(window, self.color, (self.x, self.y, self.size, self.size))
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
boss_health = 11  # Stage 3 boss health updated to 11 hits
stage_4_boss_health = 40  # Stage 4 boss health

# Explosions
explosions = []

# Score and font
score = 0
font = pygame.font.SysFont(None, 36)

def draw_angry_face(x, y, enemy):
    if enemy['enemy_type'].startswith('enemy'):
        # Drawing code for regular enemies remains unchanged
        pygame.draw.circle(window, BLACK, (x + 5, y + 10), 5)
        pygame.draw.circle(window, BLACK, (x + 20, y + 10), 5)
        if enemy['mouth_state'] == 'open':
            pygame.draw.circle(window, BLACK, (x + 12, y + 20), 3)
        else:
            pygame.draw.line(window, BLACK, (x + 5, y + 20), (x + 20, y + 20), 2)
    else:
        # Bosses have bigger faces
        pygame.draw.circle(window, WHITE, (x + 10, y + 20), 15)  # Add a white circle for the eye
        pygame.draw.circle(window, WHITE, (x + 65, y + 20), 15)  # Add a white circle for the eye
        pygame.draw.circle(window, BLACK, (x + 15, y + 30), 10)  # Black circle for the pupil
        pygame.draw.circle(window, BLACK, (x + 60, y + 30), 10)  # Black circle for the pupil
        if enemy['mouth_state'] == 'open':
            pygame.draw.circle(window, BLACK, (x + 37, y + 60), 20)
        else:
            pygame.draw.line(window, BLACK, (x + 15, y + 60), (x + 60, y + 60), 5)

        # Adjusted call to draw_tail with corrected parameters
        draw_tail(x, y, enemy['width'], enemy['height'])

def draw_tail(x, y, enemy_width, enemy_height):
    global tail_angle
    tail_color = GREEN  # Tail color for "boss" enemies

    # Adjustable Tail Parameters (Adjust these as needed)
    tail_width = 90  # Width of the tail's base
    tail_height = 40  # Height from base to tip of the tail
    oscillation_amplitude = 5  # How much the tail moves up and down
    oscillation_speed = 0.05  # Speed of tail movement - this affects 'tail_angle' update rate

    # Oscillation logic for natural movement
    oscillation = math.sin(tail_angle) * oscillation_amplitude  # Adjust multiplier for greater range

    # Starting position of the tail, centering it vertically on the enemy
    tail_start_x = x + enemy_width  # Positions the tail right next to the enemy
    tail_start_y = y + (enemy_height // 2) - (tail_height // 2) + oscillation  # Apply oscillation here
    
    # Define points for the oscillating triangle tail
    point1 = (tail_start_x, tail_start_y)
    point2 = (tail_start_x + tail_width, tail_start_y + (tail_height // 2))  # Tip of the tail
    point3 = (tail_start_x, tail_start_y + tail_height)  # Bottom base corner of the tail
    
    # Draw the oscillating tail
    pygame.draw.polygon(window, tail_color, [point1, point2, point3])

    # Your event handling
    pass

def toggle_enemy_mouth_state(enemy):
    enemy['mouth_state'] = 'open' if enemy['mouth_state'] == 'closed' else 'closed'

def next_stage():
    global current_stage
    current_stage += 1
    generate_enemies(current_stage)

def check_all_enemies_defeated():
    global running
    if not enemies:
        if current_stage == 4:
            display_end_game_message("SALLY WINS")
            running = False
        else:
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
            'mouth_state': 'closed',
            'last_shot': pygame.time.get_ticks()
        })

def generate_particles(x, y, enemy_type):
    size_mapping = {
        'enemy1': 30,
        'enemy2': 45,
        'boss3': 200,
        'boss4': 450
    }

    particle_color = ORANGE
    particle_size = 2
    particle_lifetime = 30

    num_particles = size_mapping.get(enemy_type, 30) // 2  # Generate number of particles based on enemy type
    for _ in range(num_particles):
        particle_velocity_x = random.randint(-5, 5)
        particle_velocity_y = random.randint(-5, 5)
        particle_x = x + random.randint(-10, 10)
        particle_y = y + random.randint(-10, 10)
        
        new_particle = Particle(particle_x, particle_y, particle_color, particle_size, particle_velocity_x, particle_velocity_y, particle_lifetime)
        particles.append(new_particle)

    return particles

def fire_bullet(rect, speed, is_enemy, enemy_type=None, enemy=None):
    if enemy_type == 'enemy1':
        size = ENEMY1_BULLET_SIZE = (20, 50)
    elif enemy_type == 'enemy2':
        size = ENEMY2_BULLET_SIZE = (30, 70)
    elif enemy_type == 'boss3':
        size = BOSS3_BULLET_SIZE = (100, 130)
    elif enemy_type == 'boss4':
        size = BOSS4_BULLET_SIZE = (230, 200)
    else:
        size = (20, 20)  # Default bullet size

    bullet = {
        'rect': pygame.Rect(rect.x, rect.y, size[0], size[1]),
        'speed': speed,
        'is_enemy': is_enemy
    }
    (enemy_bullets if is_enemy else player_bullets).append(bullet)
    if enemy:
        toggle_enemy_mouth_state(enemy)  # Toggle mouth state when enemy fires

def display_end_game_message(message):
    window.fill(BLACK)
    text = font.render(message, True, WHITE)
    window.blit(text, (WINDOW_WIDTH // 2 - text.get_width() // 2, WINDOW_HEIGHT // 2 - text.get_height() // 2))
    pygame.display.update()
    pygame.time.wait(5000)  # Wait for 5 seconds

def update_display():
    window.fill(BLACK)
    # ... (other drawing code)

    for explosion in explosions:
        for particle in explosion:
            if particle.lifetime > 0:
                particle.update()
                particle.draw(window)
            else:
                explosion.remove(particle)

    pygame.display.flip()

    # Draw the cat head
    pygame.draw.circle(window, WHITE, (spaceship_x + SPACESHIP_WIDTH // 2, spaceship_y + SPACESHIP_HEIGHT // 2), SPACESHIP_WIDTH // 2)  # Head
    pygame.draw.circle(window, BLACK, (spaceship_x + SPACESHIP_WIDTH // 4, spaceship_y + SPACESHIP_HEIGHT // 4), SPACESHIP_WIDTH // 8)  # Left eye
    pygame.draw.circle(window, BLACK, (spaceship_x + SPACESHIP_WIDTH * 3 // 4, spaceship_y + SPACESHIP_HEIGHT // 4), SPACESHIP_WIDTH // 8)  # Right eye
    pygame.draw.line(window, BLACK, (spaceship_x + SPACESHIP_WIDTH // 4, spaceship_y + SPACESHIP_HEIGHT * 3 // 4), (spaceship_x + SPACESHIP_WIDTH * 3 // 4, spaceship_y + SPACESHIP_HEIGHT * 3 // 4), 2)  # Mouth

    # Draw the tabby stripes
    for i in range(3):
        start_x = spaceship_x + SPACESHIP_WIDTH // 4
        start_y = spaceship_y + SPACESHIP_HEIGHT // 4 + i * (SPACESHIP_HEIGHT // 8)
        end_x = spaceship_x + SPACESHIP_WIDTH * 3 // 4
        end_y = start_y
        pygame.draw.line(window, BLACK, (start_x, start_y), (end_x, end_y), 2)

    # ... (rest of the code)
    for enemy in enemies:
        enemy_color = RED if not enemy['is_boss'] else BLUE
        pygame.draw.rect(window, enemy_color, (enemy['x'], enemy['y'], enemy['width'], enemy['height']))
        draw_angry_face(enemy['x'], enemy['y'], enemy)  # Pass the enemy object
        if enemy['is_boss']:
            max_health = boss_health if enemy['enemy_type'] == 'boss3' else stage_4_boss_health
            health_percentage = enemy['health'] / max_health
            pygame.draw.rect(window, GREEN, (WINDOW_WIDTH - 210, 10, 200 * health_percentage, 20))
    
    for bullet in player_bullets + enemy_bullets:
        bullet_color = GREEN if not bullet['is_enemy'] else RED
        pygame.draw.rect(window, bullet_color, bullet['rect'])
    
    for explosion in explosions[:]:
        pygame.draw.circle(window, ORANGE, (explosion['x'], explosion['y']), explosion['size'])
        explosion['timer'] -= 1
        if explosion['timer'] <= 0:
            explosions.remove(explosion)
    pygame.display.flip()

generate_enemies(current_stage)

running = True
while running:
    # Update tail_angle to animate tails
    tail_angle += oscillation_speed

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and pygame.time.get_ticks() - last_player_shot_time > player_bullet_fire_rate:
                fire_bullet(pygame.Rect(spaceship_x + SPACESHIP_WIDTH // 2 - 10, spaceship_y, 20, 20), player_bullet_speed, False)
                blaster_sound.play()

    # Player movement
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and spaceship_x > 0:
        spaceship_x -= spaceship_speed
    if keys[pygame.K_RIGHT] and spaceship_x < WINDOW_WIDTH - SPACESHIP_WIDTH:
        spaceship_x += spaceship_speed

    # Enemy logic and bullet update
    now = pygame.time.get_ticks()
    for enemy in enemies[:]:
        enemy['x'] += enemy['speed']
        if enemy['x'] <= 0 or enemy['x'] + enemy['width'] >= WINDOW_WIDTH:
            enemy['speed'] *= -1
        if now - enemy['last_shot'] > enemy_fire_rate and enemy['health'] > 0:
            fire_bullet(pygame.Rect(enemy['x'] + enemy['width'] // 2, enemy['y'] + enemy['height'], 20, 20), enemy_bullet_speed, True, enemy['enemy_type'], enemy)
            enemy['last_shot'] = now

        # Existing enemy logic and bullet update stays unchanged

    # Processing enemy and player bullets
    for bullet in player_bullets[:] + enemy_bullets[:]:  # Combine lists for iteration
        bullet_rect = bullet['rect']
        bullet['rect'].y += bullet['speed']

        if bullet_rect.y < 0 or bullet_rect.y > WINDOW_HEIGHT:
            if bullet in player_bullets:
                player_bullets.remove(bullet)
            elif bullet in enemy_bullets:  # Use elif for clarity
                enemy_bullets.remove(bullet)
        else:
            # Player bullet collision detection with enemies
            if not bullet['is_enemy']:  
                for enemy in enemies[:]:  
                    if bullet_rect.colliderect(pygame.Rect(enemy['x'], enemy['y'], enemy['width'], enemy['height'])):
                        enemy_hit_sound.play()
                        player_bullets.remove(bullet)  # Bullet cleanup
                        
                        # Particle effect for hitting an enemy
                        generate_particles(enemy['x'] + enemy['width'] // 2, enemy['y'] + enemy['height'] // 2, enemy['enemy_type'])
                        
                        enemy['health'] -= 1
                        if enemy['health'] <= 0:
                            enemies.remove(enemy)  # Enemy cleanup
                            score += 1000 if enemy['is_boss'] else 500
                        break  # Stop checking once a bullet hits an enemy

    # NEW: Collision detection for enemy bullets with the player
    player_rect = pygame.Rect(spaceship_x, spaceship_y, SPACESHIP_WIDTH, SPACESHIP_HEIGHT)
        # Collision detection for enemy bullets with the player
    player_rect = pygame.Rect(spaceship_x, spaceship_y, SPACESHIP_WIDTH, SPACESHIP_HEIGHT)
    for bullet in enemy_bullets[:]:
        if player_rect.colliderect(bullet['rect']):
            # If a collision is detected, play the hit sound
            player_hit_sound.play()

            # Remove the bullet that hit the player
            enemy_bullets.remove(bullet)

            # Display the game over message and end the game loop
            display_end_game_message("Game Over! Your Score: " + str(score))
            
            # Wait a bit before closing to let the player see the message 
            pygame.time.wait(2000)  # Delay in milliseconds

            # Here, 'running = False' is used to break from the game loop
            running = False
            
            break  # Exit the loop to prevent processing further bullets after game over  # Assuming one hit per update cycle; remove if processing all hits

    # Check if all enemies are defeated remains unchanged
    check_all_enemies_defeated()

    # Drawing game objects and particles
    window.fill(BLACK)
    # Draw the spaceship
    pygame.draw.circle(window, WHITE, (spaceship_x + SPACESHIP_WIDTH // 2, spaceship_y + SPACESHIP_HEIGHT // 2), SPACESHIP_WIDTH // 2)  # Head
    pygame.draw.circle(window, BLACK, (spaceship_x + SPACESHIP_WIDTH // 4, spaceship_y + SPACESHIP_HEIGHT // 4), SPACESHIP_WIDTH // 8)  # Left eye
    pygame.draw.circle(window, BLACK, (spaceship_x + SPACESHIP_WIDTH * 3 // 4, spaceship_y + SPACESHIP_HEIGHT // 4), SPACESHIP_WIDTH // 8)  # Right eye
    pygame.draw.line(window, BLACK, (spaceship_x + SPACESHIP_WIDTH // 4, spaceship_y + SPACESHIP_HEIGHT * 3 // 4), (spaceship_x + SPACESHIP_WIDTH * 3 // 4, spaceship_y + SPACESHIP_HEIGHT * 3 // 4), 2)  # Mouth
    # Draw the tabby stripes
    for i in range(3):
        start_x = spaceship_x + SPACESHIP_WIDTH // 4
        start_y = spaceship_y + SPACESHIP_HEIGHT // 4 + i * (SPACESHIP_HEIGHT // 8)
        end_x = spaceship_x + SPACESHIP_WIDTH * 3 // 4
        end_y = start_y
        pygame.draw.line(window, BLACK, (start_x, start_y), (end_x, end_y), 2)

    for enemy in enemies:
        enemy_color = RED if not enemy['is_boss'] else BLUE
        pygame.draw.rect(window, enemy_color, (enemy['x'], enemy['y'], enemy['width'], enemy['height']))
        draw_angry_face(enemy['x'], enemy['y'], enemy)

    for bullet in player_bullets + enemy_bullets:
        bullet_color = GREEN if not bullet['is_enemy'] else RED
        pygame.draw.rect(window, bullet_color, bullet['rect'])

    for particle in particles:
        if particle.lifetime > 0:
            particle.update()
            particle.draw(window)
        else:
            particles.remove(particle)

    pygame.display.flip()
    pygame.time.delay(10)

pygame.quit()
