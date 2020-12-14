from kalah_python.utils.agents import UserAgent, RandomAgent
from kalah_python.utils.board import Board
from kalah_python.utils.env import KalahEnv


def main():
    board = Board()
    agent_s = RandomAgent(board=board)
    agent_n = RandomAgent(board=board)
    kalah_env = KalahEnv(board, agent_s, agent_n)
    kalah_env.play_game()


if __name__ == '__main__':
    main()
