import time
from dataclasses import dataclass
from typing import Tuple, Union, List, Optional

import numpy as np
import torch
import torch.nn.functional as F

from kalah_python.utils.agents import ACAgent, Agent
from kalah_python.utils.board import Board
from kalah_python.utils.dataclasses import HyperParams, ActionInfo
from kalah_python.utils.enums import KalahEnvState, Action, Side, AgentState
import logging
from sys import stdout
EPS = np.finfo(np.float32).eps.item()  # the smallest possible value (epsilon)

# for debugging
torch.autograd.set_detect_anomaly(True)
logging.basicConfig(stream=stdout, level=logging.INFO)

DELIM = "=================================================="


class Episode:
    def __init__(self, epi_num: int, h_params: HyperParams,
                 optimizer: torch.optim.Optimizer, game_res: 'Result'):
        self.epi_num = epi_num
        self.h_params = h_params
        self.optimizer = optimizer
        self.game_res = game_res
        self.policy_losses: List[torch.Tensor] = list()
        self.value_losses: List[torch.Tensor] = list()
        self.loss: Optional[torch.Tensor] = None

    # compute discounted rewards
    def comp_disc_rewards(self, rewards: List[float]) -> List[torch.Tensor]:
        global EPS
        discounted: List[float] = list()
        R = 0
        for r in reversed(rewards):
            R = r + self.h_params.discount_factor * R
            discounted.insert(0, R)
        else:
            # zero-centered mean
            discounted_np = np.array(discounted)
            discounted_norm_np = (discounted_np - discounted_np.mean()) / (discounted_np.std() + EPS)
            return [
                torch.scalar_tensor(val, dtype=torch.float32)
                for val in discounted_norm_np
            ]

    # accumulate losses
    def build_losses(self, action_infos: List[ActionInfo], disc_rewards: List[torch.Tensor]):
        """
        returns policy_losses, value_losses
        :return:
        """
        for action_info, disc_reward in zip(action_infos, disc_rewards):
            critique = action_info.critique
            log_prob = action_info.logit
            advantage = disc_reward - critique
            self.policy_losses.append(-log_prob * advantage)  # actor (policy) loss for this action
            self.value_losses.append(F.smooth_l1_loss(critique.squeeze(), disc_reward))

    def build_loss(self):
        # add all the oss
        loss = torch.stack(self.policy_losses).sum() \
               + torch.stack(self.value_losses).sum()
        self.loss = loss

    def update_weights(self):
        self.optimizer.zero_grad()
        self.loss.backward()
        self.optimizer.step()

    def finish(self):
        raise NotImplementedError

    def log(self, start_time: float, logger: logging.Logger):
        """
        each episode implements a different logging logic

        """
        logger.info("\n" + str(self.game_res.board))
        if not self.game_res.draw:
            logger.info("winner:" + str(self.game_res.winner))
            logger.info("win_score:" + str(self.game_res.win_score))
        else:
            logger.info("the game ended in draw")


class OppEpisode(Episode):

    def __init__(self, ac_agent: ACAgent, opp_agent: Agent,
                 epi_num: int, h_params: HyperParams,
                 optimizer: torch.optim.Optimizer, game_res: 'Result'):
        super().__init__(epi_num, h_params, optimizer, game_res)
        self.ac_agent_action_infos = ac_agent.action_info_buffer
        self.ac_agent_rewards = ac_agent.reward_buffer
        # just for the sake of logging.
        self.opp_agent_actions = opp_agent.action_buffer
        self.ac_agent_str = str(ac_agent)

    def finish(self):
        # comp rewards & losses with the agent's info.
        disc_rewards = self.comp_disc_rewards(self.ac_agent_rewards)
        self.build_losses(self.ac_agent_action_infos, disc_rewards)
        self.build_loss()
        # update the weights
        self.update_weights()

    def log(self, start_time: float, logger: logging.Logger):
        global DELIM
        super().log(start_time, logger)
        reward = sum(self.ac_agent_rewards)
        # log results
        time_elapsed = time.time() - start_time
        logger.info('episode:{}'.format(self.epi_num))
        logger.info('player:{}\treward_total: {:.2f}\treward_avg: {:.2f}'
                    .format(self.ac_agent_str,
                            reward, reward / len(self.ac_agent_rewards)))
        logger.info("time_elapsed:" + str(time_elapsed))
        logger.info(DELIM)


