from typing import Tuple, Dict
from overrides import overrides
from kalah_python.utils.agent import Agent, Action, SwapAction, MoveAction
from kalah_python.utils.server import Server
from config import HOST, PORT


class UserAgent(Agent):

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
        for key, action in possible_actions.items():
            print("option[{}]:{}".format(key, action))
        option_key = None
        while not possible_actions.get(option_key, None):
            option_key = input("Choose an option:")
        return possible_actions[option_key]


def main():
    server = Server(agent=UserAgent())
    server.start_hosting(host=HOST, port=PORT)


if __name__ == '__main__':
    main()
