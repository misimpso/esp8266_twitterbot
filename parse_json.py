class ParseJson:

    def __init__(self, filter_map):
        self.filter_map = filter_map

    def parse(self, socket):
        data = socket.recv(1024)
        print(data)
        return 0