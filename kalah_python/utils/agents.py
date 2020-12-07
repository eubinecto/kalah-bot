from typing import Optional, Callable, List

import numpy as np
from torch.distributions import Categorical

from kalah_python.utils.ac import ActorCritic
from kalah_python.utils.board import Board, Side
from transitions import Machine
from enum import Enum, auto
from overrides import overrides
import random
from torch import from_numpy, Tensor


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


class ACAgent(Agent):
    """
    Actor-Critic agent.
    """

    @overrides
    def __init__(self, ac_model: ActorCritic, board: Board = None):
        super(ACAgent, self).__init__(board=board)
        self.ac_model: ActorCritic = ac_model

    @overrides
    def decide_on_action(self, possible_actions: List[Action]) -> Action:
        """
        :param possible_actions:
        :return:
        """
        # load the pretrained model from data. (<1GB)
        action_mask = ACAgent.action_mask(possible_actions)
        # get the probabilities for each action.
        action_probs, _ = self.ac_model.forward(x=from_numpy(self.board.board_flat),
                                                action_mask=from_numpy(action_mask))
        # sample an action according to the prob distribution.
        return ACAgent.sample_action(action_probs)

    @staticmethod
    def sample_action(action_probs: Tensor):
        cat_dist = Categorical(action_probs)
        # sample an index to an action (an index to action_probs)
        action_idx: int = cat_dist.sample().item()
        return Action(value=action_idx + 1)

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
