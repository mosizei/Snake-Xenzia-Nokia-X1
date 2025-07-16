import torch
import torch.optim as optim
from torch.distributions import Categorical
import numpy as np
from snake_game.model import a2c_net
from snake_game.main import main, get_game_state
import pandas as pd
from collections import deque
import random
import torch.nn.functional as F

# Hyperparameters
learning_rate = 0.001
gamma = 0.99
log_interval = 10
num_episodes = 1000
max_steps_per_episode = 500

class SnakeEnv:
    def __init__(self):
        self.action_map = {0: "UP", 1: "DOWN", 2: "LEFT", 3: "RIGHT"}

    def reset(self):
        self.game_over = False
        self.snake = Snake(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        self.food = Food(SCREEN_WIDTH, SCREEN_HEIGHT, BLOCK_SIZE)
        self.score = 0
        return get_game_state(self.snake, self.food, SCREEN_WIDTH, SCREEN_HEIGHT, BLOCK_SIZE)

    def step(self, action):
        direction = self.action_map[action]
        self.snake.change_direction(direction)
        self.snake.move()

        reward = 0
        if self.snake.get_head_position() == self.food.position:
            self.snake.grow()
            self.food.respawn()
            self.score += 1
            reward = 10

        if self.snake.collides_with_self() or \
           not (0 <= self.snake.get_head_position()[0] < SCREEN_WIDTH) or \
           not (0 <= self.snake.get_head_position()[1] < SCREEN_HEIGHT):
            self.game_over = True
            reward = -10

        next_state = get_game_state(self.snake, self.food, SCREEN_WIDTH, SCREEN_HEIGHT, BLOCK_SIZE)
        return next_state, reward, self.game_over, self.score

def train():
    env = SnakeEnv()
    in_channels = 3
    num_actions = 4

    # Adjust grid_size in the model based on the actual game grid
    grid_width = SCREEN_WIDTH // BLOCK_SIZE
    grid_height = SCREEN_HEIGHT // BLOCK_SIZE

    # We need to pass the correct grid size to the model
    # Let's assume the model is adapted to take grid dimensions
    # Re-defining the model to accept grid dimensions
    class a2c_net_dynamic(a2c_net):
        def __init__(self, in_channels, num_actions, grid_height, grid_width):
            super().__init__(in_channels, num_actions)
            # Override the flattened size calculation
            self.fc_input_size = 32 * grid_height * grid_width
            self.fc1 = nn.Linear(self.fc_input_size, 256)
            # Re-initialize final layers to use the new fc1
            self.actor = nn.Linear(256, num_actions)
            self.critic = nn.Linear(256, 1)

    model = a2c_net_dynamic(in_channels, num_actions, grid_height, grid_width)
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)

    episode_rewards = []

    for i_episode in range(num_episodes):
        state = env.reset()
        state = torch.from_numpy(state).unsqueeze(0)

        rewards = []
        log_probs = []
        values = []

        for t in range(max_steps_per_episode):
            policy, value = model(state)
            m = Categorical(policy)
            action = m.sample()

            next_state, reward, done, _ = env.step(action.item())

            rewards.append(reward)
            log_probs.append(m.log_prob(action))
            values.append(value)

            state = torch.from_numpy(next_state).unsqueeze(0)

            if done:
                break

        # Update model
        R = 0
        policy_loss = []
        value_loss = []
        returns = []

        for r in reversed(rewards):
            R = r + gamma * R
            returns.insert(0, R)

        returns = torch.tensor(returns, dtype=torch.float32)
        if len(returns) > 1:
             returns = (returns - returns.mean()) / (returns.std() + 1e-5)

        for log_prob, value, R_t in zip(log_probs, values, returns):
            advantage = R_t - value.item()
            policy_loss.append(-log_prob * advantage)
            value_loss.append(F.smooth_l1_loss(value.squeeze(0), torch.tensor([R_t])))

        optimizer.zero_grad()
        loss = torch.stack(policy_loss).sum() + torch.stack(value_loss).sum()
        loss.backward()
        optimizer.step()

        episode_rewards.append(sum(rewards))

        if i_episode % log_interval == 0:
            print(f'Episode {i_episode}\tLast reward: {episode_rewards[-1]:.2f}\tAverage reward: {np.mean(episode_rewards[-log_interval:]):.2f}')

    df = pd.DataFrame({'episode': range(len(episode_rewards)), 'reward': episode_rewards})
    df.to_csv('training_log.csv', index=False)
    print("Training log saved to training_log.csv")

if __name__ == '__main__':
    # Add screen dimensions to be accessible by the env
    from snake_game.main import SCREEN_WIDTH, SCREEN_HEIGHT, BLOCK_SIZE
    from snake_game.snake import Snake
    from snake_game.food import Food

    # Make them global for the env class to use
    globals().update({
        'SCREEN_WIDTH': SCREEN_WIDTH,
        'SCREEN_HEIGHT': SCREEN_HEIGHT,
        'BLOCK_SIZE': BLOCK_SIZE,
        'Snake': Snake,
        'Food': Food
    })

    train()
