import socket


def listen_reader(host, port):
    """ Open specified port and return file-like object """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # set SOL_SOCKET.SO_REUSEADDR=1 to reuse the socket if
    # needed later without waiting for timeout (after it is
    # closed, for example)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((host, port))
    sock.listen(0)  # do not queue connections
    request, addr = sock.accept()
    return request.makefile('r', 0)


if __name__ == '__main__':
    HOST = 'localhost'
    PORT = 8000
    print("Start")
    for line in listen_reader(HOST, PORT):
        print(line)
