from typing import Dict, List
from overrides import overrides
from kalah_python.utils.agent import Agent, Action
from kalah_python.utils.server import Server
from config import HOST, PORT


class MiniMaxAgent(Agent):
    def minimax_first_attempt(self, moves: List[Action]) -> Action:
        raise NotImplemented

    @overrides
    def decide_on_action(self, possible_actions: Dict[str, Action]) -> Action:
        """
        :param possible_actions:
        :return:
        """
        print("------decide_on_action----")
        print("It is your turn:")
        print(self.board)
        print("your side:", self.side)
        moves = [*possible_actions.values()]
        action = self.minimax_first_attempt(self, moves)
        print("MiniMax choice: " + str(action))
        return action


def main():
    server = Server(agent=MiniMaxAgent())
    server.start_hosting(host=HOST, port=PORT)


if __name__ == '__main__':
    main()