class SelfEpisode(Episode):
    def __init__(self, ac_agent_n: ACAgent, ac_agent_s: ACAgent,
                 epi_num: int, h_params: HyperParams,
                 optimizer: torch.optim.Optimizer, game_res: 'Result'):
        # actions for the two actions
        super().__init__(epi_num, h_params, optimizer, game_res)
        self.ac_agent_n_action_infos = ac_agent_n.action_info_buffer
        self.ac_agent_s_action_infos = ac_agent_s.action_info_buffer
        # rewards for the two actions
        self.ac_agent_n_rewards = ac_agent_n.reward_buffer
        self.ac_agent_s_rewards = ac_agent_s.reward_buffer
        self.ac_agent_n_str = str(ac_agent_n)
        self.ac_agent_s_str = str(ac_agent_s)

    def finish(self):
        disc_rewards_n = self.comp_disc_rewards(self.ac_agent_n_rewards)
        disc_rewards_s = self.comp_disc_rewards(self.ac_agent_s_rewards)
        self.build_losses(self.ac_agent_n_action_infos, disc_rewards_n)
        self.build_losses(self.ac_agent_s_action_infos, disc_rewards_s)
        self.build_loss()
        self.update_weights()

    def log(self, start_time: float, logger: logging.Logger):
        """
        reference:

        :return:
        """
        global DELIM
        super().log(start_time, logger)
        reward_n = sum(self.ac_agent_n_rewards)
        reward_s = sum(self.ac_agent_s_rewards)
        # log results
        time_elapsed = time.time() - start_time
        logger.info('episode {}'.format(self.epi_num))
        logger.info('player:{}\treward_total: {:.2f}\treward_avg: {:.2f}'
                    .format(self.ac_agent_n_str, reward_n,
                            reward_n / len(self.ac_agent_n_rewards)))
        logger.info('player:{}\treward_total: {:.2f}\treward_avg: {:.2f}'
                    .format(self.ac_agent_s_str, reward_s,
                            reward_s / len(self.ac_agent_s_rewards)))
        logger.info("time elapsed:" + str(time_elapsed))
        logger.info(DELIM)


@dataclass
class Result:
    draw: bool
    win_score: int  # should always be positive
    winner: Union[Agent, ACAgent, None]
    loser: Union[Agent, ACAgent, None]
    board: Board


