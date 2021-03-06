import copy
from functools import lru_cache
from typing import Optional, Callable, List
import numpy as np

from kalah_python.utils.board import Board, Side
from transitions import Machine
from overrides import overrides
import random

from kalah_python.utils.enums import AgentState, Action
import logging

# only used for RL.
# from torch.distributions import Categorical
# from kalah_python.utils.ac import ActorCritic
# import torch
# from kalah_python.utils.dataclasses import ActionInfo
from typing import Tuple

logger = logging.getLogger("transitions.core")
logger.setLevel(logging.WARN)


class Agent:
    # trigger, source, dest
    TRANSITIONS = [
        ['new_match_1st', AgentState.INIT, AgentState.DECIDE_ON_1ST_MOVE],
        ['new_match_2nd', AgentState.INIT, AgentState.WAIT_FOR_1ST_MOVE],
        ['moves', AgentState.DECIDE_ON_1ST_MOVE, AgentState.WAIT_FOR_MOVE_RESULT],
        ['moves', AgentState.MAKE_MOVE_OR_SWAP, AgentState.WAIT_FOR_GAME_STATE],
        ['moves', AgentState.DECIDE_ON_MOVE, AgentState.WAIT_FOR_GAME_STATE],
        ['swaps', AgentState.MAKE_MOVE_OR_SWAP, AgentState.WAIT_FOR_GAME_STATE],
        ['opp_no_swap', AgentState.WAIT_FOR_SWAP_DECISION, AgentState.WAIT_FOR_GAME_STATE],
        ['game_state_is_opp', AgentState.WAIT_FOR_MOVE_RESULT, AgentState.WAIT_FOR_SWAP_DECISION],
        ['game_state_is_opp', AgentState.WAIT_FOR_GAME_STATE, "="],  # reflexive trigger
        {
            'trigger': 'opp_swap',
            'source': AgentState.WAIT_FOR_SWAP_DECISION,
            'dest': AgentState.DECIDE_ON_MOVE,
            'before': 'swap_side'
        },
        ['game_state_is_you', AgentState.WAIT_FOR_1ST_MOVE, AgentState.MAKE_MOVE_OR_SWAP],
        ['game_state_is_you', AgentState.WAIT_FOR_GAME_STATE, AgentState.DECIDE_ON_MOVE],
        ['game_state_is_end', AgentState.WAIT_FOR_GAME_STATE, AgentState.FINISHED],
        # trigger from all states.
        ['game_over', '*', AgentState.EXIT],
        ['reset', '*', AgentState.INIT]
    ]

    # triggers. Just class-level type hints for dynamically added attrs
    # https://stackoverflow.com/a/49052572
    new_match_1st: Callable
    new_match_2nd: Callable
    moves: Callable
    swaps: Callable
    opp_swap: Callable
    opp_no_swap: Callable
    game_state_is_opp: Callable
    game_state_is_you: Callable
    game_state_is_end: Callable
    game_over: Callable
    reset: Callable  # this trigger is to be used by KalahEnv.

    # state attribute will be accessible
    state: AgentState

    def __init__(self, board: Board = None, verbose: bool = True, buffer: bool = True):
        # an agent maintains an up-to-date board,
        # the current state of the agent,
        # and the current turn.
        self.board: Board = Board() if not board else board
        self.machine = Machine(model=self, states=AgentState,
                               transitions=Agent.TRANSITIONS, initial=AgentState.INIT)
        self.side: Optional[Side] = None
        self.action: Optional[Action] = None
        self.verbose: bool = verbose
        self.buffer: bool = buffer
        self.action_buffer: List[Action] = list()
        self.reward_buffer: List[float] = list()

    def decide_on_action(self, possible_actions: List[Action], **kwargs) -> Action:
        """
        To be implemented by subclasses
        :return:
        """
        raise NotImplementedError

    def possible_actions(self) -> List[Action]:
        actions = [
                Action(value=nonzero_hole_idx)
                for nonzero_hole_idx in self.board.nonzero_holes(self.side)
        ]
        if self.state == AgentState.MAKE_MOVE_OR_SWAP:
            actions.append(Action.SWAP)
        return actions

    def action_is_registered(self) -> bool:
        return self.action is not None

    def register_action(self, action: Action):
        if self.action:
            raise ValueError("an action is already registered.")
        self.action = action

    def unregister_action(self):
        if not self.action:
            raise ValueError("an action is supposed to be registered")
        del self.action
        self.action = None

    def commit_action(self):
        if not self.action_is_registered():
            raise ValueError("attempted to commit an action which is not registered")
        if self.buffer:  # store the actions made to the buffer. (for debugging)
            self.action_buffer.append(self.action)
        # and unregister the action
        if self.action in Action.move_actions():
            self.moves()
        elif self.action == Action.SWAP:
            self.swap_side()
            self.swaps()  # then trigger
        else:
            raise ValueError("Invalid registered action:" + str(self.action))

    def swap_side(self):
        print("swapping side")
        if self.side == Side.NORTH:
            self.side = Side.SOUTH
        elif self.side == Side.SOUTH:
            self.side = Side.NORTH
        else:
            raise ValueError("Invalid side:" + str(self.side))

    def on_enter_DECIDE_ON_1ST_MOVE(self):
        # 1st player
        self.side = Side.SOUTH
        # get an action and register
        action = self.decide_on_action(self.possible_actions())
        self.register_action(action)

    def on_enter_WAIT_FOR_1ST_MOVE(self):
        # 2nd player
        self.side = Side.NORTH

    def on_enter_MAKE_MOVE_OR_SWAP(self):
        # get an action and register
        action = self.decide_on_action(self.possible_actions())
        self.register_action(action)

    def on_enter_DECIDE_ON_MOVE(self):
        # get an action and register
        action = self.decide_on_action(self.possible_actions())
        self.register_action(action)

    def on_enter_FINISHED(self):
        if self.verbose:
            print("------- game is finished --------")
            print(self.board)

    def on_enter_EXIT(self):
        if self.verbose:
            print("------- game was aborted --------")
            print(self.board)

    def __str__(self) -> str:
        return "side={}".format(self.side)


