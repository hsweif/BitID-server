import argparse
import socket
import threading
import queue


class TagReader(threading.Thread):
    def __init__(self, stop_event, host, port, buf_size=512):
        threading.Thread.__init__(self)
        self.host = host
        self.port = port
        self.stopped = stop_event
        self.buf_size = buf_size
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.s.connect((self.host, self.port))
        except BlockingIOError:
            pass
        print('connected: ' + str(self.s))

    def run(self):
        while not self.stopped.is_set():
            try:
                data = self.s.recv(self.buf_size).decode('utf-8')
                print(data)
            except(socket.error, IndexError, ValueError) as e:
                print(e)
                continue
        self.s.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", "-p", dest="port", default=8000, type=int, help="Port")
    parser.add_argument("--host", dest="host", default="localhost", type=str, help="Host IP")

    args = parser.parse_args()
    HOST = args.host
    PORT = args.port
    print("Server start...")
    q = queue.Queue()
    stop = threading.Event()
    tag_reader = TagReader(stop, HOST, PORT, 512)
    tag_reader.start()
