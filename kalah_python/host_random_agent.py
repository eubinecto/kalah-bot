from typing import Union
from kalah_python.utils.agent import Agent, MoveAction, SwapAction
from overrides import overrides  # external library for overrides annotation.
from config import HOST, PORT
from kalah_python.utils.server import Server


class RandomAgent(Agent):

    def __init__(self):
        super().__init__()

    @overrides
    def decide_on_move(self) -> MoveAction:
        # TODO: ...
        # you have access to the current status of
        # these states.
        print(self.board)
        print(self.side)

    @overrides
    def decide_on_move_or_swap(self) -> Union[MoveAction, SwapAction]:
        # TODO: ...
        # you have access to the current status of
        # these states.
        print(self.board)
        print(self.side)


def main():
    server = Server(agent=RandomAgent())
    server.start_hosting(host=HOST, port=PORT)


if __name__ == '__main__':
    main()
