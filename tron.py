import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
GRID_SIZE = 20

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
PLAYER1_COLOR = (0, 255, 0)
PLAYER2_COLOR = (255, 0, 0)
POWER_UP_COLOR = (0, 0, 255)
OBSTACLE_COLOR = (128, 128, 128)

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

def main():
    # Initialize players
    player1 = Player(100, 100, PLAYER1_COLOR)
    player2 = Player(600, 300, PLAYER2_COLOR)  # Adjusted position to prevent immediate collision

    # Set initial directions to avoid immediate wall collisions
    player1.direction = RIGHT
    player2.direction = LEFT

    # Controls for players
    controls = {
        pygame.K_w: (player1, UP),
        pygame.K_s: (player1, DOWN),
        pygame.K_a: (player1, LEFT),
        pygame.K_d: (player1, RIGHT),
        pygame.K_UP: (player2, UP),
        pygame.K_DOWN: (player2, DOWN),
        pygame.K_LEFT: (player2, LEFT),
        pygame.K_RIGHT: (player2, RIGHT),
    }

    # Scores
    player1_score = 0
    player2_score = 0

    # Power-up
    power_up = (random.randint(1, (WIDTH // GRID_SIZE) - 2) * GRID_SIZE,
                random.randint(1, (HEIGHT // GRID_SIZE) - 2) * GRID_SIZE)

    # Obstacles
    obstacles = [(200, 200), (400, 400), (600, 200)]

    running = True
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
        player2.move()

        # Combine all trails (current positions included)
        all_trails = set(player1.trail + player2.trail)

        # Check for collisions
        if player1.check_collision(WIDTH, HEIGHT, all_trails, obstacles):
            print("Player 2 Wins!")
            player2_score += 1
            running = False
        if player2.check_collision(WIDTH, HEIGHT, all_trails, obstacles):
            print("Player 1 Wins!")
            player1_score += 1
            running = False

        # Check for power-up collection
        if (player1.x, player1.y) == power_up:
            print("Player 1 collected the power-up!")
            power_up = None  # Remove power-up
        if (player2.x, player2.y) == power_up:
            print("Player 2 collected the power-up!")
            power_up = None  # Remove power-up

        # Draw players' trails
        for x, y in player1.trail:
            pygame.draw.rect(screen, player1.color, (x, y, GRID_SIZE, GRID_SIZE))
        for x, y in player2.trail:
            pygame.draw.rect(screen, player2.color, (x, y, GRID_SIZE, GRID_SIZE))

        # Draw the power-up
        if power_up:
            pygame.draw.rect(screen, POWER_UP_COLOR, (*power_up, GRID_SIZE, GRID_SIZE))

        # Draw obstacles
        for obs in obstacles:
            pygame.draw.rect(screen, OBSTACLE_COLOR, (*obs, GRID_SIZE, GRID_SIZE))

        # Display scores
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Player 1: {player1_score}  Player 2: {player2_score}", True, WHITE)
        screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 10))

        # Update display
        pygame.display.flip()
        clock.tick(10)  # Adjust speed for better gameplay

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
