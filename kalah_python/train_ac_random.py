from kalah_python.utils.ac import ActorCritic
from kalah_python.utils.agents import ACAgent, RandomAgent
from kalah_python.utils.dataclasses import HyperParams
from kalah_python.utils.enums import Action
from kalah_python.utils.env import ACOppKalahEnv
from kalah_python.utils.board import Board
from kalah_python.utils.train import Train


def main():
    h_params = HyperParams()
    board = Board()
    ac_model = ActorCritic(state_size=Board.STATE_SIZE, action_size=len(Action))
    # the same board, and the same model
    ac_agent = ACAgent(ac_model, board=board, verbose=False)
    random_agent = RandomAgent(board=board, verbose=False)
    env = ACOppKalahEnv(board=board, ac_agent=ac_agent,
                        opp_agent=random_agent, ac_is_south=False,
                        h_params=h_params)  # instantiate a game environment.
    train = Train(ac_kalah_env=env, ac_model=ac_model)
    train.start()


if __name__ == '__main__':
    main()
