from pathlib import Path
from stats import AppStats
import errno
import json
import traceback
import socket
import stats
from stats import WorkerAppStats
from stats import AppStats

from rich.console import Console

from stats import RouterSubscription
import time
from rich.live import Live
from rich.table import Table
import pydantic

class RouterStats(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(strict=True)
    version: str
    pid: int = pydantic.Field(ge=0)
    uid: int = pydantic.Field(ge=0)
    gid: int = pydantic.Field(ge=0)
    cwd: str
    active_sessions: int = pydantic.Field(ge=0)
    http: list[str]  # ['0.0.0.0:8034', '127.0.0.1:5700'],
    subscriptions: list[RouterSubscription]
    cheap: int = pydantic.Field(ge=0)

def run(stats_address):
    if not all([stats_address.exists(), stats_address.is_socket()]):
        raise Exception(f"unable to read stats from {(stats_address)}")

    def unix_addr(arg):
        sfamily = socket.AF_UNIX
        addr = arg
        return sfamily, addr, socket.gethostname()

    js = ""
    sfamily, addr, host = unix_addr(stats_address)
    # console.info(f"{sfamily=} {str(addr)=} {host=}")

    try:
        s = None
        s = socket.socket(sfamily, socket.SOCK_STREAM)
        s.connect(str(addr))
        while True:
            data = s.recv(4096)
            if len(data) < 1:
                break
            js += data.decode('utf8', 'ignore')
        if s:
            s.close()
    except ConnectionRefusedError as e:
        print('connection refused')
    except FileNotFoundError as e:
        print(f"socket @ {addr} not available")
    except IOError as e:
        if e.errno != errno.EINTR:
            #uwsgi.log(f"socket @ {addr} not available")
            pass
    except Exception:
        print(traceback.format_exc())
    else:
        try:
            return json.loads(js)
        except json.JSONDecodeError:
            print(traceback.format_exc())
            print(js)

if __name__ == "__main__":
    stats_address = Path("run/sub1-stats.sock")
    stats = run(stats_address)


# class AppStats(pydantic.BaseModel):
#     model_config = pydantic.ConfigDict(strict=True)
#     version: str
#     listen_queue: int
#     listen_queue_errors: int
#     signal_queue: int
#     load: int
#     pid: int
#     uid: int
#     gid: int
#     cwd: str
#     locks: list[dict[str, int]]
#     sockets: list[stats.SocketStats]
#     workers: list[stats.WorkerStats]




nodes = ["127.0.0.1:9027", "127.0.0.1:9030"]
for node in nodes:
    port = node.split(":")[-1]
    socket_address = f"{port}_stats.sock"
    node_stats = Path("9027_stats.sock")
    print(node_stats)

stats_address2 = Path("run/9027_stats.sock")
stats2 = run(stats_address2)

app_stats = AppStats(**stats2)
print(app_stats.workers)
worker_amount = app_stats.workers
print(len(app_stats.workers)) #print amount workers

router_stats = RouterStats(**stats)
print(router_stats)

    # import ipdb;ipdb.set_trace()
for sub in router_stats.subscriptions:
    print(f"{sub.key=}")

table = Table()
table.add_column("Virtual Hosts", justify="right", style="cyan", no_wrap=True)
table.add_column("Nodes", style="magenta")
table.add_column("Total Workers", style="magenta")
table.add_row(sub.key, f"{len(sub.nodes)}", f"{len(app_stats.workers)}")

console = Console()
console.print(table)

