from kalah_python.utils.board import Side, Board


class GameNode:

    def __init__(self, board, player, depth, moves=None):
        self.board = board
        self.player = player
        self.depth = depth
        self.moves = moves
        self.next = None
        self.value = None
        self.best_move = None
        self.is_over = False

    # TODO: This is where the heuristics will be used
    def update_value(self):
        self.value = 0

    # TODO: Update the board and player(side)
    def move(self, move):
        node = self
        simulate_move(self, move, node)

    def value(self):
        if self.value is None:
            self.update_value()
        return self.value

    def maximizing(self, side):
        return self.player == side

    def over(self):
        return self.is_over

    def __str__(self):
        return f"BOARD {self.board} ---- \n" \
               f"PLAYER:{self.player} ---- \n" \
               f"DEPTH:{self.depth} ---\n" \
               f"MOVES:{self.moves} ---\n" \
               f"BESTMOVE:{self.best_move}"

    # 1) Update thestate: - seeds in wells after and anction was made
    #                     - update the stores for each player
    #                     - decide who's move is


def simulate_move(self, action: Action, node: GameNode) -> GameNode:
    """
        :return: GameNoe.
        """
    pass
    board = node.board
    side = node.player

    seeds_added_to_store = 0
    # TODO: use Paul's code to implement this method. The code has been commented out for now
    if action == Action.SWAP:
        # return current side state, offset
        # SOUTH_TURN: moves
        # NORTH_TURN: swaps
        # then.. it is still NORTH_TURN.
        # the side has already been changed,so don't have to give it opposite.
        node.player = self.player = (Side.SOUTH, Side.NORTH)[self.player == Side.NORTH]
        return node

    hole = action.value
    seeds_to_sow = board.hole(hole, side)
    board.set_hole(hole, side, 0)

    holes = Board.HOLES_PER_SIDE  # you can directly access to the static var
    receiving_pits = 2 * holes + 1
    rounds = seeds_to_sow // receiving_pits  # floor() : truncate the floating points
    extra = seeds_to_sow % receiving_pits
    # sow the seeds of the full rounds (if any):
    if rounds != 0:
        for hole in range(1, holes + 1):
            board.add_seeds_to_hole(hole, side, rounds)
            board.add_seeds_to_hole(hole, side.opposite(), rounds)
        board.add_seeds_to_store(side, rounds)
    # sow the extra seeds
    sow_side = side
    sow_hole = hole
    for extra in reversed(range(1, extra + 1)):
        sow_hole = sow_hole + 1
        if sow_hole == 1:  # last pit was a store sow_side = sow_side.opposite()
            sow_side = sow_side.opposite()
        if sow_hole > holes:
            if sow_side == side:
                sow_hole = 0
                board.add_seeds_to_store(sow_side, 1)
                seeds_added_to_store += 1
                continue
            else:
                sow_side = sow_side.opposite()
                sow_hole = 1
        board.add_seeds_to_hole(sow_hole, sow_side, 1)

    # capture:
    if sow_side == side \
            and sow_hole > 0 \
            and board.hole(sow_hole, sow_side) == 1 \
            and board.opposite_hole(sow_hole, sow_side) > 0:
        board.add_seeds_to_store(side, 1 + board.opposite_hole(sow_hole, sow_side))
        seeds_added_to_store += 1 + board.opposite_hole(sow_hole, sow_side)
        board.set_hole(sow_hole, side, 0)
        board.set_hole(sow_hole, side.opposite(), 0)

    # game over (game ends)?
    finished_side = None
    if not board.nonzero_holes(side):
        finished_side = side
    elif not board.nonzero_holes(side.opposite()):
        finished_side = side.opposite()

    if finished_side:
        seeds = 0
        collecting_side = finished_side.opposite()
        for hole in range(1, holes + 1):
            seeds = seeds + board.hole(hole, collecting_side)
            board.set_hole(hole, collecting_side, 0)
        board.add_seeds_to_store(collecting_side, seeds)
        seeds_added_to_store += seeds
        # here, we are not returning game over, but returning
        # game_ends
        node.value = seeds_added_to_store
        node.is_over = True
        return node

    # your store minus opponent's store at the move
    node.board = board
    node.value = seeds_added_to_store
    if side == Side.SOUTH:
        node.player = side.NORTH
        return node
    else:
        node.player = side.SOUTH
        return node
