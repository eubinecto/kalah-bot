import socket
import time
# code reference: https://stackoverflow.com/questions/1908878/netcat-implementation-in-python

HOST = 'localhost'
PORT = 12345
# 1 byte = 1 character.
BUFF_SIZE = 100


def main():
    global HOST, PORT, BUFF_SIZE
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    # become a server socket
    # Finally, the argument to listen tells the socket library that we want it to queue up as many as
    # 5 connect requests (the normal max) before refusing outside connections.
    # If the rest of the code is written properly, that should be plenty.
    server_socket.listen(5)
    # now that we have a server socket prepared, we can enter the
    # main loop of the server
    while True:
        # accept connections from outside
        # this socket.accept() won't terminate until it accepts any connection
        # from outside.
        print("attempting to accept any connection...")
        client_socket, address = server_socket.accept()
        if client_socket:
            print(client_socket.recvmsg(BUFF_SIZE))


if __name__ == '__main__':
    main()
