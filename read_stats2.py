from pathlib import Path
import errno
import json
import traceback
import socket

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
    stats_address = Path("run/sub2-stats.sock")
    stats = run(stats_address)
    print(stats)
    router_stats = RouterStats(**stats)


    #import ipdb; ipdb.set_trace()
    table = Table()
    table.add_column("Name", justify="right", style="cyan", no_wrap=True)
    table.add_column("Subscription", style="magenta")
    table.add_column("Worker's count",  justify="right", style="green")

    for sub in router_stats.subscriptions:
        table.add_row("key", f"{sub.key=}", f"{len(sub.nodes)=}")
        table.add_row("hash", f"{sub.hash=}")
        table.add_row("hits", f"{sub.hits=}")
        table.add_row("sni_enabled", f"{sub.sni_enabled=}")
        #print(f"{sub.key=}")
        for n in sub.nodes:
            table.add_row("node's name", f"{n.name=}")
            # table.add_row("node2", f"{n.name=}")


    console = Console()
    console.print(table)




    # for field, value in router_stats.__dict__.items():
    #     table.add_row(field, str(value))
    #
    #
    #
    # console = Console()
    # console.print(table)
    #
    # for i in router_stats.__dict__.items():
    #     print(i)


