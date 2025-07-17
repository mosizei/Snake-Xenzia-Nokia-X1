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
    head_x, head_y = snake.get_head_position()

    # Distances to walls
    dist_wall_up = head_y
    dist_wall_down = screen_height - head_y
    dist_wall_left = head_x
    dist_wall_right = screen_width - head_x

    # Relative position of food
    food_rel_x = head_x - food.position[0]
    food_rel_y = head_y - food.position[1]

    # Snake's direction (one-hot encoded)
    dir_up = 1 if snake.direction == "UP" else 0
    dir_down = 1 if snake.direction == "DOWN" else 0
    dir_left = 1 if snake.direction == "LEFT" else 0
    dir_right = 1 if snake.direction == "RIGHT" else 0

    # Dangers in 8 directions
    danger_up = 1 if (head_x, head_y - block_size) in snake.body or head_y - block_size < 0 else 0
    danger_down = 1 if (head_x, head_y + block_size) in snake.body or head_y + block_size >= screen_height else 0
    danger_left = 1 if (head_x - block_size, head_y) in snake.body or head_x - block_size < 0 else 0
    danger_right = 1 if (head_x + block_size, head_y) in snake.body or head_x + block_size >= screen_width else 0
    danger_up_left = 1 if (head_x - block_size, head_y - block_size) in snake.body or head_y - block_size < 0 or head_x - block_size < 0 else 0
    danger_up_right = 1 if (head_x + block_size, head_y - block_size) in snake.body or head_y - block_size < 0 or head_x + block_size >= screen_width else 0
    danger_down_left = 1 if (head_x - block_size, head_y + block_size) in snake.body or head_y + block_size >= screen_height or head_x - block_size < 0 else 0
    danger_down_right = 1 if (head_x + block_size, head_y + block_size) in snake.body or head_y + block_size >= screen_height or head_x + block_size >= screen_width else 0

    state = [
        dist_wall_up, dist_wall_down, dist_wall_left, dist_wall_right,
        food_rel_x, food_rel_y,
        dir_up, dir_down, dir_left, dir_right,
        danger_up, danger_down, danger_left, danger_right,
        danger_up_left, danger_up_right, danger_down_left, danger_down_right
    ]

    return np.array(state, dtype=np.float32)

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
