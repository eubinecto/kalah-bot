from typing import Union
from kalah_python.utils.agent import Agent, MoveAction, SwapAction
from overrides import overrides  # external library for overrides annotation.


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
        print(self.state)

    @overrides
    def decide_on_swap(self) -> SwapAction:
        # TODO: ...
        # you have access to the current status of
        # these states.
        print(self.board)
        print(self.side)
        print(self.state)

    @overrides
    def decide_on_move_or_swap(self) -> Union[MoveAction, SwapAction]:
        # TODO: ...
        # you have access to the current status of
        # these states.
        print(self.board)
        print(self.side)
        print(self.state)


def main():
    random_agent = RandomAgent()
    random_agent.start_playing(is_south=True)


if __name__ == '__main__':
    main()
