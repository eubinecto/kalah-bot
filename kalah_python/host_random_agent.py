from kalah_python.utils.agents import RandomAgent
from kalah_python.utils.server import Server
from config import HOST, PORT


def main():
    server = Server(agent=RandomAgent())
    server.start_hosting(host=HOST, port=PORT)


if __name__ == '__main__':
    main()
