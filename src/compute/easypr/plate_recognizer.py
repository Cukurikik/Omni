import torch
import torch.nn as nn

class PlateRecognizerNet(nn.Module):
    def __init__(self, num_chars=65):
        super(PlateRecognizerNet, self).__init__()
        self.conv1 = nn.Conv2d(1, 32, kernel_size=3, padding=1)
        self.relu = nn.ReLU()
        self.maxpool = nn.MaxPool2d(2)
        self.fc = nn.Linear(32 * 12 * 12, num_chars) # Assuming 24x24 input

    def forward(self, x):
        x = self.conv1(x)
        x = self.relu(x)
        x = self.maxpool(x)
        x = x.view(x.size(0), -1)
        x = self.fc(x)
        return x
