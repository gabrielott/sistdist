#!/usr/bin/env python3

import multiprocessing, rpyc, time
from node import start_node

def main():
    nodes = []

    nodes.append((1, 15001, [("127.0.0.1", 15002), ("127.0.0.1", 15003)]))
    nodes.append((2, 15002, [("127.0.0.1", 15001), ("127.0.0.1", 15007), ("127.0.0.1", 15009)]))
    nodes.append((3, 15003, [("127.0.0.1", 15001), ("127.0.0.1", 15004)]))
    nodes.append((4, 15004, [("127.0.0.1", 15003), ("127.0.0.1", 15005)]))
    nodes.append((5, 15005, [("127.0.0.1", 15004), ("127.0.0.1", 15006), ("127.0.0.1", 15007)]))
    nodes.append((6, 15006, [("127.0.0.1", 15005), ("127.0.0.1", 15008)]))
    nodes.append((7, 15007, [("127.0.0.1", 15005), ("127.0.0.1", 15002), ("127.0.0.1", 15010)]))
    nodes.append((8, 15008, [("127.0.0.1", 15006), ("127.0.0.1", 15010)]))
    nodes.append((9, 15009, [("127.0.0.1", 15002)]))
    nodes.append((10, 15010, [("127.0.0.1", 15007), ("127.0.0.1", 15008)]))

    processes = []
    for i in range(10):
        processes.append(multiprocessing.Process(target=start_node, args=nodes[i]))
        processes[i].start()

    time.sleep(1)

    def callback(response):
        print(f"response: {response}")

    conn = rpyc.connect("127.0.0.1", 15001)
    conn.root.election(callback)

    for i in range(10):
        processes[i].join()

if __name__ == "__main__":
    main()
