from pathlib import Path
# the root directory of this project
# define the directories here
from os import path
import logging

from datetime import datetime


def now() -> str:
    now_obj = datetime.now()
    return now_obj.strftime("%d_%m_%Y__%H_%M_%S")


# hostname and port number to host the server socket (default values)
HOST = 'localhost'
PORT = 12346


ROOT_DIR = Path(__file__).resolve().parent
DATA_DIR = path.join(ROOT_DIR, "data")
LOGS_DIR = path.join(DATA_DIR, "logs")
MODELS_DIR = path.join(DATA_DIR, "models")

now_str = now()  # for storing every logs possible
# paths to models
TRAIN_SELF_STATE_DICT = path.join(MODELS_DIR, "ac_train_self_{}.pkl".format(now_str))
TRAIN_RANDOM_STATE_DICT = path.join(MODELS_DIR, "ac_train_random_{}.pkl".format(now_str))
TRAIN_MINIMAX_STATE_DICT = path.join(MODELS_DIR, "ac_train_minimax_{}.pkl".format(now_str))

# paths to models
TRAIN_SELF_LOG = path.join(LOGS_DIR, "ac_train_self_{}.log".format(now_str))
TRAIN_RANDOM_LOG = path.join(LOGS_DIR, "ac_train_random_{}.log".format(now_str))
TRAIN_MINIMAX_LOG = path.join(LOGS_DIR, "ac_train_minimax_{}.log".format(now_str))

# instantiate loggers
train_self_logger = logging.getLogger("train_self")
train_random_logger = logging.getLogger("train_random")
train_minimax_logger = logging.getLogger("train_minimax")


# # for minimax
# fh_minimax = logging.FileHandler(TRAIN_MINIMAX_LOG)
# fh_minimax.setLevel(logging.DEBUG)
# train_minimax_logger.addHandler(fh_minimax)