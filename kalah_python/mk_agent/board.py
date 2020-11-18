from termcolor import colored
from typing import List


class Board:
    # constants for configuration.
    NUM_WELLS: int = 7
    INIT_STONES: int = 7
    NORTH_COLOR: str = 'magenta'
    SOUTH_COLOR: str = 'blue'

    def __init__(self):
        self.north_wells: List[int] = [Board.INIT_STONES] * Board.NUM_WELLS
        self.south_wells: List[int] = [Board.INIT_STONES] * Board.NUM_WELLS
        self.north_score: int = 0
        self.south_score: int = 0

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

    def __str__(self) -> str:
        """
        string representation of the board.
        :return:
        """
        north = colored(
            "{} -- ".format(self.north_score)
            + " ".join((str(well) for well in self.north_wells)),
            color=Board.NORTH_COLOR
        )
        south = colored(
            " ".join((str(well) for well in self.south_wells))
            + " -- {}".format(self.south_score),
            color=Board.SOUTH_COLOR
        )

        return north + "\n" + south
