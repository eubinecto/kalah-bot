from typing import Tuple
import torch.nn as nn
import torch.nn.functional as F
import torch


class Actor(nn.Module):

    def __init__(self, in_size: int, action_size: int):
        super(Actor, self).__init__()
        self.in_size = in_size
        self.action_size = action_size
        # feature extraction -> action logits
        self.linear_layers = nn.Sequential(
            nn.Linear(in_size, 128),
            nn.ReLU(inplace=False),
            nn.Linear(128, action_size)
        )

    def forward(self, x: torch.Tensor, action_mask: torch.Tensor) -> torch.Tensor:
        """
        :param x: input to Actor. Could be states, or features of the states.
        :param action_mask:
        :return: probability distribution over the possible actions.
        """
        if x.isnan().any():
            raise ValueError("some of the values of x is nan:" + str(x))
        if x.shape[0] != self.in_size:  # error handling.
            raise ValueError("shape mismatch:{}!={}".format(x.shape[0], self.in_size))
        # TODO: this might affect the performance
        y_1 = self.linear_layers(x)
        # element-wise multiplication of two tensors
        # https://discuss.pytorch.org/t/how-to-do-elementwise-multiplication-of-two-vectors/13182/2
        y_2 = y_1 * action_mask
        neg_inf = torch.scalar_tensor(float('-inf'))
        # replacing particular element of a tensor
        # https://discuss.pytorch.org/t/recommended-way-to-replace-a-partcular-value-in-a-tensor/25424
        y_1_masked = torch.where(y_2 == 0, neg_inf, y_2)
        y_3 = F.softmax(y_1_masked, dim=0)  # logits -> probability distributions.
        return y_3.clone()  # probability distribution over the possible actions.


class Critic(nn.Module):

    def __init__(self, in_size: int):
        super(Critic, self).__init__()
        self.in_size = in_size
        # feature extraction -> critique value
        self.linear_layers = nn.Sequential(
            nn.Linear(in_size, 128),
            nn.ReLU(inplace=False),  # relu activation
            nn.Linear(128, 1)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        if x.isnan().any():
            raise ValueError("some of the values of x is nan:" + str(x))
        if x.shape[0] != self.in_size:  # error handling.
            raise ValueError("shape mismatch:{}!={}".format(x.shape[0], self.in_size))
        y_1 = self.linear_layers(x)
        return y_1.clone()  # critique of the states


class ActorCritic(nn.Module):
    """
    implements both actor and critic in one model
    """
    def __init__(self, state_size: int, action_size: int):
        super(ActorCritic, self).__init__()
        self.linear_layers = nn.Sequential(
            nn.Linear(state_size, 128),
            nn.ReLU(inplace=False)
        )
        self.actor = Actor(in_size=128, action_size=action_size)
        self.critic = Critic(in_size=128)

    def forward(self, x: torch.Tensor, action_mask: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        returns probability distribution over possible actions, and a critique value on the states.
        """
        if x.isnan().any():
            raise ValueError("some of the values of x is nan:" + str(x))
        y_1 = self.linear_layers.forward(x)
        y_2 = self.actor.forward(y_1, action_mask)  # features -> action probs
        y_3 = self.critic.forward(y_1)  # features -> state evaluation (single value)
        return y_2.clone(), y_3.clone()  # action_probs, critique.
