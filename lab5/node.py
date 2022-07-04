#!/usr/bin/env python3

import sys, rpyc
from rpyc.utils.server import ThreadedServer
from threading import Lock, Thread

NNODES = 4
server = None

class NodeService(rpyc.Service):
    def __init__(self, identifier, n):
        self.identifier = identifier
        self.x = 0
        self.n = n
        self.primary = (self.identifier == 1)
        self.history = []
        self.lock = Lock()

    # Chamado pela cópia primária durante o broadcast
    def exposed_update(self, sender, x):
        if self.primary:
            print(f"{self.identifier}: Cópia não primária tentou fazer broadcast.")

        with self.lock:
            self.x = x
            self.history.append((sender, self.x))

    # Chamado por uma outra cópia que quer se tornar primária
    def exposed_request_primary(self):
        with self.lock:
            if self.primary:
                self.primary = False
                return True

    # Chamado quando a própria cópia quer atualizar a variável
    def exposed_write(self, x):
        with self.lock:
            self.become_primary()
            self.x = x
            self.history.append((self.identifier, self.x))
            self.broadcast()

    def exposed_read(self):
        return self.x

    def exposed_history(self):
        return self.history

    def exposed_primary(self):
        return self.primary

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
            conn.root.update(self.identifier, self.x)
            conn.close()

def start_node(identifier):
    global server
    server = ThreadedServer(NodeService(identifier, NNODES), port=15000+identifier)
    server.start()

def main():
    identifier = int(sys.argv[1])

    thread = Thread(target=start_node, args=(identifier,))
    thread.start()

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
        elif cmd == "history":
            for sender, value in conn.root.history():
                print(f"{sender}: {value}")
        elif cmd == "whoami":
            print(identifier)
        elif cmd == "primary":
            print(conn.root.primary())
        elif cmd in ["help", "h", "?"]:
            print("Comandos:")
            print("read --> Imprime valor atual de x")
            print("write <n> -> Modifica valor de x para n")
            print("history -> Imprime o histórico")
            print("whoami -> Imprime o identificador da node")
            print("primary -> Imprime true se a node é a cópia primária, false caso contrário")
        elif cmd == "exit":
            server.close()
            break

if __name__ == "__main__":
    main()
