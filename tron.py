import pygame
import sys
import random
import math
import os

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600  # Adjusted board size for better visibility
GRID_SIZE = 20

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
PLAYER1_COLOR = (0, 255, 0)
PLAYER2_COLOR = (255, 0, 0)
POWER_UP_COLOR = (0, 0, 255)
OBSTACLE_COLOR = (128, 128, 128)

# Sounds
pygame.mixer.init()
BASE_PATH = os.path.dirname(__file__)
BACKGROUND_MUSIC = os.path.join(BASE_PATH, "background_music.mp3")
COLLISION_SOUND = os.path.join(BASE_PATH, "collision.wav")
POWER_UP_SOUND = os.path.join(BASE_PATH, "power_up.wav")

try:
    # Load and play background music
    pygame.mixer.music.load(BACKGROUND_MUSIC)
    pygame.mixer.music.play(-1)  # Loop indefinitely
    collision_sound = pygame.mixer.Sound(COLLISION_SOUND)
    power_up_sound = pygame.mixer.Sound(POWER_UP_SOUND)
except pygame.error as e:
    print(f"Sound error: {e}")
    collision_sound = None
    power_up_sound = None

# Initialize screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tron Game")

# Clock for controlling frame rate
clock = pygame.time.Clock()

# Directions
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

class Player:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.direction = RIGHT
        self.trail = [(x, y)]  # Start with the initial position

    def move(self):
        # Add the current position to the trail before moving
        self.trail.append((self.x, self.y))
        # Update the player's position based on direction
        self.x += self.direction[0] * GRID_SIZE
        self.y += self.direction[1] * GRID_SIZE

    def check_collision(self, width, height, trails, obstacles):
        # Check if the player hits the wall
        if self.x < 0 or self.x >= width or self.y < 0 or self.y >= height:
            return True
        # Check if the player collides with any trail or obstacle
        if (self.x, self.y) in trails or (self.x, self.y) in obstacles:
            return True
        return False

def ai_move(player, target_player, all_trails, obstacles):
    """Smarter AI logic to chase the target player while avoiding collisions."""
    directions = [UP, DOWN, LEFT, RIGHT]
    best_direction = None
    min_distance = math.inf

    for d in directions:
        new_x = player.x + d[0] * GRID_SIZE
        new_y = player.y + d[1] * GRID_SIZE
        if (new_x, new_y) not in all_trails and (new_x, new_y) not in obstacles and 0 <= new_x < WIDTH and 0 <= new_y < HEIGHT:
            # Calculate the distance to the target player
            distance = math.sqrt((new_x - target_player.x) ** 2 + (new_y - target_player.y) ** 2)
            if distance < min_distance:
                min_distance = distance
                best_direction = d

    if best_direction:
        player.direction = best_direction

def generate_power_up():
    """Generate a new power-up location."""
    return (random.randint(1, (WIDTH // GRID_SIZE) - 2) * GRID_SIZE,
            random.randint(1, (HEIGHT // GRID_SIZE) - 2) * GRID_SIZE)

def move_obstacles(obstacles):
    """Move the obstacles dynamically in random directions."""
    new_obstacles = []
    directions = [UP, DOWN, LEFT, RIGHT]
    for obs in obstacles:
        direction = random.choice(directions)
        new_x = obs[0] + direction[0] * GRID_SIZE
        new_y = obs[1] + direction[1] * GRID_SIZE
        # Ensure obstacles stay within bounds
        if 0 <= new_x < WIDTH and 0 <= new_y < HEIGHT:
            new_obstacles.append((new_x, new_y))
        else:
            new_obstacles.append(obs)  # Keep the obstacle in place if it goes out of bounds
    return new_obstacles

def main():
    # Initialize players
    player1 = Player(100, 100, PLAYER1_COLOR)
    ai_player = Player(700, 500, PLAYER2_COLOR)  # Adjusted AI starting position

    # Ensure player 2 (AI) is drawn from the start
    ai_player.trail.append((700, 500))

    # Set initial directions to avoid immediate wall collisions
    player1.direction = RIGHT
    ai_player.direction = LEFT

    # Controls for player 1
    controls = {
        pygame.K_w: (player1, UP),
        pygame.K_s: (player1, DOWN),
        pygame.K_a: (player1, LEFT),
        pygame.K_d: (player1, RIGHT),
    }

    # Scores
    player1_score = 0
    ai_score = 0

    # Power-up
    power_up = generate_power_up()

    # Obstacles
    obstacles = [(200, 200), (400, 300), (600, 400)]

    running = True
    collision_detected = False
    obstacle_move_counter = 0

    while running:
        screen.fill(BLACK)

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in controls:
                    player, new_direction = controls[event.key]
                    # Prevent reversing direction
                    if (new_direction[0] != -player.direction[0] and
                        new_direction[1] != -player.direction[1]):
                        player.direction = new_direction

        # Move players
        player1.move()
        ai_move(ai_player, player1, set(player1.trail + ai_player.trail), obstacles)
        ai_player.move()

        # Move obstacles every 20 frames
        obstacle_move_counter += 1
        if obstacle_move_counter >= 20:
            obstacles = move_obstacles(obstacles)
            obstacle_move_counter = 0

        # Combine all trails (current positions included)
        all_trails = set(player1.trail + ai_player.trail)

        # Check for collisions
        if not collision_detected:
            if player1.check_collision(WIDTH, HEIGHT, all_trails, obstacles) or (player1.x, player1.y) == (ai_player.x, ai_player.y):
                print("AI Wins!")
                ai_score += 1
                if collision_sound:
                    collision_sound.play()
                collision_detected = True
            elif ai_player.check_collision(WIDTH, HEIGHT, all_trails, obstacles) or (ai_player.x, ai_player.y) == (player1.x, player1.y):
                print("Player 1 Wins!")
                player1_score += 1
                if collision_sound:
                    collision_sound.play()
                collision_detected = True

        # Stop the game if any collision is detected
        if collision_detected:
            running = False

        # Check for power-up collection
        if (player1.x, player1.y) == power_up:
            print("Player 1 collected the power-up! Speed boost activated!")
            if power_up_sound:
                power_up_sound.play()
            power_up = generate_power_up()  # Generate a new power-up
            clock.tick(15)  # Temporarily increase speed for Player 1
        if (ai_player.x, ai_player.y) == power_up:
            print("AI collected the power-up! Speed boost activated!")
            if power_up_sound:
                power_up_sound.play()
            power_up = generate_power_up()  # Generate a new power-up
            clock.tick(15)  # Temporarily increase speed for AI

        # Draw players' trails
        for x, y in player1.trail:
            pygame.draw.rect(screen, player1.color, (x, y, GRID_SIZE, GRID_SIZE))
        for x, y in ai_player.trail:
            pygame.draw.rect(screen, ai_player.color, (x, y, GRID_SIZE, GRID_SIZE))

        # Draw the power-up
        if power_up:
            pygame.draw.rect(screen, POWER_UP_COLOR, (*power_up, GRID_SIZE, GRID_SIZE))

        # Draw obstacles
        for obs in obstacles:
            pygame.draw.rect(screen, OBSTACLE_COLOR, (*obs, GRID_SIZE, GRID_SIZE))

        # Display scores
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Player 1: {player1_score}  AI: {ai_score}", True, WHITE)
        screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 10))

        # Update display
        pygame.display.flip()
        clock.tick(10)  # Adjust speed for better gameplay

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()