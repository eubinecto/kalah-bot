from typing import Optional, Union, Callable
from kalah_python.utils.board import Board, Side
from transitions import Machine
from enum import Enum, auto
from dataclasses import dataclass
from overrides import overrides
import asyncio


@dataclass
class Action:
    def to_cmd(self) -> bytes:
        raise NotImplementedError


@dataclass
class MoveAction(Action):
    side: Side
    hole_idx: int

    @overrides
    def to_cmd(self) -> bytes:
        return "MOVE;{}\n".format(self.hole_idx).encode('utf8')

    def validate_hole_idx(self):
        if self.side == Side.NORTH:
            if self.hole_idx < 0 \
                    or self.hole_idx > Board.HOLES_PER_SIDE - 1:
                raise ValueError("Invalid hole_idx for side NORTH:" + str(self.hole_idx))
        elif self.side == Side.SOUTH:
            if self.hole_idx < 1 \
                    or self.hole_idx > Board.HOLES_PER_SIDE:
                raise ValueError("Invalid hole_idx for side SOUTH:" + str(self.hole_idx))
        else:
            raise ValueError("Invalid side:" + self.side.name)


@dataclass
class SwapAction(Action):

    @overrides
    def to_cmd(self) -> bytes:
        return "SWAP\n".encode('utf8')


class Agent(object):
    class State(Enum):
        INIT = auto()
        DECIDE_ON_1ST_MOVE = auto()
        WAIT_FOR_MOVE_RESULT = auto()
        WAIT_FOR_1ST_MOVE = auto()
        MAKE_MOVE_OR_SWAP = auto()
        WAIT_FOR_SWAP_DECISION = auto()
        DECIDE_ON_MOVE = auto()
        WAIT_FOR_GAME_STATE = auto()
        FINISHED = auto()
        # make sure this state is the last one.
        EXIT = auto()
    # trigger, source, dest
    TRANSITIONS = [
        ['new_match_1st', State.INIT, State.DECIDE_ON_1ST_MOVE],
        ['new_match_2nd', State.INIT, State.WAIT_FOR_1ST_MOVE],
        ['moves', State.DECIDE_ON_1ST_MOVE, State.WAIT_FOR_MOVE_RESULT],
        ['moves', State.MAKE_MOVE_OR_SWAP, State.WAIT_FOR_GAME_STATE],
        ['moves', State.DECIDE_ON_MOVE, State.WAIT_FOR_GAME_STATE],
        ['swaps', State.MAKE_MOVE_OR_SWAP, State.WAIT_FOR_GAME_STATE],
        ['opp_swaps', State.WAIT_FOR_SWAP_DECISION, State.DECIDE_ON_MOVE],
        ['opp_does_not_swap', State.WAIT_FOR_SWAP_DECISION, State.WAIT_FOR_GAME_STATE],
        ['game_state_is_opp', State.WAIT_FOR_MOVE_RESULT, State.WAIT_FOR_SWAP_DECISION],
        ['game_state_is_you', State.WAIT_FOR_1ST_MOVE, State.MAKE_MOVE_OR_SWAP],
        ['game_state_is_you', State.WAIT_FOR_GAME_STATE, State.DECIDE_ON_MOVE],
        ['game_state_is_end', State.WAIT_FOR_GAME_STATE, State.FINISHED],
        # from all states.
        ['game_over', '*', State.EXIT]
    ]
    # triggers. Just class-level type hints for dynamically added attrs
    # https://stackoverflow.com/a/49052572
    new_match_1st: Optional[Callable]
    new_match_2nd: Optional[Callable]
    moves: Optional[Callable]
    swaps: Optional[Callable]
    opp_swaps: Optional[Callable]
    opp_does_not_swap: Optional[Callable]
    game_state_is_opp: Optional[Callable]
    game_state_is_you: Optional[Callable]
    game_state_is_end: Optional[Callable]
    game_over: Optional[Callable]

    # state attribute will be accessible
    state: State

    def __init__(self):
        # an agent maintains an up-to-date board,
        # the current state of the agent,
        # and the current turn.
        self.board: Board = Board()  # init a (7,7) board
        self.machine = Machine(model=self, states=Agent.State,
                               transitions=Agent.TRANSITIONS, initial=Agent.State.INIT)
        self.side: Optional[Side] = None

    def decide_on_move_or_swap(self) -> Union[MoveAction, SwapAction]:
        """
        To be implemented by subclasses
        :return: returns either a move action or a swap action.
        """
        raise NotImplementedError

    def decide_on_move(self) -> MoveAction:
        """
        To be implemented by subclasses
        :return:
        """
        raise NotImplementedError

    def on_enter_DECIDE_ON_1ST_MOVE(self):
        self.side = Side.SOUTH

    def on_enter_WAIT_FOR_1ST_MOVE(self):
        self.side = Side.NORTH
