from dataclasses import dataclass
from pathlib import Path
# the root directory of this project
# define the directories here
from os import path
ROOT_DIR = Path(__file__).resolve().parent
DATA_DIR = path.join(ROOT_DIR, "data")
AC_MODEL_PKL_PATH = path.join(DATA_DIR, "ac_model.pkl")

# hostname and port number to host the server socket
HOST = 'localhost'
PORT = 12345


# hyper parameters for actor-critic
@dataclass
class HyperParams:
    NUM_EPISODES: int = 1000
    OFFSET_W: float = 0.60
    NEW_SEEDS_W: float = 1 - OFFSET_W
    BONUS_W: float = 0.80
    BONUS_VALUE: float = 1000
    DISCOUNT_FACTOR: float = 0.99
    LEARNING_RATE: float = 3e-2
