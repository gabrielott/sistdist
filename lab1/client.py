#!/usr/bin/env python3

import socket

HOST = ""
PORT = 1234

print("Digite 'exit' para sair.")

with socket.socket() as s:
    s.connect((HOST, PORT))
    print("Conexão estabelecida com o servidor.")
    data = s.recv(1024)
    print(f"Recebido do servidor: {data.decode('utf-8')}")

    while True:
        txt = input("Digite algo: ")
        if txt == "exit":
            break
        s.sendall(txt.encode("utf-8"))

        data = s.recv(1024)
        print(f"Recebido do servidor: {data.decode('utf-8')}")
