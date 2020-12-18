# from kalah_python.utils.ac import ActorCritic
# from kalah_python.utils.agents import ACAgent, MiniMaxAgent
# from kalah_python.utils.dataclasses import HyperParams
# from kalah_python.utils.enums import Action
# from kalah_python.utils.env import ACOppKalahEnv
# from kalah_python.utils.board import Board
# from kalah_python.utils.train import Train
# from kalah_python.config import TRAIN_MINIMAX_LOG, TRAIN_MINIMAX_STATE_DICT, train_minimax_logger
# import logging
#
# # for random
# fh_random = logging.FileHandler(TRAIN_MINIMAX_LOG)
# fh_random.setLevel(logging.DEBUG)
# train_minimax_logger.addHandler(fh_random)
# transition_logger = logging.getLogger("transitions.core")
# transition_logger.setLevel(logging.WARN)
#
# # h_params setup
# h_params_config = {
#     'num_episodes': 3000,
#     'win_bonus': 10,
#     'discount_factor': 0.99,  # (gamma)
#     'learning_rate': 3e-2,  # for optimizer
#     'neurons': 512
# }
#
# h_params = HyperParams(**h_params_config)
#
#
# def main():
#     global h_params
#     board = Board()
#     ac_model = ActorCritic(state_size=Board.STATE_SIZE, action_size=len(Action), neurons=h_params.neurons)
#     # the same board, and the same model
#     ac_agent = ACAgent(ac_model, board=board, verbose=False)
#     minimax_agent = MiniMaxAgent(board=board, verbose=False)
#     env = ACOppKalahEnv(board=board, ac_agent=ac_agent,
#                         opp_agent=minimax_agent, ac_is_south=False,
#                         h_params=h_params)  # instantiate a game environment.
#     train = Train(ac_kalah_env=env, ac_model=ac_model,
#                   logger=train_minimax_logger, save_path=TRAIN_MINIMAX_STATE_DICT)
#     train.start()
#     train.save_model()
#
#
# if __name__ == '__main__':
#     main()
