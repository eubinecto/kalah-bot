from typing import Optional

from kalah_python.utils.ac import ActorCritic
from kalah_python.utils.agents import ACAgent, Action
from kalah_python.utils.board import Board, Side
from enum import Enum, auto


class EnvState(Enum):
    SOUTH_TURN = auto()
    NORTH_TURN = auto()
    GAME_OVER = auto()


class KalahEnv:
    # write bash scripts.

    def __init__(self, agent_s: ACAgent, agent_n: ACAgent,
                 ac_model: ActorCritic):
        """
        :param agent_s: the agent who will play on the south side of the board
        :param agent_n: the agent who will play on the north side of the board
        :param ac_model: The Actor-critic model to be used for training.
        """
        # instantiate 2 agents
        self.agent_s: ACAgent = agent_s
        self.agent_n: ACAgent = agent_n
        self.ac_model: ActorCritic = ac_model
        self.env_state: Optional[EnvState] = None

    def play_game(self) -> float:
        """
        starts the game.
        :return:
        """
        self.agent_s.new_match_1st()  # south is the 1st player
        self.agent_n.new_match_2nd()  # north is the second player
        self.env_state = EnvState.SOUTH_TURN  # start with south.

        while self.env_state != EnvState.GAME_OVER:
            if self.env_state == EnvState.SOUTH_TURN:
                self.order_agent(self.agent_s)
            elif self.env_state == EnvState.NORTH_TURN:
                self.order_agent(self.agent_n)
            else:
                raise ValueError("Invalid env_state: " + str(self.env_state))

        reward = ...
        return reward

    def reset(self):
        """
        resets the game.
        :return:
        """
        self.agent_s.reset()
        self.agent_n.reset()

    def order_agent(self, ac_agent: ACAgent):
        """
        orders the given agent to commit an action.
        :param ac_agent:
        :return:
        """
        if not ac_agent.action_is_registered():
            raise ValueError("Action should have been registered, but it is not.")
        # TODO: make a move.
        self.env_state = self.make_move(board=ac_agent.board,
                                        action=ac_agent.action,
                                        side=ac_agent.side)
        # make_move was successful.
        # proceed to commit & unregister the action executed.
        ac_agent.commit_action()
        ac_agent.unregister_action()

    def game_is_over(self) -> bool:
        return self.env_state == EnvState.GAME_OVER

    @staticmethod
    def make_move(board: Board, action: Action, side: Side) -> EnvState:
        """
        :return: state, reward and done.
        """
        pass
        # TODO: use Paul's code to implement this method. The code has been commented out for now
        if action == Action.SWAP:
            pass

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
                    continue
                else:
                    sow_side = sow_side.opposite()
                    sow_hole = 1
            board.add_seeds_to_hole(sow_side, sow_hole, 1)

        # capture:
        if sow_side == side \
                and sow_hole > 0 \
                and board.hole(sow_hole, sow_side) == 1\
                and board.opposite_hole(sow_hole, sow_side) > 0:
            board.add_seeds_to_store(side, 1 + board.opposite_hole(sow_hole, sow_side))
            board.set_hole(sow_hole, side, 0)
            board.set_hole(sow_hole, side.opposite(), 0)

        # game over?
        finished_side = None
        if not board.nonzero_indices(side):
            finished_side = side
        elif not board.nonzero_indices(side.opposite()):
            finished_side = side.opposite()
        if not finished_side:
            seeds = 0
            collecting_side = finished_side.opposite()
            for hole in range(1, holes + 1):
                seeds = seeds + board.hole(hole, collecting_side)
                board.set_hole(hole, collecting_side, 0)
            board.add_seeds_to_store(collecting_side, seeds)
            return EnvState.GAME_OVER
        if side == Side.SOUTH:
            return EnvState.NORTH_TURN
        else:
            return EnvState.SOUTH_TURN

    # this is only needed if we want to visualise the environment changing as the agent plays out the game
    def render(self):
        pass
