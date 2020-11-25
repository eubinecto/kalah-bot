from typing import Tuple, Dict
from overrides import overrides
from kalah_python.utils.agent import Agent, Action, SwapAction, MoveAction
from kalah_python.utils.server import Server
from config import HOST, PORT


class UserAgent(Agent):

    @overrides
    def decide_on_action(self, possible_actions: Tuple[Action]) -> Action:
        print("------decide_on_action----")
        print("It is your turn:")
        print(self.board)
        print("your side:", self.side)
        options: Dict[str, Action] = dict()
        for action in possible_actions:
            if isinstance(action, SwapAction):
                options['s'] = action
            elif isinstance(action, MoveAction):
                options[str(action.hole_idx)] = action
        for key, action in options.items():
            print("option[{}]:{}".format(key, action))
        option_key = None
        while not options.get(option_key, None):
            option_key = input("Choose an option:")
        return options[option_key]


def main():
    server = Server(agent=UserAgent())
    server.start_hosting(host=HOST, port=PORT)


if __name__ == '__main__':
    main()