# subclasses of the Agent class.
class RandomAgent(Agent):

    def __init__(self, board: Board = None, verbose: bool = True, buffer: bool = True):
        super().__init__(board, verbose, buffer)

    @overrides
    def decide_on_action(self, possible_actions: List[Action]) -> Action:
        """
        :param possible_actions:
        :return:
        """
        action = random.choice(possible_actions)
        if self.verbose:
            print("------decide_on_action----")
            print("It is your turn:")
            print(self.board)
            print("your side:", self.side)
            print("random action: " + str(action))
        return action

    def __str__(self) -> str:
        return "random_agent|" + super().__str__()


class UserAgent(Agent):

    @overrides
    def decide_on_action(self, possible_actions: List[Action]) -> Action:
        """
        :param possible_actions:
        :return:
        """
        print("------decide_on_action----")
        print("It is your turn:")
        print(self.board)
        print("your side:", self.side)
        options = {
            str(action.value): action
            for action in possible_actions
        }
        for option, action in options.items():
            print("[{}]:{}".format(option, str(action)))
        option_key = None
        while not options.get(option_key, None):
            option_key = input("Choose an option:")
        return options[option_key]

    def __str__(self) -> str:
        return "user_agent|" + super().__str__()


# class ACAgent(Agent):
#     """
#     Actor-Critic agent.
#     """
#     @overrides
#     def __init__(self, ac_model: ActorCritic, board: Board = None,
#                  buffer: bool = True, verbose: bool = False):
#         """
#         :param ac_model:
#         :param board:
#         :param buffer: True: save actions & rewards to the buffer. Set this True if you are training,
#         False otherwise.
#         """
#         super(ACAgent, self).__init__(board=board, verbose=verbose, buffer=buffer)
#         self.ac_model: ActorCritic = ac_model
#         # buffers to be used for.. backprop
#         # ac agent maintains an action info buffer, along with action & reward buffers
#         self.action_info_buffer: List[ActionInfo] = list()
#
#     @overrides
#     def decide_on_action(self, possible_actions: List[Action]) -> Action:
#         """
#         :param possible_actions:
#         :return:
#         """
#
#         # load the pretrained model from data. (<1GB)
#         action_mask = self.action_mask(possible_actions)
#         states = torch.tensor(self.board.board_flat(self.side), dtype=torch.float32)  # board (flattened) representation
#         action_mask = torch.tensor(action_mask, dtype=torch.float32)  # mask impossible actions
#         probs, critique = self.ac_model.forward(states, action_mask)  # prob. dist over the actions, critique on states
#         action, logit, prob = self.sample_action(probs)
#         if self.buffer:
#             self.action_info_buffer.append(ActionInfo(logit, prob, critique, action))
#         # sample an action according to the prob distribution.
#         if self.verbose:
#             print("------decide on action------")
#             print(self.board)
#             print("side:" + str(self.side))
#             print("next action:" + str(action))
#         return action
#
#     @staticmethod
#     def sample_action(action_probs: torch.Tensor) -> Tuple[Action, torch.Tensor, torch.Tensor]:
#         m = Categorical(action_probs)
#         # sample an index to an action (an index to action_probs)
#         action: torch.Tensor = m.sample()
#         if action.item() == 7:
#             value = -1
#         else:
#             value = action.item() + 1
#         # log_prob is a tensor.
#         return Action(value), m.log_prob(action), m.probs[action]
#
#     @staticmethod
#     def action_mask(possible_actions: List[Action]) -> np.ndarray:
#         """
#         :param possible_actions:
#         :return:
#         """
#         all_actions = Action.all_actions()
#         return np.array([
#             # if the action is possible, set the value to 1. if not, set
#             # the value to 0.
#             1 if action in possible_actions else 0
#             for action in all_actions
#         ])
#
#     def clear_buffers(self):
#         self.reward_buffer.clear()
#         self.action_info_buffer.clear()
#
#     def __str__(self) -> str:
#         return "ac_agent|" + super().__str__()


