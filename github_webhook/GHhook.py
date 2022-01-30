from ipaddress import ip_address
from flask import Flask, Response, request
from requests import get
from pathlib import Path
import argparse
import json
import iptools
try:
    import LIFOtimer
    import reporeader
except ImportError:
    from . import LIFOtimer
    from . import reporeader


def parse():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "config_file",
        help="Configuration file",
        type=lambda s: str(s) 
    )
    parser.add_argument(
        "-ip",
        help="IP address of this server",
        type=lambda s: ip_address(s).__str__(),
        default="0.0.0.0"
    )
    parser.add_argument(
        "-port",
        "-p",
        help="Bind this server to this PORT",
        type=lambda s: int(s),
        default=443
    )

    return parser.parse_args()

args = parse()

config_file = args.config_file

try:
    with open(config_file, "r", encoding="UTF-8") as config:
        conf = json.load(config)
except json.decoder.JSONDecodeError:
    print("%s must be a valid configuration file" % config_file)
    exit()

SERVER_IP = args.ip
SERVER_PORT = args.port

REMOTE_URL = conf["url_repositorio"]
DIR_NAME = conf["ruta_repositorios"]
WAIT_FOR_EVENTS = conf["tiempo_espera_pull"]
UPDATE_META = conf["pedir_meta_github"]

META = "https://api.github.com/meta"
META_FILE = Path(META).stem

AVAILABLE_METHOD = "push"

app = Flask(__name__)

@app.post("/")
def hook():
    request.get_json(force=True)

    try:
        from_repo = request.json["repository"]["html_url"]
    except KeyError:
        return Response(status=400)

    try:
        sender_ip = request.headers["X-Forwarded-For"]
    except KeyError:
        sender_ip = request.remote_addr

    for ip in ips:
        range = iptools.IpRangeList(ip)

        if not sender_ip in range:
            continue

        if not REMOTE_URL.find(from_repo) == -1:
            LIFOtimer.refresh(reporeader.pull, WAIT_FOR_EVENTS, DIR_NAME, REMOTE_URL)
            return Response(status=200)

        break

    return Response(status=400)

if __name__ == "__main__":

    try:
        if not UPDATE_META: raise KeyError()
        meta = get(META).json()
        ips = meta["hooks"]
        with open(META_FILE, "w") as fp:
            json.dump(meta, fp)
    except KeyError:
        if not Path(META_FILE).is_file():
            print("%s is not a file, enable 'pedir_meta_github' to fetch '%s'" % (META_FILE, META))
            exit()
        with open(META_FILE, "r") as fp:
            meta = json.load(fp)

    ips = meta["hooks"]

    LIFOtimer.refresh(reporeader.pull, 0, DIR_NAME, REMOTE_URL)

    app.run(
        host=               SERVER_IP,
        port=               SERVER_PORT,
        ssl_context=        'adhoc'
    )
