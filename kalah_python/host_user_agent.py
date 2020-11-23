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
        print(self.state)
        print(self.side)
        hole_idx = int(input("Enter hole_idx:"))
        return MoveAction(side=self.side, hole_idx=hole_idx)

    @overrides
    def decide_on_move_or_swap(self) -> Union[MoveAction, SwapAction]:
        # TODO ...
        # you have access to the current status of
        # these states.
        print(self.board)
        print(self.state)
        print(self.side)
        m_or_s = input("[m]ove or [s]wap?:")
        if m_or_s == "m":
            return self.decide_on_move()
        elif m_or_s == 's':
            return SwapAction()


def main():
    server = Server(agent=UserAgent())
    server.start_hosting(host=HOST, port=PORT)


if __name__ == '__main__':
    main()
