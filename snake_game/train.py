import torch
import torch.optim as optim
from torch.distributions import Categorical
import numpy as np
from snake_game.model import a2c_net
from snake_game.main import main
import pandas as pd

# Hyperparameters
learning_rate = 0.001
gamma = 0.99
log_interval = 10
num_episodes = 500

def get_state(game):
    # This function needs to be implemented based on how the game state is represented
    # For now, let's assume it returns a dummy tensor
    # You'll need to replace this with actual game state extraction logic
    return torch.randn(1, 3, 20, 20) # Example state

def train():
    # Define the dimensions of the state and action space
    # Example: 3 channels for state (e.g., snake, food, obstacles), 20x20 grid
    in_channels = 3
    num_actions = 4 # Up, Down, Left, Right

    model = a2c_net(in_channels=in_channels, num_actions=num_actions)
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)

    episode_rewards = []

    for i_episode in range(num_episodes):
        # Reset environment and get initial state
        # This part needs to be adapted to your game's API
        # For example, you might need a `game.reset()` method
        # and a way to get the initial state.

        # Simulating a game loop for demonstration
        # Replace this with actual interaction with your game environment

        rewards = []
        log_probs = []
        values = []

        # Let's simulate a few steps in an episode
        for t in range(100): # Simulating 100 steps
            # Get current state
            state = get_state(None) # `None` because `get_state` is a placeholder

            # Get policy and value from the model
            policy, value = model(state)

            # Sample an action from the policy
            m = Categorical(policy)
            action = m.sample()

            # Simulate taking an action and getting a reward and next state
            # This is where you would call your game's `step` function
            # e.g., next_state, reward, done, _ = game.step(action.item())
            reward = np.random.rand() # Placeholder reward
            done = t == 99 # Placeholder for `done` flag

            rewards.append(reward)
            log_probs.append(m.log_prob(action))
            values.append(value)

            if done:
                break

        # After the episode, calculate returns and update the model
        R = 0
        policy_loss = []
        value_loss = []
        returns = []

        for r in reversed(rewards):
            R = r + gamma * R
            returns.insert(0, R)

        returns = torch.tensor(returns)
        returns = (returns - returns.mean()) / (returns.std() + 1e-5)

        for log_prob, value, R in zip(log_probs, values, returns):
            advantage = R - value.item()
            policy_loss.append(-log_prob * advantage)
            value_loss.append(F.smooth_l1_loss(value, torch.tensor([R])))

        optimizer.zero_grad()
        loss = torch.stack(policy_loss).sum() + torch.stack(value_loss).sum()
        loss.backward()
        optimizer.step()

        episode_rewards.append(sum(rewards))

        if i_episode % log_interval == 0:
            print(f'Episode {i_episode}\tLast reward: {episode_rewards[-1]:.2f}\tAverage reward: {np.mean(episode_rewards[-log_interval:]):.2f}')

    # Save training data for visualization
    df = pd.DataFrame({'episode': range(len(episode_rewards)), 'reward': episode_rewards})
    df.to_csv('training_log.csv', index=False)
    print("Training log saved to training_log.csv")

if __name__ == '__main__':
    train()
