from kalah_python.utils.ac import ActorCritic
from kalah_python.utils.agents import ACAgent
from kalah_python.utils.board import Board
from kalah_python.utils.server import Server
from config import HOST, PORT, AC_MODEL_STATE_DICT_PATH
import torch


def main():
    # load a pretrained model, and host.
    from kalah_python.utils.enums import Action
    ac_model = ActorCritic(state_size=Board().board_size, action_size=len(Action))
    ac_model.load_state_dict(torch.load(AC_MODEL_STATE_DICT_PATH))
    server = Server(agent=ACAgent(ac_model, buffer=False))
    server.start_hosting(host=HOST, port=PORT)


if __name__ == '__main__':
    main()
