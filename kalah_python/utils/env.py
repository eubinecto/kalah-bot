from typing import Optional

from kalah_python.utils.ac import ActorCritic
from kalah_python.utils.agents import ACAgent, Action
from kalah_python.utils.board import Board, Side
from enum import Enum, auto


class EnvState(Enum):
    SOUTH_TURN = auto()
    NORTH_TURN = auto()
    GAME_OVER = auto()


class GameOverError(Exception):
    pass


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

    def start_game(self):
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
        try:
            self.make_move(board=ac_agent.board,
                           action=ac_agent.action,
                           side=ac_agent.side)
        except GameOverError:
            self.env_state = EnvState.GAME_OVER
        else:
            # make_move was successful.
            # proceed to commit & unregister the action executed.
            ac_agent.commit_action()
            ac_agent.unregister_action()
            # change the states of the env.
            if ac_agent.side == Side.SOUTH:
                self.env_state = EnvState.NORTH_TURN
            elif ac_agent.side == Side.NORTH:
                self.env_state = EnvState.SOUTH_TURN
            else:
                raise ValueError("invalid ac_agent state:" + str(ac_agent))

    def make_move(self, board: Board, action: Action, side: Side):
        """
        :return: state, reward and done.
        """
        pass
        # TODO: use Paul's code to implement this method. The code has been commented out for now
        # side = action.side
        # if isinstance(action, SwapAction):
        #     pass
        #
        # hole = action.hole_idx
        # seeds_to_sow = board.seed_on_side(side, hole)
        # board.set_seeds_in_hole(side, hole, 0)
        #
        # holes = board.get_number_of_holes()
        # receiving_pits = 2 * holes + 1
        # rounds = seeds_to_sow / receiving_pits
        # extra = seeds_to_sow % receiving_pits
        # # sow the seeds of the full rounds (if any):
        # if rounds != 0:
        #     for rounds in range(hole, holes + 1):
        #         board.add_seeds_to_hole(side, hole, rounds)
        #         board.add_seeds_to_hole(side.opposite(), hole, rounds)
        #     board.add_seeds_to_store(side, rounds)
        # # sow the extra seeds
        # sow_side = side
        # sow_hole = hole
        # for extra in reversed(range(1, extra + 1)):
        #     sow_hole = sow_hole + 1
        #     if sow_hole == 1: # last pit was a sto  sow_side = sow_side.opposite()
        #         if sow_hole > holes:
        #             if sow_side == side:
        #                 sow_hole = 0
        #                 board.add_seeds_to_store(side, 1)

    # this is only needed if we want to visualise the environment changing as the agent plays out the game
    def render(self):
        pass
