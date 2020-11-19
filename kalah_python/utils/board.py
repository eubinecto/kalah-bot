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

    def update_board(self, new_board: np.ndarray):
        if self._board.shape != new_board.shape:
            raise ValueError("shape mismatch:{}!={}"
                             .format(self._board.shape, new_board.shape))
        # just copy the values into the board from the new board
        np.copyto(dst=self._board, src=new_board)

    @property
    def north_store(self) -> int:
        return self._board[Board.NORTH_ROW, 0]

    @property
    def south_store(self) -> int:
        return self._board[Board.SOUTH_ROW, -1]

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
