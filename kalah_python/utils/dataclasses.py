from dataclasses import dataclass

import torch

from kalah_python.utils.enums import Action


@dataclass
class SavedAction:
    logit: torch.Tensor
    prob: torch.Tensor
    critique: torch.Tensor
    action: Action


# hyper parameters for actor-critic
@dataclass
class HyperParams:
    NUM_EPISODES: int = 1500
    OFFSET_W: float = 0.70  # weight for the offset reward after each move
    NEW_SEEDS_W: float = 0.70
    WIN_BONUS: int = 10
    DISCOUNT_FACTOR: float = 0.90  # (gamma)
    LEARNING_RATE: float = 3e-2  # for optimizer
