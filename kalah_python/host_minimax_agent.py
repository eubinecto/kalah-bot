from typing import Union
from kalah_python.utils.agent import Agent, MoveAction, SwapAction
from kalah_python.utils.server import Server
from overrides import overrides  # external library for overrides annotation.
from config import HOST, PORT


class MinimaxAgent(Agent):

    def __init__(self):
        super().__init__()
        # add instance variables here
        # if you want

    @overrides
    def decide_on_move(self) -> MoveAction:
        # TODO: ...
        # you have access to the current status of
        # these states.
        print(self.board)
        print(self.state)
        print(self.side)

    @overrides
    def decide_on_move_or_swap(self) -> Union[MoveAction, SwapAction]:
        # TODO: ...
        # you have access to the current status of
        # these states.
        print(self.board)
        print(self.state)
        print(self.side)


def main():
    server = Server(agent=MinimaxAgent())
    server.start_hosting(host=HOST, port=PORT)


if __name__ == '__main__':
    main()
