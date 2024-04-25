import torch
from torch import nn

class ResidualBlock(nn.Module):
    def __init__(self, in_channels, out_channels, stride=1):
        super(ResidualBlock, self).__init__()
        self.conv1 = nn.Conv2d(in_channels, out_channels, kernel_size=3, stride=stride, padding=1, bias=False)
        self.bn1 = nn.BatchNorm2d(out_channels)
        self.relu = nn.ReLU()
        self.conv2 = nn.Conv2d(out_channels, out_channels, kernel_size=3, stride=1, padding=1, bias=False)
        self.bn2 = nn.BatchNorm2d(out_channels)

        self.shortcut = nn.Sequential()
        if stride != 1 or in_channels != out_channels:
            self.shortcut = nn.Sequential(
                nn.Conv2d(in_channels, out_channels, kernel_size=1, stride=stride, bias=False),
                nn.BatchNorm2d(out_channels)
            )

    def forward(self, x):
        out = self.relu(self.bn1(self.conv1(x)))
        out = self.bn2(self.conv2(out))
        out += self.shortcut(x)
        out = self.relu(out)
        return out
    
class ResNet(nn.Module):
    def __init__(self, block, num_blocks=20, num_classes=15):
        super(ResNet, self).__init__()
        self.in_channels = 256
        self.value_num = 256
        self.policy_num = 2
        self.classes = num_classes**2

        #initial block
        self.conv1 = nn.Conv2d(1, self.in_channels, kernel_size=3, stride=1, padding=1, bias=False)
        self.bn1 = nn.BatchNorm2d(self.in_channels)
        self.relu = nn.ReLU()

        #RNN Blocks
        self.layers = []
        for _ in range(num_blocks):
            self.layers.append(block(self.in_channels, self.in_channels))
        self.layers = nn.Sequential(*self.layers)

        # Policy Block
        self.policy_conv = nn.Conv2d(self.in_channels, self.policy_num, kernel_size=1, stride=1, padding=1, bias = False)
        self.policy_bn = nn.BatchNorm2d(self.policy_num)
        self.policy_relu = nn.ReLU()
        self.policy_linear = nn.Linear((self.policy_num+num_classes)**2*self.policy_num, self.classes)  # 수정된 부분

        # Value Block
        self.value_conv = nn.Conv2d(self.in_channels, 1, kernel_size=1, stride=1, padding = 1, bias=False)
        self.value_bn1 = nn.BatchNorm2d(1)
        self.value_linear = nn.Linear((self.policy_num+num_classes)**2, self.value_num)  # 수정된 부분
        self.value_relu = nn.ReLU()
        self.value_output = nn.Tanh()


    def forward(self, x):
        # Initial block
        out = self.relu(self.bn1(self.conv1(x)))

        # Residual blocks
        out = self.layers(out)

        # Policy head
        policy = self.policy_relu(self.policy_bn(self.policy_conv(out)))
        policy = policy.view(policy.size(0), -1)  # 평탄화
        policy = self.policy_linear(policy)  # 최종 정책 출력

        # Value head
        value = self.value_relu(self.value_bn1(self.value_conv(out)))
        value = value.view(value.size(0), -1)  # 평탄화
        value = self.value_linear(value)
        value = self.value_relu(value)
        value = self.value_output(value)  # 최종 값 출력

        return policy, value

    