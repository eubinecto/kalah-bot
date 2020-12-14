from typing import Optional, Callable, List, Tuple
import numpy as np
from torch.distributions import Categorical
from kalah_python.utils.ac import ActorCritic
from kalah_python.utils.board import Board, Side
from transitions import Machine
from overrides import overrides
import random
import torch
from kalah_python.utils.dataclasses import SavedAction
from kalah_python.utils.enums import AgentState, Action
import logging
logger = logging.getLogger("transitions.core")
logger.setLevel(logging.WARN)


class Agent(object):
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

    def __init__(self, board: Board = None):
        # an agent maintains an up-to-date board,
        # the current state of the agent,
        # and the current turn.
        self.board: Board = Board() if not board else board
        self.machine = Machine(model=self, states=AgentState,
                               transitions=Agent.TRANSITIONS, initial=AgentState.INIT)
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
        # and unregister the action
        if self.action in Action.move_actions():
            self.moves()
        elif self.action == Action.SWAP:
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
    def __init__(self, ac_model: ActorCritic, board: Board = None, buffer: bool = True):
        """
        :param ac_model:
        :param board:
        :param buffer: True: save actions & rewards to the buffer. Set this True if you are training,
        False otherwise.
        """
        super(ACAgent, self).__init__(board=board)
        self.ac_model: ActorCritic = ac_model
        # buffers to be used for.. backprop
        self.saved_action_buffer: List[SavedAction] = list()
        self.reward_buffer: List[float] = list()
        self.buffer = buffer

    @overrides
    def decide_on_action(self, possible_actions: List[Action]) -> Action:
        """
        :param possible_actions:
        :return:
        """
        print("------decide on action------")
        print(self.board)
        print("side:" + str(self.side))
        # load the pretrained model from data. (<1GB)
        action_mask = self.action_mask(possible_actions)
        states = torch.tensor(self.board.board_flat(self.side), dtype=torch.float32)  # board (flattened) representation
        action_mask = torch.tensor(action_mask, dtype=torch.float32)  # mask impossible actions
        probs, critique = self.ac_model.forward(states, action_mask)  # prob. dist over the actions, critique on states
        action, logit, prob = self.sample_action(probs)
        if self.buffer:
            self.saved_action_buffer.append(SavedAction(logit, prob, critique, action))
        # sample an action according to the prob distribution.
        print("next action:" + str(action))
        return action

    @staticmethod
    def sample_action(action_probs: torch.Tensor) -> Tuple[Action, torch.Tensor, torch.Tensor]:
        m = Categorical(action_probs)
        # sample an index to an action (an index to action_probs)
        action: torch.Tensor = m.sample()
        if action.item() == 7:
            value = -1
        else:
            value = action.item() + 1
        # log_prob is a tensor.
        return Action(value), m.log_prob(action), m.probs[action]

    @staticmethod
    def action_mask(possible_actions: List[Action]) -> np.ndarray:
        """
        :param possible_actions:
        :return:
        """
        all_actions = Action.all_actions()
        return np.array([
            # if the action is possible, set the value to 1. if not, set
            # the value to 0.
            1 if action in possible_actions else 0
            for action in all_actions
        ])

    def clear_buffers(self):
        del self.reward_buffer[:]
        del self.saved_action_buffer[:]

    def __str__(self) -> str:
        return str(self.side)
