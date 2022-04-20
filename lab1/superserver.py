#!/usr/bin/env python3

import socket

HOST = ""
PORT = 1234

with socket.socket() as s:
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen()

    conns = []
    for i in range(2):
        conns.append(s.accept())
        print(f"Connect #{i}")

    while True:
        for conn, addr in conns:
            data = conn.recv(1024)
            print(f"Mensagem recebida de {addr}: {data.decode('utf-8')}")

            conn.sendall(data)
