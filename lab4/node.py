#!/usr/bin/env python3

import rpyc
from rpyc.utils.server import ThreadedServer

class ProbeEchoService(rpyc.Service):
    def __init__(self, identifier, neighbours):
        self.identifier = identifier
        self.neighbours = neighbours
        self.probed = False
        self.responses = [self.identifier]

    def on_connect(self, conn):
        pass

    def on_disconnect(self, conn):
        pass

    def exposed_election(self, callback):
        if self.probed:
            callback(None)
            return

        self.probed = True

        def new_callback(response):
            self.responses.append(response)
            if len(self.responses) == len(self.neighbours) + 1:
                print(f"{self.identifier}: received final response {max(x for x in self.responses if x is not None)}")
                callback(max(x for x in self.responses if x is not None))

        for socket in self.neighbours:
            print(f"{self.identifier}: sending to {socket[1] - 15000}")
            conn = rpyc.connect(*socket)
            conn.root.election(new_callback)
            conn.close()

def start_node(identifier, port, neighbours):
    t = ThreadedServer(ProbeEchoService(identifier, neighbours), port=port)
    t.start()

if __name__ == "__main__":
    neighbours = [
        ("127.0.0.1", 4321),
    ]
    start_node(0, 1234, neighbours)
