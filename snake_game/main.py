import pygame
import argparse
from snake_game.snake import Snake
from snake_game.food import Food
import numpy as np

# Screen dimensions
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 480
BLOCK_SIZE = 10

def get_game_state(snake, food, screen_width, screen_height, block_size):
    # The state is a 3-channel image:
    # 1. Food location
    # 2. Snake head location
    # 3. Snake body location

    grid_width = screen_width // block_size
    grid_height = screen_height // block_size

    state = np.zeros((3, grid_height, grid_width), dtype=np.float32)

    # Channel 1: Food location
    food_x, food_y = food.position
    state[0, food_y // block_size, food_x // block_size] = 1

    # Channel 2: Snake head
    head_x, head_y = snake.get_head_position()
    state[1, head_y // block_size, head_x // block_size] = 1

    # Channel 3: Snake body
    for part in snake.body[1:]:
        part_x, part_y = part
        state[2, part_y // block_size, part_x // block_size] = 1

    return state

def main(headless=False, get_state_func=None, action_queue=None):
    pygame.init()
    if not headless:
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('Snake')
        clock = pygame.time.Clock()

    snake = Snake(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
    food = Food(SCREEN_WIDTH, SCREEN_HEIGHT, BLOCK_SIZE)
    score = 0
    running = True
    game_over = False

    while running:
        if not headless:
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
        elif action_queue and not action_queue.empty():
            action = action_queue.get()
            snake.change_direction(action)

        snake.move()

        if snake.get_head_position() == food.position:
            snake.grow()
            food.respawn()
            score += 1

        if snake.collides_with_self() or \
           not (0 <= snake.get_head_position()[0] < SCREEN_WIDTH) or \
           not (0 <= snake.get_head_position()[1] < SCREEN_HEIGHT):
            game_over = True
            running = False

        if not headless:
            screen.fill((0, 0, 0))
            snake.draw(screen)
            food.draw(screen)
            pygame.display.flip()
            clock.tick(15)

        if get_state_func:
            state = get_state_func(snake, food, SCREEN_WIDTH, SCREEN_HEIGHT, BLOCK_SIZE)
            # This is where you would pass the state to the training loop
            # For now, we just compute it

    pygame.quit()
    return score

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run Snake game.')
    parser.add_argument('--headless', action='store_true', help='Run in headless mode for training.')
    args = parser.parse_args()
    main(headless=args.headless)
