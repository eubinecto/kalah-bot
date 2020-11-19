from typing import Optional
from kalah_python.board import Board
from enum import Enum, auto


class Agent(object):
    class Turn(Enum):
        YOU = auto()
        OPPONENT = auto()
        END = auto()

    class State(Enum):
        DECIDE_ON_1ST_MOVE = auto()
        WAIT_FOR_MOVE_RESULT = auto()
        WAIT_FOR_1ST_MOVE = auto()
        MAKE_MOVE_OR_SWAP = auto()
        WAIT_FOR_SWAP_DECISION = auto()
        DECIDE_ON_MOVE = auto()
        WAIT_FOR_TURN = auto()
        FINISHED = auto()
        # make sure this state is the last one.
        EXIT = auto()

    # trigger, source, dest

    def __init__(self):
        # an agent maintains an up-to-date board,
        # the current state of the agent,
        # and the current turn.
        self.board: Board = Board()
        self.state: Optional[Agent.State] = None
        self.turn: Optional[Agent.Turn] = None

    def move(self, well_idx: int):
        pass

    def swap(self, opp_well_idx: int, you_well_idx: int):
        pass

    #  1st player state handlers
    def decide_on_first_move(self):
        self.state = Agent.State.DECIDE_ON_1ST_MOVE
        # TODO ...
        self.wait_for_move_result()

    def wait_for_move_result(self):
        self.state = Agent.State.WAIT_FOR_MOVE_RESULT
        # TODO ...
        self.wait_for_swap_decision()

    def wait_for_swap_decision(self):
        self.state = Agent.State.WAIT_FOR_SWAP_DECISION
        # TODO ...
        self.decide_on_move()

    # 2nd player state handlers
    def wait_for_1st_move(self):
        self.state = Agent.State.WAIT_FOR_1ST_MOVE
        # TODO ...
        self.make_move_or_swap()

    def make_move_or_swap(self):
        self.state = Agent.State.MAKE_MOVE_OR_SWAP
        # TODO ...
        self.wait_for_turn()

    # common state handlers
    def decide_on_move(self):
        self.state = Agent.State.DECIDE_ON_MOVE
        # TODO ...
        self.wait_for_turn()

    def wait_for_turn(self):
        self.state = Agent.State.WAIT_FOR_TURN
        while self.turn == Agent.Turn.OPPONENT:
            self.wait_for_turn()
        else:
            if self.turn == Agent.Turn.YOU:
                self.decide_on_move()
            elif self.turn == Agent.Turn.END:
                self.finish_game()
            else:
                raise ValueError("Invalid Turn value:" + str(self.turn))

    def finish_game(self):
        self.state = Agent.State.FINISHED
        # TODO: maybe print out the stats.


def main():
    pass


if __name__ == '__main__':
    main()
