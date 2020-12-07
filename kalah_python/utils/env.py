from typing import Optional

from kalah_python.utils.ac import ActorCritic
from kalah_python.utils.agents import ACAgent, Action
from kalah_python.utils.board import Board, Side
from enum import Enum, auto


class EnvState(Enum):
    SOUTH_TURN = auto()
    NORTH_TURN = auto()
    GAME_ENDS = auto()


class KalahEnv:
    # write bash scripts.

    def __init__(self, board: Board,
                 agent_s: ACAgent, agent_n: ACAgent,
                 ac_model: ActorCritic = None):
        """
        :param agent_s: the agent who will play on the south side of the board
        :param agent_n: the agent who will play on the north side of the board
        :param ac_model: The Actor-critic model to be used for training.
        """
        # keep the reference to the board on environment level as well.
        # note that this is the same board as those the two agents maintain.
        self.board = board
        # instantiate 2 agents
        self.agent_s: ACAgent = agent_s
        self.agent_n: ACAgent = agent_n
        self.ac_model: ActorCritic = ac_model
        self.env_state: Optional[EnvState] = None

    def play_game(self) -> float:
        """
        playing a full game, and return a reward.
        what should be the reward?
        :return:
        """
        self.agent_s.new_match_1st()  # south is the 1st player
        self.agent_n.new_match_2nd()  # north is the second player
        self.env_state = EnvState.SOUTH_TURN  # start with south.
        while self.env_state != EnvState.GAME_ENDS:
            if self.env_state == EnvState.SOUTH_TURN:
                self.order_agent(self.agent_s)
            elif self.env_state == EnvState.NORTH_TURN:
                self.order_agent(self.agent_n)
            else:
                raise ValueError("Invalid env_state: " + str(self.env_state))
            # self.render()

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
        self.env_state = self.make_move(board=self.board,
                                        action=ac_agent.action,
                                        side=ac_agent.side)
        # make_move was successful.
        # proceed to commit & unregister the action executed.
        ac_agent.commit_action()
        ac_agent.unregister_action()
        # notify the game state to both agents
        self.notify_game_state()

    def notify_game_state(self):
        if self.env_state == EnvState.NORTH_TURN:
            self.agent_n.game_state_is_you()
            self.agent_s.game_state_is_opp()
        elif self.env_state == EnvState.SOUTH_TURN:
            self.agent_n.game_state_is_opp()
            self.agent_s.game_state_is_you()
        elif self.env_state == EnvState.GAME_ENDS:
            self.agent_n.game_state_is_end()
            self.agent_s.game_state_is_end()
        else:
            raise ValueError("Invalid env_state:" + str(self.env_state))

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
            board.add_seeds_to_hole(sow_hole, sow_side, 1)

        # capture:
        if sow_side == side \
                and sow_hole > 0 \
                and board.hole(sow_hole, sow_side) == 1\
                and board.opposite_hole(sow_hole, sow_side) > 0:
            board.add_seeds_to_store(side, 1 + board.opposite_hole(sow_hole, sow_side))
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
            # here, we are not returning game over, but returning
            # game_ends instead.
            return EnvState.GAME_ENDS
        if side == Side.SOUTH:
            return EnvState.NORTH_TURN
        else:
            return EnvState.SOUTH_TURN

    def render(self):
        """
        this is only needed if we want to visualise the environment changing as the agent plays out the game
        :return:
        """
        print(self.board)
