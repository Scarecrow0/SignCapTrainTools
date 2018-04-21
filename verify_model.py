# Siamese-Networks

import torch
import torch.nn as nn
import torch.nn.functional as F

# CNN: input len -> output len
# Lout=floor((Lin+2∗padding−dilation∗(kernel_size−1)−1)/stride+1)

LEARNING_RATE = 0.0001
WEIGHT_DECAY = 0.0000002
EPOCH = 500
BATCH_SIZE = 32

class SiameseNetwork(nn.Module):
    def __init__(self, train=True):
        """
        用于生成vector 进行识别结果验证
        :param train: 设置是否为train 模式
        """
        nn.Module.__init__(self)
        if train:
            self.status = 'train'
        else:
            self.status = 'eval'

        self.cnn1 = nn.Sequential(
            nn.Conv1d(  # 14 x 64
                in_channels=14,
                out_channels=42,
                kernel_size=4,
                padding=2,
                stride=1,
            ),  # 28 x 64
            # need Norm ?
            # 通常插入在激活函数和C/FC层之间 对神经网络的中间参数进行normalization
            nn.BatchNorm1d(42),  # 42 x 64
            nn.LeakyReLU(),
            # only one pooling
            nn.MaxPool1d(kernel_size=2),  # 42 x 32

            nn.Conv1d(
                in_channels=42,
                out_channels=60,
                kernel_size=3,
                padding=1,
                stride=1
            ),  # 60 x 32
            nn.BatchNorm1d(60),  # 60 x 32
            nn.LeakyReLU(),
            # nn.MaxPool1d(kernel_size=2),  # 32 x 8
        )

        self.out = nn.Sequential(
            nn.Dropout(),
            nn.Linear(60 * 32, 512),
            nn.LeakyReLU(),
            nn.Dropout(),
            nn.Linear(512, 256),
            nn.LeakyReLU(),
            nn.Dropout(),
            nn.Linear(256, 128)
        )

    def forward_once(self, x):
        x = self.cnn1(x)
        x = x.view(x.size(0), -1)
        out = self.out(x)
        return out

    def forward(self, *xs):
        """
        train 模式输出两个vector 进行对比
        eval 模式输出一个vector
        """
        if self.status == 'train':
            out1 = self.forward_once(xs[0])
            out2 = self.forward_once(xs[1])
            return out1, out2
        else:
            return self.forward_once(xs[0])

class ContrastiveLoss(torch.nn.Module):
    """
    Contrastive loss function.
    Based on: http://yann.lecun.com/exdb/publis/pdf/hadsell-chopra-lecun-06.pdf
    """

    def __init__(self, margin=2.0):
        super(ContrastiveLoss, self).__init__()
        self.margin = margin

    def forward(self, output1, output2, label):
        euclidean_distance = F.pairwise_distance(output1, output2)
        loss_contrastive = torch.mean((1 - label) * torch.pow(euclidean_distance, 2) +
                                      label * torch.pow(torch.clamp(self.margin - euclidean_distance,
                                                                    min=0.0), 2))
        return loss_contrastive
