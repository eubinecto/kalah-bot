from typing import Union
from overrides import overrides
from kalah_python.utils.agent import Agent, MoveAction, SwapAction
from kalah_python.utils.server import Server
from config import HOST, PORT


class UserAgent(Agent):

    @overrides
    def decide_on_move(self) -> MoveAction:
        """
        User agent just asks for an input from the user.
        """
        # TODO: ...
        # you have access to the current status of
        # these states.
        print(self.board)
        print(self.side)

    @overrides
    def decide_on_move_or_swap(self) -> Union[MoveAction, SwapAction]:
        # TODO ...
        # you have access to the current status of
        # these states.
        print(self.board)
        print(self.side)


def main():
    server = Server(agent=UserAgent())
    server.start_hosting(host=HOST, port=PORT)


if __name__ == '__main__':
    main()
