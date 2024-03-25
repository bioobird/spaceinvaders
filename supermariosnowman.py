import pygame
import random

# Initialize Pygame
pygame.init()

# Set up the game window
WINDOW_WIDTH, WINDOW_HEIGHT = 800, 600
window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Snowman Mario")

# Define colors
BLUE = (135, 206, 235)  # Sky blue color
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
ORANGE = (255, 165, 0)
GREEN = (0, 255, 0)
BROWN = (165, 42, 42)  # Enemy color

# Set up the player character
player_x = 50
player_y = WINDOW_HEIGHT - 90
player_radius = 20  # Radius of the largest circle (body)
player_radius_decrement = 5  # Decrement for the next smaller circle
player_speed_x = 0
player_speed_y = 0
gravity = 0.5

# Set up placeholder green dots
green_dots = []
for _ in range(100):
    x = random.randint(0, WINDOW_WIDTH * 2)
    y = random.randint(0, WINDOW_HEIGHT)
    green_dots.append((x, y))

# Set up enemies (Goombas)
enemies = []
for _ in range(10):  # Generate 10 enemies
    x = random.randint(WINDOW_WIDTH, WINDOW_WIDTH * 2)
    y = WINDOW_HEIGHT - 20  # Enemy height
    direction = random.choice([-1, 1])  # Random direction
    enemies.append({"x": x, "y": y, "direction": direction})

def scroll(player_x, player_y):
    # Define the scroll boundaries
    scroll_threshold_left = 200
    scroll_threshold_right = WINDOW_WIDTH - 200

    # Calculate the horizontal scroll offset
    if player_x < scroll_threshold_left:
        scroll_offset_x = player_x - scroll_threshold_left
    elif player_x > scroll_threshold_right:
        scroll_offset_x = player_x - scroll_threshold_right
    else:
        scroll_offset_x = 0

    # Return the scroll offsets
    return scroll_offset_x, 0  # Vertical offset is 0 for now

def update_display(player_x, player_y, scroll_offset_x, scroll_offset_y, score):
    # Clear the window
    window.fill(BLUE)

    # Draw the score
    font = pygame.font.Font(None, 36)  # Create a font object
    score_text = font.render(f"Score: {score}", True, WHITE)  # Render the score text
    window.blit(score_text, (10, 10))  # Display the score text

    # Draw the player character (snowman)
    pygame.draw.circle(window, WHITE, (player_x - scroll_offset_x, player_y - scroll_offset_y), player_radius)  # Body
    pygame.draw.circle(window, WHITE, (player_x - scroll_offset_x, player_y - scroll_offset_y - player_radius - player_radius_decrement), player_radius - player_radius_decrement)  # Head
    pygame.draw.circle(window, WHITE, (player_x - scroll_offset_x, player_y - scroll_offset_y - (player_radius * 2) - (player_radius_decrement * 2)), player_radius - (player_radius_decrement * 2))  # Top part

    # Draw the eyes, nose, and smile
    pygame.draw.circle(window, BLACK, (player_x - scroll_offset_x - 5, player_y - scroll_offset_y - player_radius - player_radius_decrement - 5), 2)  # Left eye
    pygame.draw.circle(window, BLACK, (player_x - scroll_offset_x + 5, player_y - scroll_offset_y - player_radius - player_radius_decrement - 5), 2)  # Right eye
    pygame.draw.circle(window, ORANGE, (player_x - scroll_offset_x, player_y - scroll_offset_y - player_radius - player_radius_decrement), 3)  # Nose
    pygame.draw.circle(window, BLACK, (player_x - scroll_offset_x - 5, player_y - scroll_offset_y - player_radius - player_radius_decrement + 5), 2)  # Left part of smile
    pygame.draw.circle(window, BLACK, (player_x - scroll_offset_x, player_y - scroll_offset_y - player_radius - player_radius_decrement + 5), 2)  # Middle part of smile
    pygame.draw.circle(window, BLACK, (player_x - scroll_offset_x + 5, player_y - scroll_offset_y - player_radius - player_radius_decrement + 5), 2)  # Right part of smile

    # Draw the placeholder green dots
    for dot_x, dot_y in green_dots:
        pygame.draw.circle(window, GREEN, (dot_x - scroll_offset_x, dot_y - scroll_offset_y), 5)

    # Draw the enemies (Goombas)
    for enemy in enemies:
        enemy_x = enemy["x"] - scroll_offset_x
        enemy_y = enemy["y"]
        pygame.draw.circle(window, BROWN, (enemy_x, enemy_y), 10)  # Enemy body

        # Draw enemy eyes
        pygame.draw.circle(window, WHITE, (enemy_x - 3, enemy_y - 6), 2)  # Left eye
        pygame.draw.circle(window, BLACK, (enemy_x - 3, enemy_y - 6), 1)  # Left eye pupil
        pygame.draw.circle(window, WHITE, (enemy_x + 3, enemy_y - 6), 2)  # Right eye
        pygame.draw.circle(window, BLACK, (enemy_x + 3, enemy_y - 6), 1)  # Right eye pupil

        # Draw enemy fangs
        pygame.draw.polygon(window, WHITE, [(enemy_x - 4, enemy_y + 4), (enemy_x - 2, enemy_y + 2), (enemy_x, enemy_y + 4)])  # Left fang
        pygame.draw.polygon(window, WHITE, [(enemy_x + 4, enemy_y + 4), (enemy_x + 2, enemy_y + 2), (enemy_x, enemy_y + 4)])  # Right fang

        # Update enemy positions
        enemy["x"] += enemy["direction"] * 2  # Move enemies horizontally
        if enemy["x"] < 0 or enemy["x"] > WINDOW_WIDTH * 2:
            enemy["direction"] *= -1  # Reverse direction if enemy hits the screen edge

    # Update the display
    pygame.display.update()

# Game loop
score = 0  # Initialize the score
running = True
while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Handle key presses
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        player_speed_x = -5
    elif keys[pygame.K_RIGHT]:
        player_speed_x = 5
    else:
        player_speed_x = 0

    if keys[pygame.K_SPACE]:
        if player_y == WINDOW_HEIGHT - player_radius:  # Check if the player is on the ground
            player_speed_y = -10

    # Update game state
    player_speed_y += gravity
    player_x += player_speed_x
    player_y += player_speed_y

    # Check if the player is on the ground
    if player_y >= WINDOW_HEIGHT - player_radius:
        player_y = WINDOW_HEIGHT - player_radius
        player_speed_y = 0

    # Check for collisions between player and enemies
    player_rect = pygame.Rect(player_x - player_radius, player_y - player_radius, player_radius * 2, player_radius * 2)
    for enemy in enemies[:]:  # Iterate over a copy of the list to avoid modifying it during iteration
        enemy_rect = pygame.Rect(enemy["x"] - 10, enemy["y"] - 10, 20, 20)
        if player_rect.colliderect(enemy_rect):
            if player_y + player_radius < enemy["y"]:  # Player on top of enemy
                enemies.remove(enemy)  # Remove the enemy
                score += 100  # Increase the score
            else:
                running = False  # End the game if player touches enemy from the side or below
                break

    # Calculate the scroll offset
    scroll_offset_x, scroll_offset_y = scroll(player_x, player_y)

    # Update the display
    update_display(player_x, player_y, scroll_offset_x, scroll_offset_y, score)

# Quit Pygame
pygame.quit()
