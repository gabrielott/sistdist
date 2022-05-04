#!/usr/bin/env python3

import socket, os, re, sys, threading
from select import select

HOST = ""
PORT = 1234

def handle_request(conn, addr):
    with conn:
        # Recebe e trata o nome do arquivo
        # A função basename garante que só arquivos no diretório atual sejam acessíveis.
        file = conn.recv(1024)
        file = file.decode("utf-8")
        file = os.path.basename(file)

        if not os.path.isfile(file):
            conn.sendall("Arquivo não existe.".encode("utf-8"))
            print(f"{addr} requisitou o arquivo '{file}', que não existe.")
            return

        print(f"{addr} requisitou o arquivo '{file}' com sucesso.")

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

def handle_command(cmd):
    if cmd == "exit":
        if len(threading.enumerate()) > 1:
            print("Aguardando todas as conexões serem terminadas...")
            for thread in filter(lambda t: t is not threading.current_thread(), threading.enumerate()):
                thread.join()

        sys.exit()
    else:
        print("Comando desconhecido.")

def main():
    with socket.socket() as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen()
        s.setblocking(False)

        while True:
            read, _, _ = select([sys.stdin, s], [], [])

            for ready in read:
                if ready is s:
                    client = s.accept()
                    thread = threading.Thread(target=handle_request, args=client)
                    thread.start()
                elif ready is sys.stdin:
                    cmd = input()
                    handle_command(cmd)

if __name__ == "__main__":
    main()
