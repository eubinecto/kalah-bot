from dataclasses import dataclass
from typing import Optional, Callable, List, Tuple

import numpy as np
from torch.distributions import Categorical
from functools import lru_cache

from kalah_python.utils.ac import ActorCritic
from kalah_python.utils.board import Board, Side
from transitions import Machine
from enum import Enum, auto
from overrides import overrides
import random
from torch import Tensor
import torch
import copy


class Action(Enum):
    # all possible moves are defined here.
    MOVE_1ST_WELL = 1
    MOVE_2ND_WELL = 2
    MOVE_3RD_WELL = 3
    MOVE_4TH_WELL = 4
    MOVE_5TH_WELL = 5
    MOVE_6TH_WELL = 6
    MOVE_7TH_WELL = 7
    SWAP = 's'  # this is not a number

    @staticmethod
    def all_actions() -> List['Action']:
        """
        just get all the possible actions.
        Note that they are ordered.
        :return:
        """
        return list(Action)

    @staticmethod
    def move_actions() -> List['Action']:
        """
        :return: Only the move actions. (Everything but SWAP action)
        """
        return [
            action
            for action in Action
            if action != Action.SWAP  # everything but swap
        ]

    def to_cmd(self):
        if self == Action.SWAP:
            # command for swap action
            cmd = "SWAP\n".encode('utf8')
        else:
            # command for move action
            cmd = "MOVE;{}\n".format(self.value).encode('utf8')
        return cmd

    @overrides
    def __str__(self) -> str:
        if self != Action.SWAP:
            msg = "MOVE;{}".format(self.value)
        else:
            msg = "SWAP"
        return msg


@dataclass
class SavedAction:
    logit: float  # log probability of this action
    critique: float  # the critique score on the states generated by Critic.
    action: Action


class Agent(object):
    class State(Enum):
        INIT = auto()
        DECIDE_ON_1ST_MOVE = auto()
        WAIT_FOR_MOVE_RESULT = auto()
        WAIT_FOR_1ST_MOVE = auto()
        MAKE_MOVE_OR_SWAP = auto()
        WAIT_FOR_SWAP_DECISION = auto()
        DECIDE_ON_MOVE = auto()
        WAIT_FOR_GAME_STATE = auto()
        FINISHED = auto()
        # make sure this state is the last one.
        EXIT = auto()

    # trigger, source, dest
    TRANSITIONS = [
        ['new_match_1st', State.INIT, State.DECIDE_ON_1ST_MOVE],
        ['new_match_2nd', State.INIT, State.WAIT_FOR_1ST_MOVE],
        ['moves', State.DECIDE_ON_1ST_MOVE, State.WAIT_FOR_MOVE_RESULT],
        ['moves', State.MAKE_MOVE_OR_SWAP, State.WAIT_FOR_GAME_STATE],
        ['moves', State.DECIDE_ON_MOVE, State.WAIT_FOR_GAME_STATE],
        ['swaps', State.MAKE_MOVE_OR_SWAP, State.WAIT_FOR_GAME_STATE],
        ['game_state_is_opp', State.WAIT_FOR_SWAP_DECISION, State.WAIT_FOR_GAME_STATE],
        ['game_state_is_opp', State.WAIT_FOR_MOVE_RESULT, State.WAIT_FOR_SWAP_DECISION],
        ['game_state_is_opp', State.WAIT_FOR_GAME_STATE, "="],  # reflexive trigger
        ['game_state_is_you', State.WAIT_FOR_SWAP_DECISION, State.DECIDE_ON_MOVE],
        ['game_state_is_you', State.WAIT_FOR_1ST_MOVE, State.MAKE_MOVE_OR_SWAP],
        ['game_state_is_you', State.WAIT_FOR_GAME_STATE, State.DECIDE_ON_MOVE],
        ['game_state_is_end', State.WAIT_FOR_GAME_STATE, State.FINISHED],
        # from all states.
        ['game_over', '*', State.EXIT],
        ['reset', '*', State.INIT]
    ]

    # triggers. Just class-level type hints for dynamically added attrs
    # https://stackoverflow.com/a/49052572
    new_match_1st: Callable
    new_match_2nd: Callable
    moves: Callable
    swaps: Callable
    game_state_is_opp: Callable
    game_state_is_you: Callable
    game_state_is_end: Callable
    game_over: Callable
    reset: Callable  # this trigger is to be used by KalahEnv.

    # state attribute will be accessible
    state: State

    def __init__(self, board: Board = None):
        # an agent maintains an up-to-date board,
        # the current state of the agent,
        # and the current turn.
        self.board: Board = Board() if not board else board
        self.machine = Machine(model=self, states=Agent.State,
                               transitions=Agent.TRANSITIONS, initial=Agent.State.INIT)
        self.side: Optional[Side] = None
        self.action: Optional[Action] = None

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
        if self.state == Agent.State.MAKE_MOVE_OR_SWAP:
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
        # and unregister the action
        if self.action in Action.move_actions():
            self.moves()
        elif self.action == Action.SWAP:
            self.swap_side()  # first swap side
            self.swaps()  # then trigger
        else:
            raise ValueError("Invalid registered action:" + str(self.action))

    def swap_side(self):
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
        print("------- game is finished --------")
        print(self.board)

    def on_enter_EXIT(self):
        print("------- game was aborted --------")
        print(self.board)