class GameNode:

    def __init__(self, board, player, moves=None):
        self.board = board
        self.player = player
        self.depth = 0
        self.moves = moves
        self.next = None
        self.value = 0.0
        self.best_move = None
        self.is_over = False

    # TODO: Update the board and player(side)
    def move(self, move):
        node = self
        simulate_move(self, move, node)
        actions = [
            Action(value=nonzero_hole_idx)
            for nonzero_hole_idx in self.board.nonzero_holes(node.player)
        ]
        self.moves = actions

    def maximizing(self, side):

        if self.player == side:
            return True
        else:
            return False

    def over(self):
        if len(self.moves) < 1:
            self.is_over = True
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
        :return: GameNode.
        """
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
    last_seed_in_store = False
    for extra in reversed(range(1, extra + 1)):
        sow_hole = sow_hole + 1
        if sow_hole == 1:  # last pit was a store sow_side = sow_side.opposite()
            sow_side = sow_side.opposite()
        if sow_hole > holes:
            if sow_side == side:
                sow_hole = 0
                board.add_seeds_to_store(sow_side, 1)
                seeds_added_to_store += 1
                # if the last seed goes it the store than we get another move
                if extra == 1:
                    last_seed_in_store = True
                continue
            else:
                sow_side = sow_side.opposite()
                sow_hole = 1
        board.add_seeds_to_hole(sow_hole, sow_side, 1)

    # capture:
    capture_flag = False
    if sow_side == side \
            and sow_hole > 0 \
            and board.hole(sow_hole, sow_side) == 1 \
            and board.opposite_hole(sow_hole, sow_side) > 0:
        board.add_seeds_to_store(side, 1 + board.opposite_hole(sow_hole, sow_side))
        seeds_added_to_store += 1 + board.opposite_hole(sow_hole, sow_side)
        board.set_hole(sow_hole, side, 0)
        board.set_hole(sow_hole, side.opposite(), 0)
        capture_flag = True

    # game over (game ends)?
    finished_side = None
    if not board.nonzero_holes(side):
        finished_side = side
    elif not board.nonzero_holes(side.opposite()):
        finished_side = side.opposite()

    # capture_value = 0
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

        node.value = evaluate_game_state(board, seeds_added_to_store, capture_flag,
                                         last_seed_in_store, node.player, action)

        node.is_over = True
        actions = [
            Action(value=nonzero_hole_idx)
            for nonzero_hole_idx in board.nonzero_holes(node.player)
        ]
        node.moves = actions
        return node

    node.board = board
    node.value = evaluate_game_state(board, seeds_added_to_store, capture_flag,
                                     last_seed_in_store, node.player, action)

    actions = [
        Action(value=nonzero_hole_idx)
        for nonzero_hole_idx in board.nonzero_holes(node.player)
    ]
    node.moves = actions
    if not capture_flag and not last_seed_in_store:
        if side == Side.SOUTH:
            node.player = side.NORTH
            return node
        else:
            node.player = side.SOUTH
            return node
    else:
        return node


def evaluate_game_state(board, seeds_added_to_store, capturing_move, last_seed_in_store, side, action):
    capture_value = reward_capturing_move(capturing_move, last_seed_in_store)
    score_difference = board.store_offset(side)
    hoard_value = board.get_hoard_side_value(side)
    play_right_holes = reward_playing_pits_closest_to_opponent(action)
    opponent_store = get_opponent_store(board, side)

    return 0.25 * score_difference + 0.8 * capture_value + seeds_added_to_store + 0.3 * hoard_value \
           + play_right_holes - 0.05 * opponent_store


def reward_playing_pits_closest_to_opponent(action):
    if action.value > 4:
        return 2
    else:
        return 0


def get_opponent_store(board, side):
    if side == Side.NORTH:
        return board.store(Side.SOUTH)
    else:
        return board.store(Side.NORTH)


def reward_capturing_move(capturing_move, last_seed_in_store):
    if capturing_move or last_seed_in_store:
        if capturing_move:
            return 20
        else:
            return 18
    else:
        return 0


class MiniMaxAgent(Agent):

    @lru_cache()
    def choose_mini_max_move(self, gnode, max_depth=3, alpha=-9999.0, beta=9999):
        """
        Choose bestMove for gnode along w final value
        """
        if self.verbose:
            print("IN THE MINIMAX FUNCTION WITH GNODE:")
            print(f"DEPTH: {gnode.depth}")
            print(f"Player: {gnode.player}")
            print(f"Value: {gnode.value}")
            print(f"Moves: {gnode.moves}")
            print(f"Board: {gnode.board}")
        if gnode.depth <= max_depth and not gnode.over():
            for move in gnode.moves:
                nxt_gnode = copy.deepcopy(gnode)
                nxt_gnode.depth = gnode.depth + 1
                if self.verbose:
                    print(f"Calling with the Move:{move}")
                nxt_gnode.move(move)
                self.choose_mini_max_move(nxt_gnode, max_depth, alpha, beta)  # recursion here
                keep = (gnode.next is None)  # 1st of sequence
                if gnode.maximizing(self.side):
                    if keep or nxt_gnode.value > gnode.value:
                        max_evaluation = -999.0
                        gnode.value = nxt_gnode.value
                        gnode.next = nxt_gnode
                        gnode.best_move = move
                        max_evaluation = max(max_evaluation, gnode.value)
                        alpha = max(alpha, max_evaluation)
                        if beta <= alpha:
                            break
                else:
                    if keep or nxt_gnode.value < gnode.value:
                        min_evaluation = 999.0
                        gnode.value = nxt_gnode.value
                        gnode.next = nxt_gnode
                        gnode.best_move = move
                        min_evaluation = min(min_evaluation, gnode.value)
                        beta = min(beta, min_evaluation)
                        if beta <= alpha:
                            break
        return gnode

    @overrides
    def decide_on_action(self, possible_actions: List[Action], **kwargs) -> Action:
        """
                :param possible_actions:
                :return:
                """
        if self.verbose:
            print("------decide_on_action----")
            print("It is your turn:")
            print(self.board)
            print("-------DEV------------")
            print("Your side is:")
            print(self.side)
        root = GameNode(self.board, self.side, possible_actions)
        root.best_move = Action.SWAP
        returned_state = self.choose_mini_max_move(root)
        if self.verbose:
            print(returned_state)
            print(root)
            print("-------END------------")

        return returned_state.best_move
