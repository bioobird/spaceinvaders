import pygame
import random
import time
import math

# Initialize Pygame and its mixer
pygame.init()
pygame.mixer.init()

# Load the sound
player_hit_sound = pygame.mixer.Sound("mixkit-arcade-retro-game-over-213.wav")
blaster_sound = pygame.mixer.Sound("blaster.wav")  # Loading the blaster sound
enemy_hit_sound = pygame.mixer.Sound("baseball_hit.wav")
backround_music = pygame.mixer.Sound("mixkit-blizzard-cold-winds-1153.wav")

# Game window parameters
WINDOW_WIDTH, WINDOW_HEIGHT = 800, 600
window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Space Invaders")

# Define colors
BLACK, WHITE, GREEN, RED, BLUE, ORANGE, YELLOW = (0, 0, 0), (255, 255, 255), (0, 255, 0), (255, 0, 0), (0, 0, 255), (255, 165, 0), (255, 255, 0)

# Global Oscillation Variables
tail_angle = 0
oscillation_amplitude = 10  # Feel free to adjust
oscillation_speed = 0.05  # Feel free to adjust
particles = []

SPACESHIP_WIDTH = 50

ENEMY1_SIZE = 25
ENEMY2_SIZE = 45
BOSS3_SIZE = SPACESHIP_WIDTH * 4  # You mentioned boss sizes in terms of the spaceship width
BOSS4_SIZE = SPACESHIP_WIDTH * 5  # Adjust these as necessary
BOSS5_SIZE = SPACESHIP_WIDTH * 6 
# Player properties
SPACESHIP_WIDTH, SPACESHIP_HEIGHT = 25, 30
spaceship_x = (WINDOW_WIDTH - SPACESHIP_WIDTH) // 2
spaceship_y = WINDOW_HEIGHT - SPACESHIP_HEIGHT - 10
spaceship_speed = 5
# Global variable for bubble projectiles
bubble_projectiles = []

# Bullet properties
player_bullets = []
player_bullet_speed = -5
player_bullet_fire_rate = 150  # milliseconds
last_player_shot_time = pygame.time.get_ticks()

enemy_bullets = []
enemy_bullet_speed = 3

# Enemies
enemies = []
enemy_fire_rate = 2000  # milliseconds
current_stage = 1

# Health definitions
enemy1_health = 1  # Health for each individual enemy in stages 1
enemy2_health = 1  # Health for each individual enemy in stages 2
boss3_health = 10  # Stage 3 boss health
boss4_health = 10  # Stage 4 boss health
boss5_health = 10  # Stage 5 boss health

# Explosions
explosions = []

# Score and font
score = 0
font = pygame.font.SysFont(None, 36)


def generate_particles(x, y, type):
    # Default values for particles
    num_particles = 20  # Adjust as necessary
    particle_color = ORANGE  # Adjust as needed
    particle_size = 2  # Default size of particles
    particle_lifetime = 30  # Default lifetime of particles

    # Adjustments for specific types
    if type == "bubble_pop":
        particle_color = ORANGE
    elif type == "enemy_hit":
        # Example customization for when an enemy is hit
        particle_color = RED
        particle_velocity_range = (-5, 5)  # Same range but different color
    else:
        # Default or unknown type handling
        particle_velocity_range = (-2, 2)  # Less explosive effect for default case
    
    # Loop to generate and append each new particle
    for _ in range(num_particles):
        particle_velocity_x = random.randint(*particle_velocity_range)
        particle_velocity_y = random.randint(*particle_velocity_range)
        particle_x = x + random.randint(-10, 10)  # Spawn around the event's position
        particle_y = y + random.randint(-10, 10)  # Spawn around the event's position
        
        new_particle = Particle(particle_x, particle_y, particle_color, particle_size, particle_velocity_x, particle_velocity_y, particle_lifetime)
        particles.append(new_particle)

