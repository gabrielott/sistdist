#!/usr/bin/env python3

import sys, rpyc
from rpyc.utils.server import ThreadedServer
from threading import Lock, Thread

NNODES = 2

class NodeService(rpyc.Service):
    def __init__(self, identifier, n):
        self.identifier = identifier
        self.x = 0
        self.n = n
        self.primary = (self.identifier == 1)
        self.lock = Lock()

    def exposed_read(self):
        return self.x

    # Chamado pela cópia primária durante o broadcast
    def exposed_update(self, x):
        with self.lock:
            self.x = x

    # Chamado por uma outra cópia que quer se tornar primária
    def exposed_request_primary(self):
        with self.lock:
            return self.primary

    # Chamado quando a própria cópia quer atualizar a variável
    def exposed_write(self, x):
        with self.lock:
            self.become_primary()
            self.x = x
            self.broadcast()

    def become_primary(self):
        if not self.primary:
            for identifier in range(1, self.n + 1):
                if identifier == self.identifier:
                    continue
                conn = rpyc.connect("127.0.0.1", 15000 + identifier)
                self.primary = conn.root.request_primary()
                conn.close()
                if self.primary:
                    break
            else:
                print(f"{self.identifier}: Erro ao tentar virar cópia primária")

    def broadcast(self):
        for identifier in range(1, self.n + 1):
            if identifier == self.identifier:
                continue
            conn = rpyc.connect("127.0.0.1", 15000 + identifier)
            conn.root.update(self.x)
            conn.close()

def start_node(identifier):
    t = ThreadedServer(NodeService(identifier, NNODES), port=15000+identifier)
    t.start()

def main():
    identifier = int(sys.argv[1])

    server = Thread(target=start_node, args=(identifier,))
    server.start()

    conn = rpyc.connect("127.0.0.1", 15000 + identifier)

    while True:
        cmdline = input("> ")

        split = cmdline.split()
        cmd = split[0]
        if len(split) > 1:
            arg = split[1]

        if cmd == "read":
            print(conn.root.read())
        elif cmd == "write":
            conn.root.write(int(arg))
        elif cmd == "exit":
            exit()


if __name__ == "__main__":
    main()