class KalahEnv:
    def __init__(self, board: Board, agent_s: Agent, agent_n: Agent):
        self.board = board
        self.agent_s: Union[Agent, ACAgent] = agent_s
        self.agent_n: Union[Agent, ACAgent] = agent_n
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
                turn_agent = self.agent_s
                self.update_env(turn_agent)
                self.raise_triggers(turn_agent)
            elif self.env_state == KalahEnvState.NORTH_TURN:
                turn_agent = self.agent_n
                self.update_env(turn_agent)
                self.raise_triggers(turn_agent)
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

    def update_env(self, turn_agent: Agent) -> int:
        """
        this should not change any signals, whatsoever.
        :param turn_agent:
        :return:
        """
        if self.board.seeds != 98:
            print("########")
            print(self.board)
            print("########")
            raise ValueError("Should be 98 but was: " + str(self.board.seeds))

        if not turn_agent.action_is_registered():
            raise ValueError("Action should have been registered, but it is not.")
        # have to commit & agent action before execute action (due to swap)
        if turn_agent.action == Action.SWAP:
            env_state, seeds_added_to_store = self.execute_swap()
        else:
            env_state, seeds_added_to_store = self.execute_move(turn_agent.action, turn_agent.board,
                                                                turn_agent.side, turn_agent.state)
        self.env_state = env_state
        return seeds_added_to_store

    def agent(self, side: Side):
        if side == Side.NORTH:
            return self.agent_n
        elif side == Side.SOUTH:
            return self.agent_s
        else:
            raise ValueError

    def raise_triggers(self, turn_agent: Agent):
        # first, must commit the action taken
        turn_agent_src_state = turn_agent.state
        turn_agent_action = turn_agent.action
        turn_agent.commit_action()  # if the action was SWAP, this will swap the side.
        turn_agent.unregister_action()

        if turn_agent_src_state == AgentState.MAKE_MOVE_OR_SWAP:
            opp_agent = self.agent(turn_agent.side.opposite())
            if turn_agent_action == Action.SWAP:
                opp_agent.opp_swap()  # this will register an action
            else:
                opp_agent.opp_no_swap()  # this will swap the side.
                self.notify_state()
        else:
            self.notify_state()

    def notify_state(self):
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

    def execute_swap(self) -> Tuple[KalahEnvState, int]:
        # the agent trying to swap must be the north agent.
        # now swap the agents
        self.agent_n, self.agent_s = self.agent_s, self.agent_n
        seeds_added_to_store = 0
        return KalahEnvState.NORTH_TURN, seeds_added_to_store

    @staticmethod
    def execute_move(action: Action, board: Board, side: Side, agent_state: AgentState) -> Tuple[KalahEnvState, int]:
        """
        :param: side: the current side of the agent
        :return: state, reward and done.
        """
        hole = action.value

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
        if sow_hole == 0 and agent_state != AgentState.DECIDE_ON_1ST_MOVE:
            if side == Side.SOUTH:
                return KalahEnvState.SOUTH_TURN, seeds_added_to_store
            else:
                return KalahEnvState.NORTH_TURN, seeds_added_to_store
        else:
            if side == Side.SOUTH:
                return KalahEnvState.NORTH_TURN, seeds_added_to_store
            else:
                return KalahEnvState.SOUTH_TURN, seeds_added_to_store

    def render(self):
        """
        this is only needed if we want to visualise the environment changing as the agent plays out the game
        :return:
        """
        print(self.board)


