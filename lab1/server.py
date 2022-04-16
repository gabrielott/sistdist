#!/usr/bin/env python3

import socket

HOST = ""
PORT = 1234

with socket.socket() as s:
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen()

    conn, addr = s.accept()
    with conn:
        print(f"Conectado com {addr}")
        conn.sendall(b"Oi, eu sou o servidor\n")
        while True:
            data = conn.recv(1024)
            if not data:
                break
            print(f"Mensagem recebida: {data.decode('utf-8')}")

            conn.sendall(data)
