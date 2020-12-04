from kalah_python.utils.agents import UserAgent
from kalah_python.utils.server import Server
from config import HOST, PORT


def main():
    server = Server(agent=UserAgent())
    server.start_hosting(host=HOST, port=PORT)


if __name__ == '__main__':
    main()
