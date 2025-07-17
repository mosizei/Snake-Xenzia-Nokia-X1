import torch
import torch.nn as nn
import torch.nn.functional as F

class a2c_net(nn.Module):
    def __init__(self, input_size, num_actions):
        super(a2c_net, self).__init__()
        self.fc1 = nn.Linear(input_size, 256)
        self.fc2 = nn.Linear(256, 256)
        self.actor = nn.Linear(256, num_actions)
        self.critic = nn.Linear(256, 1)

    def forward(self, x):
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        policy = self.actor(x)
        value = self.critic(x)
        return F.softmax(policy, dim=-1), value
