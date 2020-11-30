from typing import List
import subprocess
import torch.nn as nn
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.distributions import Categorical

from kalah_python.utils.agent import Agent


class ActorCritic(nn.Module):
    """
    implements both actor and critic in one model
    """
    def __init__(self):
        super(ActorCritic, self).__init__()
        # dense layer to learn patterns of the input.
        # 4: the four numbers that represent the status of the Cart Pole.
        # 128: hyper parameter; how much hidden units do you want? here it is set to 128.
        self.affine1: nn.Linear = nn.Linear(4, 128)
        # actor's layer
        # 128: it is 128 because that's the dim of the affine layer
        # 2: Two neurons, two logits. One for the logits of left move. The other for the
        # logits of right move.
        self.actor_head: nn.Linear = nn.Linear(128, 2)
        # critic's layer
        # just 1 neuron.d
        self.critic_head: nn.Linear = nn.Linear(128, 1)
        # action & reward buffer
        # why do we need to have all of them stored here?
        self.saved_actions = []
        self.rewards = []

    def forward(self, x):
        """
        forward of both actor and critic
        """
        # given the four inputs (the status of the cart pole)
        x = F.relu(self.affine1(x))
        # actor: chooses action to take from state s_t
        # by returning probabilities of each action. (logits are normalised to probs)
        action_prob = F.softmax(self.actor_head(x), dim=-1)
        # critic: evaluates being in the state s_t
        # why is this in plural?
        state_val = self.critic_head(x)
        # return values for both actor and critic as a tuple of 2 values:
        # 1. a list with the probability of each action over the action space
        # 2. the value from state s_t
        return action_prob, state_val


class Env:
    # run two instances of `host_ac_agent` on terminal.
    # write bash scripts.
    # java ManKalah.jar.

    def __init__(self, agent1: Agent, agent2: Agent):
        # instantiate 2 agents
        self.agent1: Agent = agent1
        self.agent2: Agent = agent2
        # reset board
        # agent 1 play first
        # while ( game is not over)
        #   agent 1 or 2 (alternate) chooses action
        #   action =
        #   UpdateBoardState(action)
        pass

    def start_game(self, host_info_1: tuple, host_info_2: tuple):
        """
        starts the game of two agents..\
        :param host_info_1:
        :param host_info_2:
        :return:
        """
        host_1, port_1 = host_info_1
        host_2, port_2 = host_info_2
        bashCommand = "java -jar ./kalah/ManKalah.jar \"nc {} {}\" \"nc {} {}\"".format(
            host_1, port_1,
            host_2, port_2
        )
        process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
        output, error = process.communicate()


    def step(self):
        """
        :return: state, reward and done.
        """
        pass

    # this is only needed if we want to visualise the environment changing as the agent plays out the game
    def render(self):
        pass
