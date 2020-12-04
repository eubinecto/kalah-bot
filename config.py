
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
