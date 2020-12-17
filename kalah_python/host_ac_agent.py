from kalah_python.utils.ac import ActorCritic
from kalah_python.utils.agents import ACAgent
from kalah_python.utils.board import Board
from kalah_python.utils.enums import Action
from kalah_python.utils.server import Server
from kalah_python.config import HOST, PORT
import torch
import argparse


def main():
    parser = argparse.ArgumentParser()
    # e.g. ./data/models/ac_train_self_15_12_2020__16_41_26.pkl
    parser.add_argument("model_path", type=str)  # positional
    # optional args
    parser.add_argument("--host", default=HOST, type=str)
    parser.add_argument("--port", default=PORT, type=int)
    parser.add_argument("--listen_forever", default=False, type=bool)

    args = parser.parse_args()
    model_path = args.model_path
    # load a pretrained model, and host.
    ac_model = ActorCritic(state_size=Board.STATE_SIZE, action_size=len(Action))
    ac_model.load_state_dict(torch.load(model_path))
    server = Server(agent=ACAgent(ac_model, buffer=False),
                    listen_forever=args.listen_forever)
    server.start_hosting(host=args.host, port=args.port)


if __name__ == '__main__':
    main()