def fire_bubble(x, y, enemy=None):
    # Create and add the bubble to the projectile list
    bubble = {
        'rect': pygame.Rect(x, y, 50, 50),  # Bubble size 50x50 pixels
        'speed': -2  # Slower upward movement
    }
    bubble_projectiles.append(bubble)

    # Check if an enemy object is passed and it's a boss that can toggle mouth state
    if enemy is not None and enemy['is_boss']:
        # Toggle the enemy's mouth state whenever a bubble is fired
        toggle_enemy_mouth_state(enemy)
        
    if enemy is not None:
        toggle_enemy_mouth_state(enemy)
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

def draw_angry_face(x, y, enemy):
    # Debugging - Remove after confirmation
    # print(f"Drawing face for {enemy['enemy_type']} with mouth_state {enemy['mouth_state']} at (x:{x}, y:{y})")
    
    if enemy['enemy_type'].startswith('enemy'):
        # Drawing code for regular enemies with enhanced eyes
        pygame.draw.circle(window, WHITE, (x + 5, y + 10), 7)  # Left eye
        pygame.draw.circle(window, WHITE, (x + 20, y + 10), 7)  # Right eye
        pygame.draw.circle(window, BLACK, (x + 5, y + 10), 5)   # Left pupil
        pygame.draw.circle(window, BLACK, (x + 20, y + 10), 5)  # Right pupil
        
        # Toggle mouth open/closed
        if enemy['mouth_state'] == 'open':
            pygame.draw.circle(window, BLACK, (x + 12, y + 20), 3)  # Mouth open
        else:
            pygame.draw.line(window, BLACK, (x + 5, y + 20), (x + 20, y + 20), 2)  # Mouth closed
    else:  
        # Drawing for bosses
        pygame.draw.circle(window, WHITE, (x + 10, y + 20), 15)  # Left eye
        pygame.draw.circle(window, WHITE, (x + 65, y + 20), 15)  # Right eye
        pygame.draw.circle(window, BLACK, (x + 15, y + 30), 10)  # Left pupil
        pygame.draw.circle(window, BLACK, (x + 60, y + 30), 10)  # Right pupil

        # Ensuring 'mouth_state' impacts boss mouth visuals. Draw open or closed mouth accordingly.
        if enemy['mouth_state'] == 'open':
            pygame.draw.circle(window, BLACK, (x + 37, y + 60), 20)  # Boss mouth open
        else:
            pygame.draw.line(window, BLACK, (x + 15, y + 60), (x + 60, y + 60), 5)  # Boss mouth closed # Boss mouth closed
    
    # Draw the tail for all enemies and bosses.
    draw_tail(x, y, enemy['width'], enemy['height'], enemy['enemy_type'])

