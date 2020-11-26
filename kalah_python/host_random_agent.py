from typing import Dict
from overrides import overrides
from kalah_python.utils.agent import Agent, Action
from kalah_python.utils.server import Server
from config import HOST, PORT
import random


class RandomAgent(Agent):
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
        option, action = random.choice(list(possible_actions.items()))
        print("random action: " + str(action))
        return action


def main():
    server = Server(agent=RandomAgent())
    server.start_hosting(host=HOST, port=PORT)


if __name__ == '__main__':
    main()
