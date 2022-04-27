#!/usr/bin/env python3

import socket, os, re

HOST = ""
PORT = 1234

with socket.socket() as s:
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen()

    while True:
        conn, addr = s.accept()
        with conn:
            # Recebe e trata o nome do arquivo
            # A função basename garante que só arquivos no diretório atual sejam acessíveis.
            file = conn.recv(1024)
            file = file.decode("utf-8")
            file = os.path.basename(file)

            if not os.path.isfile(file):
                conn.sendall("Arquivo não existe.".encode("utf-8"))
                print(f"{addr} requisitou arquivo '{file}', que não existe.")
                continue

            print(f"{addr} requisitou arquivo '{file}' com sucesso.")

            # Conta ocorrências de cada palavra
            occurrences = {}
            with open(file, "rt") as f:
                while True:
                    line = f.readline()
                    if not line:
                        break

                    split = re.split(r"\W+", line)
                    for word in filter(lambda w: w, split):
                        occurrences[word] = occurrences.get(word, 0) + 1

            # Ordena palavras de acordo com suas ocorrências
            words = list(occurrences.keys())
            words.sort(key=lambda w: occurrences[w], reverse=True)

            # Envia resposta ao cliente
            ans = "/".join(words[:5]).encode("utf-8")
            conn.sendall(ans)
