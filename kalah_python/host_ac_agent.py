from kalah_python.utils.agents import ACAgent
from kalah_python.utils.server import Server
from config import HOST, PORT, AC_MODEL_PKL_PATH
import torch


def main():
    # load a pretrained model, and host.
    ac_model = torch.load(AC_MODEL_PKL_PATH)
    server = Server(agent=ACAgent(ac_model))
    server.start_hosting(host=HOST, port=PORT)


if __name__ == '__main__':
    main()
