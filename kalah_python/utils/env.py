from dataclasses import dataclass
from typing import Tuple, Optional
from kalah_python.utils.agents import ACAgent, Agent
from kalah_python.utils.board import Board
from kalah_python.utils.dataclasses import HyperParams
from kalah_python.utils.enums import KalahEnvState, Action, Side, AgentState
from config import train_logger


@dataclass
class Result:
    draw: bool
    winner: Optional[ACAgent] = None
    loser: Optional[ACAgent] = None
    win_score: int = 0


class KalahEnv:
    def __init__(self, board: Board, agent_s: Agent, agent_n: Agent):
        self.board = board
        self.agent_s = agent_s
        self.agent_n = agent_n
        self.env_state = KalahEnvState.INIT

    def play_game(self):
        """
        playing a full game, and return a reward.
        what should be the reward?
        :return:
        """
        self.agent_s.new_match_1st()  # south is the 1st player
        self.agent_n.new_match_2nd()  # north is the second player
        self.env_state = KalahEnvState.SOUTH_TURN  # start with south.
        while self.env_state != KalahEnvState.GAME_ENDS:
            if self.env_state == KalahEnvState.SOUTH_TURN:
                self.order_agent(self.agent_s)
            elif self.env_state == KalahEnvState.NORTH_TURN:
                self.order_agent(self.agent_n)
            else:
                raise ValueError("Invalid env_state: " + str(self.env_state))

    def reset(self):
        """
        resets the game environment.
        """
        # reset signal
        self.agent_s.reset()
        self.agent_n.reset()
        # reset the board
        self.board.reset()
        # reset the env state as well
        self.env_state = KalahEnvState.INIT

    def order_agent(self, agent: Agent):
        """
        orders the given agent to commit an action.
        :param agent:
        :return:
        """
        if not agent.action_is_registered():
            raise ValueError("Action should have been registered, but it is not.")
        # have to commit & agent action before execute action (due to swap)
        agent.commit_action()
        if agent.action == Action.SWAP:
            env_state, _ = self.execute_swap(agent)
        else:
            env_state, _ = self.execute_move(agent)
        # update the environment states
        self.env_state = env_state
        self.notify_game_state()  # notify the game state to both agents

    def notify_game_state(self):
        # TODO: what if you are making a move again
        if self.env_state == KalahEnvState.NORTH_TURN:
            self.agent_n.game_state_is_you()
            self.agent_s.game_state_is_opp()
        elif self.env_state == KalahEnvState.SOUTH_TURN:
            self.agent_n.game_state_is_opp()
            self.agent_s.game_state_is_you()
        elif self.env_state == KalahEnvState.GAME_ENDS:
            self.agent_n.game_state_is_end()
            self.agent_s.game_state_is_end()
        else:
            raise ValueError("Invalid env_state:" + str(self.env_state))

    def execute_swap(self, agent: Agent) -> Tuple[KalahEnvState, int]:
        # the side of north agent should have been changed
        agent.unregister_action()
        assert agent.side == Side.SOUTH
        # the side of south agent should be changed now...
        self.agent_s.side = Side.NORTH
        # now swap the agents
        self.agent_n, self.agent_s = self.agent_s, self.agent_n
        seeds_added_to_store = 0
        return KalahEnvState.NORTH_TURN, seeds_added_to_store

    @staticmethod
    def execute_move(agent: Agent) -> Tuple[KalahEnvState, int]:
        """
        :param: side: the current side of the agent
        :return: state, reward and done.
        """
        hole = agent.action.value
        board = agent.board
        side = agent.side
        agent.unregister_action()  # unregister action here.

        seeds_added_to_store = 0
        seeds_to_sow = board.hole(hole, side)
        board.set_hole(hole, side, 0)

        holes = Board.HOLES_PER_SIDE  # you can directly access to the static var
        receiving_pits = 2 * holes + 1
        rounds = seeds_to_sow // receiving_pits  # floor() : truncate the floating points
        extra = seeds_to_sow % receiving_pits  # the first "extra" number of holes get "rounds"+1 seeds,
        # the remaining ones get "rounds" seeds
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
            board.set_hole(board.opposite_hole_idx(sow_hole), side.opposite(), 0)

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
            return KalahEnvState.GAME_ENDS, seeds_added_to_store
        # your store minus opponent's store at the move
        if sow_hole == 0 and agent.state != AgentState.WAIT_FOR_MOVE_RESULT:
            if side == Side.SOUTH:
                return KalahEnvState.SOUTH_TURN, seeds_added_to_store
            else:
                return KalahEnvState.NORTH_TURN, seeds_added_to_store
        else:
            if side == Side.SOUTH:
                return KalahEnvState.NORTH_TURN, seeds_added_to_store
            else:
                return KalahEnvState.SOUTH_TURN, seeds_added_to_store


