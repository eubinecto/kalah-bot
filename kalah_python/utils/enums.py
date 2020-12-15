from enum import Enum, auto, unique
from typing import List


@unique
class Action(Enum):
    # all possible moves are defined here.
    MOVE_1ST_WELL = 1
    MOVE_2ND_WELL = 2
    MOVE_3RD_WELL = 3
    MOVE_4TH_WELL = 4
    MOVE_5TH_WELL = 5
    MOVE_6TH_WELL = 6
    MOVE_7TH_WELL = 7
    SWAP = -1

    @staticmethod
    def all_actions() -> List['Action']:
        """
        just get all the possible actions.
        Note that they are ordered.
        :return:
        """
        return list(Action)

    @staticmethod
    def move_actions() -> List['Action']:
        """
        :return: Only the move actions. (Everything but SWAP action)
        """
        return [
            action
            for action in Action
            if action != Action.SWAP  # everything but swap
        ]

    def to_cmd(self):
        if self == Action.SWAP:
            # command for swap action
            cmd = "SWAP\n".encode('utf8')
        else:
            # command for move action
            cmd = "MOVE;{}\n".format(self.value).encode('utf8')
        return cmd

    def __str__(self) -> str:
        if self != Action.SWAP:
            msg = "MOVE;{}".format(self.value)
        else:
            msg = "SWAP"
        return msg


class AgentState(Enum):
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


class KalahEnvState(Enum):
    INIT = auto()
    SOUTH_TURN = auto()
    NORTH_TURN = auto()
    GAME_ENDS = auto()


class Side(Enum):
    NORTH = auto()
    SOUTH = auto()

    def opposite(self) -> 'Side':
        if self == Side.NORTH:
            return Side.SOUTH
        elif self == Side.SOUTH:
            return Side.NORTH
        else:
            raise ValueError("invalid side:" + str(self))

    def store_idx(self) -> int:
        if self == Side.NORTH:
            return 0
        elif self == Side.SOUTH:
            return 7
        else:
            raise ValueError("invalid side:" + str(self))
