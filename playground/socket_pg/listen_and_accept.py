import socket
from config import HOST, PORT

# 1 byte = 1 character, so 100 should be enough.
BUFF_SIZE = 100


def main():
    global BUFF_SIZE
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
            # https://docs.python.org/3.8/library/socket.html#socket.socket.recvmsg
            # The return value of socket.recvmsg() is a 4-tuple: (data, ancdata, msg_flags, address).
            # The data is the message
            data, ancdata, _, _ = client_socket.recvmsg(BUFF_SIZE)
            print(str(data))


if __name__ == '__main__':
    main()