# Ensure draw_tail is defined with the additional enemy_type parameter as previously described
def draw_tail(x, y, enemy_width, enemy_height, enemy_type):
    global tail_angle
    # The code inside your draw_tail function goes here
    # This includes your logic for oscillation and drawing the tail
    # Adjust tail colors and sizes based on enemy type
    if enemy_type in ['enemy1', 'enemy2']:
        tail_color = BLUE  # Different color for regular enemies, for distinction
        tail_width = 40  # Smaller width for regular enemy tails
        tail_height = 20  # Smaller height for regular enemy tails
        half_moon_radius = 10  # Smaller radius for the half-moon on regular enemies
    else:  # Defaults for boss3 and boss4
        tail_color = GREEN  # Tail color for "boss" enemies
        tail_width = 90  # Width of the tail's base
        tail_height = 40  # Height from base to tip of the tail
        half_moon_radius = 20  # Radius of the "C" shape or half-moon
    
    # Oscillation logic for natural movement
    oscillation = math.sin(tail_angle) * oscillation_amplitude

    # Starting position of the tail, adjusts with oscillation
    tail_start_x = x + enemy_width
    tail_start_y = y + (enemy_height // 2) - (tail_height // 2) + oscillation

    # Define points for the oscillating triangle tail
    point1 = (tail_start_x, tail_start_y)
    point2 = (tail_start_x + tail_width, tail_start_y + (tail_height // 2))  # Tip of the tail
    point3 = (tail_start_x, tail_start_y + tail_height)

    # Draw the oscillating tail triangle
    pygame.draw.polygon(window, tail_color, [point1, point2, point3])

    # Half-moon Parameters refined based on entity type
    half_moon_thickness = 5  # Thickness, constant for simplicity

    # The rectangle that bounds the circle (ellipse) from which the arc is generated
    arc_rect = [point2[0] - half_moon_radius, point2[1] - half_moon_radius,
                half_moon_radius * 2, half_moon_radius * 2]

    # Drawing the half-moon ("C" shape) at the tip of the tail
    pygame.draw.arc(window, tail_color, arc_rect,
                    math.pi/2, 3*math.pi/2, half_moon_thickness)  # Draw arc from π/2 to 3π/2 radians

    # Your event handling
    pass

def toggle_enemy_mouth_state(enemy):
    enemy['mouth_state'] = 'open' if enemy['mouth_state'] == 'closed' else 'closed'

def next_stage():
    global current_stage
    current_stage += 1
    generate_enemies(current_stage)

def check_all_enemies_defeated():
    global running, current_stage
    if not enemies:
        if current_stage == 5:  # Adjusting for Stage 5 completion
            display_end_game_message("YOU WIN!")
            running = False
        else:
            next_stage()

def generate_enemies(stage):
    global enemies
    enemies.clear()
    
    enemy_size_mapping = {
        'enemy1': ENEMY1_SIZE,
        'enemy2': ENEMY2_SIZE,
        'boss3': BOSS3_SIZE,
        'boss4': BOSS4_SIZE,
        'boss5': BOSS5_SIZE,
    }
    
    # Example logic for assigning health based on the stage and enemy type
    if stage in [1, 2]:
        enemy_count = 10
        enemy_type = 'enemy1' if stage == 1 else 'enemy2'
        enemy_health = enemy1_health if stage == 1 else enemy2_health
    elif stage == 3:
        enemy_count = 1
        enemy_type = 'boss3'
        enemy_health = boss3_health
    elif stage == 4:
        enemy_count = 1
        enemy_type = 'boss4'
        enemy_health = boss4_health
    elif stage == 5:
        enemy_count = 1
        enemy_type = 'boss5'
        enemy_health = boss5_health

    enemy_size = enemy_size_mapping[enemy_type]
    
    for _ in range(enemy_count):
        enemies.append({
            'x': random.randint(0, WINDOW_WIDTH - enemy_size),
            'y': 50 if stage >= 3 else random.randint(50, 150),
            'width': enemy_size,
            'height': enemy_size,  # Assuming square shape; adjust dimensions as necessary
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

def generate_bubble_particles(x, y):
    # Configuration for high visibility
    particle_color = YELLOW
    particle_size = 10
    particle_lifetime = 180
    num_particles = 50

    # Enhanced logic here:
    # For example, adjust the number of particles based on specific gameplay elements.
    # If you had different types of bubbles, this is where you'd adjust particle parameters accordingly.

    # Generates particles
    for _ in range(num_particles):
        particle_velocity_x = random.randint(-1, 1)  # Slight movement for more dynamism
        particle_velocity_y = random.randint(-1, 1)
        particle_x = x + random.randint(-5, 5)  # Small variation in spawn point for a burst effect
        particle_y = y + random.randint(-5, 5)
        
        new_particle = Particle(particle_x, particle_y, particle_color, particle_size, particle_velocity_x, particle_velocity_y, particle_lifetime)
        particles.append(new_particle)

def fire_bullet(rect, speed, is_enemy, enemy_type=None, enemy=None, is_bubble=False):
    # Define bullet sizes for all enemy types including boss5
    bullet_sizes = {
        'enemy1': (20, 50),
        'enemy2': (30, 70),
        'boss3': (100, 130),
        'boss4': (150, 150),
        'boss5': (120, 120),  # Define a unique or suitable size for boss5 bullets
    }

    if is_bubble:
        size = (50, 50)  # Fixed size for bubbles (width, height)
        speed = -2  # Upward movement for bubbles
    else:
        size = bullet_sizes.get(enemy_type, (20, 20))  # Use the get method to fetch sizes or default

    bullet = {
        'rect': pygame.Rect(rect.x, rect.y, size[0], size[1]),
        'speed': speed,
        'is_enemy': is_enemy,
        'is_bubble': is_bubble
    }
    (enemy_bullets if is_enemy else player_bullets).append(bullet)

    # Toggle mouth state (Ensure all necessary enemies, including bosses, have a 'mouth_state' attribute)
    if enemy and 'mouth_state' in enemy:
        toggle_enemy_mouth_state(enemy)

def display_end_game_message(message):
    window.fill(BLACK)
    text = font.render(message, True, WHITE)
    window.blit(text, (WINDOW_WIDTH // 2 - text.get_width() // 2, WINDOW_HEIGHT // 2 - text.get_height() // 2))
    pygame.display.update()
    pygame.time.wait(5000)  # Wait for 5 seconds

def update_display():
    # Clear the screen at the start of each frame
    window.fill(BLACK)

    # Draw the spaceship
    pygame.draw.circle(window, WHITE, (spaceship_x + SPACESHIP_WIDTH // 2, spaceship_y + SPACESHIP_HEIGHT // 2), SPACESHIP_WIDTH // 2)
    pygame.draw.circle(window, BLACK, (spaceship_x + SPACESHIP_WIDTH // 4, spaceship_y + SPACESHIP_HEIGHT // 4), SPACESHIP_WIDTH // 8)
    pygame.draw.circle(window, BLACK, (spaceship_x + SPACESHIP_WIDTH * 3 // 4, spaceship_y + SPACESHIP_HEIGHT // 4), SPACESHIP_WIDTH // 8)
    pygame.draw.line(window, BLACK, (spaceship_x + SPACESHIP_WIDTH // 4, spaceship_y + SPACESHIP_HEIGHT * 3 // 4), (spaceship_x + SPACESHIP_WIDTH * 3 // 4, spaceship_y + SPACESHIP_HEIGHT * 3 // 4), 2)

    # Draw the tabby stripes on the spaceship
    for i in range(3):
        start_x = spaceship_x + SPACESHIP_WIDTH // 4
        start_y = spaceship_y + SPACESHIP_HEIGHT // 4 + i * (SPACESHIP_HEIGHT // 8)
        end_x = spaceship_x + SPACESHIP_WIDTH * 3 // 4
        end_y = start_y
        pygame.draw.line(window, BLACK, (start_x, start_y), (end_x, end_y), 2)

    # Draw enemies and their health bars (if applicable)
    for enemy in enemies:
        enemy_color = RED if not enemy['is_boss'] else BLUE
        pygame.draw.rect(window, enemy_color, (enemy['x'], enemy['y'], enemy['width'], enemy['height']))
        draw_angry_face(enemy['x'], enemy['y'], enemy)
        draw_tail(enemy['x'], enemy['y'], enemy['width'], enemy['height'], enemy['enemy_type'])

        # Adjusted health bar drawing for boss enemies with specific variables
        if enemy['is_boss']:
            if enemy['enemy_type'] == 'boss3':
                max_health = boss3_health
            elif enemy['enemy_type'] == 'boss4':
                max_health = boss4_health
            elif enemy['enemy_type'] == 'boss5':  # Add support for boss5
                max_health = boss5_health
            health_percentage = enemy['health'] / max_health
            pygame.draw.rect(window, GREEN, (WINDOW_WIDTH - 210, 10, 200 * health_percentage, 20))

    # Draw all bullets
    for bullet in player_bullets + enemy_bullets:
        bullet_color = GREEN if not bullet['is_enemy'] else RED
        pygame.draw.rect(window, bullet_color, bullet['rect'])

    # Handle explosion effect particles
    for explosion in explosions[:]:
        pygame.draw.circle(window, ORANGE, (explosion['x'], explosion['y']), explosion['size'])
        explosion['timer'] -= 1
        if explosion['timer'] <= 0:
            explosions.remove(explosion)

    # Handle general particle effects
    for particle in particles[:]:
        if particle.lifetime > 0:
            particle.draw(window)
            particle.update()
        else:
            particles.remove(particle)

    # Update the display
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
            if event.key == pygame.K_SPACE and (pygame.time.get_ticks() - last_player_shot_time > player_bullet_fire_rate):
                last_player_shot_time = pygame.time.get_ticks()
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
    for enemy in enemies[:]:  # Ensure loop iteration is correct
        enemy['x'] += enemy['speed']
        if enemy['x'] <= 0 or enemy['x'] + enemy['width'] >= WINDOW_WIDTH:
            enemy['speed'] *= -1  # Reverse direction when hitting bounds

        if now - enemy['last_shot'] > enemy_fire_rate and enemy['health'] > 0:
            # Fire standard bullet
            fire_bullet(pygame.Rect(enemy['x'] + enemy['width'] // 2, enemy['y'] + enemy['height'], 20, 20), enemy_bullet_speed, True, enemy['enemy_type'], enemy)
            if enemy['enemy_type'] in ['boss3', 'boss4', 'boss5']:
                fire_bubble(enemy['x'] + enemy['width'] // 2 - 25, enemy['y'], enemy)  # Fire bubbles with the corrected function call
            enemy['last_shot'] = now

    # Processing enemy and player bullets
    for bullet in player_bullets[:] + enemy_bullets[:]:
        bullet['rect'].y += bullet['speed']
        if bullet['rect'].y < 0 or bullet['rect'].y > WINDOW_HEIGHT:
            if bullet in player_bullets:
                player_bullets.remove(bullet)
            if bullet in enemy_bullets:
                enemy_bullets.remove(bullet)
        else:
            # Collision detection with enemies
            if not bullet['is_enemy']:
                for enemy in enemies[:]:
                    if bullet['rect'].colliderect(pygame.Rect(enemy['x'], enemy['y'], enemy['width'], enemy['height'])):
                        enemy_hit_sound.play()
                        player_bullets.remove(bullet)
                        generate_particles(enemy['x'] + enemy['width'] // 2, enemy['y'] + enemy['height'] // 2, enemy['enemy_type'])
                        enemy['health'] -= 1
                        if enemy['health'] <= 0:
                            enemies.remove(enemy)
                            score += 1000 if enemy['is_boss'] else 500
                        break

    # Bubble projectiles handling
    for bubble in bubble_projectiles[:]:
        bubble['rect'].y += bubble['speed']
        if bubble['rect'].y <= 0:
            center_x = bubble['rect'].x + bubble['rect'].width / 2
            center_y = bubble['rect'].y + bubble['rect'].height / 2
            generate_bubble_particles(center_x, center_y)
            bubble_projectiles.remove(bubble)

    # Collision detection for enemy bullets with the player
    player_rect = pygame.Rect(spaceship_x, spaceship_y, SPACESHIP_WIDTH, SPACESHIP_HEIGHT)
    for bullet in enemy_bullets[:]:
        if player_rect.colliderect(bullet['rect']):
            player_hit_sound.play()
            enemy_bullets.remove(bullet)
            display_end_game_message("Game Over! Your Score: " + str(score))
            pygame.time.wait(2000)
            running = False
            break

    # Check if all enemies are defeated
    check_all_enemies_defeated()

    # Drawing game objects and particles
    update_display()

    pygame.time.delay(10)

pygame.quit()
