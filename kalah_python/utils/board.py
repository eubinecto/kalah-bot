from typing import List

from termcolor import colored
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
            raise ValueError("invalid side:" + str(self))


class Board:
    NORTH_ROW: int = 0
    SOUTH_ROW: int = 1
    HOLES_PER_SIDE: int = 7
    SEEDS_PER_HOLE: int = 7
    # for pretty printing board with termcolor module
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
        self._board = np.array([
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

    def nonzero_indices(self, side: Side) -> List[int]:
        if side == Side.NORTH:
            # exclude first idx, which is the store for the north
            return [
                idx
                for idx, hole in enumerate(self.north_holes)
                if hole != 0
            ]
        elif side == Side.SOUTH:
            # exclude the last idx, which
            return [
                idx
                for idx, hole in enumerate(self.south_holes)
                if hole != 0
            ]
        else:
            raise ValueError("invalid side:" + str(side))

    def update_board(self, change_msg: str):
        """
        :param change_msg: e.g. CHANGE;1;7,7,7,7,7,7,7,0,0,8,8,8,8,8,8,1;YOU

        :return:
        """
        board_state = change_msg.split(";")[2]
        north_state = reversed([int(seed) for seed in board_state.split(",")[:8]])
        south_state = [int(seed) for seed in board_state.split(",")[8:]]
        new_board = np.array([list(north_state), south_state])
        if self._board.shape != new_board.shape:
            raise ValueError("shape mismatch:{}!={}"
                             .format(self._board.shape, new_board.shape))
        # just copy the values into the board from the new board
        np.copyto(dst=self._board, src=new_board)

    def get_store(self, side: Side) -> int:
        if side == Side.NORTH:
            return self.north_store
        elif side == Side.SOUTH:
            return self.south_store
        else:
            raise ValueError("Invalid side:" + str(side))

    # aliases
    @property
    def north_store(self) -> int:
        return self._board[Board.NORTH_ROW, 0]

    @property
    def south_store(self) -> int:
        return self._board[Board.SOUTH_ROW, -1]

    @property
    def north_holes(self) -> np.ndarray:
        # this array is flipped reversed to normalise the index with south holes.
        flipped: np.ndarray = np.flip(self._board[self.idx_of_side(Side.NORTH), 1:])
        return flipped

    @property
    def south_holes(self) -> np.ndarray:
        return self._board[self.idx_of_side(Side.SOUTH), :-1]

    def __str__(self) -> str:
        """
        string representation of the board.
        :return:
        """
        north = colored(
            "N: "
            + "{} -- ".format(self.north_store)
            + " ".join((str(hole) for hole in self._board[Board.NORTH_ROW, 1:])),
            color=Board.NORTH_COLOR
        )
        south = colored(
            "S: "
            + " ".join((str(hole) for hole in self._board[Board.SOUTH_ROW, :-1]))
            + " -- {}".format(self.south_store),
            color=Board.SOUTH_COLOR
        )

        return north + "\n" + south
