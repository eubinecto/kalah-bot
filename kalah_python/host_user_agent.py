from typing import Union
from overrides import overrides
from kalah_python.utils.agent import Agent, MoveAction, SwapAction


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
        print(self.state)
        return MoveAction(self.side, hole_idx=0)

    @overrides
    def decide_on_swap(self) -> SwapAction:
        """
        User agent just asks for an input from the user
        """
        # TODO ...
        # you have access to the current status of
        # these states.
        print(self.board)
        print(self.side)
        print(self.state)
        return SwapAction(self.side,
                          opp_hole_idx=0,
                          you_hole_idx=0)

    @overrides
    def decide_on_move_or_swap(self) -> Union[MoveAction, SwapAction]:
        # TODO ...
        # you have access to the current status of
        # these states.
        print(self.board)
        print(self.side)
        print(self.state)


def main():
    user_agent = UserAgent()
    user_agent.start_playing(is_south=True)


if __name__ == '__main__':
    main()
