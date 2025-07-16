import pygame
from snake_game.snake import Snake
from snake_game.food import Food

# Screen dimensions
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 480
BLOCK_SIZE = 10

def draw_text(surface, text, size, x, y):
    font = pygame.font.Font(pygame.font.get_default_font(), size)
    text_surface = font.render(text, True, (255, 255, 255))
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surface.blit(text_surface, text_rect)

def main():
    """Main function to run the game."""
    pygame.init()
    try:
        pygame.mixer.init()
        sound_enabled = True
    except pygame.error:
        sound_enabled = False
        print("Warning: Audio device not found. Running without sound.")

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Snake")

    # Sound effects
    if sound_enabled:
        try:
            eat_sound = pygame.mixer.Sound("snake_game/sounds/eat.wav")
            game_over_sound = pygame.mixer.Sound("snake_game/sounds/game_over.wav")
        except pygame.error:
            eat_sound = None
            game_over_sound = None
            print("Warning: Could not load sound files.")
    else:
        eat_sound = None
        game_over_sound = None


    snake = Snake(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
    food = Food(SCREEN_WIDTH, SCREEN_HEIGHT, BLOCK_SIZE)
    score = 0

    clock = pygame.time.Clock()
    running = True
    game_over = False
    while running:
        if game_over:
            if sound_enabled and game_over_sound:
                game_over_sound.play()
            draw_text(screen, "Game Over", 64, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 4)
            draw_text(screen, f"Score: {score}", 22, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
            draw_text(screen, "Press any key to play again", 18, SCREEN_WIDTH / 2, SCREEN_HEIGHT * 3 / 4)
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    main()

        else:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        snake.change_direction("UP")
                    elif event.key == pygame.K_DOWN:
                        snake.change_direction("DOWN")
                    elif event.key == pygame.K_LEFT:
                        snake.change_direction("LEFT")
                    elif event.key == pygame.K_RIGHT:
                        snake.change_direction("RIGHT")

            snake.move()

            # Wrap around screen
            x, y = snake.get_head_position()
            if x >= SCREEN_WIDTH:
                x = 0
            elif x < 0:
                x = SCREEN_WIDTH - BLOCK_SIZE
            if y >= SCREEN_HEIGHT:
                y = 0
            elif y < 0:
                y = SCREEN_HEIGHT - BLOCK_SIZE
            snake.body[0] = (x, y)

            # Collision with food
            if snake.get_head_position() == food.position:
                if sound_enabled and eat_sound:
                    eat_sound.play()
                snake.grow()
                food.respawn()
                score += 1

            # Collision with self
            if snake.collides_with_self():
                game_over = True

            screen.fill((0, 0, 0))  # Black background
            snake.draw(screen)
            food.draw(screen)
            draw_text(screen, f"Score: {score}", 18, SCREEN_WIDTH / 2, 10)
            pygame.display.flip()

            clock.tick(15)  # Game speed

    pygame.quit()

if __name__ == '__main__':
    main()
