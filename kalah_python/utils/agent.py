from typing import Optional, Union
from kalah_python.utils.board import Board, Side
from kalah_python.utils.protocol import Protocol
from enum import Enum, auto
from dataclasses import dataclass
from overrides import overrides


class Turn(Enum):
    YOU = auto()
    OPPONENT = auto()
    END = auto()


class State(Enum):
    INIT = auto()
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


@dataclass
class Action:
    # common attribute for MoveAction & SwapAction
    state: State

    def validate(self):
        """
        make sure you validate your action before executing it.
        """
        raise NotImplementedError

    def to_cmd(self) -> str:
        raise NotImplementedError

    def _validate_state(self):
        raise NotImplementedError


@dataclass
class MoveAction(Action):
    side: Side
    hole_idx: int

    @overrides
    def validate(self):
        self._validate_hole_idx()
        self._validate_state()

    @overrides
    def to_cmd(self) -> str:
        return "MOVE;{}\n".format(self.hole_idx)

    @overrides
    def _validate_state(self):
        movable_states = (
            State.DECIDE_ON_1ST_MOVE,
            State.DECIDE_ON_MOVE,
            State.MAKE_MOVE_OR_SWAP
        )
        if self.state not in movable_states:
            raise ValueError("cannot from the state:" + self.state.name)

    def _validate_hole_idx(self):
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
    def validate(self):
        self._validate_state()

    @overrides
    def to_cmd(self) -> str:
        return "SWAP\n"

    @overrides
    def _validate_state(self):
        if self.state != State.MAKE_MOVE_OR_SWAP:
            raise ValueError("cannot swap from the state:" + self.state.name)


class Agent(object):
    # trigger, source, dest

    def __init__(self, protocol: Protocol):
        # an agent maintains an up-to-date board,
        # the current state of the agent,
        # and the current turn.
        self.board: Board = Board()  # init a (7,7) board
        self.state: State = State.INIT  # start with initial state.
        self.protocol: Optional[Protocol] = protocol  # register a protocol
        self.side: Optional[Side] = None
        self.turn: Optional[Turn] = None

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

    def decide_on_swap(self) -> SwapAction:
        """
        To be implemented by subclasses
        :return:
        """
        raise NotImplementedError

    def start_playing(self, is_south: bool):
        if is_south:
            # start playing as a 1st player
            # 1st player is on the south side
            self.side = Side.SOUTH
            self.turn = Turn.YOU
            self._decide_on_1st_move()
        else:
            # start playing as a 2nd player
            # 2nd player is on the north side
            self.side = Side.NORTH
            self.turn = Turn.OPPONENT
            self._wait_for_1st_move()

    def _execute(self, action: Action):
        # first, validate the action
        action.validate()  # exception will be thrown if action is invalid
        # to execute the action,
        # send command to the game engine via protocol instance
        self.protocol.send_cmd(action.to_cmd())
        # execute the action. The action is either move or swap.

    #  -------------- 1st player state handlers ------------ #
    def _decide_on_1st_move(self):
        self.state = State.DECIDE_ON_1ST_MOVE
        move_action = self.decide_on_move()
        self._execute(move_action)
        self._wait_for_move_result()

    def _wait_for_move_result(self):
        self.state = State.WAIT_FOR_MOVE_RESULT
        while self.turn == Turn.YOU:
            # do nothing. just polling the turn
            pass
        else:
            if self.turn == Turn.OPPONENT:
                self._wait_for_swap_decision()
            else:
                raise ValueError("Invalid turn: " + str(self.turn))

    def _wait_for_swap_decision(self):
        self.state = State.WAIT_FOR_SWAP_DECISION
        # TODO have to know whether opponent did not swap or not...
        self._decide_on_move()

    # --------------- 2nd player state handlers -------------- #
    def _wait_for_1st_move(self):
        self.state = State.WAIT_FOR_1ST_MOVE
        while self.turn == Turn.OPPONENT:
            # do nothing. just polling the turn
            pass
        else:
            if self.turn == Turn.YOU:
                self._make_move_or_swap()
            else:
                raise ValueError("Invalid turn: " + str(self.turn))

    def _make_move_or_swap(self):
        self.state = State.MAKE_MOVE_OR_SWAP
        action = self.decide_on_move_or_swap()
        self._execute(action)
        self._wait_for_turn()

    # --------------- common state handlers ----------------- #
    def _decide_on_move(self):
        self.state = State.DECIDE_ON_MOVE
        move_action = self.decide_on_move()
        self._execute(move_action)
        self._wait_for_turn()

    def _wait_for_turn(self):
        self.state = State.WAIT_FOR_TURN
        while self.turn == Turn.OPPONENT:
            # Just polling the turn.
            pass
        else:
            if self.turn == Turn.YOU:
                self._decide_on_move()
            elif self.turn == Turn.END:
                self._finish_game()
            else:
                raise ValueError("Invalid Turn value:" + str(self.turn))

    def _finish_game(self):
        self.state = State.FINISHED
        print(self.board)
        print("game is finished")
