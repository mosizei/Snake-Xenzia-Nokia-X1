import torch
import torch.nn as nn
import torch.nn.functional as F

class a2c_net(nn.Module):
    def __init__(self, in_channels, num_actions):
        super(a2c_net, self).__init__()
        self.conv1 = nn.Conv2d(in_channels, 16, kernel_size=3, stride=1, padding=1)
        self.conv2 = nn.Conv2d(16, 32, kernel_size=3, stride=1, padding=1)

        # Calculate the size of the flattened features after the convolutional layers
        # This depends on the input dimensions. Let's assume an example input size, e.g., 20x20
        # The formula for output size is (W - K + 2P) / S + 1
        # With kernel_size=3, stride=1, padding=1, the size remains the same.
        # So, for a 20x20 input, the output of conv2 is 32x20x20.
        # We need to adjust this based on the actual grid size used in the game.
        # Let's say grid_size is the dimension of the game grid (e.g., 20)
        grid_size = 20 # Example, adjust as per game's grid
        self.fc_input_size = 32 * grid_size * grid_size

        self.fc1 = nn.Linear(self.fc_input_size, 256)

        # Output layers
        self.actor = nn.Linear(256, num_actions) # Policy
        self.critic = nn.Linear(256, 1) # Value

    def forward(self, x):
        x = F.relu(self.conv1(x))
        x = F.relu(self.conv2(x))
        x = x.view(x.size(0), -1) # Flatten the tensor
        x = F.relu(self.fc1(x))

        policy = self.actor(x)
        value = self.critic(x)

        return F.softmax(policy, dim=-1), value
