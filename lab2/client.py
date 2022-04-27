#!/usr/bin/env python3

import socket, sys

HOST = ""
PORT = 1234

if len(sys.argv) != 2:
    print("Uso: ./client.py NOME_DO_ARQUIVO")
    exit(1)

file = sys.argv[1]

with socket.socket() as s:
    s.connect((HOST, PORT))

    s.sendall(file.encode("utf-8"))
    ans = s.recv(1024)

    print(ans.decode("utf-8"))
