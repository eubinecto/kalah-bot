from kalah_python.utils.ac import ActorCritic
from kalah_python.utils.agents import ACAgent, RandomAgent
from kalah_python.utils.dataclasses import HyperParams
from kalah_python.utils.enums import Action
from kalah_python.utils.env import ACOppKalahEnv
from kalah_python.utils.board import Board
from kalah_python.utils.train import Train
from kalah_python.config import train_random_logger, TRAIN_RANDOM_STATE_DICT, TRAIN_RANDOM_LOG
import logging

# for random
fh_random = logging.FileHandler(TRAIN_RANDOM_LOG)
fh_random.setLevel(logging.DEBUG)
train_random_logger.addHandler(fh_random)
transition_logger = logging.getLogger("transitions.core")
transition_logger.setLevel(logging.WARN)

# h_params setup
h_params_config = {
    'num_episodes': 20000,
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
    ac_agent = ACAgent(ac_model, board=board, verbose=False)
    random_agent = RandomAgent(board=board, verbose=False)
    env = ACOppKalahEnv(board=board, ac_agent=ac_agent,
                        opp_agent=random_agent, ac_is_south=False,
                        h_params=h_params)  # instantiate a game environment.
    train = Train(ac_kalah_env=env, ac_model=ac_model,
                  logger=train_random_logger, save_path=TRAIN_RANDOM_STATE_DICT)
    train.start()
    train.save_model()


if __name__ == '__main__':
    main()
