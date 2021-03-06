from kalah_python.utils.agents import UserAgent
from kalah_python.utils.server import Server
from kalah_python.config import HOST, PORT
import argparse


def main():
    parser = argparse.ArgumentParser()
    # optional args
    parser.add_argument("--host", default=HOST, type=str)
    parser.add_argument("--port", default=PORT, type=int)
    parser.add_argument("--listen_forever", dest='listen_forever', default=False, action='store_true')
    args = parser.parse_args()
    server = Server(agent=UserAgent(), listen_forever=args.listen_forever)
    server.start_hosting(host=args.host, port=args.port)


if __name__ == '__main__':
    main()
