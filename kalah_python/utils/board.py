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

    def store_idx(self) -> int:
        if self == Side.NORTH:
            return 0
        elif self == Side.SOUTH:
            return 7
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
        # the right most column from the player's perspective
        # is the number of seeds in the player's store.
        self.north_board: np.ndarray = np.array([0] + ([self.SEEDS_PER_HOLE] * self.HOLES_PER_SIDE))
        self.south_board: np.ndarray = np.array([0] + ([self.SEEDS_PER_HOLE] * self.HOLES_PER_SIDE))

    @staticmethod
    def opposite_hole_idx(hole_idx: int) -> int:
        if hole_idx < 1 or hole_idx > 7:  # error check
            raise ValueError("hole_idx is out of range.")
        return 7 - hole_idx + 1

    def nonzero_indices(self, side: Side) -> List[int]:
        return [
            idx
            for idx, hole in enumerate(self.holes(side))
            if hole != 0
        ]

    def update_board(self, change_msg: str):
        """
        to be used with the server.
        Not to be used for actor critic.
        :return:
        """
        #
        board_state = change_msg.split(";")[2]
        north_state = np.array(
            [int(board_state.split(",")[7])]
            + [int(seed) for seed in board_state.split(",")[:7]]
        )  # 1,2,3,4,5,6,7 -- store
        south_state = np.array(
            [int(board_state.split(",")[-1])]
            + [int(seed) for seed in board_state.split(",")[8:-1]]
        )  # 1,2,3,4,5,6,7 -- store
        if self.north_board.shape != north_state.shape or self.south_board.shape != south_state.shape:
            raise ValueError("shape mismatch")
        # just copy the values into the board from the new board
        np.copyto(dst=self.north_board, src=north_state)
        np.copyto(dst=self.south_board, src=south_state)

    def store(self, side: Side) -> int:
        """
        returns the current number of stones in the store of the side given.
        :param side:
        :return:
        """
        if side == Side.NORTH:
            return self.north_store
        elif side == Side.SOUTH:
            return self.south_store
        else:
            raise ValueError("Invalid side:" + str(side))

    # for adding seeds
    def add_seeds_to_store(self, side: Side, seeds: int):
        if side == Side.NORTH:
            self.north_board[0] += seeds
        elif side == Side.SOUTH:
            self.south_board[0] += seeds
        else:
            raise ValueError("Invalid side:" + str(side))

    def add_seeds_to_hole(self, hole_idx: int, side: Side, seeds: int):
        if side == Side.NORTH:
            self.north_board[hole_idx] += seeds
        elif side == Side.SOUTH:
            self.south_board[hole_idx] += seeds
        else:
            raise ValueError("Invalid side:" + str(side))

    def hole(self, hole_idx: int, side: Side) -> int:
        if side == Side.NORTH:
            return self.north_board[hole_idx]
        elif side == Side.SOUTH:
            return self.south_board[hole_idx]
        else:
            raise ValueError("Invalid side:" + str(side))

    def opposite_hole(self, hole_idx: int, side: Side) -> int:
        opposite_hole_idx = Board.opposite_hole_idx(hole_idx)
        if side == Side.NORTH:
            return self.hole(opposite_hole_idx, Side.SOUTH)
        elif side == Side.SOUTH:
            return self.hole(opposite_hole_idx, Side.NORTH)

    def holes(self, side: Side) -> np.ndarray:
        if side == Side.NORTH:
            return self.north_holes
        elif side == Side.SOUTH:
            return self.south_holes
        else:
            raise ValueError("Invalid side:" + str(side))

    # aliases - getters
    @property
    def north_store(self) -> int:
        return self.north_board[0]

    @property
    def south_store(self) -> int:
        return self.south_board[0]

    @property
    def north_holes(self) -> np.ndarray:
        """
        note that this returns a copy
        :return:
        """
        return np.copy(self.north_board[1:])  # omit the store.

    @property
    def south_holes(self) -> np.ndarray:
        """
        note that this returns the copy.
        :return:
        """
        # better get a copy, just in case you don't mess up things.
        return np.copy(self.south_board[1:])

    @property
    def board_size(self) -> int:
        """
        returns the number of holes (including the stores)
        on the board
        :return:
        """
        return self.north_board.size + self.south_board.size

    @property
    def board_flat(self) -> np.ndarray:
        """
        returns a vector (1D) representation of the board.
        this will be the input to ac model.
        :return:
        """
        # just concatenate the two boards.
        return np.concatenate((self.north_board, self.south_board))

    #  setters
    def set_hole(self, hole_idx: int, side: Side, seeds: int):
        if side == Side.NORTH:
            self.north_board[hole_idx] = seeds
        elif side == Side.SOUTH:
            self.south_board[hole_idx] = seeds
        else:
            raise ValueError("Invalid side:" + str(side))

    def __str__(self) -> str:
        """
        string representation of the board.
        :return:
        """
        north = colored(
            "N: "
            + "{} -- ".format(self.north_store)
            + " ".join((str(hole) for hole in reversed(self.north_holes))),
            color=Board.NORTH_COLOR
        )
        south = colored(
            "S: "
            + " ".join((str(hole) for hole in self.south_holes))
            + " -- {}".format(self.south_store),
            color=Board.SOUTH_COLOR
        )

        return north + "\n" + south
