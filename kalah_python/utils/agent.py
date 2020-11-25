from typing import Optional, Union, Callable, List, Tuple
from kalah_python.utils.board import Board, Side
from transitions import Machine
from enum import Enum, auto
from dataclasses import dataclass
from overrides import overrides
import logging


@dataclass
class Action:
    def to_cmd(self) -> bytes:
        raise NotImplementedError


@dataclass
class MoveAction(Action):
    hole_idx: int

    @overrides
    def to_cmd(self) -> bytes:
        return "MOVE;{}\n".format(self.hole_idx).encode('utf8')

    def __str__(self) -> str:
        return "MOVE;{}".format(self.hole_idx)


@dataclass
class SwapAction(Action):

    @overrides
    def to_cmd(self) -> bytes:
        return "SWAP\n".encode('utf8')

    def __str__(self) -> str:
        return "SWAP"


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
        ['game_state_is_opp', State.WAIT_FOR_SWAP_DECISION, State.WAIT_FOR_GAME_STATE],
        ['game_state_is_opp', State.WAIT_FOR_MOVE_RESULT, State.WAIT_FOR_SWAP_DECISION],
        ['game_state_is_opp', State.WAIT_FOR_GAME_STATE, "="],  # reflexive trigger
        ['game_state_is_you', State.WAIT_FOR_SWAP_DECISION, State.DECIDE_ON_MOVE],
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
        self.action: Optional[Union[MoveAction, SwapAction]] = None

    def decide_on_action(self, options: List[Action]) -> Action:
        """
        To be implemented by subclasses
        :return:
        """
        raise NotImplementedError

    def possible_actions(self) -> List[Action]:
        if self.side == Side.NORTH:
            # north is the second player (can choose to swap)
            actions: List[Action] = [
                MoveAction(nonzero_idx + 1)
                # the order should be reversed
                for nonzero_idx in self.board.nonzero_indices(self.side)
            ]
            if self.state == Agent.State.MAKE_MOVE_OR_SWAP:
                return actions + [SwapAction()]
            else:
                return actions
        elif self.side == Side.SOUTH:
            # south is the first player, so it can only move.
            return [
                MoveAction(nonzero_idx + 1)
                for nonzero_idx in self.board.nonzero_indices(self.side)
            ]

    def action_is_registered(self) -> bool:
        return self.action is not None

    def register_action(self, action: Action):
        if self.action:
            raise ValueError("an action is already registered.")
        self.action = action

    def unregister_action(self):
        if not self.action:
            raise ValueError("an action is supposed to be registered")
        del self.action
        self.action = None

    def commit_action(self):
        if not self.action_is_registered():
            raise ValueError("attempted to commit an action which is not registered")
        # and unregister the action
        if isinstance(self.action, MoveAction):
            self.moves()
        elif isinstance(self.action, SwapAction):
            self.swap_side()  # first swap side
            self.swaps()  # then trigger
        else:
            raise ValueError("Invalid registered action")

    def swap_side(self):
        if self.side == Side.NORTH:
            self.side = Side.SOUTH
        elif self.side == Side.SOUTH:
            self.side = Side.NORTH
        else:
            raise ValueError("Invalid side:" + str(self.side))

    def on_enter_DECIDE_ON_1ST_MOVE(self):
        # 1st player
        self.side = Side.SOUTH
        # get an action and register
        action = self.decide_on_action(self.possible_actions())
        self.register_action(action)

    def on_enter_WAIT_FOR_1ST_MOVE(self):
        # 2nd player
        self.side = Side.NORTH

    def on_enter_MAKE_MOVE_OR_SWAP(self):
        # get an action and register
        action = self.decide_on_action(self.possible_actions())
        self.register_action(action)

    def on_enter_DECIDE_ON_MOVE(self):
        # get an action and register
        action = self.decide_on_action(self.possible_actions())
        self.register_action(action)

    def on_enter_FINISHED(self):
        print("game is finished")
        print(self.board)

    def on_enter_EXIT(self):
        print("game was aborted")
        print(self.board)