class ACKalahEnv(KalahEnv):

    def __init__(self, board: Board,
                 agent_s: Union[Agent, ACAgent], agent_n: Union[Agent, ACAgent],
                 h_params: HyperParams):
        super().__init__(board, agent_s, agent_n)
        self.h_params = h_params
        self.game_res: Optional[Result] = None

    def play_game(self):
        super().play_game()
        self.build_game_res()
        # after the game ends, reward the winner and penalise the loser
        self.reward_and_penalise(self.game_res)

    def build_game_res(self):
        """
        returns a reference to the winner agent, with the score. (offset)
        """
        if self.env_state != KalahEnvState.GAME_ENDS:  # error handling.
            raise ValueError("The game should have ended, but it has not.")

        south_offset = self.board.store_offset(self.agent_s.side)
        if south_offset > 0:
            # south is the winner
            self.game_res = Result(draw=False, winner=self.agent_s,
                                   loser=self.agent_n, win_score=south_offset,
                                   board=self.board)
        elif south_offset < 0:
            # north is the winner
            self.game_res = Result(draw=False, winner=self.agent_n,
                                   loser=self.agent_s, win_score=(-1 * south_offset),
                                   board=self.board)
        else:
            # game ended in a draw
            self.game_res = Result(draw=True, winner=None, loser=None, win_score=0,
                                   board=self.board)

    # should be implemented
    def reward_and_penalise(self, game_res: Result):
        raise NotImplementedError

    def reset(self):
        """
        resets the game environment.
        """
        # make sure you clear the buffers
        super().reset()
        self.game_res = None
        self.reset_buffers()

    def reset_buffers(self):
        raise NotImplementedError

    def episode(self, epi_num: int, optimizer: torch.optim.Optimizer) -> Episode:
        raise NotImplementedError

    # ----- reward: every move  -------- #
    def reward(self, side: Side, new_seeds: int) -> float:
        """
        return new_seeds_w * new seeds + offset_w * offset(side)
        """
        # note: the rewards must be non-negative
        offset = self.board.store_offset(side)
        if offset > 0:
            reward = new_seeds + offset
        else:
            reward = new_seeds
        return reward

    # ----- reward: won the game / lost the game  ---- #
    def reward_winner(self, winner: ACAgent, win_score: int):
        for idx, reward in enumerate(winner.reward_buffer):
            # increase the rewards by x %, which is proportional to win_score %
            winner.reward_buffer[idx] = reward * (1 + (win_score / self.board.seeds)) + self.h_params.win_bonus

    def penalise_loser(self, loser: ACAgent, win_score: int):
        for idx, reward in enumerate(loser.reward_buffer):
            # decrease the rewards by x %
            loser.reward_buffer[idx] = reward * (1 - (win_score / self.board.seeds))

    def update_env(self, turn_agent: ACAgent):
        """
        orders the given agent to commit an action.
        :param turn_agent:
        :return:
        """
        seeds_added_to_store = super().update_env(turn_agent)
        reward = self.reward(turn_agent.side, seeds_added_to_store)
        turn_agent.reward_buffer.append(reward)


class ACOppKalahEnv(ACKalahEnv):

    def __init__(self, board: Board, ac_agent: ACAgent, opp_agent: Agent,
                 ac_is_south: bool, h_params: HyperParams):
        if ac_is_south:
            super().__init__(board, agent_s=ac_agent, agent_n=opp_agent, h_params=h_params)
        else:
            super().__init__(board, agent_s=opp_agent, agent_n=ac_agent, h_params=h_params)
        self.ac_agent = ac_agent  # maintains a reference to ac_agent
        self.opp_agent = opp_agent

    def reward_and_penalise(self, game_res: Result):
        """
        reward the winner, penalise the loser, and penalise both
        if the game ended in draw.
        :return:
        """
        # get the result of the game..
        if not game_res.draw:  # there was a winner (not a draw).
            if self.ac_agent == game_res.winner:
                # ac_agent has won
                self.reward_winner(self.ac_agent, game_res.win_score)
            else:
                # ac agent has lost
                self.penalise_loser(self.ac_agent, game_res.win_score)
        else:  # the game ended in a draw
            # penalise both agents, as if they were both losers
            self.penalise_loser(self.ac_agent, game_res.win_score)

    def reset_buffers(self):
        # we just have one buffer to be cleared
        self.ac_agent.clear_buffers()

    def episode(self, epi_num: int, optimizer: torch.optim.Optimizer) -> OppEpisode:
        return OppEpisode(self.ac_agent, self.opp_agent,
                          epi_num, self.h_params, optimizer, self.game_res)


class ACSelfKalahEnv(ACKalahEnv):

    def __init__(self, board: Board, agent_s: ACAgent, agent_n: ACAgent, h_params: HyperParams):
        """
        :param agent_s: the agent who will play on the south side of the board
        :param agent_n: the agent who will play on the north side of the board
        """
        super().__init__(board, agent_s, agent_n, h_params)

    def reset_buffers(self):
        # we have two buffers to be cleared
        self.agent_n.clear_buffers()
        self.agent_s.clear_buffers()

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

    def episode(self, epi_num: int, optimizer: torch.optim.Optimizer) -> SelfEpisode:
        return SelfEpisode(self.agent_n, self.agent_s,
                           epi_num, self.h_params, optimizer, self.game_res)
