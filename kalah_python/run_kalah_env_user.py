from kalah_python.utils.agents import UserAgent
from kalah_python.utils.board import Board
from kalah_python.utils.env import KalahEnv


def main():
    board = Board()
    agent_s = UserAgent(board=board)
    agent_n = UserAgent(board=board)
    kalah_env = KalahEnv(board, agent_s, agent_n)
    kalah_env.play_game()


if __name__ == '__main__':
    main()
