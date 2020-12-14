from typing import Optional, List
from kalah_python.utils.ac import ActorCritic
from kalah_python.utils.agents import ACAgent
from kalah_python.utils.dataclasses import HyperParams, SavedAction
from kalah_python.utils.enums import Action
from kalah_python.utils.env import ACKalahEnv
from kalah_python.utils.board import Board
import numpy as np
import torch
import torch.nn.functional as F
import torch.optim as optim
from config import AC_MODEL_STATE_DICT_PATH, train_logger

# for debugging purposes
torch.autograd.set_detect_anomaly(True)

# global variables.
optimiser: Optional[optim.Adam] = None  # for optimising weights & biases of an ActorCritic model
EPS = np.finfo(np.float32).eps.item()  # the smallest possible value (epsilon)


def discounted_rewards(rewards: List[float], h_params: HyperParams) -> List[torch.Tensor]:
    global EPS
    discounted: List[float] = list()
    R = 0
    for r in reversed(rewards):
        R = r + h_params.DISCOUNT_FACTOR * R
        discounted.insert(0, R)
    else:
        # zero-centered mean
        discounted_np = np.array(discounted)
        discounted_norm_np = (discounted_np - discounted_np.mean()) / (discounted_np.std() + EPS)
        return [
            torch.scalar_tensor(val, dtype=torch.float32)
            for val in discounted_norm_np
        ]


def finish_episode(agent: ACAgent, h_params: HyperParams):
    """
    Training code. Calculates actor and critic loss and performs backprop.
    """
    global optimiser, EPS
    if not optimiser:
        raise ValueError("Optimiser has not been set")
    saved_actions: List[SavedAction] = agent.saved_action_buffer
    policy_losses: List[torch.Tensor] = []  # list to save actor (policy) loss
    value_losses: List[torch.Tensor] = []  # list to save critic (value) loss
    rewards: List[torch.Tensor] = discounted_rewards(agent.reward_buffer, h_params)
    # get the losses
    for saved_action, reward in zip(saved_actions, rewards):
        critique = saved_action.critique
        log_prob = saved_action.logit
        advantage = reward - critique
        policy_losses.append(-log_prob * advantage)  # actor (policy) loss for this action
        value_losses.append(F.smooth_l1_loss(critique.squeeze(), reward))  # critic (value) loss using L1 smooth loss
    # sum up all the values of policy_losses and value_losses
    loss = torch.stack(policy_losses).sum() + torch.stack(value_losses).sum()
    # perform backprop
    optimiser.zero_grad()
    loss.backward()
    # update the weights
    optimiser.step()


def main():
    global optimiser
    h_params = HyperParams()
    board = Board()
    ac_model = ActorCritic(state_size=board.board_size, action_size=len(Action))
    # the same board, and the same model
    agent_s = ACAgent(ac_model, board=board)
    agent_n = ACAgent(ac_model, board=board)
    env = ACKalahEnv(board, agent_s, agent_n, h_params)  # instantiate a game environment.
    # init the optimiser
    optimiser = optim.Adam(ac_model.parameters(), lr=h_params.LEARNING_RATE)
    # what is this for?
    running_reward_n = 10
    running_reward_s = 10
    for episode in range(h_params.NUM_EPISODES):  # train as much as we can
        # for each episode, reset the env
        env.reset()
        # play the game. agent_s starts first.
        env.play_game()
        # update ac_model's parameters for both sides.
        finish_episode(agent_n, h_params)  # train the north agent
        # finish_episode(agent_s, h_params)
        # these are just for logging the progress
        reward_n = sum(agent_n.reward_buffer)
        reward_s = sum(agent_s.reward_buffer)
        running_reward_n = 0.05 * reward_n + (1 - 0.05) * running_reward_n
        running_reward_s = 0.05 * reward_s + (1 - 0.05) * running_reward_s
        # log results
        print('Episode {}'.format(episode))
        train_logger.info('Episode {}'.format(episode))
        train_logger.info('  Player North\tLast reward: {:.2f}\tAverage reward: {:.2f}'.format(reward_n,
                                                                                               running_reward_n))
        train_logger.info('  Player South\tLast reward: {:.2f}\tAverage reward: {:.2f}'.format(reward_s,
                                                                                               running_reward_s))
        train_logger.info("==================")

    else:  # on successful completion of the for loop
        torch.save(ac_model.state_dict(), AC_MODEL_STATE_DICT_PATH)


if __name__ == '__main__':
    main()
