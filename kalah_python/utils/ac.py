from typing import Tuple

import torch.nn as nn
import torch.nn.functional as F
from torch import Tensor


class Actor(nn.Module):

    def __init__(self, in_size: int, action_size: int):
        super(Actor, self).__init__()
        self.in_size = in_size
        self.action_size = action_size
        self.linear_1 = nn.Linear(in_size, 128)
        # add more linear layers here, if having one layer is not enough.
        self.linear_2 = nn.Linear(128, action_size)

    def forward(self, x: Tensor, action_mask: Tensor) -> Tensor:
        """
        :param x: input to Actor. Could be states, or features of the states.
        :param action_mask: a tensor representation of the action mask.
        :return: probability distribution over the possible actions.
        """
        if x.shape == (self.in_size,):  # error handling.
            raise ValueError("shape mismatch:{}!={}".format(x.shape, (self.in_size,)))
        y_1 = F.relu(self.linear_1(x))  # feature extraction from the inputs.
        y_2 = self.linear_2(y_1)  # evaluate logits over the action space.
        # element-wise multiplication of two tensors
        # https://discuss.pytorch.org/t/how-to-do-elementwise-multiplication-of-two-vectors/13182/2
        y_2_masked = y_2 * action_mask  # logits for impossible actions are set to zero. (elem-wise multiplication)
        y_3 = F.softmax(y_2_masked)  # logits -> probability distributions.
        return y_3  # probability distribution over the possible actions.


class Critic(nn.Module):

    def __init__(self, in_size: int):
        super(Critic, self).__init__()
        self.in_size = in_size
        self.linear_1 = nn.Linear(in_size, 128)
        self.linear_2 = nn.Linear(128, 1)  # critic outputs 1 value.

    def forward(self, x: Tensor) -> Tensor:
        if x.shape == (self.in_size,):  # error handling.
            raise ValueError("shape mismatch:{}!={}".format(x.shape, (self.in_size,)))
        y_1 = F.relu(self.linear_1(x))
        # TODO: Qus - Critic is not given any info about the behaviour of Actor.
        #      then How is this a "critique" of the actions?
        y_2 = self.linear_2(y_1)
        return y_2  # critique of the states


class ActorCritic(nn.Module):
    """
    implements both actor and critic in one model
    """
    def __init__(self, state_size: int, action_size: int):
        super(ActorCritic, self).__init__()
        self.linear_1 = nn.Linear(state_size, 128)  # feature extraction layer. observation -> features.
        self.actor = Actor(in_size=128, action_size=action_size)
        self.critic = Critic(in_size=128)

    def forward(self, x: Tensor, action_mask: Tensor) -> Tuple[Tensor, Tensor]:
        """
        returns probability distribution over possible actions.
        & state_val. (critic_head_y).
        """
        y_1 = F.relu(self.linear_1(x))  # states -> features
        y_2 = self.actor.forward(x=y_1, action_mask=action_mask)  # features -> action probs
        y_3 = self.critic.forward(x=y_1)  # features -> state evaluation (single value)
        return y_2, y_3  # action_probs, critique.
