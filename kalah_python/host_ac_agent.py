from kalah_python.utils.ac import ActorCritic
from kalah_python.utils.agents import ACAgent
from kalah_python.utils.board import Board
from kalah_python.utils.server import Server
from kalah_python.config import HOST, PORT, TRAIN_SELF_STATE_DICT
import torch


def main():
    # load a pretrained model, and host.
    from kalah_python.utils.enums import Action
    ac_model = ActorCritic(state_size=Board.STATE_SIZE, action_size=len(Action))
    ac_model.load_state_dict(torch.load(TRAIN_SELF_STATE_DICT))
    server = Server(agent=ACAgent(ac_model, buffer=False))
    server.start_hosting(host=HOST, port=PORT)


if __name__ == '__main__':
    main()
