from typing import Optional
from kalah_python.utils.ac import ActorCritic
from kalah_python.utils.env import KalahEnv
from kalah_python.utils.agents import ACAgent, Action, SavedAction
from kalah_python.utils.board import Board

import numpy as np
import torch
import torch.nn.functional as F
import torch.optim as optim
from config import AC_MODEL_PKL_PATH, HyperParams


# global variables.
OPTIMISER: Optional[optim.Adam] = None  # for optimising weights & biases of an ActorCritic model
EPS = np.finfo(np.float32).eps.item()  # the smallest possible value (epsilon)


def finish_episode(agent: ACAgent, h_param: HyperParams):
    """
    Training code. Calculates actor and critic loss and performs backprop.
    """

    global OPTIMISER, EPS
    R = 0
    saved_actions = agent.saved_action_buffer
    policy_losses = []  # list to save actor (policy) loss
    value_losses = []  # list to save critic (value) loss
    returns = []  # list to save the true values
    rewards = agent.reward_buffer
    # calculate the true value using rewards returned from the environment
    for r in reversed(rewards):
        # calculate the discounted value
        R = r + h_param.DISCOUNT_FACTOR * R
        returns.insert(0, R)

    returns = torch.tensor(returns)
    returns = (returns - returns.mean()) / (returns.std() + EPS)

    for saved_action, R in zip(saved_actions, returns):
        saved_action: SavedAction
        value = saved_action.critique
        log_prob = saved_action.logit
        advantage = R - value

        # calculate actor (policy) loss
        policy_losses.append(-log_prob * advantage)

        # calculate critic (value) loss using L1 smooth loss
        value_losses.append(F.smooth_l1_loss(torch.tensor([value]), torch.tensor([R])))

    if not OPTIMISER:
        raise ValueError("Optimiser has not been set")
    # reset gradients
    OPTIMISER.zero_grad()

    # sum up all the values of policy_losses and value_losses
    loss = torch.stack(policy_losses).sum() + torch.stack(value_losses).sum()

    # perform backprop
    loss.backward()
    OPTIMISER.step()

    # reset rewards and action buffer
    agent.clear_buffers()


def main():
    global OPTIMISER
    h_params = HyperParams()
    board = Board()
    ac_model = ActorCritic(state_size=board.board_size, action_size=len(Action))

    OPTIMISER = optim.Adam(ac_model.parameters(), lr=h_params.LEARNING_RATE)

    # the same board, and the same
    agent_s = ACAgent(ac_model, board=board)
    agent_n = ACAgent(ac_model, board=board)
    env = KalahEnv(board, agent_s, agent_n, ac_model, h_params)  # instantiate a game environment.

    running_reward_n = 10
    running_reward_s = 10

    for episode in range(h_params.NUM_EPISODES):  # train as much as we can
        # for each episode, reset the env
        env.reset()
        # play the game. agent_s starts first.
        env.play_game()

        reward_n = sum(agent_n.reward_buffer)
        reward_s = sum(agent_s.reward_buffer)

        finish_episode(agent_s, h_params)
        finish_episode(agent_n, h_params)

        running_reward_n = 0.05 * reward_n + (1 - 0.05) * running_reward_n
        running_reward_s = 0.05 * reward_s + (1 - 0.05) * running_reward_s

        # log results
        print('Episode {}'.format(episode))
        print('  Player North\tLast reward: {:.2f}\tAverage reward: {:.2f}'.format(reward_n, running_reward_n))
        print('  Player South\tLast reward: {:.2f}\tAverage reward: {:.2f}'.format(reward_n, running_reward_n))
    else:  # on successful completion of the for loop
        #
        # model.rewards.append(reward)
        # episode_reward += reward
        # TODO: backprop | reward | save the model | account for the swap action
        #  000 times
        #         # reset env (reset agents, reset board)
        #         #
        #         # while ( game i#s not over)
        #             communicate board state to current turn's agent
        #         #   agent 1 or 2 (alternate) chooses action
        #         #   action = decide_on_action_train(env.possible_actions()., env.model)
        #         #   env.make_move(action)
        torch.save(ac_model.state_dict(), AC_MODEL_PKL_PATH)


if __name__ == '__main__':
    main()

# code adapted from : https://github.com/pytorch/examples/blob/master/reinforcement_learning/actor_critic.py
# def main_actor_critic():
#     global ADAM_LR, ARGS, EPISODE_STEPS
#     # pre-built environment for CartPole. (seems like a hello world of RL)
#     env = gym.make('CartPole-v0')
#     # set the same random seeds for env & torch.
#     env.seed(ARGS.seed)
#     torch.manual_seed(ARGS.seed)
#     # instantiate an ActorCritic model, and an Adam optimiser for the model.
#     ac_model = ActorCritic()
#     optimizer = optim.Adam(ac_model.parameters(), lr=ADAM_LR)
#     running_reward = 10
#     # run infinitely many episodes
#     # starting from 1st episode.
#     for i_episode in count(1):
#         # reset environment and episode reward to the initial position.
#         state = env.reset()  # restarting Kalah
#         ep_reward = 0
#         # for each episode, only run 9999 steps so that we don't
#         # infinite loop while learning
#         for t in range(1, EPISODE_STEPS):
#             # select action from policy
#             action = decide_on_action(state, ac_model)
#             # take the action
#             state, reward, done, _ = env.step(action)  # register_action
#             # wait for the server
#             # update state, reward, done variables
#             # how do I get the...
#             if ARGS.render:
#                 env.render()
#             ac_model.rewards.append(reward)
#             ep_reward += reward
#             if done:  # this will be true if the pole passes the "tipping point".
#                 break
#         # update cumulative reward (the conservative reward)
#         running_reward = 0.05 * ep_reward + (1 - 0.05) * running_reward
#         # perform backprop
#         finish_episode(ac_model, optimizer)
#         # log results
#         if i_episode % ARGS.log_interval == 0:
#             print('Episode {}\tLast reward: {:.2f}\tAverage reward: {:.2f}'.format(
#                 i_episode, ep_reward, running_reward))
#
#         # check if we have "solved" the cart pole problem
#         if running_reward > env.spec.reward_threshold:
#             print("Solved! Running reward is now {} and "
#                   "the last episode runs to {} time steps!".format(running_reward, t))
#             break
#
#     # after training is done, save the model.
#     torch.save(ac_model.state_dict(), "./data/cart_pole.model")
