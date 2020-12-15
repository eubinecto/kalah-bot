from pathlib import Path
# the root directory of this project
# define the directories here
from os import path
import logging

ROOT_DIR = Path(__file__).resolve().parent
DATA_DIR = path.join(ROOT_DIR, "data")
AC_MODEL_STATE_DICT_PATH = path.join(DATA_DIR, "ac_model.pkl")
TRAIN_LOG = path.join(DATA_DIR, "ac_train.log")
# hostname and port number to host the server socket
HOST = 'localhost'
PORT = 12346


# create logger with 'spam_application'
train_logger = logging.getLogger('train_ac')
train_logger.setLevel(logging.INFO)
# create file handler which logs even debug messages
fh = logging.FileHandler(TRAIN_LOG)
fh.setLevel(logging.DEBUG)
train_logger.addHandler(fh)
