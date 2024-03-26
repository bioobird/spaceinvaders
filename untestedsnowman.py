import pygame
import random

# Initialize Pygame
pygame.init()

# Set up the game window
WINDOW_WIDTH, WINDOW_HEIGHT = 800, 600
window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Snowman Mario")

# Load sound files
kill_goomba_sound = pygame.mixer.Sound("baseball_hit.wav")
goomba_kills_player_sound = pygame.mixer.Sound("pacman_dies_y.wav")

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

def update_display(player_x, player_y, scroll_offset_x, scroll_offset_y, score, start_screen, selected_option):
    # Clear the window
    window.fill(BLUE)

    if start_screen:
        # Drawing the start screen elements
        title_font = pygame.font.Font(None, 72)
        title_text = title_font.render("SUPER MARIO SNOWMAN", True, WHITE)
        title_rect = title_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 4))
        window.blit(title_text, title_rect)

        font = pygame.font.Font(None, 48)
        start_text = font.render("Start Game", True, WHITE)
        quit_text = font.render("Quit Game", True, WHITE)

        start_rect = start_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
        quit_rect = quit_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 3 * 2))
        window.blit(start_text, start_rect)
        window.blit(quit_text, quit_rect)
        
        if selected_option == 1:
            pygame.draw.rect(window, WHITE, quit_rect, 2)  # Highlight the "Quit Game" option
    else:
        # Draw game score
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Score: {score}", True, WHITE)
        window.blit(score_text, (10, 10))

        # Draw player character (snowman)
        pygame.draw.circle(window, WHITE, (player_x - scroll_offset_x, player_y - scroll_offset_y), player_radius)
        pygame.draw.circle(window, WHITE, (player_x - scroll_offset_x, (player_y - scroll_offset_y) - player_radius), player_radius - player_radius_decrement)
        pygame.draw.circle(window, WHITE, (player_x - scroll_offset_x, (player_y - scroll_offset_y) - 2 * player_radius), player_radius - 2 * player_radius_decrement)
        # Face
        pygame.draw.circle(window, BLACK, (player_x - scroll_offset_x - 8, player_y - scroll_offset_y - 2 * player_radius + 20), 2)
        pygame.draw.circle(window, BLACK, (player_x - scroll_offset_x + 8, player_y - scroll_offset_y - 2 * player_radius + 20), 2)
        pygame.draw.circle(window, ORANGE, (player_x - scroll_offset_x, player_y - scroll_offset_y - 2 * player_radius + 15), 3)        
        pygame.draw.circle(window, BLACK, (player_x - scroll_offset_x - 6, player_y - scroll_offset_y - 2 * player_radius + 8), 2)
        pygame.draw.circle(window, BLACK, (player_x - scroll_offset_x + 6, player_y - scroll_offset_y - 2 * player_radius + 8), 2)

        # Draw placeholder green dots
        for dot_x, dot_y in green_dots:
            pygame.draw.circle(window, GREEN, (dot_x - scroll_offset_x, dot_y - scroll_offset_y), 5)

        # Draw the enemies (Goombas)
        for enemy in enemies:
            enemy_x = enemy['x'] - scroll_offset_x
            enemy_y = enemy['y']
            bodyRadius = 30  # Increased size
            capWidth = 72  # Increased size
            capHeight = 30  # Increased size
            capYOffset = -54  # Position adjustment
            whiteRectYOffset = -24  # Position adjustment for the white outline

            # Draw the enemy body
            pygame.draw.circle(window, BROWN, (enemy_x, enemy_y), bodyRadius)

            # Draw the mushroom cap
            pygame.draw.ellipse(window, BROWN, (enemy_x - capWidth // 2, enemy_y + capYOffset, capWidth, capHeight))
            pygame.draw.rect(window, WHITE, (enemy_x - capWidth // 2, enemy_y + whiteRectYOffset, capWidth, 6))
            
            # Draw enemy eyes adjusted for size
            pygame.draw.circle(window, WHITE, (enemy_x - 9, enemy_y - 18), 6)
            pygame.draw.circle(window, BLACK, (enemy_x - 9, enemy_y - 18), 3)
            pygame.draw.circle(window, WHITE, (enemy_x + 9, enemy_y - 18), 6)
            pygame.draw.circle(window, BLACK, (enemy_x + 9, enemy_y - 18), 3)

    # Update the display
    pygame.display.update()
    
# Game loop
score = 0  # Initialize the score
start_screen = True  # Set the start screen flag
selected_option = 0  # Initialize the selected option (0 for "Start Game", 1 for "Quit Game")
while True:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                selected_option = 0  # Select "Start Game"
            elif event.key == pygame.K_DOWN:
                selected_option = 1  # Select "Quit Game"
            elif event.key == pygame.K_SPACE:
                if selected_option == 0:
                    start_screen = False  # Start the game
                else:
                    pygame.quit()
                    quit()

    # Display start screen or continue with the game
    if start_screen:
        update_display(player_x, player_y, 0, 0, score, start_screen, selected_option)
        continue  # Skip the rest of the loop

    # Update player movement based on key presses
    keys = pygame.key.get_pressed()
    player_speed_x = 0
    if keys[pygame.K_LEFT]:
        player_speed_x = -5
    if keys[pygame.K_RIGHT]:
        player_speed_x = 5
    if keys[pygame.K_SPACE] and player_y == WINDOW_HEIGHT - player_radius:
        player_speed_y = -10  # Initial jump velocity
    
    player_speed_y += gravity  # Apply gravity
    player_x += player_speed_x
    player_y += player_speed_y

    # Player ground collision
    if player_y >= WINDOW_HEIGHT - player_radius:
        player_y = WINDOW_HEIGHT - player_radius
        player_speed_y = 0

    # Update Goomba positions and handle screen edge reversal
    for enemy in enemies:
        enemy["x"] += enemy["direction"] * 2  # Move Goomba
        # Check if Goomba has moved out of the initial spawn area and reverse direction if needed
        if enemy["x"] <= WINDOW_WIDTH or enemy["x"] >= WINDOW_WIDTH * 2:
            enemy["direction"] *= -1

    # Handle collisions between player and Goombas
    player_rect = pygame.Rect(player_x - player_radius, player_y - player_radius, player_radius * 2, player_radius * 2)
    for enemy in list(enemies):  # Iterate over a copy of the list
        enemy_rect = pygame.Rect(enemy["x"] - 72 // 2, enemy["y"] - 60 // 2, 72, 60)  # Representing Goomba size
        if player_rect.colliderect(enemy_rect):
            if player_y < enemy["y"]:  # Check if player lands on top
                enemies.remove(enemy)
                score += 100
                kill_goomba_sound.play()
            else:  # Player hits Goomba from the side or bottom
                goomba_kills_player_sound.play()
                score = 0
                start_screen = True
                break  # Stop checking collisions and reset the game

    # Calculate the scroll offset
    scroll_offset_x, scroll_offset_y = scroll(player_x, player_y)
    
    # Render the game frame with updated positions
    update_display(player_x, player_y, scroll_offset_x, scroll_offset_y, score, start_screen, selected_option)

# Add these lines at the end of the game loop
pygame.quit()
quit()
