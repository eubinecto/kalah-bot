from kalah_python.utils.ac import ActorCritic
from kalah_python.utils.agents import ACAgent
from kalah_python.utils.dataclasses import HyperParams
from kalah_python.utils.enums import Action
from kalah_python.utils.env import ACSelfKalahEnv
from kalah_python.utils.board import Board
from kalah_python.utils.train import Train


def main():
    h_params = HyperParams()
    board = Board()
    ac_model = ActorCritic(state_size=Board.STATE_SIZE, action_size=len(Action))
    # the same board, and the same model
    agent_s = ACAgent(ac_model, board=board)
    agent_n = ACAgent(ac_model, board=board)
    env = ACSelfKalahEnv(board, agent_s, agent_n, h_params)  # instantiate a game environment.
    train = Train(ac_kalah_env=env, ac_model=ac_model)
    train.start()


if __name__ == '__main__':
    main()
