# this is where algorithm for actor critic
from dataclasses import dataclass
from itertools import count
from typing import List

from kalah_python.utils.ac import ActorCritic
from kalah_python.utils.env import KalahEnv
from kalah_python.utils.agents import ACAgent, Action
from kalah_python.utils.board import Board


@dataclass
class SavedAction:
    logit: float  # log probability of this action
    critique: float  # the critique score on the states generated by Critic.
    action: Action


# hyper parameters
EPISODE_STEPS: int = 1000

# CACHES
# shortcut for lowercase -> uppercase: cmd + shift + U.
AGENT_S_SAVED_ACTIONS: List[SavedAction] = list()
AGENT_N_SAVED_ACTIONS: List[SavedAction] = list()
AGENT_S_SAVED_REWARDS: List[float] = list()
AGENT_N_SAVED_REWARDS: List[float] = list()


def main():
    # caches.
    global AGENT_N_SAVED_ACTIONS, \
        AGENT_S_SAVED_ACTIONS, \
        AGENT_N_SAVED_REWARDS, \
        AGENT_S_SAVED_REWARDS

    board = Board()  # the same board is shared by the two agents.
    agent_s = ACAgent(board=board)
    agent_n = ACAgent(board=board)
    ac_model = ActorCritic(state_size=board.board_size, action_size=len(Action))
    env = KalahEnv(agent_s, agent_n, ac_model)  # instantiate a game environment.
    for i_episode in count(1):  # infinite loop.
        # for each episode, reset the env
        env.reset()
        # start the game. agent_s starts first.
        env.start_game()
        while not env.game_is_over():
            # either agent_s or agent_n makes a move.
            for episode in range(EPISODE_STEPS):
                env.make_move()

    # for each episode in 1000 times
    #         # reset env (reset agents, reset board)
    #         #
    #         # while ( game is not over)
    #             communicate board state to current turn's agent
    #         #   agent 1 or 2 (alternate) chooses action
    #         #   action = decide_on_action_train(env.possible_actions()., env.model)
    #         #   env.make_move(action)
    pass


if __name__ == '__main__':
    main()

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
