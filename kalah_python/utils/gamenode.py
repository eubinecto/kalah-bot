from kalah_python.utils.board import Side


class GameNode:

    def __init__(self, board, player, depth, moves=None):
        self.board = board
        self.player = player
        self.depth = depth
        self.moves = moves
        self.next = None
        self.value = None
        self.best_move = None

    # TODO: This is where the heuristics will be used
    def update_value(self):
        self.value = 0

    # TODO: Update the board and player(side)
    def move(self, move):
        self.board = Board.simulate_move(move)
        self.player = (Side.SOUTH, Side.NORTH)[self.player == Side.NORTH]

    def value(self):
        if self.value is None:
            self.update_value()
        return self.value

    def maximizing(self, side):
        return self.player == side

    def over(self):
        return len(self.board.nonzero_holes(Side.NORTH)) == 0 or len(self.board.nonzero_holes(Side.SOUTH)) == 0

    def __str__(self):
        return f"BOARD {self.board} ---- " \
               f"PLAYER:{self.player} ---- " \
               f"DEPTH:{self.depth} ----" \
               f"MOVES:{self.moves}"