# subclasses of the Agent class.
class RandomAgent(Agent):
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
        action = random.choice(possible_actions)
        print("random action: " + str(action))
        return action


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

    capture_value = 0
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
        # TODO  Have a method to calculate the value

        if capture_flag or last_seed_in_store:
            if capture_flag:
                capture_value = 25
            else:
                capture_value = 15
        node.value = 0.25 * board.store_offset(node.player) + 0.8 * capture_value + seeds_added_to_store
        node.value += 0.3 * board.get_hoard_side_value(node.player)
        if action.value < 4:
            node.value += 2
        if side == Side.SOUTH:
            node.value -= 0.1 * board.store(Side.NORTH)
        else:
            node.value -= 0.1 * board.store(Side.SOUTH)
        node.is_over = True
        actions = [
            Action(value=nonzero_hole_idx)
            for nonzero_hole_idx in board.nonzero_holes(node.player)
        ]
        node.moves = actions
        return node

    # TODO Use the value method here as well
    node.board = board

    number_of_rocks_on_side = 0
    if capture_flag or last_seed_in_store:
        capture_value = 20
    if sow_side == Side.SOUTH:
        for hole in node.board.south_holes:
            number_of_rocks_on_side = number_of_rocks_on_side + int(hole)
    else:
        for hole in node.board.north_holes:
            number_of_rocks_on_side = number_of_rocks_on_side + int(hole)

    if capture_flag or last_seed_in_store:
        capture_value = 20
    node.value = 0.25 * board.store_offset(node.player) + 0.8 * capture_value + seeds_added_to_store
    node.value += 0.3 * board.get_hoard_side_value(node.player)
    if action.value < 4:
        node.value += 2
    if side == Side.SOUTH:
        node.value -= 0.1 * board.store(Side.NORTH)
    else:
        node.value -= 0.1 * board.store(Side.SOUTH)


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


class MiniMaxAgent(Agent):

    @lru_cache()
    def choose_mini_max_move(self, gnode, max_depth=3, alpha = -9999.0, beta = 9999):
        "Choose bestMove for gnode along w final value"
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
        print("------decide_on_action----")
        print("It is your turn:")
        print(self.board)
        print("-------DEV------------")
        print("Your side is:")
        print(self.side)
        root = GameNode(self.board, self.side, possible_actions)
        root.best_move = Action.SWAP
        returned_state = self.choose_mini_max_move(root)
        print(returned_state)
        print(root)
        print("-------END------------")

        return returned_state.best_move


class ACAgent(Agent):
    """
    Actor-Critic agent.
    """

    @overrides
    def __init__(self, ac_model: ActorCritic, board: Board = None):
        super(ACAgent, self).__init__(board=board)
        self.ac_model: ActorCritic = ac_model
        # buffers to be used for.. backprop
        self.saved_action_buffer: List[SavedAction] = list()
        self.reward_buffer: List[float] = list()

    @overrides
    def decide_on_action(self, possible_actions: List[Action], buffer: bool = False) -> Action:
        """
        :param possible_actions:
        :param buffer: True: save actions & rewards to the buffer.
        :return:
        """
        # load the pretrained model from data. (<1GB)
        action_mask = ACAgent.action_mask(possible_actions)
        # get the probabilities for each action.
        x = torch.tensor(self.board.board_flat, dtype=torch.float32)
        action_mask = torch.tensor(action_mask, dtype=torch.float32)
        action_probs, state_eval = self.ac_model.forward(x, action_mask)
        action, logit = ACAgent.sample_action(action_probs)
        self.saved_action_buffer.append(SavedAction(logit, state_eval.item(), action))
        # sample an action according to the prob distribution.
        return action

    @staticmethod
    def sample_action(action_probs: Tensor) -> Tuple[Action, float]:
        m = Categorical(action_probs)
        # sample an index to an action (an index to action_probs)
        action = m.sample()
        return Action(value=action.item() + 1), m.log_prob(action)

    @staticmethod
    def action_mask(possible_actions: List[Action]) -> np.ndarray:
        """
        :param possible_actions:
        :return:
        """
        all_actions = Action.all_actions()
        return np.array([
            # if the action is possible, set the value as 1. if not, set
            # the value as 0.
            1 if action in possible_actions else 0
            for action in all_actions
        ])

    def clear_buffers(self):
        self.reward_buffer.clear()
        self.saved_action_buffer.clear()
