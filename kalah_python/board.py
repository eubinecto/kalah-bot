from termcolor import colored
from typing import List
import numpy as np
import enum


class Side(enum.Enum):
    NORTH = enum.auto()
    SOUTH = enum.auto()

    def opposite(self) -> 'Side':
        if self == Side.NORTH:
            return Side.SOUTH
        elif self == Side.SOUTH:
            return Side.NORTH
        else:
            # dummy
            return Side.NORTH


class Board:
    NORTH_ROW: int = 0
    SOUTH_ROW: int = 1
    HOLES_PER_SIDE: int = 7
    SEEDS_PER_HOLE: int = 7
    # for printing out
    NORTH_COLOR: str = 'magenta'
    SOUTH_COLOR: str = 'blue'

    def __init__(self):
        """
        initialises a (7, 7) board.
        """
        # for the south side: self.board[Board.SOUTH_ROW, :]
        # for the north side: self.board[Board.NORTH_ROW, :]
        # the right most column from the player's perspective
        # is the number of seeds in the player's store.
        self.board = np.array([
            [0] + ([self.SEEDS_PER_HOLE] * self.HOLES_PER_SIDE),
            ([self.SEEDS_PER_HOLE] * self.HOLES_PER_SIDE) + [0]
        ])

    @staticmethod
    def idx_of_side(side: Side) -> int:
        if side == Side.NORTH:
            return Board.NORTH_ROW
        elif side == Side.SOUTH:
            return Board.SOUTH_ROW
        else:
            # should never get there
            return -1

    def update_board(self, msg: str):
        """
        parse the message from the server, and update the current state of
        the board.
        here are some example messages from the server:
        CHANGE;1;7,7,7,7,7,7,7,0,0,8,8,8,8,8,8,1;OPP
        which means: change has been made as the following.. and the it is OPP's turn.

        :param msg: message from the game server
        """
        pass

    @property
    def north_store(self) -> int:
        return self.board[Board.NORTH_ROW, 0]

    @property
    def south_store(self) -> int:
        return self.board[Board.SOUTH_ROW, -1]

    def __str__(self) -> str:
        """
        string representation of the board.
        :return:
        """
        north = colored(
            "N: "
            + "{} -- ".format(self.north_store)
            + " ".join((str(hole) for hole in self.board[Board.NORTH_ROW, 1:])),
            color=Board.NORTH_COLOR
        )
        south = colored(
            "S: "
            + " ".join((str(hole) for hole in self.board[Board.SOUTH_ROW, :-1]))
            + " -- {}".format(self.south_store),
            color=Board.SOUTH_COLOR
        )

        return north + "\n" + south