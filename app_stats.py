from random import randint
from stats import AppStats
from pathlib import Path


def read_stats(socket_address):
    sockets = {
        "9027_stats.sock": "{app1 - stats}"
    }
    if socket_address in sockets:
        return sockets[socket_address]
    else:
        return "could not lookup socket"

if __name__ == "__main__":
    counter = 0
    nodes =["127.0.0.1:9027", "127.0.0.1:9030"]
    for node in nodes:
        port = node.split(":")[-1]
        socket_address = f"{port}_stats.sock"
        stats = read_stats(socket_address)
        print(stats)

        #print(f"{worker_count=}")
        #counter = counter + worker_count
    #print(counter)