class ACKalahEnv(KalahEnv):

    def __init__(self, board: Board, agent_s: ACAgent, agent_n: ACAgent, h_params: HyperParams):
        """
        :param agent_s: the agent who will play on the south side of the board
        :param agent_n: the agent who will play on the north side of the board
        """
        super().__init__(board, agent_s, agent_n)
        self.h_params: HyperParams = h_params

    def play_game(self):
        """
        playing a full game, and return a reward.
        what should be the reward?
        :return:
        """
        super().play_game()
        game_res = self.game_res()
        train_logger.info(str(self.board))
        if not game_res.draw:
            train_logger.info("winner: " + str(game_res.winner.side))
            train_logger.info("win score: " + str(game_res.win_score))
        else:
            train_logger.info("the game ended in draw")
        # after the game ends, reward the winner and penalise the loser
        self.reward_and_penalise(game_res)

    def reset(self):
        """
        resets the game environment.
        """
        # type casting
        self.agent_n: ACAgent
        self.agent_s: ACAgent
        # reset signal
        self.agent_s.reset()
        self.agent_n.reset()
        # reset the board
        self.board.reset()
        # clear the buffers here
        self.agent_n.clear_buffers()
        self.agent_s.clear_buffers()
        # reset the env state as well
        self.env_state = KalahEnvState.INIT

    def order_agent(self, agent: ACAgent):
        """
        orders the given agent to commit an action.
        :param agent:
        :return:
        """
        if self.board.seeds != 98:
            print("########")
            print(self.board)
            print("########")
            raise ValueError("Should be 98 but was: " + str(self.board.seeds))

        if not agent.action_is_registered():
            raise ValueError("Action should have been registered, but it is not.")
        # have to commit & agent action before execute action (due to swap)
        agent.commit_action()
        if agent.action == Action.SWAP:
            env_state, seeds_added_to_store = self.execute_swap(agent)
        else:
            env_state, seeds_added_to_store = self.execute_move(agent)
        reward = self.reward(agent.side, seeds_added_to_store)
        agent.reward_buffer.append(reward)
        # update the environment state.
        self.env_state = env_state
        self.notify_game_state()

    def reward_and_penalise(self, game_res: Result):
        """
        reward the winner, penalise the loser, and penalise both
        if the game ended in draw.
        :return:
        """
        # get the result of the game..
        self.agent_n: ACAgent
        self.agent_s: ACAgent
        if not game_res.draw:  # there was a winner (not a draw).
            self.reward_winner(game_res.winner, game_res.win_score)
            self.penalise_loser(game_res.loser, game_res.win_score)
        else:  # the game ended in a draw
            # penalise both agents, as if they were both losers
            self.penalise_loser(self.agent_n, game_res.win_score)
            self.penalise_loser(self.agent_s, game_res.win_score)

    def reward_winner(self, winner: ACAgent, win_score: int):
        for idx, reward in enumerate(winner.reward_buffer):
            # increase the rewards by x %, which is proportional to win_score %
            winner.reward_buffer[idx] = reward * (1 + (win_score / self.board.seeds))

    def penalise_loser(self, loser: ACAgent, win_score: int):
        for idx, reward in enumerate(loser.reward_buffer):
            # decrease the rewards by x %
            loser.reward_buffer[idx] = reward * (1 - (win_score / self.board.seeds))

    def game_res(self) -> Result:
        """
        returns a reference to the winner agent, with the score. (offset)
        """
        self.agent_n: ACAgent
        self.agent_s: ACAgent
        if self.env_state != KalahEnvState.GAME_ENDS:  # error handling.
            raise ValueError("The game should have ended, but it has not.")

        south_offset = self.board.store_offset(self.agent_s.side)
        if south_offset > 0:
            # south is the winner
            return Result(draw=False, winner=self.agent_s,
                          loser=self.agent_n, win_score=south_offset)
        elif south_offset < 0:
            # north is the winner
            return Result(draw=False, winner=self.agent_n,
                          loser=self.agent_s, win_score=(-1 * south_offset))
        else:
            # game ended in a draw
            return Result(draw=True)

    def reward(self, side: Side, new_seeds: int) -> float:
        """
        return new_seeds_w * new seeds + offset_w * offset(side)
        :param side:
        :param new_seeds:
        :return:
        """
        # note: the rewards must be non-negative
        offset = self.board.store_offset(side)
        if offset > 0:
            reward = new_seeds + offset
        else:
            reward = new_seeds
        return reward

    def render(self):
        """
        this is only needed if we want to visualise the environment changing as the agent plays out the game
        :return:
        """
        print(self.board)
