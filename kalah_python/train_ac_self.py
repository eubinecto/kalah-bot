from kalah_python.utils.ac import ActorCritic
from kalah_python.utils.agents import ACAgent
from kalah_python.utils.dataclasses import HyperParams
from kalah_python.utils.enums import Action
from kalah_python.utils.env import ACSelfKalahEnv
from kalah_python.utils.board import Board
from kalah_python.utils.train import Train
from kalah_python.config import train_self_logger, TRAIN_SELF_STATE_DICT, TRAIN_SELF_LOG
import logging

# set handlers
# for self
fh_self = logging.FileHandler(TRAIN_SELF_LOG)
fh_self.setLevel(logging.DEBUG)
train_self_logger.addHandler(fh_self)

# h_params setup
h_params_config = {
    # 2000 will be enough. self-play without policy search is bound to overfit to itself. (local optima)
    'num_episodes': 2000,
    'win_bonus': 10,
    'discount_factor': 0.90,  # (gamma)
    'learning_rate': 3e-2,  # for optimizer
}

h_params = HyperParams(**h_params_config)


def main():
    global h_params
    board = Board()
    ac_model = ActorCritic(state_size=Board.STATE_SIZE, action_size=len(Action))
    # the same board, and the same model
    agent_s = ACAgent(ac_model, board=board)
    agent_n = ACAgent(ac_model, board=board)
    env = ACSelfKalahEnv(board, agent_s, agent_n, h_params)  # instantiate a game environment.
    train = Train(ac_kalah_env=env, ac_model=ac_model,
                  logger=train_self_logger, save_path=TRAIN_SELF_STATE_DICT)
    # start training and save the model.
    train.start()
    train.save_model()


if __name__ == '__main__':
    main()
